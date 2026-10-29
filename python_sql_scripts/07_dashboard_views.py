"""Step 7: create the Power BI summary views."""

from common import db, execute, print_rows, query_all, require_tables, run_timed, write_results_xlsx


VIEWS = [
    """
    CREATE OR REPLACE VIEW dashboard_kpis AS
    SELECT ra.total_ratings,
           (SELECT COUNT(DISTINCT user_id) FROM ratings) total_users,
           (SELECT COUNT(*) FROM movies) total_movies,
           (SELECT COUNT(*) FROM tags) total_tags,
           ra.average_rating, ra.positive_rating_rate
    FROM (
        -- One scan of ratings instead of three separate full scans.
        SELECT COUNT(*) total_ratings, AVG(rating) average_rating,
               AVG(rating >= 4.0) positive_rating_rate
        FROM ratings
    ) ra
    """,
    """
    CREATE OR REPLACE VIEW dashboard_rating_distribution AS
    SELECT rating, COUNT(*) rating_count,
           COUNT(*) / SUM(COUNT(*)) OVER () rating_share
    FROM ratings GROUP BY rating
    """,
    # Same optimised query as rubric query 3 in 05_feature_tables.py.
    """
    CREATE OR REPLACE VIEW dashboard_genre_kpis AS
    SELECT mg.genre,
           CAST(SUM(ma.rating_count) AS UNSIGNED) rating_count,
           SUM(ma.rating_sum)/SUM(ma.rating_count) avg_rating,
           SUM(ma.positive_count)/SUM(ma.rating_count) positive_rate
    FROM (
        SELECT /*+ NO_INDEX(ratings) */
               movie_id, COUNT(*) rating_count, SUM(rating) rating_sum,
               SUM(rating>=4.0) positive_count
        FROM ratings GROUP BY movie_id
    ) ma
    JOIN movie_genres mg ON mg.movie_id=ma.movie_id
    GROUP BY mg.genre
    """,
    """
    CREATE OR REPLACE VIEW dashboard_movie_popularity AS
    SELECT m.movie_id, m.title, m.genres, ms.rating_count, ms.avg_rating, ms.positive_rate
    FROM train_movie_stats ms JOIN movies m ON m.movie_id=ms.movie_id
    WHERE ms.rating_count>=100
    """,
    # Bayesian average with m = 100 prior ratings pulls low-count titles towards
    # the TRAIN mean; wilson_positive_low is the 95% Wilson lower bound.
    """
    CREATE OR REPLACE VIEW dashboard_movie_adjusted_scores AS
    SELECT m.movie_id, m.title, m.genres, ms.rating_count, ms.avg_rating,
           (ms.rating_sum + 100*g.global_avg)/(ms.rating_count + 100) bayesian_avg_rating,
           ms.positive_rate,
           (ms.positive_count + 100*g.global_positive_rate)/(ms.rating_count + 100)
               bayesian_positive_rate,
           (ms.positive_rate + 1.9208/ms.rating_count
               - 1.96*SQRT((ms.positive_rate*(1-ms.positive_rate) + 0.9604/ms.rating_count)
                           /ms.rating_count))
               /(1 + 3.8416/ms.rating_count) wilson_positive_low
    FROM train_movie_stats ms JOIN movies m ON m.movie_id=ms.movie_id
    CROSS JOIN (
        SELECT SUM(rating_sum)/SUM(rating_count) global_avg,
               SUM(positive_count)/SUM(rating_count) global_positive_rate
        FROM train_movie_stats
    ) g
    """,
    # Joins 10M rows (a few minutes); the split only changes when step 4 reruns.
    """
    CREATE OR REPLACE VIEW dashboard_split_summary AS
    SELECT s.data_split, COUNT(*) rows_in_split,
           FROM_UNIXTIME(MIN(r.rating_ts)) period_start,
           FROM_UNIXTIME(MAX(r.rating_ts)) period_end
    FROM rating_split s JOIN ratings r ON r.rating_id=s.rating_id
    GROUP BY s.data_split
    """,
    """
    CREATE OR REPLACE VIEW dashboard_segment_profiles AS
    SELECT seg.cluster_id, seg.segment_name, COUNT(*) user_count,
           AVG(us.rating_count) avg_user_ratings, AVG(us.avg_rating) avg_rating,
           AVG(us.positive_rate) avg_positive_rate,
           AVG(us.rating_stddev) avg_rating_stddev, AVG(us.active_days) avg_active_days
    FROM user_segments seg JOIN train_user_stats us ON us.user_id=seg.user_id
    GROUP BY seg.cluster_id, seg.segment_name
    """,
    """
    CREATE OR REPLACE VIEW dashboard_segment_genres AS
    SELECT seg.cluster_id, seg.segment_name, ugs.genre,
           COUNT(DISTINCT ugs.user_id) users_with_genre,
           SUM(ugs.genre_rating_count) genre_rating_count,
           AVG(ugs.genre_avg_rating) avg_genre_rating,
           AVG(ugs.genre_positive_rate) avg_genre_positive_rate
    FROM user_segments seg JOIN train_user_genre_stats ugs ON ugs.user_id=seg.user_id
    GROUP BY seg.cluster_id, seg.segment_name, ugs.genre
    """,
    """
    CREATE OR REPLACE VIEW dashboard_content_opportunities AS
    SELECT rp.model_version, rp.cluster_id, seg.segment_name, rp.movie_id, m.title, m.genres,
           COUNT(*) test_support, AVG(rp.probability_liked) predicted_like_probability,
           AVG(rp.actual_liked) actual_positive_rate,
           ms.rating_count train_popularity, ms.avg_rating train_avg_rating
    FROM rating_predictions rp
    JOIN movies m ON m.movie_id=rp.movie_id
    JOIN train_movie_stats ms ON ms.movie_id=rp.movie_id
    JOIN user_segments seg
      ON seg.user_id=rp.user_id AND seg.cluster_id=rp.cluster_id
    WHERE rp.data_split='TEST'
    -- rating_predictions is keyed by (rating_id, model_version); grouping by
    -- version stops a second model run from doubling test_support.
    GROUP BY rp.model_version, rp.cluster_id, seg.segment_name, rp.movie_id, m.title, m.genres,
             ms.rating_count, ms.avg_rating
    """,
    # 95% Wilson interval of the TEST positive rate per segment-title cell.
    """
    CREATE OR REPLACE VIEW dashboard_opportunity_intervals AS
    SELECT o.model_version, o.cluster_id, o.segment_name, o.movie_id, o.title, o.test_support,
           o.predicted_like_probability, o.actual_positive_rate,
           (o.actual_positive_rate + 1.9208/o.test_support
               - 1.96*SQRT((o.actual_positive_rate*(1-o.actual_positive_rate)
                            + 0.9604/o.test_support)/o.test_support))
               /(1 + 3.8416/o.test_support) positive_rate_ci_low,
           (o.actual_positive_rate + 1.9208/o.test_support
               + 1.96*SQRT((o.actual_positive_rate*(1-o.actual_positive_rate)
                            + 0.9604/o.test_support)/o.test_support))
               /(1 + 3.8416/o.test_support) positive_rate_ci_high
    FROM dashboard_content_opportunities o
    """,
    # Four rows per model version and split instead of millions of predictions.
    """
    CREATE OR REPLACE VIEW dashboard_confusion_matrix AS
    SELECT model_version, data_split, actual_liked, predicted_liked, COUNT(*) row_count
    FROM rating_predictions
    GROUP BY model_version, data_split, actual_liked, predicted_liked
    """,
    """
    CREATE OR REPLACE VIEW dashboard_model_metrics AS
    SELECT model_name, model_version, split_name, metric_name, metric_value, run_timestamp
    FROM model_metrics
    """,
]


def main() -> None:
    with db() as connection:
        require_tables(
            connection,
            ("ratings", "movies", "tags", "movie_genres", "rating_split", "user_segments",
             "train_user_stats", "train_user_genre_stats", "rating_predictions",
             "train_movie_stats", "model_metrics"),
        )
        for statement in VIEWS:
            execute(connection, statement)
        results = []
        for view in (
            "dashboard_kpis", "dashboard_rating_distribution", "dashboard_genre_kpis",
            "dashboard_movie_popularity", "dashboard_movie_adjusted_scores",
            "dashboard_split_summary",
            "dashboard_segment_profiles", "dashboard_segment_genres",
            "dashboard_content_opportunities", "dashboard_opportunity_intervals",
            "dashboard_confusion_matrix",
            "dashboard_model_metrics",
        ):
            columns, rows = run_timed(
                f"query {view}",
                lambda v=view: query_all(connection, f"SELECT * FROM `{v}` LIMIT 20"),
                connection=connection,
            )
            print_rows(view, columns, rows)
            results.append((view.removeprefix("dashboard_"), columns, rows))
        write_results_xlsx(__file__, results)


if __name__ == "__main__":
    main()


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
            ("ratings", "movies", "tags", "user_segments", "train_user_stats",
             "train_user_genre_stats", "rating_predictions", "train_movie_stats", "model_metrics"),
        )
        for statement in VIEWS:
            execute(connection, statement)
        results = []
        for view in (
            "dashboard_kpis", "dashboard_segment_profiles", "dashboard_segment_genres",
            "dashboard_content_opportunities", "dashboard_model_metrics",
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


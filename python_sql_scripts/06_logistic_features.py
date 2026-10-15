"""Step 6: create the KNIME logistic-regression feature view."""

from common import db, execute, print_rows, query_all, require_tables, run_timed, scalar, write_results_xlsx


GENRES = [
    ("Action", "action"), ("Adventure", "adventure"), ("Animation", "animation"),
    ("Children", "children"), ("Comedy", "comedy"), ("Crime", "crime"),
    ("Documentary", "documentary"), ("Drama", "drama"), ("Fantasy", "fantasy"),
    ("Film-Noir", "film_noir"), ("Horror", "horror"), ("Musical", "musical"),
    ("Mystery", "mystery"), ("Romance", "romance"), ("Sci-Fi", "scifi"),
    ("Thriller", "thriller"), ("War", "war"), ("Western", "western"),
]


def main() -> None:
    with db() as connection:
        require_tables(
            connection,
            ("ratings", "rating_split", "movies", "train_user_stats", "train_movie_stats", "user_segments"),
        )
        if int(scalar(connection, "SELECT COUNT(*) FROM user_segments")) == 0:
            raise RuntimeError("user_segments is empty; run the KNIME clustering write-back first")
        # A DB Writer with "Remove existing table" recreates user_segments with
        # cluster_id as text ('cluster_0'); joins to the INT cluster_id in
        # rating_predictions then silently match nothing.
        cluster_type = scalar(
            connection,
            "SELECT DATA_TYPE FROM information_schema.columns "
            "WHERE table_schema = DATABASE() AND table_name = 'user_segments' "
            "AND column_name = 'cluster_id'",
        )
        if str(cluster_type).lower() not in {"int", "tinyint", "smallint", "mediumint", "bigint"}:
            raise RuntimeError(
                f"user_segments.cluster_id is {cluster_type}, expected INT. "
                "Run sql/migrate_user_segments.sql once, and keep "
                "'Remove existing table' unticked in the KNIME DB Writer."
            )
        genre_sql = ",\n".join(
            f"CASE WHEN FIND_IN_SET('{genre}', REPLACE(m.genres, '|', ',')) > 0 "
            f"THEN 1 ELSE 0 END AS genre_{alias}"
            for genre, alias in GENRES
        )
        execute(connection, "DROP VIEW IF EXISTS ml_rating_features")
        execute(
            connection,
            f"""
            CREATE VIEW ml_rating_features AS
            SELECT r.rating_id, r.user_id, r.movie_id, s.data_split,
              CASE WHEN r.rating >= 4.0 THEN 1 ELSE 0 END liked,
              CASE WHEN s.data_split='TRAIN' AND us.rating_count>1
                THEN (us.rating_sum-r.rating)/(us.rating_count-1) ELSE us.avg_rating END user_prior_avg_rating,
              CASE WHEN s.data_split='TRAIN' AND us.rating_count>1
                THEN (us.positive_count-(r.rating>=4.0))/(us.rating_count-1) ELSE us.positive_rate END user_prior_positive_rate,
              us.rating_count user_activity, us.rating_stddev user_rating_stddev, us.active_days user_active_days,
              CASE WHEN s.data_split='TRAIN' AND ms.rating_count>1
                THEN (ms.rating_sum-r.rating)/(ms.rating_count-1) ELSE ms.avg_rating END movie_prior_avg_rating,
              CASE WHEN s.data_split='TRAIN' AND ms.rating_count>1
                THEN (ms.positive_count-(r.rating>=4.0))/(ms.rating_count-1) ELSE ms.positive_rate END movie_prior_positive_rate,
              ms.rating_count movie_popularity, ms.rating_stddev movie_rating_stddev, seg.cluster_id,
              {genre_sql}
            FROM ratings r
            JOIN rating_split s ON s.rating_id=r.rating_id
            JOIN movies m ON m.movie_id=r.movie_id
            JOIN train_user_stats us ON us.user_id=r.user_id
            JOIN train_movie_stats ms ON ms.movie_id=r.movie_id
            JOIN user_segments seg ON seg.user_id=r.user_id
            WHERE us.rating_count>1 AND ms.rating_count>1
            """,
        )
        # Plan section 16 requires reporting how many rows the warm-start
        # filter drops per split. The split totals come from the small
        # rating_split index, so this costs one pass over the view as before.
        columns, rows = run_timed(
            "count feature rows and cold-start exclusions",
            lambda: query_all(
                connection,
                """
                SELECT t.data_split, t.total_rows,
                       COALESCE(f.feature_rows, 0) feature_rows,
                       t.total_rows - COALESCE(f.feature_rows, 0) cold_start_excluded_rows,
                       (t.total_rows - COALESCE(f.feature_rows, 0)) / t.total_rows cold_start_excluded_rate
                FROM (
                    SELECT data_split, COUNT(*) total_rows
                    FROM rating_split GROUP BY data_split
                ) t
                LEFT JOIN (
                    SELECT data_split, COUNT(*) feature_rows
                    FROM ml_rating_features GROUP BY data_split
                ) f ON f.data_split = t.data_split
                ORDER BY t.data_split
                """,
            ),
            connection=connection,
        )
        print_rows("Feature rows", columns, rows)
        write_results_xlsx(__file__, [("Feature rows", columns, rows)])


if __name__ == "__main__":
    main()


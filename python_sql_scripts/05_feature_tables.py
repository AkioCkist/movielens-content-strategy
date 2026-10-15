"""Step 5: build leakage-safe TRAIN aggregates with atomic publication."""

import argparse

from common import (
    db,
    execute,
    print_rows,
    query_all,
    require_tables,
    run_timed,
    scalar,
    swap_staging_tables,
    write_results_xlsx,
)


BUILDS = [
    (
        "train_user_stats",
        """
        CREATE TABLE train_user_stats_staging (
            user_id INT UNSIGNED NOT NULL,
            rating_count BIGINT UNSIGNED NOT NULL,
            rating_sum DECIMAL(20,2) NOT NULL,
            avg_rating DOUBLE NOT NULL,
            rating_stddev DOUBLE NULL,
            positive_count BIGINT UNSIGNED NOT NULL,
            positive_rate DOUBLE NOT NULL,
            distinct_movies BIGINT UNSIGNED NOT NULL,
            first_rating_ts INT UNSIGNED NOT NULL,
            last_rating_ts INT UNSIGNED NOT NULL,
            active_days INT NOT NULL,
            PRIMARY KEY (user_id)
        ) ENGINE=InnoDB
        """,
        """
        INSERT INTO train_user_stats_staging
        SELECT r.user_id, COUNT(*), SUM(r.rating), AVG(r.rating), STDDEV_SAMP(r.rating),
               SUM(r.rating >= 4.0), AVG(r.rating >= 4.0), COUNT(DISTINCT r.movie_id),
               MIN(r.rating_ts), MAX(r.rating_ts),
               DATEDIFF(FROM_UNIXTIME(MAX(r.rating_ts)), FROM_UNIXTIME(MIN(r.rating_ts)))
        FROM rating_split s STRAIGHT_JOIN ratings r ON r.rating_id=s.rating_id
        WHERE s.data_split='TRAIN' GROUP BY r.user_id
        """,
    ),
    (
        "train_movie_stats",
        """
        CREATE TABLE train_movie_stats_staging (
            movie_id INT UNSIGNED NOT NULL,
            rating_count BIGINT UNSIGNED NOT NULL,
            rating_sum DECIMAL(20,2) NOT NULL,
            avg_rating DOUBLE NOT NULL,
            rating_stddev DOUBLE NULL,
            positive_count BIGINT UNSIGNED NOT NULL,
            positive_rate DOUBLE NOT NULL,
            distinct_users BIGINT UNSIGNED NOT NULL,
            PRIMARY KEY (movie_id)
        ) ENGINE=InnoDB
        """,
        """
        INSERT INTO train_movie_stats_staging
        SELECT r.movie_id, COUNT(*), SUM(r.rating), AVG(r.rating), STDDEV_SAMP(r.rating),
               SUM(r.rating >= 4.0), AVG(r.rating >= 4.0), COUNT(DISTINCT r.user_id)
        FROM rating_split s STRAIGHT_JOIN ratings r ON r.rating_id=s.rating_id
        WHERE s.data_split='TRAIN' GROUP BY r.movie_id
        """,
    ),
    (
        "train_user_genre_stats",
        """
        CREATE TABLE train_user_genre_stats_staging (
            user_id INT UNSIGNED NOT NULL,
            genre VARCHAR(50) NOT NULL,
            genre_rating_count BIGINT UNSIGNED NOT NULL,
            genre_avg_rating DOUBLE NOT NULL,
            genre_positive_rate DOUBLE NOT NULL,
            PRIMARY KEY (user_id, genre),
            INDEX idx_user_genre_genre (genre)
        ) ENGINE=InnoDB
        """,
        """
        INSERT INTO train_user_genre_stats_staging
        SELECT r.user_id, mg.genre, COUNT(*), AVG(r.rating), AVG(r.rating >= 4.0)
        FROM rating_split s
        STRAIGHT_JOIN ratings r ON r.rating_id=s.rating_id
        STRAIGHT_JOIN movie_genres mg ON mg.movie_id=r.movie_id
        WHERE s.data_split='TRAIN' GROUP BY r.user_id, mg.genre
        """,
    ),
]

USER_SEGMENTS_DDL = """
CREATE TABLE user_segments (
    user_id INT UNSIGNED NOT NULL,
    cluster_id INT NOT NULL,
    segment_name VARCHAR(100) NOT NULL,
    distance_to_centroid DECIMAL(18,8) NULL,
    model_version VARCHAR(50) NOT NULL,
    model_run_date DATETIME NOT NULL,
    PRIMARY KEY (user_id),
    INDEX idx_user_segments_cluster (cluster_id),
    INDEX idx_user_segments_version (model_version)
) ENGINE=InnoDB
"""

RUBRIC_QUERIES = [
    (
        "High ratings since 2005 (sample)",
        "SELECT * FROM ratings WHERE rating>=4.0 "
        "AND rating_ts>=UNIX_TIMESTAMP('2005-01-01') LIMIT 100",
    ),
    (
        "Rating distribution",
        """
        SELECT rating, COUNT(*) rating_count,
               ROUND(100.0*COUNT(*)/SUM(COUNT(*)) OVER (), 2) rating_percent
        FROM ratings GROUP BY rating ORDER BY rating
        """,
    ),
    (
        "Genre KPIs",
        # Aggregate 10M ratings to ~10.7K movie rows in one sequential scan,
        # then fan out to genres. Same result as joining every rating to
        # movie_genres (~20M joined rows), because count, sum and positive
        # count are additive: AVG = SUM(sum)/SUM(count). NO_INDEX keeps the
        # inner GROUP BY on a sequential scan instead of 10M random primary-key
        # lookups through idx_ratings_movie (which does not cover rating).
        """
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
        GROUP BY mg.genre ORDER BY rating_count DESC
        """,
    ),
    (
        "Top TRAIN movies (minimum 100 ratings)",
        """
        SELECT m.movie_id, m.title, ms.rating_count, ms.avg_rating, ms.positive_rate
        FROM train_movie_stats ms JOIN movies m ON m.movie_id=ms.movie_id
        WHERE ms.rating_count>=100
        ORDER BY ms.avg_rating DESC, ms.rating_count DESC LIMIT 20
        """,
    ),
]


def run_rubric_queries(connection) -> None:
    require_tables(
        connection,
        ("ratings", "movie_genres", "movies", "train_movie_stats"),
    )
    results = []
    for title, sql in RUBRIC_QUERIES:
        columns, rows = run_timed(
            title,
            lambda q=sql: query_all(connection, q),
            connection=connection,
        )
        print_rows(title, columns, rows)
        results.append((title, columns, rows))
    write_results_xlsx(__file__, results)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--queries-only",
        action="store_true",
        help="Run only the four KPI/rubric queries from section 12.4",
    )
    args = parser.parse_args()
    with db() as connection:
        if args.queries_only:
            run_rubric_queries(connection)
            return
        execute(connection, "DROP TABLE IF EXISTS user_segments")
        execute(connection, USER_SEGMENTS_DDL)
        require_tables(connection, ("ratings", "rating_split", "movie_genres"))
        publish: list[tuple[str, str]] = []
        for target, create_sql, insert_sql in BUILDS:
            staging = f"{target}_staging"
            execute(connection, f"DROP TABLE IF EXISTS `{staging}`")
            execute(connection, create_sql)
            run_timed(
                f"build {target}",
                lambda q=insert_sql: execute(connection, q),
                connection=connection,
            )
            count = int(scalar(connection, f"SELECT COUNT(*) FROM `{staging}`"))
            if count == 0:
                raise RuntimeError(f"Refusing to publish empty table {target}")
            publish.append((target, staging))
            print(f"[info] {target}: {count:,} rows")
        run_timed(
            "atomically publish all feature tables",
            lambda: swap_staging_tables(connection, publish),
            connection=connection,
        )
        run_rubric_queries(connection)


if __name__ == "__main__":
    main()

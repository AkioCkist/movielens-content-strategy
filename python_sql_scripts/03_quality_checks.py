"""Step 3: run data-quality checks and print a compact report."""

from common import db, print_rows, query_all, require_tables, run_timed, write_results_xlsx


CHECKS = [
    (
        "Row counts",
        """
        SELECT
          (SELECT COUNT(*) FROM ratings) AS rating_rows,
          (SELECT COUNT(*) FROM movies) AS movie_rows,
          (SELECT COUNT(*) FROM tags) AS tag_rows,
          (SELECT COUNT(DISTINCT user_id) FROM ratings) AS users,
          (SELECT COUNT(DISTINCT movie_id) FROM ratings) AS rated_movies
        """,
    ),
    (
        "Rating range",
        "SELECT MIN(rating) minimum_rating, MAX(rating) maximum_rating, "
        "AVG(rating) average_rating FROM ratings",
    ),
    (
        "Rating period",
        "SELECT FROM_UNIXTIME(MIN(rating_ts)) first_rating, "
        "FROM_UNIXTIME(MAX(rating_ts)) last_rating FROM ratings",
    ),
    (
        "Rating distribution",
        "SELECT rating, COUNT(*) rating_count FROM ratings GROUP BY rating ORDER BY rating",
    ),
    (
        "Orphan ratings",
        "SELECT COUNT(*) orphan_ratings FROM ratings r "
        "LEFT JOIN movies m ON m.movie_id=r.movie_id WHERE m.movie_id IS NULL",
    ),
    (
        "Orphan tags",
        "SELECT COUNT(*) orphan_tags FROM tags t "
        "LEFT JOIN movies m ON m.movie_id=t.movie_id WHERE m.movie_id IS NULL",
    ),
    (
        "Duplicate user/movie pairs (sample)",
        # ~10M distinct groups overflow the in-memory temp table; SQL_BIG_RESULT
        # makes MySQL group by sorting instead of a disk-based temp table.
        "SELECT SQL_BIG_RESULT user_id, movie_id, COUNT(*) duplicate_count FROM ratings "
        "GROUP BY user_id, movie_id HAVING COUNT(*) > 1 "
        "ORDER BY user_id, movie_id LIMIT 20",
    ),
    (
        "Invalid rows",
        "SELECT SUM(rating NOT BETWEEN 0.5 AND 5.0 OR MOD(rating*10,5)<>0) "
        "invalid_rating_rows, SUM(rating_ts=0) invalid_timestamp_rows FROM ratings",
    ),
    (
        "Users below 20 ratings",
        "SELECT COUNT(*) users_below_minimum_history FROM "
        "(SELECT user_id FROM ratings GROUP BY user_id HAVING COUNT(*)<20) x",
    ),
]


def main() -> None:
    with db() as connection:
        require_tables(connection, ("ratings", "movies", "tags"))
        results = []
        for title, sql in CHECKS:
            columns, rows = run_timed(
                title,
                lambda q=sql: query_all(connection, q),
                connection=connection,
            )
            print_rows(title, columns, rows)
            results.append((title, columns, rows))
        write_results_xlsx(__file__, results)


if __name__ == "__main__":
    main()


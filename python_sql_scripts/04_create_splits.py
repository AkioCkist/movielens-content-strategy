"""Step 4: create an exact chronological 70/15/15 split without NTILE."""

from common import (
    db,
    execute,
    print_rows,
    query_all,
    require_tables,
    run_timed,
    scalar,
    swap_staging_table,
    write_results_xlsx,
)


STAGING = "rating_split_staging"


def boundary(connection, offset: int) -> tuple[int, int]:
    columns, rows = query_all(
        connection,
        "SELECT rating_ts, rating_id FROM ratings "
        "ORDER BY rating_ts, rating_id LIMIT 1 OFFSET %s",
        (max(0, offset),),
    )
    if not rows:
        raise RuntimeError(f"Could not find split boundary at offset {offset}")
    return int(rows[0][0]), int(rows[0][1])


def main() -> None:
    with db() as connection:
        require_tables(connection, ("ratings",))
        total = int(scalar(connection, "SELECT COUNT(*) FROM ratings"))
        if total < 3:
            raise RuntimeError("At least 3 ratings are required")
        # Match MySQL NTILE(20) exactly: earlier buckets receive the remainder.
        bucket_size, remainder = divmod(total, 20)
        train_rows = 14 * bucket_size + min(remainder, 14)
        valid_rows = 3 * bucket_size + max(0, min(remainder - 14, 3))
        train_end = boundary(connection, train_rows - 1)
        valid_end = boundary(connection, train_rows + valid_rows - 1)
        print(f"Rows: {total:,}; TRAIN={train_rows:,}; VALID={valid_rows:,}; TEST={total-train_rows-valid_rows:,}")

        execute(connection, f"DROP TABLE IF EXISTS {STAGING}")
        execute(
            connection,
            f"""
            CREATE TABLE {STAGING} (
                rating_id BIGINT UNSIGNED NOT NULL,
                data_split VARCHAR(5) NOT NULL,
                PRIMARY KEY (rating_id),
                INDEX idx_rating_split_name (data_split)
            ) ENGINE=InnoDB
            """,
        )
        run_timed(
            "build chronological split",
            lambda: execute(
                connection,
                f"""
                INSERT INTO {STAGING} (rating_id, data_split)
                SELECT rating_id,
                    CASE
                      WHEN (rating_ts < %s OR (rating_ts = %s AND rating_id <= %s)) THEN 'TRAIN'
                      WHEN (rating_ts < %s OR (rating_ts = %s AND rating_id <= %s)) THEN 'VALID'
                      ELSE 'TEST'
                    END
                FROM ratings
                """,
                (train_end[0], train_end[0], train_end[1], valid_end[0], valid_end[0], valid_end[1]),
            ),
            connection=connection,
        )
        staged = int(scalar(connection, f"SELECT COUNT(*) FROM {STAGING}"))
        if staged != total:
            raise RuntimeError(f"Split validation failed: expected {total}, got {staged}")
        swap_staging_table(connection, "rating_split", STAGING)
        columns, rows = query_all(
            connection,
            """
            SELECT s.data_split, COUNT(*) rows_in_split,
                   FROM_UNIXTIME(MIN(r.rating_ts)) period_start,
                   FROM_UNIXTIME(MAX(r.rating_ts)) period_end
            FROM rating_split s JOIN ratings r ON r.rating_id=s.rating_id
            GROUP BY s.data_split ORDER BY MIN(r.rating_ts)
            """,
        )
        print_rows("Split summary", columns, rows)
        write_results_xlsx(__file__, [("Split summary", columns, rows)])


if __name__ == "__main__":
    main()


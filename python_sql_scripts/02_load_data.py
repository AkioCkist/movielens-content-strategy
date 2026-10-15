"""Step 2: load MovieLens .dat files and populate movie_genres."""

from __future__ import annotations

import argparse
from pathlib import Path

from common import data_dir, db, execute, executemany, run_timed, scalar, write_results_xlsx


LOADS = {
    "movies": (
        "movies.dat",
        """
        LOAD DATA LOCAL INFILE %s INTO TABLE movies
        CHARACTER SET utf8mb4
        FIELDS TERMINATED BY '::' LINES TERMINATED BY '\n'
        (@movie_id, @title, @genres)
        SET movie_id=CAST(@movie_id AS UNSIGNED), title=@title,
            genres=TRIM(TRAILING '\r' FROM @genres)
        """,
    ),
    "ratings": (
        "ratings.dat",
        """
        LOAD DATA LOCAL INFILE %s INTO TABLE ratings
        CHARACTER SET utf8mb4
        FIELDS TERMINATED BY '::' LINES TERMINATED BY '\n'
        (@user_id, @movie_id, @rating, @rating_ts)
        SET user_id=CAST(@user_id AS UNSIGNED),
            movie_id=CAST(@movie_id AS UNSIGNED),
            rating=CAST(@rating AS DECIMAL(2,1)),
            rating_ts=CAST(TRIM(TRAILING '\r' FROM @rating_ts) AS UNSIGNED)
        """,
    ),
    "tags": (
        "tags.dat",
        """
        LOAD DATA LOCAL INFILE %s INTO TABLE tags
        CHARACTER SET utf8mb4
        FIELDS TERMINATED BY '::' LINES TERMINATED BY '\n'
        (@user_id, @movie_id, @tag_text, @tag_ts)
        SET user_id=CAST(@user_id AS UNSIGNED),
            movie_id=CAST(@movie_id AS UNSIGNED), tag_text=@tag_text,
            tag_ts=CAST(TRIM(TRAILING '\r' FROM @tag_ts) AS UNSIGNED)
        """,
    ),
}


def load_table(connection, table: str, path: Path, reload: bool) -> None:
    current = int(scalar(connection, f"SELECT COUNT(*) FROM `{table}`"))
    if current and not reload:
        print(f"[skip] {table}: already has {current:,} rows (use --reload to replace)")
        return
    if reload:
        execute(connection, f"TRUNCATE TABLE `{table}`")
    if not path.is_file():
        raise FileNotFoundError(path)
    # Forward slashes are accepted by MySQL on Windows and avoid escape issues.
    execute(connection, LOADS[table][1], (path.as_posix(),))
    loaded = int(scalar(connection, f"SELECT COUNT(*) FROM `{table}`"))
    print(f"[info] {table}: {loaded:,} rows")


def movie_genre_rows(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            movie_id, _, genres = line.rstrip("\r\n").split("::", 2)
            for genre in genres.split("|"):
                yield int(movie_id), genre


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--reload",
        action="store_true",
        help="TRUNCATE raw tables before loading (destructive; omitted by default)",
    )
    args = parser.parse_args()
    source_dir = data_dir()
    print(f"Data directory: {source_dir}")
    missing = [source_dir / item[0] for item in LOADS.values() if not (source_dir / item[0]).is_file()]
    if missing:
        raise FileNotFoundError("Missing source files: " + ", ".join(str(path) for path in missing))

    with db() as connection:
        for table, (filename, _) in LOADS.items():
            run_timed(
                f"load {table}",
                lambda t=table, p=source_dir / filename: load_table(
                    connection, t, p, args.reload
                ),
                connection=connection,
            )

        if args.reload:
            execute(connection, "TRUNCATE TABLE movie_genres")
        rows = list(movie_genre_rows(source_dir / "movies.dat"))
        run_timed(
            "populate movie_genres",
            lambda: executemany(
                connection,
                "INSERT IGNORE INTO movie_genres (movie_id, genre) VALUES (%s, %s)",
                rows,
            ),
            connection=connection,
        )
        count_rows = []
        for table in ("movies", "ratings", "tags", "movie_genres"):
            count = int(scalar(connection, f"SELECT COUNT(*) FROM `{table}`"))
            print(f"{table}: {count:,}")
            count_rows.append((table, count))
        write_results_xlsx(
            __file__,
            [("Row counts", ("table_name", "row_count"), count_rows)],
        )


if __name__ == "__main__":
    main()


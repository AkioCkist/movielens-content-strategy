"""Step 1: create the schema and all high-value indexes."""

from common import database_name, db, ensure_index, execute, ident


TABLES = [
    """
    CREATE TABLE IF NOT EXISTS movies (
        movie_id INT UNSIGNED NOT NULL,
        title VARCHAR(500) NOT NULL,
        genres VARCHAR(255) NOT NULL,
        PRIMARY KEY (movie_id)
    ) ENGINE=InnoDB
    """,
    """
    CREATE TABLE IF NOT EXISTS ratings (
        rating_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
        user_id INT UNSIGNED NOT NULL,
        movie_id INT UNSIGNED NOT NULL,
        rating DECIMAL(2,1) NOT NULL,
        rating_ts INT UNSIGNED NOT NULL,
        PRIMARY KEY (rating_id),
        INDEX idx_ratings_user (user_id),
        INDEX idx_ratings_movie (movie_id),
        INDEX idx_ratings_ts (rating_ts)
    ) ENGINE=InnoDB
    """,
    """
    CREATE TABLE IF NOT EXISTS tags (
        tag_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
        user_id INT UNSIGNED NOT NULL,
        movie_id INT UNSIGNED NOT NULL,
        tag_text VARCHAR(500) NOT NULL,
        tag_ts INT UNSIGNED NOT NULL,
        PRIMARY KEY (tag_id),
        INDEX idx_tags_user (user_id),
        INDEX idx_tags_movie (movie_id)
    ) ENGINE=InnoDB
    """,
    """
    CREATE TABLE IF NOT EXISTS movie_genres (
        movie_id INT UNSIGNED NOT NULL,
        genre VARCHAR(50) NOT NULL,
        PRIMARY KEY (movie_id, genre),
        INDEX idx_movie_genres_genre (genre)
    ) ENGINE=InnoDB
    """,
    """
    CREATE TABLE IF NOT EXISTS user_segments (
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
    """,
    """
    CREATE TABLE IF NOT EXISTS rating_predictions (
        rating_id BIGINT UNSIGNED NOT NULL,
        user_id INT UNSIGNED NOT NULL,
        movie_id INT UNSIGNED NOT NULL,
        cluster_id INT NOT NULL,
        actual_liked TINYINT UNSIGNED NOT NULL,
        predicted_liked TINYINT UNSIGNED NOT NULL,
        probability_liked DECIMAL(10,8) NOT NULL,
        data_split VARCHAR(5) NOT NULL,
        model_version VARCHAR(50) NOT NULL,
        model_run_date DATETIME NOT NULL,
        PRIMARY KEY (rating_id, model_version),
        INDEX idx_predictions_movie (movie_id),
        INDEX idx_predictions_cluster (cluster_id),
        INDEX idx_predictions_split (data_split),
        INDEX idx_predictions_version (model_version)
    ) ENGINE=InnoDB
    """,
    """
    CREATE TABLE IF NOT EXISTS model_metrics (
        model_name VARCHAR(100) NOT NULL,
        model_version VARCHAR(50) NOT NULL,
        split_name VARCHAR(10) NOT NULL,
        metric_name VARCHAR(50) NOT NULL,
        metric_value DECIMAL(18,8) NOT NULL,
        run_timestamp DATETIME NOT NULL,
        PRIMARY KEY (model_name, model_version, split_name, metric_name)
    ) ENGINE=InnoDB
    """,
]


def main() -> None:
    schema = database_name()
    with db(with_database=False) as connection:
        execute(
            connection,
            f"CREATE DATABASE IF NOT EXISTS {ident(schema)} "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci",
        )
    with db() as connection:
        for statement in TABLES:
            execute(connection, statement)

    # Existing databases may have been created by the old SQL before indexes
    # were added. Add only missing indexes, one at a time, with reconnect/poll.
    indexes = [
        ("ratings", "idx_ratings_user", ("user_id",)),
        ("ratings", "idx_ratings_movie", ("movie_id",)),
        ("ratings", "idx_ratings_ts", ("rating_ts",)),
        ("tags", "idx_tags_user", ("user_id",)),
        ("tags", "idx_tags_movie", ("movie_id",)),
    ]
    for table, name, columns in indexes:
        ensure_index(table, name, columns)
    print(f"\nSchema {schema!r} is ready.")


if __name__ == "__main__":
    main()


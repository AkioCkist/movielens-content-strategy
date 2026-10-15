-- MovieLens Content Strategy
-- Load the raw .dat files. Mirrors python_sql_scripts/02_load_data.py.
-- Replace the paths with the extracted ml-10M100K directory on the local machine.
-- MySQL Workbench must be configured with OPT_LOCAL_INFILE=1.
-- Run on EMPTY tables only: LOAD DATA appends, so re-running duplicates rows.
-- To reload deliberately, TRUNCATE movies, ratings, tags, movie_genres first,
-- then rerun 04_create_splits.sql and 05_feature_tables.sql.
-- Indexes already exist from 01_create_schema.sql; no CREATE INDEX is needed.

USE movielens_strategy;

-- Optional, requires the appropriate server privilege:
-- SET GLOBAL local_infile = 1;

LOAD DATA LOCAL INFILE 'C:/Users/doubl/Documents/movielens-content-strategy/data/ml-10M100K/movies.dat'
INTO TABLE movies
CHARACTER SET utf8mb4
FIELDS TERMINATED BY '::'
LINES TERMINATED BY '\n'
(@movie_id, @title, @genres)
SET
    movie_id = CAST(@movie_id AS UNSIGNED),
    title = @title,
    genres = TRIM(TRAILING '\r' FROM @genres);

LOAD DATA LOCAL INFILE 'C:/Users/doubl/Documents/movielens-content-strategy/data/ml-10M100K/ratings.dat'
INTO TABLE ratings
CHARACTER SET utf8mb4
FIELDS TERMINATED BY '::'
LINES TERMINATED BY '\n'
(@user_id, @movie_id, @rating, @rating_ts)
SET
    user_id = CAST(@user_id AS UNSIGNED),
    movie_id = CAST(@movie_id AS UNSIGNED),
    rating = CAST(@rating AS DECIMAL(2,1)),
    rating_ts = CAST(TRIM(TRAILING '\r' FROM @rating_ts) AS UNSIGNED);

LOAD DATA LOCAL INFILE 'C:/Users/doubl/Documents/movielens-content-strategy/data/ml-10M100K/tags.dat'
INTO TABLE tags
CHARACTER SET utf8mb4
FIELDS TERMINATED BY '::'
LINES TERMINATED BY '\n'
(@user_id, @movie_id, @tag_text, @tag_ts)
SET
    user_id = CAST(@user_id AS UNSIGNED),
    movie_id = CAST(@movie_id AS UNSIGNED),
    tag_text = @tag_text,
    tag_ts = CAST(TRIM(TRAILING '\r' FROM @tag_ts) AS UNSIGNED);

-- One row per (movie, genre). The Python script splits the same '|' list in
-- Python; both produce identical rows. INSERT IGNORE makes it safe to rerun.
INSERT IGNORE INTO movie_genres (movie_id, genre)
SELECT
    m.movie_id,
    jt.genre
FROM movies AS m
JOIN JSON_TABLE(
    CONCAT('["', REPLACE(m.genres, '|', '","'), '"]'),
    '$[*]' COLUMNS (
        genre VARCHAR(50) PATH '$'
    )
) AS jt;

SELECT 'movies' AS table_name, COUNT(*) AS row_count FROM movies
UNION ALL SELECT 'ratings', COUNT(*) FROM ratings
UNION ALL SELECT 'tags', COUNT(*) FROM tags
UNION ALL SELECT 'movie_genres', COUNT(*) FROM movie_genres;

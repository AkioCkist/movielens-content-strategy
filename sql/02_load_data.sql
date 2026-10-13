-- MovieLens Content Strategy
-- Replace DATA_DIR with the extracted ml-10M100K directory on the local machine.
-- MySQL Workbench must be configured with OPT_LOCAL_INFILE=1.

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

-- Secondary indexes are created after bulk loading for faster imports.
CREATE INDEX idx_ratings_user ON ratings(user_id);
CREATE INDEX idx_ratings_movie ON ratings(movie_id);
CREATE INDEX idx_ratings_ts ON ratings(rating_ts);
CREATE INDEX idx_ratings_user_ts ON ratings(user_id, rating_ts);
CREATE INDEX idx_ratings_movie_ts ON ratings(movie_id, rating_ts);
CREATE INDEX idx_tags_user ON tags(user_id);
CREATE INDEX idx_tags_movie ON tags(movie_id);

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

SELECT COUNT(*) AS movie_rows FROM movies;
SELECT COUNT(*) AS rating_rows FROM ratings;
SELECT COUNT(*) AS tag_rows FROM tags;
SELECT COUNT(*) AS movie_genre_rows FROM movie_genres;
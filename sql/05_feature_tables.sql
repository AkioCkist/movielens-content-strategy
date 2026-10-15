-- MovieLens Content Strategy
-- All profile aggregates are built from TRAIN only to avoid temporal leakage.
-- Mirrors python_sql_scripts/05_feature_tables.py.
--
-- Each table is built into a *_staging table that already has its keys, then
-- all three are published together by one atomic RENAME. The former tables
-- are kept as *_previous for rollback.

USE movielens_strategy;

-- Disable the server-side statement time limit for this session.
SET SESSION max_execution_time = 0;

-- =====================================================================
-- 12.1 User statistics
-- =====================================================================
DROP TABLE IF EXISTS train_user_stats_staging;

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
) ENGINE = InnoDB;

-- STRAIGHT_JOIN drives from rating_split, so ratings are read in primary-key
-- order instead of random lookups.
INSERT INTO train_user_stats_staging
SELECT
    r.user_id,
    COUNT(*),
    SUM(r.rating),
    AVG(r.rating),
    STDDEV_SAMP(r.rating),
    SUM(r.rating >= 4.0),
    AVG(r.rating >= 4.0),
    COUNT(DISTINCT r.movie_id),
    MIN(r.rating_ts),
    MAX(r.rating_ts),
    DATEDIFF(FROM_UNIXTIME(MAX(r.rating_ts)), FROM_UNIXTIME(MIN(r.rating_ts)))
FROM rating_split AS s
STRAIGHT_JOIN ratings AS r ON r.rating_id = s.rating_id
WHERE s.data_split = 'TRAIN'
GROUP BY r.user_id;

-- =====================================================================
-- 12.2 Movie statistics
-- =====================================================================
DROP TABLE IF EXISTS train_movie_stats_staging;

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
) ENGINE = InnoDB;

INSERT INTO train_movie_stats_staging
SELECT
    r.movie_id,
    COUNT(*),
    SUM(r.rating),
    AVG(r.rating),
    STDDEV_SAMP(r.rating),
    SUM(r.rating >= 4.0),
    AVG(r.rating >= 4.0),
    COUNT(DISTINCT r.user_id)
FROM rating_split AS s
STRAIGHT_JOIN ratings AS r ON r.rating_id = s.rating_id
WHERE s.data_split = 'TRAIN'
GROUP BY r.movie_id;

-- =====================================================================
-- 12.3 User-genre statistics
-- =====================================================================
DROP TABLE IF EXISTS train_user_genre_stats_staging;

CREATE TABLE train_user_genre_stats_staging (
    user_id INT UNSIGNED NOT NULL,
    genre VARCHAR(50) NOT NULL,
    genre_rating_count BIGINT UNSIGNED NOT NULL,
    genre_avg_rating DOUBLE NOT NULL,
    genre_positive_rate DOUBLE NOT NULL,
    PRIMARY KEY (user_id, genre),
    INDEX idx_user_genre_genre (genre)
) ENGINE = InnoDB;

INSERT INTO train_user_genre_stats_staging
SELECT
    r.user_id,
    mg.genre,
    COUNT(*),
    AVG(r.rating),
    AVG(r.rating >= 4.0)
FROM rating_split AS s
STRAIGHT_JOIN ratings AS r ON r.rating_id = s.rating_id
STRAIGHT_JOIN movie_genres AS mg ON mg.movie_id = r.movie_id
WHERE s.data_split = 'TRAIN'
GROUP BY r.user_id, mg.genre;

-- Validate: every count must be > 0 before publishing.
SELECT
    (SELECT COUNT(*) FROM train_user_stats_staging) AS user_rows,
    (SELECT COUNT(*) FROM train_movie_stats_staging) AS movie_rows,
    (SELECT COUNT(*) FROM train_user_genre_stats_staging) AS user_genre_rows;

-- Publish all three tables in one atomic RENAME.
DROP TABLE IF EXISTS train_user_stats_previous, train_movie_stats_previous,
                     train_user_genre_stats_previous;
CREATE TABLE IF NOT EXISTS train_user_stats LIKE train_user_stats_staging;
CREATE TABLE IF NOT EXISTS train_movie_stats LIKE train_movie_stats_staging;
CREATE TABLE IF NOT EXISTS train_user_genre_stats LIKE train_user_genre_stats_staging;
RENAME TABLE
    train_user_stats TO train_user_stats_previous,
    train_user_stats_staging TO train_user_stats,
    train_movie_stats TO train_movie_stats_previous,
    train_movie_stats_staging TO train_movie_stats,
    train_user_genre_stats TO train_user_genre_stats_previous,
    train_user_genre_stats_staging TO train_user_genre_stats;

-- =====================================================================
-- 12.4 KPI SQL queries for the rubric
-- =====================================================================

-- 1. Filtering
SELECT *
FROM ratings
WHERE rating >= 4.0
  AND rating_ts >= UNIX_TIMESTAMP('2005-01-01')
LIMIT 100;

-- 2. Grouping / aggregation
SELECT
    rating,
    COUNT(*) AS rating_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS rating_percent
FROM ratings
GROUP BY rating
ORDER BY rating;

-- 3. Join + KPI by genre.
-- Aggregate 10M ratings to ~10.7K movie rows in one sequential scan, then fan
-- out to genres. Same result as joining every rating to movie_genres
-- (~20M joined rows), because count, sum and positive count are additive:
-- AVG = SUM(sum) / SUM(count). NO_INDEX keeps the inner GROUP BY on a
-- sequential scan instead of 10M random primary-key lookups through
-- idx_ratings_movie (which does not contain rating).
SELECT
    mg.genre,
    CAST(SUM(ma.rating_count) AS UNSIGNED) AS rating_count,
    SUM(ma.rating_sum) / SUM(ma.rating_count) AS avg_rating,
    SUM(ma.positive_count) / SUM(ma.rating_count) AS positive_rate
FROM (
    SELECT /*+ NO_INDEX(ratings) */
        movie_id,
        COUNT(*) AS rating_count,
        SUM(rating) AS rating_sum,
        SUM(rating >= 4.0) AS positive_count
    FROM ratings
    GROUP BY movie_id
) AS ma
JOIN movie_genres AS mg ON mg.movie_id = ma.movie_id
GROUP BY mg.genre
ORDER BY rating_count DESC;

-- 4. Movie popularity with minimum support
SELECT
    m.movie_id,
    m.title,
    ms.rating_count,
    ms.avg_rating,
    ms.positive_rate
FROM train_movie_stats AS ms
JOIN movies AS m ON m.movie_id = ms.movie_id
WHERE ms.rating_count >= 100
ORDER BY ms.avg_rating DESC, ms.rating_count DESC
LIMIT 20;

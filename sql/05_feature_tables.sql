-- MovieLens Content Strategy
-- All profile aggregates are built from TRAIN only to avoid temporal leakage.

USE movielens_strategy;

DROP TABLE IF EXISTS train_user_genre_stats;
DROP TABLE IF EXISTS train_movie_stats;
DROP TABLE IF EXISTS train_user_stats;

CREATE TABLE train_user_stats AS
SELECT
    r.user_id,
    COUNT(*) AS rating_count,
    SUM(r.rating) AS rating_sum,
    AVG(r.rating) AS avg_rating,
    STDDEV_SAMP(r.rating) AS rating_stddev,
    SUM(CASE WHEN r.rating >= 4.0 THEN 1 ELSE 0 END) AS positive_count,
    AVG(CASE WHEN r.rating >= 4.0 THEN 1.0 ELSE 0.0 END) AS positive_rate,
    COUNT(DISTINCT r.movie_id) AS distinct_movies,
    MIN(r.rating_ts) AS first_rating_ts,
    MAX(r.rating_ts) AS last_rating_ts,
    DATEDIFF(
        FROM_UNIXTIME(MAX(r.rating_ts)),
        FROM_UNIXTIME(MIN(r.rating_ts))
    ) AS active_days
FROM ratings AS r
JOIN rating_split AS s ON s.rating_id = r.rating_id
WHERE s.data_split = 'TRAIN'
GROUP BY r.user_id;

ALTER TABLE train_user_stats
    MODIFY user_id INT UNSIGNED NOT NULL,
    ADD PRIMARY KEY (user_id);

CREATE TABLE train_movie_stats AS
SELECT
    r.movie_id,
    COUNT(*) AS rating_count,
    SUM(r.rating) AS rating_sum,
    AVG(r.rating) AS avg_rating,
    STDDEV_SAMP(r.rating) AS rating_stddev,
    SUM(CASE WHEN r.rating >= 4.0 THEN 1 ELSE 0 END) AS positive_count,
    AVG(CASE WHEN r.rating >= 4.0 THEN 1.0 ELSE 0.0 END) AS positive_rate,
    COUNT(DISTINCT r.user_id) AS distinct_users
FROM ratings AS r
JOIN rating_split AS s ON s.rating_id = r.rating_id
WHERE s.data_split = 'TRAIN'
GROUP BY r.movie_id;

ALTER TABLE train_movie_stats
    MODIFY movie_id INT UNSIGNED NOT NULL,
    ADD PRIMARY KEY (movie_id);

CREATE TABLE train_user_genre_stats AS
SELECT
    r.user_id,
    mg.genre,
    COUNT(*) AS genre_rating_count,
    AVG(r.rating) AS genre_avg_rating,
    AVG(CASE WHEN r.rating >= 4.0 THEN 1.0 ELSE 0.0 END) AS genre_positive_rate
FROM ratings AS r
JOIN rating_split AS s ON s.rating_id = r.rating_id
JOIN movie_genres AS mg ON mg.movie_id = r.movie_id
WHERE s.data_split = 'TRAIN'
GROUP BY r.user_id, mg.genre;

ALTER TABLE train_user_genre_stats
    MODIFY user_id INT UNSIGNED NOT NULL,
    MODIFY genre VARCHAR(50) NOT NULL,
    ADD PRIMARY KEY (user_id, genre),
    ADD INDEX idx_user_genre_genre (genre);

-- Filtering, grouping, joining and KPI examples for the SQL rubric.
SELECT *
FROM ratings
WHERE rating >= 4.0
  AND rating_ts >= UNIX_TIMESTAMP('2005-01-01')
LIMIT 100;

SELECT
    rating,
    COUNT(*) AS rating_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS rating_percent
FROM ratings
GROUP BY rating
ORDER BY rating;

SELECT
    mg.genre,
    COUNT(*) AS rating_count,
    AVG(r.rating) AS avg_rating,
    AVG(CASE WHEN r.rating >= 4.0 THEN 1.0 ELSE 0.0 END) AS positive_rate
FROM ratings AS r
JOIN movie_genres AS mg ON mg.movie_id = r.movie_id
GROUP BY mg.genre
ORDER BY rating_count DESC;

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
-- MovieLens Content Strategy
-- Data validation and evidence queries. Run after 02_load_data.sql.

USE movielens_strategy;

SELECT COUNT(*) AS rating_rows FROM ratings;
SELECT COUNT(*) AS movie_rows FROM movies;
SELECT COUNT(*) AS tag_rows FROM tags;
SELECT COUNT(DISTINCT user_id) AS users FROM ratings;
SELECT COUNT(DISTINCT movie_id) AS rated_movies FROM ratings;

SELECT
    MIN(rating) AS minimum_rating,
    MAX(rating) AS maximum_rating,
    AVG(rating) AS average_rating
FROM ratings;

SELECT
    FROM_UNIXTIME(MIN(rating_ts)) AS first_rating,
    FROM_UNIXTIME(MAX(rating_ts)) AS last_rating
FROM ratings;

SELECT
    rating,
    COUNT(*) AS rating_count
FROM ratings
GROUP BY rating
ORDER BY rating;

SELECT COUNT(*) AS orphan_ratings
FROM ratings AS r
LEFT JOIN movies AS m ON m.movie_id = r.movie_id
WHERE m.movie_id IS NULL;

SELECT COUNT(*) AS orphan_tags
FROM tags AS t
LEFT JOIN movies AS m ON m.movie_id = t.movie_id
WHERE m.movie_id IS NULL;

SELECT
    user_id,
    movie_id,
    COUNT(*) AS duplicate_count
FROM ratings
GROUP BY user_id, movie_id
HAVING COUNT(*) > 1
LIMIT 20;

SELECT COUNT(*) AS invalid_rating_rows
FROM ratings
WHERE rating NOT BETWEEN 0.5 AND 5.0
   OR MOD(rating * 10, 5) <> 0;

SELECT COUNT(*) AS invalid_timestamp_rows
FROM ratings
WHERE rating_ts = 0;

SELECT
    COUNT(*) AS users_below_minimum_history
FROM (
    SELECT user_id
    FROM ratings
    GROUP BY user_id
    HAVING COUNT(*) < 20
) AS user_counts;

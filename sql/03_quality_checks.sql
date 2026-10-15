-- MovieLens Content Strategy
-- Data validation and evidence queries. Run after 02_load_data.sql.
-- Section 1 mirrors python_sql_scripts/03_quality_checks.py.

USE movielens_strategy;

-- =====================================================================
-- 1. Core checks (same queries as the Python pipeline)
-- =====================================================================

-- Row counts
SELECT
    (SELECT COUNT(*) FROM ratings) AS rating_rows,
    (SELECT COUNT(*) FROM movies) AS movie_rows,
    (SELECT COUNT(*) FROM tags) AS tag_rows,
    (SELECT COUNT(DISTINCT user_id) FROM ratings) AS users,
    (SELECT COUNT(DISTINCT movie_id) FROM ratings) AS rated_movies;

-- Rating range
SELECT
    MIN(rating) AS minimum_rating,
    MAX(rating) AS maximum_rating,
    AVG(rating) AS average_rating
FROM ratings;

-- Rating period
SELECT
    FROM_UNIXTIME(MIN(rating_ts)) AS first_rating,
    FROM_UNIXTIME(MAX(rating_ts)) AS last_rating
FROM ratings;

-- Rating distribution
SELECT
    rating,
    COUNT(*) AS rating_count
FROM ratings
GROUP BY rating
ORDER BY rating;

-- Orphan ratings
SELECT COUNT(*) AS orphan_ratings
FROM ratings AS r
LEFT JOIN movies AS m ON m.movie_id = r.movie_id
WHERE m.movie_id IS NULL;

-- Orphan tags
SELECT COUNT(*) AS orphan_tags
FROM tags AS t
LEFT JOIN movies AS m ON m.movie_id = t.movie_id
WHERE m.movie_id IS NULL;

-- Duplicate user/movie pairs (sample).
-- ~10M distinct groups overflow the in-memory temp table; SQL_BIG_RESULT
-- makes MySQL group by sorting instead of a disk-based temp table.
SELECT SQL_BIG_RESULT
    user_id,
    movie_id,
    COUNT(*) AS duplicate_count
FROM ratings
GROUP BY user_id, movie_id
HAVING COUNT(*) > 1
ORDER BY user_id, movie_id
LIMIT 20;

-- Invalid rows (one scan for both checks)
SELECT
    SUM(rating NOT BETWEEN 0.5 AND 5.0 OR MOD(rating * 10, 5) <> 0) AS invalid_rating_rows,
    SUM(rating_ts = 0) AS invalid_timestamp_rows
FROM ratings;

-- Users below 20 ratings (MovieLens guarantees >= 20)
SELECT COUNT(*) AS users_below_minimum_history
FROM (
    SELECT user_id
    FROM ratings
    GROUP BY user_id
    HAVING COUNT(*) < 20
) AS user_counts;

-- =====================================================================
-- 2. Additional evidence (Workbench only, not in the Python pipeline)
-- =====================================================================

-- Completeness: NULL or empty values
SELECT
    SUM(title IS NULL OR TRIM(title) = '') AS empty_titles,
    SUM(genres IS NULL OR TRIM(genres) = '') AS empty_genres,
    SUM(genres = '(no genres listed)') AS no_genre_movies,
    SUM(title NOT REGEXP '\\([0-9]{4}\\)[[:space:]]*$') AS titles_without_year
FROM movies;

SELECT
    SUM(tag_text IS NULL OR TRIM(tag_text) = '') AS empty_tags,
    COUNT(DISTINCT LOWER(TRIM(tag_text))) AS distinct_tags_normalised,
    COUNT(DISTINCT tag_text) AS distinct_tags_raw
FROM tags;

-- Uniqueness: total number of duplicated user-movie pairs
SELECT COUNT(*) AS duplicate_pairs
FROM (
    SELECT SQL_BIG_RESULT user_id, movie_id
    FROM ratings
    GROUP BY user_id, movie_id
    HAVING COUNT(*) > 1
) AS d;

-- Plausibility / outliers
SELECT COUNT(*) AS movies_with_lt_5_ratings
FROM (
    SELECT movie_id
    FROM ratings
    GROUP BY movie_id
    HAVING COUNT(*) < 5
) AS x;

SELECT
    MAX(c) AS max_ratings_per_user,
    AVG(c) AS avg_ratings_per_user
FROM (
    SELECT COUNT(*) AS c
    FROM ratings
    GROUP BY user_id
) AS u;

-- Consistency: movies without any rating
SELECT COUNT(*) AS movies_without_ratings
FROM movies AS m
WHERE NOT EXISTS (
    SELECT 1 FROM ratings AS r WHERE r.movie_id = m.movie_id
);

-- MovieLens Content Strategy
-- Feature view for KNIME Logistic Regression.
-- Mirrors python_sql_scripts/06_logistic_features.py.
-- Run after 05_feature_tables.sql and after KNIME writes user_segments.
-- Check first: SELECT COUNT(*) FROM user_segments; must be > 0.

USE movielens_strategy;

DROP VIEW IF EXISTS ml_rating_features;

-- TRAIN rows use leave-one-out aggregates (the row's own rating is removed);
-- VALID/TEST rows use the plain TRAIN aggregates.
-- Genre flags use FIND_IN_SET on the '|' list, which matches whole genre names
-- only (LIKE '%...%' would match any substring).
CREATE VIEW ml_rating_features AS
SELECT
    r.rating_id,
    r.user_id,
    r.movie_id,
    s.data_split,
    CASE WHEN r.rating >= 4.0 THEN 1 ELSE 0 END AS liked,

    CASE
        WHEN s.data_split = 'TRAIN' AND us.rating_count > 1
        THEN (us.rating_sum - r.rating) / (us.rating_count - 1)
        ELSE us.avg_rating
    END AS user_prior_avg_rating,
    CASE
        WHEN s.data_split = 'TRAIN' AND us.rating_count > 1
        THEN (us.positive_count - (r.rating >= 4.0)) / (us.rating_count - 1)
        ELSE us.positive_rate
    END AS user_prior_positive_rate,
    us.rating_count AS user_activity,
    us.rating_stddev AS user_rating_stddev,
    us.active_days AS user_active_days,

    CASE
        WHEN s.data_split = 'TRAIN' AND ms.rating_count > 1
        THEN (ms.rating_sum - r.rating) / (ms.rating_count - 1)
        ELSE ms.avg_rating
    END AS movie_prior_avg_rating,
    CASE
        WHEN s.data_split = 'TRAIN' AND ms.rating_count > 1
        THEN (ms.positive_count - (r.rating >= 4.0)) / (ms.rating_count - 1)
        ELSE ms.positive_rate
    END AS movie_prior_positive_rate,
    ms.rating_count AS movie_popularity,
    ms.rating_stddev AS movie_rating_stddev,
    seg.cluster_id,

    CASE WHEN FIND_IN_SET('Action', REPLACE(m.genres, '|', ',')) > 0 THEN 1 ELSE 0 END AS genre_action,
    CASE WHEN FIND_IN_SET('Adventure', REPLACE(m.genres, '|', ',')) > 0 THEN 1 ELSE 0 END AS genre_adventure,
    CASE WHEN FIND_IN_SET('Animation', REPLACE(m.genres, '|', ',')) > 0 THEN 1 ELSE 0 END AS genre_animation,
    CASE WHEN FIND_IN_SET('Children', REPLACE(m.genres, '|', ',')) > 0 THEN 1 ELSE 0 END AS genre_children,
    CASE WHEN FIND_IN_SET('Comedy', REPLACE(m.genres, '|', ',')) > 0 THEN 1 ELSE 0 END AS genre_comedy,
    CASE WHEN FIND_IN_SET('Crime', REPLACE(m.genres, '|', ',')) > 0 THEN 1 ELSE 0 END AS genre_crime,
    CASE WHEN FIND_IN_SET('Documentary', REPLACE(m.genres, '|', ',')) > 0 THEN 1 ELSE 0 END AS genre_documentary,
    CASE WHEN FIND_IN_SET('Drama', REPLACE(m.genres, '|', ',')) > 0 THEN 1 ELSE 0 END AS genre_drama,
    CASE WHEN FIND_IN_SET('Fantasy', REPLACE(m.genres, '|', ',')) > 0 THEN 1 ELSE 0 END AS genre_fantasy,
    CASE WHEN FIND_IN_SET('Film-Noir', REPLACE(m.genres, '|', ',')) > 0 THEN 1 ELSE 0 END AS genre_film_noir,
    CASE WHEN FIND_IN_SET('Horror', REPLACE(m.genres, '|', ',')) > 0 THEN 1 ELSE 0 END AS genre_horror,
    CASE WHEN FIND_IN_SET('Musical', REPLACE(m.genres, '|', ',')) > 0 THEN 1 ELSE 0 END AS genre_musical,
    CASE WHEN FIND_IN_SET('Mystery', REPLACE(m.genres, '|', ',')) > 0 THEN 1 ELSE 0 END AS genre_mystery,
    CASE WHEN FIND_IN_SET('Romance', REPLACE(m.genres, '|', ',')) > 0 THEN 1 ELSE 0 END AS genre_romance,
    CASE WHEN FIND_IN_SET('Sci-Fi', REPLACE(m.genres, '|', ',')) > 0 THEN 1 ELSE 0 END AS genre_scifi,
    CASE WHEN FIND_IN_SET('Thriller', REPLACE(m.genres, '|', ',')) > 0 THEN 1 ELSE 0 END AS genre_thriller,
    CASE WHEN FIND_IN_SET('War', REPLACE(m.genres, '|', ',')) > 0 THEN 1 ELSE 0 END AS genre_war,
    CASE WHEN FIND_IN_SET('Western', REPLACE(m.genres, '|', ',')) > 0 THEN 1 ELSE 0 END AS genre_western
FROM ratings AS r
JOIN rating_split AS s ON s.rating_id = r.rating_id
JOIN movies AS m ON m.movie_id = r.movie_id
JOIN train_user_stats AS us ON us.user_id = r.user_id
JOIN train_movie_stats AS ms ON ms.movie_id = r.movie_id
JOIN user_segments AS seg ON seg.user_id = r.user_id
WHERE us.rating_count > 1
  AND ms.rating_count > 1;

-- Feature rows and cold-start exclusions per split (required for the report).
-- Split totals come from the small rating_split index, so this is still one
-- pass over the view.
SELECT
    t.data_split,
    t.total_rows,
    COALESCE(f.feature_rows, 0) AS feature_rows,
    t.total_rows - COALESCE(f.feature_rows, 0) AS cold_start_excluded_rows,
    (t.total_rows - COALESCE(f.feature_rows, 0)) / t.total_rows AS cold_start_excluded_rate
FROM (
    SELECT data_split, COUNT(*) AS total_rows
    FROM rating_split
    GROUP BY data_split
) AS t
LEFT JOIN (
    SELECT data_split, COUNT(*) AS feature_rows
    FROM ml_rating_features
    GROUP BY data_split
) AS f ON f.data_split = t.data_split
ORDER BY t.data_split;

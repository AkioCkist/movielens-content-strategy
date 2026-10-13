-- MovieLens Content Strategy
-- Feature view for KNIME Logistic Regression.
-- Run after 05_feature_tables.sql and after KNIME writes user_segments.

USE movielens_strategy;

DROP VIEW IF EXISTS ml_rating_features;

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
        THEN (us.positive_count - CASE WHEN r.rating >= 4.0 THEN 1 ELSE 0 END)
             / (us.rating_count - 1)
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
        THEN (ms.positive_count - CASE WHEN r.rating >= 4.0 THEN 1 ELSE 0 END)
             / (ms.rating_count - 1)
        ELSE ms.positive_rate
    END AS movie_prior_positive_rate,
    ms.rating_count AS movie_popularity,
    ms.rating_stddev AS movie_rating_stddev,
    seg.cluster_id,

    CASE WHEN m.genres LIKE '%Action%' THEN 1 ELSE 0 END AS genre_action,
    CASE WHEN m.genres LIKE '%Adventure%' THEN 1 ELSE 0 END AS genre_adventure,
    CASE WHEN m.genres LIKE '%Animation%' THEN 1 ELSE 0 END AS genre_animation,
    CASE WHEN m.genres LIKE '%Children%' THEN 1 ELSE 0 END AS genre_children,
    CASE WHEN m.genres LIKE '%Comedy%' THEN 1 ELSE 0 END AS genre_comedy,
    CASE WHEN m.genres LIKE '%Crime%' THEN 1 ELSE 0 END AS genre_crime,
    CASE WHEN m.genres LIKE '%Documentary%' THEN 1 ELSE 0 END AS genre_documentary,
    CASE WHEN m.genres LIKE '%Drama%' THEN 1 ELSE 0 END AS genre_drama,
    CASE WHEN m.genres LIKE '%Fantasy%' THEN 1 ELSE 0 END AS genre_fantasy,
    CASE WHEN m.genres LIKE '%Film-Noir%' THEN 1 ELSE 0 END AS genre_film_noir,
    CASE WHEN m.genres LIKE '%Horror%' THEN 1 ELSE 0 END AS genre_horror,
    CASE WHEN m.genres LIKE '%Musical%' THEN 1 ELSE 0 END AS genre_musical,
    CASE WHEN m.genres LIKE '%Mystery%' THEN 1 ELSE 0 END AS genre_mystery,
    CASE WHEN m.genres LIKE '%Romance%' THEN 1 ELSE 0 END AS genre_romance,
    CASE WHEN m.genres LIKE '%Sci-Fi%' THEN 1 ELSE 0 END AS genre_scifi,
    CASE WHEN m.genres LIKE '%Thriller%' THEN 1 ELSE 0 END AS genre_thriller,
    CASE WHEN m.genres LIKE '%War%' THEN 1 ELSE 0 END AS genre_war,
    CASE WHEN m.genres LIKE '%Western%' THEN 1 ELSE 0 END AS genre_western
FROM ratings AS r
JOIN rating_split AS s ON s.rating_id = r.rating_id
JOIN movies AS m ON m.movie_id = r.movie_id
JOIN train_user_stats AS us ON us.user_id = r.user_id
JOIN train_movie_stats AS ms ON ms.movie_id = r.movie_id
JOIN user_segments AS seg ON seg.user_id = r.user_id
WHERE us.rating_count > 1
  AND ms.rating_count > 1;

SELECT
    data_split,
    COUNT(*) AS feature_rows
FROM ml_rating_features
GROUP BY data_split
ORDER BY data_split;
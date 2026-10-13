-- MovieLens Content Strategy
-- Summary views for Power BI. Run after KNIME writes model results.

USE movielens_strategy;

CREATE OR REPLACE VIEW dashboard_kpis AS
SELECT
    (SELECT COUNT(*) FROM ratings) AS total_ratings,
    (SELECT COUNT(DISTINCT user_id) FROM ratings) AS total_users,
    (SELECT COUNT(*) FROM movies) AS total_movies,
    (SELECT COUNT(*) FROM tags) AS total_tags,
    (SELECT AVG(rating) FROM ratings) AS average_rating,
    (SELECT AVG(CASE WHEN rating >= 4.0 THEN 1.0 ELSE 0.0 END)
     FROM ratings) AS positive_rating_rate;

CREATE OR REPLACE VIEW dashboard_segment_profiles AS
SELECT
    seg.cluster_id,
    seg.segment_name,
    COUNT(*) AS user_count,
    AVG(us.rating_count) AS avg_user_ratings,
    AVG(us.avg_rating) AS avg_rating,
    AVG(us.positive_rate) AS avg_positive_rate,
    AVG(us.rating_stddev) AS avg_rating_stddev,
    AVG(us.active_days) AS avg_active_days
FROM user_segments AS seg
JOIN train_user_stats AS us ON us.user_id = seg.user_id
GROUP BY seg.cluster_id, seg.segment_name;

CREATE OR REPLACE VIEW dashboard_segment_genres AS
SELECT
    seg.cluster_id,
    seg.segment_name,
    ugs.genre,
    COUNT(DISTINCT ugs.user_id) AS users_with_genre,
    SUM(ugs.genre_rating_count) AS genre_rating_count,
    AVG(ugs.genre_avg_rating) AS avg_genre_rating,
    AVG(ugs.genre_positive_rate) AS avg_genre_positive_rate
FROM user_segments AS seg
JOIN train_user_genre_stats AS ugs ON ugs.user_id = seg.user_id
GROUP BY seg.cluster_id, seg.segment_name, ugs.genre;

CREATE OR REPLACE VIEW dashboard_content_opportunities AS
SELECT
    rp.cluster_id,
    seg.segment_name,
    rp.movie_id,
    m.title,
    m.genres,
    COUNT(*) AS test_support,
    AVG(rp.probability_liked) AS predicted_like_probability,
    AVG(rp.actual_liked) AS actual_positive_rate,
    ms.rating_count AS train_popularity,
    ms.avg_rating AS train_avg_rating
FROM rating_predictions AS rp
JOIN movies AS m ON m.movie_id = rp.movie_id
JOIN train_movie_stats AS ms ON ms.movie_id = rp.movie_id
JOIN (
    SELECT DISTINCT cluster_id, segment_name
    FROM user_segments
) AS seg ON seg.cluster_id = rp.cluster_id
WHERE rp.data_split = 'TEST'
GROUP BY
    rp.cluster_id,
    seg.segment_name,
    rp.movie_id,
    m.title,
    m.genres,
    ms.rating_count,
    ms.avg_rating;

CREATE OR REPLACE VIEW dashboard_model_metrics AS
SELECT
    model_name,
    model_version,
    split_name,
    metric_name,
    metric_value,
    run_timestamp
FROM model_metrics;

-- Check the marts before connecting Power BI.
SELECT * FROM dashboard_kpis;
SELECT * FROM dashboard_segment_profiles LIMIT 20;
SELECT * FROM dashboard_segment_genres LIMIT 20;
SELECT * FROM dashboard_content_opportunities LIMIT 20;
SELECT * FROM dashboard_model_metrics LIMIT 20;
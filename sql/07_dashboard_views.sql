-- MovieLens Content Strategy
-- Summary views for Power BI. Mirrors python_sql_scripts/07_dashboard_views.py.
-- Run after KNIME writes user_segments, rating_predictions and model_metrics.

USE movielens_strategy;

CREATE OR REPLACE VIEW dashboard_kpis AS
SELECT
    ra.total_ratings,
    (SELECT COUNT(DISTINCT user_id) FROM ratings) AS total_users,
    (SELECT COUNT(*) FROM movies) AS total_movies,
    (SELECT COUNT(*) FROM tags) AS total_tags,
    ra.average_rating,
    ra.positive_rating_rate
FROM (
    -- One scan of ratings instead of three separate full scans.
    SELECT
        COUNT(*) AS total_ratings,
        AVG(rating) AS average_rating,
        AVG(rating >= 4.0) AS positive_rating_rate
    FROM ratings
) AS ra;

-- Page 1: rating distribution (10 rows).
CREATE OR REPLACE VIEW dashboard_rating_distribution AS
SELECT
    rating,
    COUNT(*) AS rating_count,
    COUNT(*) / SUM(COUNT(*)) OVER () AS rating_share
FROM ratings
GROUP BY rating;

-- Page 1: KPI by genre. Same optimised query as rubric query 3 in
-- 05_feature_tables.sql: aggregate per movie first, then fan out to genres.
CREATE OR REPLACE VIEW dashboard_genre_kpis AS
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
GROUP BY mg.genre;

-- Page 1: TRAIN movie popularity with minimum support (Top N is set in Power BI).
CREATE OR REPLACE VIEW dashboard_movie_popularity AS
SELECT
    m.movie_id,
    m.title,
    m.genres,
    ms.rating_count,
    ms.avg_rating,
    ms.positive_rate
FROM train_movie_stats AS ms
JOIN movies AS m ON m.movie_id = ms.movie_id
WHERE ms.rating_count >= 100;

-- Page 5: rows and time period of each split. Joins 10M rows, so it takes a
-- few minutes; the split only changes when 04 is rerun.
CREATE OR REPLACE VIEW dashboard_split_summary AS
SELECT
    s.data_split,
    COUNT(*) AS rows_in_split,
    FROM_UNIXTIME(MIN(r.rating_ts)) AS period_start,
    FROM_UNIXTIME(MAX(r.rating_ts)) AS period_end
FROM rating_split AS s
JOIN ratings AS r ON r.rating_id = s.rating_id
GROUP BY s.data_split;

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

-- Joined to user_segments by user_id AND cluster_id, so each prediction row
-- matches exactly one segment row. rating_predictions is keyed by
-- (rating_id, model_version); grouping by version stops a second model run
-- from doubling test_support. Filter one model_version in Power BI.
CREATE OR REPLACE VIEW dashboard_content_opportunities AS
SELECT
    rp.model_version,
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
JOIN user_segments AS seg
    ON seg.user_id = rp.user_id
   AND seg.cluster_id = rp.cluster_id
WHERE rp.data_split = 'TEST'
GROUP BY
    rp.model_version,
    rp.cluster_id,
    seg.segment_name,
    rp.movie_id,
    m.title,
    m.genres,
    ms.rating_count,
    ms.avg_rating;

-- Page 3: confusion matrix per model version and split (4 rows per version),
-- so Power BI does not have to import millions of prediction rows.
CREATE OR REPLACE VIEW dashboard_confusion_matrix AS
SELECT
    model_version,
    data_split,
    actual_liked,
    predicted_liked,
    COUNT(*) AS row_count
FROM rating_predictions
GROUP BY model_version, data_split, actual_liked, predicted_liked;

-- Pages 3 and 5: metrics, Logistic coefficients (metric_name 'coef_<feature>')
-- and K-Means silhouette by K (metric_name 'silhouette_k<K>') written by KNIME.
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
SELECT * FROM dashboard_rating_distribution LIMIT 20;
SELECT * FROM dashboard_genre_kpis LIMIT 20;
SELECT * FROM dashboard_movie_popularity LIMIT 20;
SELECT * FROM dashboard_split_summary LIMIT 20;
SELECT * FROM dashboard_segment_profiles LIMIT 20;
SELECT * FROM dashboard_segment_genres LIMIT 20;
SELECT * FROM dashboard_content_opportunities LIMIT 20;
SELECT * FROM dashboard_confusion_matrix LIMIT 20;
SELECT * FROM dashboard_model_metrics LIMIT 20;

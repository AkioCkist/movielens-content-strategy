-- MovieLens Content Strategy
-- Chronological 70/15/15 split using 20 ordered time buckets.

USE movielens_strategy;

DROP TABLE IF EXISTS rating_split;

CREATE TABLE rating_split AS
SELECT
    rating_id,
    CASE
        WHEN time_bucket <= 14 THEN 'TRAIN'
        WHEN time_bucket <= 17 THEN 'VALID'
        ELSE 'TEST'
    END AS data_split
FROM (
    SELECT
        rating_id,
        NTILE(20) OVER (ORDER BY rating_ts, rating_id) AS time_bucket
    FROM ratings
) AS ranked_ratings;

ALTER TABLE rating_split
    MODIFY rating_id BIGINT UNSIGNED NOT NULL,
    MODIFY data_split VARCHAR(5) NOT NULL,
    ADD PRIMARY KEY (rating_id),
    ADD INDEX idx_rating_split_name (data_split);

SELECT
    s.data_split,
    COUNT(*) AS rows_in_split,
    MIN(FROM_UNIXTIME(r.rating_ts)) AS period_start,
    MAX(FROM_UNIXTIME(r.rating_ts)) AS period_end
FROM rating_split AS s
JOIN ratings AS r ON r.rating_id = s.rating_id
GROUP BY s.data_split
ORDER BY MIN(r.rating_ts);
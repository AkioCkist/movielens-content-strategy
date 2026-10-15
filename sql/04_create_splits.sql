-- MovieLens Content Strategy
-- Chronological 70/15/15 split. Mirrors python_sql_scripts/04_create_splits.py.
--
-- Produces exactly the same split as
--   NTILE(20) OVER (ORDER BY rating_ts, rating_id): buckets 1-14 TRAIN,
--   15-17 VALID, 18-20 TEST
-- but without a window function over 10M rows (which ran past the
-- 900-second Workbench timeout). The boundary rows are found by reading
-- idx_ratings_ts, which is already ordered by (rating_ts, rating_id).

USE movielens_strategy;

-- 1. Bucket sizes exactly as NTILE(20) assigns them: the first
--    (total MOD 20) buckets each receive one extra row.
SELECT COUNT(*) INTO @total FROM ratings;
SET @bucket_size = @total DIV 20;  -- integer: LIMIT/OFFSET ? rejects DECIMAL
SET @remainder = MOD(@total, 20);
SET @train_rows = 14 * @bucket_size + LEAST(@remainder, 14);
SET @valid_rows = 3 * @bucket_size + GREATEST(0, LEAST(@remainder - 14, 3));

-- 2. Last (rating_ts, rating_id) of TRAIN and of VALID.
SET @train_offset = @train_rows - 1;
SET @valid_offset = @train_rows + @valid_rows - 1;
PREPARE find_boundary FROM
    'SELECT rating_ts, rating_id INTO @boundary_ts, @boundary_id
     FROM ratings ORDER BY rating_ts, rating_id LIMIT 1 OFFSET ?';
EXECUTE find_boundary USING @train_offset;
SET @train_end_ts = @boundary_ts, @train_end_id = @boundary_id;
EXECUTE find_boundary USING @valid_offset;
SET @valid_end_ts = @boundary_ts, @valid_end_id = @boundary_id;
DEALLOCATE PREPARE find_boundary;

SELECT
    @total AS total_rows,
    @train_rows AS train_rows,
    @valid_rows AS valid_rows,
    @total - @train_rows - @valid_rows AS test_rows;

-- 3. Build into a staging table that already has its keys.
DROP TABLE IF EXISTS rating_split_staging;

CREATE TABLE rating_split_staging (
    rating_id BIGINT UNSIGNED NOT NULL,
    data_split VARCHAR(5) NOT NULL,
    PRIMARY KEY (rating_id),
    INDEX idx_rating_split_name (data_split)
) ENGINE = InnoDB;

INSERT INTO rating_split_staging (rating_id, data_split)
SELECT
    rating_id,
    CASE
        WHEN rating_ts < @train_end_ts
          OR (rating_ts = @train_end_ts AND rating_id <= @train_end_id) THEN 'TRAIN'
        WHEN rating_ts < @valid_end_ts
          OR (rating_ts = @valid_end_ts AND rating_id <= @valid_end_id) THEN 'VALID'
        ELSE 'TEST'
    END
FROM ratings;

-- 4. Validate: staged_rows must equal total_rows (is_valid = 1).
--    Do NOT run step 5 if is_valid = 0.
SELECT
    COUNT(*) AS staged_rows,
    @total AS total_rows,
    COUNT(*) = @total AS is_valid
FROM rating_split_staging;

-- 5. Publish atomically; the former table is kept as rating_split_previous
--    for rollback. CREATE ... LIKE makes the RENAME work on the first run.
DROP TABLE IF EXISTS rating_split_previous;
CREATE TABLE IF NOT EXISTS rating_split LIKE rating_split_staging;
RENAME TABLE
    rating_split TO rating_split_previous,
    rating_split_staging TO rating_split;

-- 6. Split summary
SELECT
    s.data_split,
    COUNT(*) AS rows_in_split,
    FROM_UNIXTIME(MIN(r.rating_ts)) AS period_start,
    FROM_UNIXTIME(MAX(r.rating_ts)) AS period_end
FROM rating_split AS s
JOIN ratings AS r ON r.rating_id = s.rating_id
GROUP BY s.data_split
ORDER BY MIN(r.rating_ts);

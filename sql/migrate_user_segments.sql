-- MovieLens Content Strategy
-- Repair a user_segments table recreated by KNIME DB Writer.
--
-- Observed KNIME schema:
--   cluster_id VARCHAR(50) values such as 'cluster_0'
--   model_run_date DATE
--   no distance_to_centroid or idx_user_segments_version
--
-- Target schema: sql/01_create_schema.sql.
-- Safe properties:
--   * validates every cluster_id before converting it;
--   * builds and validates a staging table before publishing;
--   * swaps tables atomically;
--   * keeps the exact old table as user_segments_backup_varchar;
--   * a second run is a no-op once the target schema is present.
--
-- Run the whole file in MySQL Workbench (Ctrl+Shift+Enter).

USE movielens_strategy;

DROP PROCEDURE IF EXISTS migrate_user_segments_schema;

DELIMITER $$

CREATE PROCEDURE migrate_user_segments_schema()
migration: BEGIN
    DECLARE v_table_exists INT DEFAULT 0;
    DECLARE v_required_columns INT DEFAULT 0;
    DECLARE v_cluster_type VARCHAR(64) DEFAULT NULL;
    DECLARE v_run_date_type VARCHAR(64) DEFAULT NULL;
    DECLARE v_distance_type VARCHAR(64) DEFAULT NULL;
    DECLARE v_distance_exists INT DEFAULT 0;
    DECLARE v_required_indexes INT DEFAULT 0;
    DECLARE v_backup_exists INT DEFAULT 0;
    DECLARE v_invalid_clusters BIGINT DEFAULT 0;
    DECLARE v_source_rows BIGINT DEFAULT 0;
    DECLARE v_staging_rows BIGINT DEFAULT 0;
    DECLARE v_mismatches BIGINT DEFAULT 0;
    DECLARE v_cluster_expr TEXT;
    DECLARE v_cluster_verify_expr TEXT;
    DECLARE v_distance_expr TEXT;
    DECLARE v_distance_verify_expr TEXT;

    SELECT COUNT(*) INTO v_table_exists
    FROM information_schema.tables
    WHERE table_schema = DATABASE()
      AND table_name = 'user_segments'
      AND table_type = 'BASE TABLE';

    IF v_table_exists = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'user_segments does not exist; run 01_create_schema first';
    END IF;

    SELECT COUNT(DISTINCT column_name) INTO v_required_columns
    FROM information_schema.columns
    WHERE table_schema = DATABASE()
      AND table_name = 'user_segments'
      AND column_name IN (
          'user_id', 'cluster_id', 'segment_name',
          'model_version', 'model_run_date'
      );

    IF v_required_columns <> 5 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'user_segments is missing one or more required KNIME columns';
    END IF;

    SELECT data_type INTO v_cluster_type
    FROM information_schema.columns
    WHERE table_schema = DATABASE()
      AND table_name = 'user_segments'
      AND column_name = 'cluster_id';

    SELECT data_type INTO v_run_date_type
    FROM information_schema.columns
    WHERE table_schema = DATABASE()
      AND table_name = 'user_segments'
      AND column_name = 'model_run_date';

    SELECT COUNT(*), MAX(data_type)
      INTO v_distance_exists, v_distance_type
    FROM information_schema.columns
    WHERE table_schema = DATABASE()
      AND table_name = 'user_segments'
      AND column_name = 'distance_to_centroid';

    SELECT COUNT(DISTINCT index_name) INTO v_required_indexes
    FROM information_schema.statistics
    WHERE table_schema = DATABASE()
      AND table_name = 'user_segments'
      AND index_name IN (
          'PRIMARY',
          'idx_user_segments_cluster',
          'idx_user_segments_version'
      );

    -- Idempotent exit: the table already matches the required shape.
    IF v_cluster_type IN ('tinyint', 'smallint', 'mediumint', 'int', 'bigint')
       AND v_run_date_type = 'datetime'
       AND v_distance_exists = 1
       AND v_distance_type = 'decimal'
       AND v_required_indexes = 3 THEN
        SELECT 'SKIPPED: user_segments already has the target schema' AS migration_status;
        LEAVE migration;
    END IF;

    SELECT COUNT(*) INTO v_backup_exists
    FROM information_schema.tables
    WHERE table_schema = DATABASE()
      AND table_name = 'user_segments_backup_varchar';

    IF v_backup_exists > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Rollback table user_segments_backup_varchar already exists; inspect it before retrying';
    END IF;

    -- Reject malformed values instead of silently converting them to zero.
    SELECT COUNT(*) INTO v_invalid_clusters
    FROM user_segments
    WHERE TRIM(CAST(cluster_id AS CHAR)) NOT REGEXP '^(cluster_)?[0-9]+$'
       OR CAST(
              REGEXP_REPLACE(TRIM(CAST(cluster_id AS CHAR)), '^cluster_', '')
              AS UNSIGNED
          ) > 2147483647;

    IF v_invalid_clusters > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Invalid cluster_id values found; expected cluster_N or a non-negative integer';
    END IF;

    SELECT COUNT(*) INTO v_source_rows FROM user_segments;

    -- Only a failed, unpublished staging table is removed. Source and backup
    -- tables are never dropped by this migration.
    DROP TABLE IF EXISTS user_segments_migration;

    CREATE TABLE user_segments_migration (
        user_id INT UNSIGNED NOT NULL,
        cluster_id INT NOT NULL,
        segment_name VARCHAR(100) NOT NULL,
        distance_to_centroid DECIMAL(18,8) NULL,
        model_version VARCHAR(50) NOT NULL,
        model_run_date DATETIME NOT NULL,
        PRIMARY KEY (user_id),
        INDEX idx_user_segments_cluster (cluster_id),
        INDEX idx_user_segments_version (model_version)
    ) ENGINE = InnoDB
      CHARACTER SET utf8mb4
      COLLATE utf8mb4_unicode_ci;

    SET v_cluster_expr =
        'CAST(REGEXP_REPLACE(TRIM(CAST(cluster_id AS CHAR)), ''^cluster_'', '''') AS SIGNED)';
    SET v_cluster_verify_expr =
        'CAST(REGEXP_REPLACE(TRIM(CAST(s.cluster_id AS CHAR)), ''^cluster_'', '''') AS SIGNED)';

    IF v_distance_exists = 1 THEN
        SET v_distance_expr = 'CAST(distance_to_centroid AS DECIMAL(18,8))';
        SET v_distance_verify_expr = 'CAST(s.distance_to_centroid AS DECIMAL(18,8))';
    ELSE
        SET v_distance_expr = 'NULL';
        SET v_distance_verify_expr = 'NULL';
    END IF;

    SET @insert_user_segments_sql = CONCAT(
        'INSERT INTO user_segments_migration ',
        '(user_id, cluster_id, segment_name, distance_to_centroid, model_version, model_run_date) ',
        'SELECT CAST(user_id AS UNSIGNED), ', v_cluster_expr, ', ',
        'segment_name, ', v_distance_expr, ', ',
        'model_version, CAST(model_run_date AS DATETIME) ',
        'FROM user_segments'
    );

    PREPARE insert_user_segments_stmt FROM @insert_user_segments_sql;
    EXECUTE insert_user_segments_stmt;
    DEALLOCATE PREPARE insert_user_segments_stmt;

    SELECT COUNT(*) INTO v_staging_rows FROM user_segments_migration;

    IF v_staging_rows <> v_source_rows THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Row-count validation failed; original table was not changed';
    END IF;

    SET @verify_user_segments_sql = CONCAT(
        'SELECT COUNT(*) INTO @migration_mismatches ',
        'FROM user_segments s ',
        'JOIN user_segments_migration m ON m.user_id = CAST(s.user_id AS UNSIGNED) ',
        'WHERE m.cluster_id <> ', v_cluster_verify_expr, ' ',
        'OR BINARY m.segment_name <> BINARY s.segment_name ',
        'OR NOT (m.distance_to_centroid <=> ', v_distance_verify_expr, ') ',
        'OR BINARY m.model_version <> BINARY s.model_version ',
        'OR m.model_run_date <> CAST(s.model_run_date AS DATETIME)'
    );

    PREPARE verify_user_segments_stmt FROM @verify_user_segments_sql;
    EXECUTE verify_user_segments_stmt;
    DEALLOCATE PREPARE verify_user_segments_stmt;
    SET v_mismatches = @migration_mismatches;

    IF v_mismatches <> 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Value validation failed; original table was not changed';
    END IF;

    -- Atomic publish. Existing readers see either the old or the new table.
    RENAME TABLE
        user_segments TO user_segments_backup_varchar,
        user_segments_migration TO user_segments;

    SELECT
        'SUCCESS: migrated user_segments; rollback table retained' AS migration_status,
        v_source_rows AS rows_preserved,
        v_mismatches AS value_mismatches;
END$$

DELIMITER ;

CALL migrate_user_segments_schema();
DROP PROCEDURE migrate_user_segments_schema;

-- Verification results for evidence/screenshots.
SELECT
    c.column_name,
    c.column_type,
    c.is_nullable
FROM information_schema.columns AS c
WHERE c.table_schema = DATABASE()
  AND c.table_name = 'user_segments'
ORDER BY c.ordinal_position;

SELECT
    cluster_id,
    segment_name,
    COUNT(*) AS users
FROM user_segments
GROUP BY cluster_id, segment_name
ORDER BY cluster_id, segment_name;

SELECT
    (SELECT COUNT(*) FROM user_segments) AS migrated_rows,
    EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = DATABASE()
          AND table_name = 'user_segments_backup_varchar'
    ) AS rollback_table_exists;

SHOW CREATE TABLE user_segments;

-- Manual rollback (do not run unless validation later reveals a problem):
-- RENAME TABLE
--     user_segments TO user_segments_failed_migration,
--     user_segments_backup_varchar TO user_segments;

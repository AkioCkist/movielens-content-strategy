-- MovieLens Content Strategy
-- TEST metrics of the Logistic Regression, computed from rating_predictions.
-- Run by the KNIME node "DB SQL Executor" right after predictions are written
-- (or in Workbench). Safe to rerun: old TEST metrics of this version are deleted.
-- Change 'logit_v1' everywhere when you write a new model version.
-- Do not put semicolons inside comments: DB SQL Executor splits on them.

USE movielens_strategy;

DELETE FROM model_metrics
WHERE model_name = 'logistic_regression'
  AND model_version = 'logit_v1'
  AND split_name = 'TEST';

INSERT INTO model_metrics
    (model_name, model_version, split_name, metric_name, metric_value, run_timestamp)
SELECT 'logistic_regression', 'logit_v1', 'TEST', m.metric_name, m.metric_value, NOW()
FROM (
    SELECT 'accuracy' AS metric_name, AVG(actual_liked = predicted_liked) AS metric_value
    FROM rating_predictions WHERE model_version = 'logit_v1' AND data_split = 'TEST'
    UNION ALL
    SELECT 'precision', SUM(actual_liked = 1 AND predicted_liked = 1) / NULLIF(SUM(predicted_liked = 1), 0)
    FROM rating_predictions WHERE model_version = 'logit_v1' AND data_split = 'TEST'
    UNION ALL
    SELECT 'recall', SUM(actual_liked = 1 AND predicted_liked = 1) / NULLIF(SUM(actual_liked = 1), 0)
    FROM rating_predictions WHERE model_version = 'logit_v1' AND data_split = 'TEST'
    UNION ALL
    SELECT 'f1', 2 * SUM(actual_liked = 1 AND predicted_liked = 1)
                 / NULLIF(2 * SUM(actual_liked = 1 AND predicted_liked = 1)
                          + SUM(actual_liked = 0 AND predicted_liked = 1)
                          + SUM(actual_liked = 1 AND predicted_liked = 0), 0)
    FROM rating_predictions WHERE model_version = 'logit_v1' AND data_split = 'TEST'
    UNION ALL
    -- Majority-class baseline: always predict the most frequent class.
    SELECT 'baseline_accuracy', GREATEST(AVG(actual_liked), 1 - AVG(actual_liked))
    FROM rating_predictions WHERE model_version = 'logit_v1' AND data_split = 'TEST'
    UNION ALL
    SELECT 'test_rows', COUNT(*)
    FROM rating_predictions WHERE model_version = 'logit_v1' AND data_split = 'TEST'
    UNION ALL
    -- ROC-AUC = Mann-Whitney U / (positives * negatives), tied scores get their average rank.
    SELECT 'auc',
           (SUM(CASE WHEN actual_liked = 1 THEN rnk + (ties - 1) / 2 END)
            - SUM(actual_liked) * (SUM(actual_liked) + 1) / 2)
           / (SUM(actual_liked) * SUM(1 - actual_liked))
    FROM (
        SELECT actual_liked,
               RANK() OVER (ORDER BY probability_liked) AS rnk,
               COUNT(*) OVER (PARTITION BY probability_liked) AS ties
        FROM rating_predictions
        WHERE model_version = 'logit_v1' AND data_split = 'TEST'
    ) AS ranked
) AS m;

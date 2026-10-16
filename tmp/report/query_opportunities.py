import sys
import csv
from pathlib import Path

sys.path.insert(0, r"C:\Users\doubl\Documents\movielens-content-strategy\python_sql_scripts")

import common


def run_query(label: str, sql: str) -> None:
    print(label)
    with common.db() as connection:
        cursor = connection.cursor()
        try:
            cursor.execute(sql)
            for row in cursor.fetchall():
                print(row)
        finally:
            cursor.close()


base = """
WITH ranked AS (
    SELECT *,
           PERCENT_RANK() OVER (
               PARTITION BY model_version, cluster_id
               ORDER BY train_popularity
           ) AS pop_pct,
           PERCENT_RANK() OVER (
               PARTITION BY model_version, cluster_id
               ORDER BY predicted_like_probability
           ) AS pred_pct
    FROM dashboard_content_opportunities
    WHERE model_version = 'logit_v1'
      AND test_support >= 50
)
SELECT segment_name,
       title,
       test_support,
       ROUND(predicted_like_probability, 4),
       ROUND(actual_positive_rate, 4),
       train_popularity,
       ROUND(pop_pct, 3),
       ROUND(pred_pct, 3)
FROM ranked
WHERE {condition}
ORDER BY segment_name, predicted_like_probability {direction}
LIMIT 30
"""

run_query(
    "HIDDEN",
    base.format(
        condition="pop_pct <= 0.35 AND pred_pct >= 0.65",
        direction="DESC",
    ),
)
run_query(
    "OVEREXPOSED",
    base.format(
        condition="pop_pct >= 0.65 AND pred_pct <= 0.35",
        direction="ASC",
    ),
)

run_query(
    "SUPPORT COVERAGE",
    """
    SELECT segment_name,
           COUNT(*) AS movie_segment_pairs,
           SUM(test_support >= 20) AS support_20,
           SUM(test_support >= 50) AS support_50,
           MAX(test_support) AS maximum_support
    FROM dashboard_content_opportunities
    WHERE model_version = 'logit_v1'
    GROUP BY segment_name
    ORDER BY segment_name
    """,
)

with common.db() as connection:
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            SELECT model_version, cluster_id, segment_name, movie_id, title,
                   genres, test_support, predicted_like_probability,
                   actual_positive_rate, train_popularity, train_avg_rating
            FROM dashboard_content_opportunities
            WHERE model_version = 'logit_v1'
            """
        )
        output = Path(__file__).with_name("content_opportunities.csv")
        with output.open("w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.writer(handle)
            writer.writerow(cursor.column_names)
            writer.writerows(cursor.fetchall())
        print(f"EXPORTED {output}")
    finally:
        cursor.close()

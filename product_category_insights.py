"""
Product Category Insights – 2 queries against order_master view.
Project: stalwart-coast-484305-c5
Dataset: ecommerce_supply_chain
"""

import csv
import os
from google.cloud import bigquery

PROJECT_ID = "stalwart-coast-484305-c5"
DATASET_ID = "ecommerce_supply_chain"
VIEW = f"`{PROJECT_ID}.{DATASET_ID}.order_master`"

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
client = bigquery.Client(project=PROJECT_ID)

# ---------------------------------------------------------------------------
# Query 1 – Category sales performance (top 25 by revenue, min 100 orders)
# ---------------------------------------------------------------------------
QUERY_1 = f"""
SELECT
  COALESCE(product_category_name_english, 'uncategorized') AS category,
  ROUND(SUM(item_total), 2)                                 AS total_revenue,
  COUNT(DISTINCT order_id)                                  AS total_orders,
  ROUND(AVG(item_total), 2)                                 AS avg_order_value,
  ROUND(AVG(review_score), 2)                               AS avg_review_score,
  ROUND(100.0 * COUNTIF(is_late = TRUE AND is_delivered = TRUE)
             / NULLIF(COUNTIF(is_delivered = TRUE), 0), 1)  AS late_rate_pct,
  ROUND(AVG(IF(is_delivered = TRUE, delivery_days, NULL)), 1) AS avg_delivery_days
FROM {VIEW}
GROUP BY category
HAVING COUNT(DISTINCT order_id) >= 100
ORDER BY total_revenue DESC
LIMIT 25
"""

# ---------------------------------------------------------------------------
# Query 2 – High-risk categories (low reviews or high late rate)
# ---------------------------------------------------------------------------
QUERY_2 = f"""
SELECT
  COALESCE(product_category_name_english, 'uncategorized') AS category,
  ROUND(SUM(item_total), 2)                                 AS total_revenue,
  COUNT(DISTINCT order_id)                                  AS total_orders,
  ROUND(AVG(item_total), 2)                                 AS avg_order_value,
  ROUND(AVG(review_score), 2)                               AS avg_review_score,
  ROUND(100.0 * COUNTIF(is_late = TRUE AND is_delivered = TRUE)
             / NULLIF(COUNTIF(is_delivered = TRUE), 0), 1)  AS late_rate_pct,
  ROUND(AVG(IF(is_delivered = TRUE, delivery_days, NULL)), 1) AS avg_delivery_days
FROM {VIEW}
GROUP BY category
HAVING
  COUNT(DISTINCT order_id) >= 50
  AND (AVG(review_score) < 3.5 OR COUNTIF(is_late = TRUE AND is_delivered = TRUE) > 0.15 * COUNTIF(is_delivered = TRUE))
ORDER BY avg_review_score ASC
"""

# ---------------------------------------------------------------------------
# Execute and save
# ---------------------------------------------------------------------------
queries = [
    ("category_sales_performance_top25.csv", QUERY_1),
    ("category_high_risk.csv", QUERY_2),
]

for filename, sql in queries:
    filepath = os.path.join(OUT_DIR, filename)
    print(f"Running: {filename} ...", end=" ", flush=True)
    job = client.query(sql)
    result = job.result()
    fieldnames = [f.name for f in result.schema]
    all_rows = [dict(zip(fieldnames, list(r.values()))) for r in result]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(all_rows)
    print(f"Done ({len(all_rows)} row(s)).")

print(f"\nCSV files saved to: {OUT_DIR}")
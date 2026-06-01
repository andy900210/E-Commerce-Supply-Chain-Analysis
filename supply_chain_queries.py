"""
Run 3 supply chain analytics queries against order_master and save results as CSV.
Project: stalwart-coast-484305-c5
Dataset: ecommerce_supply_chain
"""

import csv
import os
from google.cloud import bigquery

PROJECT_ID = "stalwart-coast-484305-c5"
DATASET_ID = "ecommerce_supply_chain"
VIEW = f"`{PROJECT_ID}.{DATASET_ID}.order_master`"

# Output directory (same folder as this script)
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

client = bigquery.Client(project=PROJECT_ID)

# ---------------------------------------------------------------------------
# Query 1 – Overall delivery performance
# ---------------------------------------------------------------------------
QUERY_1 = f"""
SELECT
  COUNT(*)                                                                                    AS total_delivered_orders,
  ROUND(AVG(delivery_days), 1)                                                                AS avg_actual_delivery_days,
  ROUND(AVG(estimated_days), 1)                                                               AS avg_estimated_delivery_days,
  ROUND(100.0 * COUNTIF(is_late = FALSE) / COUNT(*), 1)                                       AS on_time_delivery_rate_pct,
  ROUND(100.0 * COUNTIF(is_late = TRUE) / COUNT(*), 1)                                        AS late_delivery_rate_pct
FROM {VIEW}
WHERE is_delivered = TRUE
"""

# ---------------------------------------------------------------------------
# Query 2 – Late orders by customer state (top 10 worst)
# ---------------------------------------------------------------------------
QUERY_2 = f"""
SELECT
  c.customer_state,
  COUNT(*)                                                AS total_orders,
  COUNTIF(c.is_late = TRUE)                               AS late_orders,
  ROUND(100.0 * COUNTIF(c.is_late = TRUE) / COUNT(*), 1)  AS late_rate_pct,
  ROUND(AVG(IF(c.is_late = TRUE, c.delay_days, NULL)), 1) AS avg_delay_days
FROM {VIEW} c
WHERE c.is_delivered = TRUE
GROUP BY c.customer_state
ORDER BY late_rate_pct DESC
LIMIT 10
"""

# ---------------------------------------------------------------------------
# Query 3 – Monthly order volume and late rate trend
# ---------------------------------------------------------------------------
QUERY_3 = f"""
SELECT
  FORMAT_TIMESTAMP('%Y-%m', order_purchase_timestamp) AS year_month,
  COUNT(*)                                            AS total_orders,
  COUNTIF(is_delivered = TRUE)                        AS delivered_orders,
  COUNTIF(is_late = TRUE)                             AS late_orders,
  ROUND(100.0 * COUNTIF(is_late = TRUE) / NULLIF(COUNTIF(is_delivered = TRUE), 0), 1) AS late_rate_pct
FROM {VIEW}
WHERE is_delivered = TRUE
GROUP BY year_month
ORDER BY year_month
"""

# ---------------------------------------------------------------------------
# Execute queries and write CSVs
# ---------------------------------------------------------------------------
queries = [
    ("overall_delivery_performance.csv", QUERY_1),
    ("late_orders_by_state_top10.csv", QUERY_2),
    ("monthly_order_volume_trend.csv", QUERY_3),
]

for filename, sql in queries:
    filepath = os.path.join(OUT_DIR, filename)
    print(f"Running: {filename} ...", end=" ", flush=True)

    job = client.query(sql)
    result = job.result()

    # Collect field names from the query schema
    fieldnames = [field.name for field in result.schema]

    # Convert all rows to dicts
    all_rows = []
    for row in result:
        all_rows.append(dict(zip(fieldnames, list(row.values()))))

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"Done ({len(all_rows)} row(s)).")

print(f"\nCSV files saved to: {OUT_DIR}")
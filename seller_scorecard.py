"""
Seller Performance Scorecard
Run against order_master view, compute composite scores, export CSVs.
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
# SQL: Aggregate seller-level metrics
# ---------------------------------------------------------------------------
SQL = f"""
WITH seller_metrics AS (
  SELECT
    seller_id,
    COUNT(DISTINCT order_id)                                                AS total_orders,
    COUNT(DISTINCT IF(is_delivered = TRUE, order_id, NULL))                 AS delivered_orders,
    COUNT(DISTINCT IF(is_late = TRUE AND is_delivered = TRUE, order_id, NULL)) AS late_orders,
    ROUND(AVG(IF(review_score IS NOT NULL, review_score, NULL)), 2)         AS avg_review_score,
    ROUND(100.0 * COUNTIF(review_score <= 2) / NULLIF(COUNT(review_score), 0), 1) AS low_review_pct,
    ROUND(AVG(IF(is_delivered = TRUE, delivery_days, NULL)), 1)             AS avg_delivery_days
  FROM {VIEW}
  WHERE seller_id IS NOT NULL
  GROUP BY seller_id
)
SELECT *
FROM seller_metrics
WHERE delivered_orders >= 10
ORDER BY seller_id
"""

# ---------------------------------------------------------------------------
# Execute query
# ---------------------------------------------------------------------------
print("Fetching seller metrics from BigQuery ...", end=" ", flush=True)
job = client.query(SQL)
result = job.result()
fieldnames = [f.name for f in result.schema]
rows = [dict(zip(fieldnames, list(r.values()))) for r in result]
print(f"Done ({len(rows)} sellers with >= 10 delivered orders).")

# ---------------------------------------------------------------------------
# Compute composite_score in Python
# ---------------------------------------------------------------------------
for r in rows:
    on_time_rate = 100.0 - (r["late_orders"] / r["delivered_orders"] * 100.0) if r["delivered_orders"] > 0 else 0.0
    r["on_time_rate"] = round(on_time_rate, 1)

    review_score = r["avg_review_score"] or 0
    low_rev_pct = r["low_review_pct"] or 0

    composite = (
        0.40 * on_time_rate
        + 0.40 * (review_score / 5.0 * 100.0)
        + 0.20 * (100.0 - low_rev_pct)
    )
    r["composite_score"] = round(composite, 2)

# Sort descending by composite_score
rows.sort(key=lambda x: x["composite_score"], reverse=True)

# ---------------------------------------------------------------------------
# Top 20 and Bottom 20
# ---------------------------------------------------------------------------
top20 = rows[:20]
bottom20 = rows[-20:]

# Write top 20
cols_top = [
    "seller_id", "total_orders", "delivered_orders", "late_orders",
    "on_time_rate", "avg_review_score", "low_review_pct",
    "avg_delivery_days", "composite_score"
]
with open(os.path.join(OUT_DIR, "seller_scorecard_top20.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols_top, extrasaction="ignore")
    w.writeheader()
    w.writerows(top20)
print(f"Saved: seller_scorecard_top20.csv ({len(top20)} rows).")

# Write bottom 20
with open(os.path.join(OUT_DIR, "seller_scorecard_bottom20.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols_top, extrasaction="ignore")
    w.writeheader()
    w.writerows(bottom20)
print(f"Saved: seller_scorecard_bottom20.csv ({len(bottom20)} rows).")

# ---------------------------------------------------------------------------
# Summary stats
# ---------------------------------------------------------------------------
scores = [r["composite_score"] for r in rows]
scores_sorted = sorted(scores)
n = len(scores)

def percentile(data, p):
    """Linear-interpolation percentile (0 <= p <= 100)."""
    if not data:
        return None
    k = (p / 100.0) * (len(data) - 1)
    f = int(k)  # floor
    c = k - f   # fractional part
    if f + 1 < len(data):
        return round(data[f] + c * (data[f + 1] - data[f]), 2)
    return round(data[f], 2)

summary = [
    {
        "metric": "seller_count",
        "value": n,
    },
    {
        "metric": "avg_composite_score",
        "value": round(sum(scores) / n, 2),
    },
    {
        "metric": "min_composite_score",
        "value": round(min(scores), 2),
    },
    {
        "metric": "max_composite_score",
        "value": round(max(scores), 2),
    },
    {
        "metric": "p25_composite_score",
        "value": percentile(scores_sorted, 25),
    },
    {
        "metric": "p50_composite_score",
        "value": percentile(scores_sorted, 50),
    },
    {
        "metric": "p75_composite_score",
        "value": percentile(scores_sorted, 75),
    },
    {
        "metric": "p90_composite_score",
        "value": percentile(scores_sorted, 90),
    },
]

with open(os.path.join(OUT_DIR, "seller_scorecard_summary.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["metric", "value"])
    w.writeheader()
    w.writerows(summary)
print(f"Saved: seller_scorecard_summary.csv ({len(summary)} rows).")

print("\n=== Seller Scorecard Complete ===")
print(f"Total sellers evaluated: {n}")
print(f"Avg composite score: {summary[1]['value']}")
print(f"Score range: {summary[2]['value']} – {summary[3]['value']}")
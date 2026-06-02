"""Verify the order_master view by running a sample query."""
from google.cloud import bigquery

PROJECT_ID = "stalwart-coast-484305-c5"
DATASET_ID = "ecommerce_supply_chain"

client = bigquery.Client(project=PROJECT_ID)

# 1. Verify the view exists and check row count
query = f"""
SELECT
  COUNT(*) AS total_rows,
  COUNT(DISTINCT order_id) AS distinct_orders,
  COUNT(DISTINCT customer_id) AS distinct_customers,
  COUNT(DISTINCT seller_id) AS distinct_sellers,
  COUNT(DISTINCT product_id) AS distinct_products
FROM `{PROJECT_ID}.{DATASET_ID}.order_master`
"""
print("=== View Summary ===")
for row in client.query(query).result():
    for key, value in row.items():
        print(f"  {key}: {value:,}")

# 2. Sample 10 rows showing key delivery metrics
query2 = f"""
SELECT
  order_id,
  order_status,
  delivery_days,
  estimated_days,
  delay_days,
  is_late,
  is_delivered,
  product_category_name,
  product_category_name_english,
  review_score,
  total_payment_value
FROM `{PROJECT_ID}.{DATASET_ID}.order_master`
ORDER BY order_purchase_timestamp DESC
LIMIT 10
"""
print("\n=== Sample Rows (most recent canceled) ===")
for row in client.query(query2).result():
    print(dict(row))

# 3. Sample delivered orders to verify calculated metrics
query3 = f"""
SELECT
  order_id,
  order_status,
  delivery_days,
  estimated_days,
  delay_days,
  is_late,
  is_delivered,
  product_category_name,
  product_category_name_english,
  review_score,
  total_payment_value
FROM `{PROJECT_ID}.{DATASET_ID}.order_master`
WHERE is_delivered = TRUE
ORDER BY RAND()
LIMIT 5
"""
print("\n=== Sample Rows (random delivered) ===")
for row in client.query(query3).result():
    print(dict(row))

print("\n=== Verification complete. ===")

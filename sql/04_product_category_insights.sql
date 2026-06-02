-- ============================================================================
-- Module 04: Product Category Insights
-- Project:   stalwart-coast-484305-c5
-- Dataset:   ecommerce_supply_chain
-- ============================================================================

-- ----------------------------------------
-- Query 4A: Category sales performance (top 25 by revenue, ≥100 orders)
-- ----------------------------------------
SELECT
  COALESCE(product_category_name_english, 'uncategorized') AS category,
  ROUND(SUM(item_total), 2)                                 AS total_revenue,
  COUNT(DISTINCT order_id)                                  AS total_orders,
  ROUND(AVG(item_total), 2)                                 AS avg_order_value,
  ROUND(AVG(review_score), 2)                               AS avg_review_score,
  ROUND(100.0 * COUNTIF(is_late = TRUE AND is_delivered = TRUE)
             / NULLIF(COUNTIF(is_delivered = TRUE), 0), 1)  AS late_rate_pct,
  ROUND(AVG(IF(is_delivered = TRUE, delivery_days, NULL)), 1) AS avg_delivery_days
FROM `stalwart-coast-484305-c5.ecommerce_supply_chain.order_master`
GROUP BY category
HAVING COUNT(DISTINCT order_id) >= 100
ORDER BY total_revenue DESC
LIMIT 25;


-- ----------------------------------------
-- Query 4B: High-risk categories (review < 3.5 OR late > 15%)
-- ----------------------------------------
SELECT
  COALESCE(product_category_name_english, 'uncategorized') AS category,
  ROUND(SUM(item_total), 2)                                 AS total_revenue,
  COUNT(DISTINCT order_id)                                  AS total_orders,
  ROUND(AVG(item_total), 2)                                 AS avg_order_value,
  ROUND(AVG(review_score), 2)                               AS avg_review_score,
  ROUND(100.0 * COUNTIF(is_late = TRUE AND is_delivered = TRUE)
             / NULLIF(COUNTIF(is_delivered = TRUE), 0), 1)  AS late_rate_pct,
  ROUND(AVG(IF(is_delivered = TRUE, delivery_days, NULL)), 1) AS avg_delivery_days
FROM `stalwart-coast-484305-c5.ecommerce_supply_chain.order_master`
GROUP BY category
HAVING
  COUNT(DISTINCT order_id) >= 50
  AND (AVG(review_score) < 3.5
       OR COUNTIF(is_late = TRUE AND is_delivered = TRUE) > 0.15 * COUNTIF(is_delivered = TRUE))
ORDER BY avg_review_score ASC;

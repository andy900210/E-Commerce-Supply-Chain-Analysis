-- ============================================================================
-- Module 02: Delivery Performance Analysis
-- Project:   stalwart-coast-484305-c5
-- Dataset:   ecommerce_supply_chain
-- ============================================================================

-- ----------------------------------------
-- Query 2A: Overall delivery performance
-- ----------------------------------------
SELECT
  COUNT(*)                                                              AS total_delivered_orders,
  ROUND(AVG(delivery_days), 1)                                          AS avg_actual_delivery_days,
  ROUND(AVG(estimated_days), 1)                                         AS avg_estimated_delivery_days,
  ROUND(100.0 * COUNTIF(is_late = FALSE) / COUNT(*), 1)                 AS on_time_delivery_rate_pct,
  ROUND(100.0 * COUNTIF(is_late = TRUE)  / COUNT(*), 1)                 AS late_delivery_rate_pct
FROM `stalwart-coast-484305-c5.ecommerce_supply_chain.order_master`
WHERE is_delivered = TRUE;


-- ----------------------------------------
-- Query 2B: Late orders by customer state (top 10 worst)
-- ----------------------------------------
SELECT
  customer_state,
  COUNT(*)                                                              AS total_orders,
  COUNTIF(is_late = TRUE)                                               AS late_orders,
  ROUND(100.0 * COUNTIF(is_late = TRUE) / COUNT(*), 1)                  AS late_rate_pct,
  ROUND(AVG(IF(is_late = TRUE, delay_days, NULL)), 1)                   AS avg_delay_days
FROM `stalwart-coast-484305-c5.ecommerce_supply_chain.order_master`
WHERE is_delivered = TRUE
GROUP BY customer_state
ORDER BY late_rate_pct DESC
LIMIT 10;


-- ----------------------------------------
-- Query 2C: Monthly order volume and late rate trend
-- ----------------------------------------
SELECT
  FORMAT_TIMESTAMP('%Y-%m', order_purchase_timestamp)                   AS year_month,
  COUNT(*)                                                              AS total_orders,
  COUNTIF(is_delivered = TRUE)                                          AS delivered_orders,
  COUNTIF(is_late = TRUE)                                               AS late_orders,
  ROUND(
    100.0 * COUNTIF(is_late = TRUE)
          / NULLIF(COUNTIF(is_delivered = TRUE), 0), 1
  )                                                                     AS late_rate_pct
FROM `stalwart-coast-484305-c5.ecommerce_supply_chain.order_master`
WHERE is_delivered = TRUE
GROUP BY year_month
ORDER BY year_month;

-- ============================================================================
-- Module 03: Seller Scorecard — Composite Performance Scoring
-- Project:   stalwart-coast-484305-c5
-- Dataset:   ecommerce_supply_chain
--
-- Note: The composite_score calculation (weighted formula) is done in
-- Python in seller_scorecard.py. This SQL fetches the raw metrics that
-- feed into the scorecard.
-- ============================================================================

WITH seller_metrics AS (
  SELECT
    seller_id,
    COUNT(DISTINCT order_id)                                                AS total_orders,
    COUNT(DISTINCT IF(is_delivered = TRUE, order_id, NULL))                 AS delivered_orders,
    COUNT(DISTINCT IF(is_late = TRUE AND is_delivered = TRUE, order_id, NULL)) AS late_orders,
    ROUND(AVG(IF(review_score IS NOT NULL, review_score, NULL)), 2)         AS avg_review_score,
    ROUND(100.0 * COUNTIF(review_score <= 2) / NULLIF(COUNT(review_score), 0), 1) AS low_review_pct,
    ROUND(AVG(IF(is_delivered = TRUE, delivery_days, NULL)), 1)             AS avg_delivery_days
  FROM `stalwart-coast-484305-c5.ecommerce_supply_chain.order_master`
  WHERE seller_id IS NOT NULL
  GROUP BY seller_id
)
SELECT *
FROM seller_metrics
WHERE delivered_orders >= 10
ORDER BY seller_id;

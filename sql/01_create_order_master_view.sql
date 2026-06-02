-- ============================================================================
-- Module 01: order_master — Master Analytics View
-- Project:   stalwart-coast-484305-c5
-- Dataset:   ecommerce_supply_chain
--
-- Joins all 8 source tables into a single flat view with calculated fields:
--   delivery_days   : actual days from purchase to delivery
--   estimated_days  : promised delivery days
--   delay_days      : actual minus estimated (negative = early, positive = late)
--   is_late         : TRUE if delivered after estimated date
--   is_delivered    : TRUE if order_status = 'delivered'
-- ============================================================================

CREATE OR REPLACE VIEW `stalwart-coast-484305-c5.ecommerce_supply_chain.order_master` AS

WITH
  -- Aggregate payments to one row per order (handles multi-installment orders)
  order_payments_agg AS (
    SELECT
      order_id,
      SUM(payment_value)                          AS total_payment_value,
      COUNT(DISTINCT payment_type)                AS payment_type_count,
      ARRAY_AGG(DISTINCT payment_type IGNORE NULLS) AS payment_types,
      MAX(payment_installments)                   AS payment_installments
    FROM `stalwart-coast-484305-c5.ecommerce_supply_chain.olist_order_payments_dataset`
    GROUP BY order_id
  )

SELECT
  -- -------------------------------------------------
  -- Order (base)
  -- -------------------------------------------------
  o.order_id,
  o.customer_id,
  o.order_status,
  o.order_purchase_timestamp,
  o.order_approved_at,
  o.order_delivered_carrier_date,
  o.order_delivered_customer_date,
  o.order_estimated_delivery_date,

  -- Calculated delivery metrics
  TIMESTAMP_DIFF(o.order_delivered_customer_date, o.order_purchase_timestamp, DAY)      AS delivery_days,
  TIMESTAMP_DIFF(o.order_estimated_delivery_date, o.order_purchase_timestamp, DAY)      AS estimated_days,
  TIMESTAMP_DIFF(o.order_delivered_customer_date, o.order_estimated_delivery_date, DAY) AS delay_days,
  (o.order_delivered_customer_date > o.order_estimated_delivery_date)                   AS is_late,
  (o.order_status = 'delivered')                                                         AS is_delivered,

  -- -------------------------------------------------
  -- Order item
  -- -------------------------------------------------
  i.order_item_id,
  i.product_id,
  i.seller_id,
  i.shipping_limit_date,
  i.price                     AS item_price,
  i.freight_value,
  i.price + i.freight_value   AS item_total,

  -- -------------------------------------------------
  -- Product
  -- -------------------------------------------------
  p.product_category_name,
  p.product_name_lenght,
  p.product_description_lenght,
  p.product_photos_qty,
  p.product_weight_g,
  p.product_length_cm,
  p.product_height_cm,
  p.product_width_cm,

  -- -------------------------------------------------
  -- Product category translation (English)
  -- -------------------------------------------------
  t.string_field_1            AS product_category_name_english,

  -- -------------------------------------------------
  -- Customer
  -- -------------------------------------------------
  c.customer_unique_id,
  c.customer_zip_code_prefix,
  c.customer_city,
  c.customer_state,

  -- -------------------------------------------------
  -- Seller
  -- -------------------------------------------------
  s.seller_zip_code_prefix,
  s.seller_city,
  s.seller_state,

  -- -------------------------------------------------
  -- Payment (aggregated per order)
  -- -------------------------------------------------
  pay.total_payment_value,
  pay.payment_type_count,
  pay.payment_types,
  pay.payment_installments,

  -- -------------------------------------------------
  -- Review
  -- -------------------------------------------------
  r.review_id,
  r.review_score,
  r.review_comment_title,
  r.review_comment_message,
  r.review_creation_date,
  r.review_answer_timestamp

FROM `stalwart-coast-484305-c5.ecommerce_supply_chain.olist_orders_dataset` o
  LEFT JOIN `stalwart-coast-484305-c5.ecommerce_supply_chain.olist_order_items_dataset` i
    ON o.order_id = i.order_id
  LEFT JOIN order_payments_agg pay
    ON o.order_id = pay.order_id
  LEFT JOIN `stalwart-coast-484305-c5.ecommerce_supply_chain.olist_order_reviews_dataset` r
    ON o.order_id = r.order_id
  LEFT JOIN `stalwart-coast-484305-c5.ecommerce_supply_chain.olist_customers_dataset` c
    ON o.customer_id = c.customer_id
  LEFT JOIN `stalwart-coast-484305-c5.ecommerce_supply_chain.olist_sellers_dataset` s
    ON i.seller_id = s.seller_id
  LEFT JOIN `stalwart-coast-484305-c5.ecommerce_supply_chain.olist_products_dataset` p
    ON i.product_id = p.product_id
  LEFT JOIN `stalwart-coast-484305-c5.ecommerce_supply_chain.product_category_name_translation` t
    ON p.product_category_name = t.string_field_0;

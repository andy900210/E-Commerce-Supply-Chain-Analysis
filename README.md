# Brazilian E-Commerce Supply Chain Analytics

Delivery performance, seller reliability, and category risk analysis for a Brazilian e-commerce marketplace. Built on Google BigQuery using the Olist dataset (100K+ orders).

## Background

This was my first BigQuery project — a full walkthrough of how I approach supply chain data when dropped into a new marketplace. The Olist dataset is messy in the way real data is messy: 9 tables with inconsistent timestamps, sellers with 1 order sitting next to sellers with 2,000, and product categories that sometimes just say "uncategorized."

I built a unified master view, then systematically answered the three questions every ops team needs answered: Are we delivering on time? Which sellers are dragging us down? Which product categories are problems?

## Data

9 tables from the Olist Brazilian E-Commerce dataset (Kaggle):
- 99,441 orders, 112,650 order items
- 3,095 sellers, 32,951 products
- Full delivery tracking with timestamps

## What I Found

**Delivery is better than it looks on paper.** The marketplace delivers in 12 days on average while promising 23.4 days — a 49% buffer that results in 92.1% on-time rate. Customers are being pleasantly surprised, which is actually good CX strategy.

**But the Northeast is broken.** Alagoas has a 24.1% late rate, Maranhão 20.2%. These aren't just "below average" — they're structurally underserved by the logistics network. A customer in Alagoas waits 8.5 extra days on average.

**March 2018 was a disaster** — 20.4% late rate, likely the hangover from a holiday demand spike that overwhelmed fulfillment capacity.

**The bottom seller is catastrophically bad:** 35.7% on-time, 1.72-star average review, 77.8% of reviews are 1-2 stars. This seller should have been deplatformed months ago.

**Only 2 product categories are truly high-risk** — "uncategorized" (data quality issue, not a logistics issue) and "office furniture" (bulky items averaging 20.4 days delivery with 3.49-star reviews).

## Modules

| # | Focus | What it answers |
|---|-------|-----------------|
| 01 | Data Model | `order_master` view joining all 9 tables with calculated fields |
| 02 | Delivery Performance | On-time rates, state rankings, monthly trends |
| 03 | Seller Scorecard | Composite score: 40% on-time + 40% review + 20% low-review penalty |
| 04 | Category Insights | Revenue leaders and categories that damage customer satisfaction |

## Project Structure

```
├── README.md
├── sql/
│   ├── 01_create_order_master_view.sql
│   ├── 02_delivery_performance.sql
│   ├── 03_seller_scorecard.sql
│   └── 04_product_category_insights.sql
├── python/
│   ├── upload_to_bigquery.py
│   ├── supply_chain_queries.py
│   ├── seller_scorecard.py
│   └── product_category_insights.py
└── output/
    ├── overall_delivery_performance.csv
    ├── late_orders_by_state_top10.csv
    ├── monthly_order_volume_trend.csv
    ├── seller_scorecard_top20.csv
    ├── seller_scorecard_bottom20.csv
    └── category_high_risk.csv
```

## How to Run

1. Download the [Olist dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) from Kaggle
2. Run `python python/upload_to_bigquery.py` to load into BigQuery
3. Execute SQL scripts in order (01 creates the view, 02-04 are independent queries)
4. Python scripts generate the CSV reports in `output/`

## About

I work in data warehousing and supply chain analytics. This project uses public data to demonstrate the same analytical patterns I apply professionally — delivery SLA monitoring, supplier scorecards, category risk assessment — without exposing proprietary business data from my employer.

Andy Yin — [LinkedIn](https://www.linkedin.com/in/andy900210) | [GitHub](https://github.com/andy900210)

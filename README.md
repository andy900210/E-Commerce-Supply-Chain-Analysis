# Brazilian E-Commerce Supply Chain Analytics

## Project Overview

A comprehensive supply chain analytics project built on **Google BigQuery**, analyzing **99,441 orders**, **112,650 order items**, **3,095 sellers**, and **32,951 products** from the Brazilian e-commerce marketplace Olist. This project evaluates delivery performance, seller reliability, and product category health to uncover actionable supply chain optimization opportunities.

**Platform:** Google BigQuery  
**Dataset:** [Olist Brazilian E-Commerce Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (Kaggle)  
**Scale:** 99,441 orders | 112,650 order items | 3,095 sellers | 32,951 products | 9 tables

---

## Business Context

A mid-size e-commerce marketplace needs to:
1. **Track delivery performance** — Are we delivering on time? Which regions are struggling?
2. **Evaluate seller reliability** — Which sellers are stars vs. risks?
3. **Identify product category risks** — Are certain categories damaging customer satisfaction?
4. **Build data-driven dashboards** — Enable stakeholders to make informed decisions
5. **Quantify late delivery impact** — Understand the cost and frequency of supply chain failures

---

## Analytical Modules

| Module | Focus Area | Key Deliverable |
|--------|-----------|-----------------|
| **01** | Data Model | `order_master` view — unified 360° view joining all 9 tables |
| **02** | Delivery Performance | Overall KPIs, state-level ranking, monthly trend |
| **03** | Seller Scorecard | Composite score (on-time × review quality × low-review rate) |
| **04** | Category Insights | Revenue leaders & high-risk categories |

---

## Key Findings

### Delivery Performance (Module 02)
- **On-time delivery rate: 92.1%** — marketplace average is strong
- **Avg actual delivery: 12.0 days** vs. **23.4 days estimated** → delivering 49% faster than promised
- **Worst performing state: Alagoas (AL)** — 24.1% late rate, buyers wait 8.5 extra days on average
- **Most volatile month: March 2018** — 20.4% late rate (peak operational strain)
- **November 2017 (Black Friday):** 13.8% late rate on 8,537 orders — seasonal demand spike

### Seller Scorecard (Module 03)
- **1,238 sellers** evaluated with ≥ 10 delivered orders
- **Average composite score: 86.58 / 100** — most sellers perform well
- **Top sellers:** Perfect 100% on-time, 5.0★ reviews, 0% low reviews
- **Bottom seller (score 32.49):** Only 35.7% on-time, 1.72★ avg review, 77.8% of reviews ≤ 2 stars — clear exit candidate
- **Score distribution:** 90th percentile = 94.41, showing a healthy tail of excellent sellers

### Category Insights (Module 04)
- **Top revenue driver:** Health & Beauty — 1.45M BRL across 8,836 orders
- **Highest AOV:** Computers — 1,147 BRL (but only 181 orders — niche/high-value)
- **Best performing:** Luggage Accessories — 4.32★ reviews, only 5.4% late rate
- ⚠️ **High-risk categories identified:**
  - **Uncategorized products** (2,248 orders, 3.16★ avg) — missing category mapping data
  - **Office Furniture** (1,273 orders, 20.4 days avg delivery) — slow logistics for bulky items, 3.49★ reviews

---

## Technical Skills Demonstrated

- **Google BigQuery:** Complex multi-table joins, CTEs, window functions, `COUNTIF`, `TIMESTAMP_DIFF`, `FORMAT_TIMESTAMP`, schema auto-detection
- **Data Modeling:** Star-schema dimensional design, aggregated master views, denormalized analytics views
- **Supply Chain Analytics:** On-time delivery rate, late rate, lead time analysis, category risk assessment, seller segmentation
- **Data Engineering:** CSV-to-BigQuery pipeline with auto-detect schema, `WRITE_TRUNCATE` for idempotent reloads
- **Python:** BigQuery client library, CSV export, composite scoring algorithms
- **Business Framing:** Translating raw SQL outputs into procurement and logistics recommendations

---

## Project Structure

```
├── README.md
├── .gitignore
├── sql/
│   ├── 01_create_order_master_view.sql       — Unified master view (9 tables joined)
│   ├── 02_delivery_performance.sql            — 3 delivery KPI queries
│   ├── 03_seller_scorecard.sql                — Seller raw metrics query
│   └── 04_product_category_insights.sql       — Sales & risk category queries
├── python/
│   ├── upload_to_bigquery.py                  — CSV → BigQuery upload pipeline
│   ├── verify_order_master.py                 — View validation script
│   ├── supply_chain_queries.py                — Delivery performance queries
│   ├── seller_scorecard.py                    — Seller composite scoring
│   └── product_category_insights.py           — Category analysis queries
└── output/
    ├── overall_delivery_performance.csv
    ├── late_orders_by_state_top10.csv
    ├── monthly_order_volume_trend.csv
    ├── seller_scorecard_top20.csv
    ├── seller_scorecard_bottom20.csv
    ├── seller_scorecard_summary.csv
    ├── category_sales_performance_top25.csv
    └── category_high_risk.csv
```

---

## How to Reproduce

1. **Load the dataset into BigQuery:**
   ```bash
   python python/upload_to_bigquery.py
   ```
   (Requires Google Cloud SDK authenticated with `gcloud auth application-default login`)

2. **Create the master analytics view:**
   Run `sql/01_create_order_master_view.sql` in BigQuery SQL workspace or via `bq query`

3. **Run analytical queries:**
   - `sql/02_delivery_performance.sql` — Delivery KPIs
   - `sql/03_seller_scorecard.sql` — Seller metrics (composite scoring in Python)
   - `sql/04_product_category_insights.sql` — Category analysis

4. **Generate CSV reports:**
   ```bash
   python python/supply_chain_queries.py
   python python/seller_scorecard.py
   python python/product_category_insights.py
   ```

---

## About

Built by **Andy Yin** — Data & Supply Chain Analytics Specialist.

This project showcases end-to-end supply chain analytics capabilities using public data (Olist Brazilian E-Commerce Dataset). It demonstrates practical application of BigQuery SQL, Python data pipelines, and business intelligence techniques that are directly transferable to real-world supply chain and procurement analytics roles.

**Contact:** [LinkedIn](https://www.linkedin.com/in/andy900210) | [GitHub](https://github.com/andy900210)

---

> *Note: Some analytical approaches demonstrated here (seller scoring, category risk assessment) mirror methodologies used in professional supply chain analytics engagements. The public dataset is used as a proxy to demonstrate analytical capabilities while respecting employer confidentiality agreements.*

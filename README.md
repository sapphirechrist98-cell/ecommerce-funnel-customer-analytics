Markdown
# 🛒 E-Commerce Product Funnel & Revenue Analytics Pipeline

An end-to-end data analytics pipeline analyzing customer drop-offs and marketing attribution across 3,600+ user interactions and $715K+ in transaction revenue.

Built with **Python (Pandas ETL)**, **MySQL (CTEs & Window Functions)**, and **Power BI (DAX Modeling & Executive Dashboards)**.

---

## 📊 Executive Dashboard Overview

[dashboard_overview.png]

---

## 📌 Executive Summary & Key Metrics
* **Total Sessions Analyzed:** **1,500** unique visitor sessions.
* **Overall Store Conversion Rate:** **13.67%** (205 completed orders).
* **Total Net Revenue:** **$715.51K** (₹7.15 Lakhs).
* **Average Order Value (AOV):** **$3,490.29**.
* **Primary Funnel Bottleneck:** **50.28%** of visitors drop off between **Product Detail View** and **Add to Cart**—identifying product page pricing transparency and trust signals as primary optimization levers.
* **Top Revenue Drivers:** **Direct** and **Organic Search** generate over 45% of total revenue.

---

## 🏗️ Technical Architecture & Pipeline

Raw Clickstream & Orders -> Python ETL (Pandas) -> Clean CSVs -> MySQL Analytics & Power BI Dashboard

1. **Step 1:** Ingestion & Deduplication (Dropped 25 duplicate clicks)
2. **Step 2:** Categorical Normalization (Standardized channels & devices)
3. **Step 3:** Timestamp Parsing (ISO & UK/Indian mixed formats)
4. **Step 4:** Financial Math (Regex price cleaning, Gross & Net Revenue)
5. **Step 5:** Funnel Feature Engineering (Stage ranks 1-5, click sequencing)
6. **Step 6:** Export Clean Production Tables

---

## 🔍 Core SQL Queries

### 1. Funnel Volumes & Cumulative Conversion Rate (CTEs)
```sql
WITH funnel_counts AS (
    SELECT 
        stage_rank,
        CASE 
            WHEN stage_rank = 1 THEN '1. Homepage View'
            WHEN stage_rank = 2 THEN '2. Product Detail View'
            WHEN stage_rank = 3 THEN '3. Add to Cart'
            WHEN stage_rank = 4 THEN '4. Initiate Checkout'
            WHEN stage_rank = 5 THEN '5. Purchase Success'
        END AS stage_name,
        COUNT(DISTINCT session_id) AS unique_sessions
    FROM ecommerce_events
    GROUP BY stage_rank, stage_name
)
SELECT 
    stage_rank,
    stage_name,
    unique_sessions,
    ROUND((unique_sessions * 100.0) / (SELECT unique_sessions FROM funnel_counts WHERE stage_rank = 1), 2) AS pct_of_homepage_visitors
FROM funnel_counts
ORDER BY stage_rank;
2. Stage-to-Stage Drop-Off Rate (LAG Window Function)
SQL
WITH funnel_counts AS (
    SELECT 
        stage_rank,
        COUNT(DISTINCT session_id) AS current_stage_sessions
    FROM ecommerce_events
    GROUP BY stage_rank
),
funnel_lag AS (
    SELECT 
        stage_rank,
        current_stage_sessions,
        LAG(current_stage_sessions, 1) OVER (ORDER BY stage_rank) AS previous_stage_sessions
    FROM funnel_counts
)
SELECT 
    stage_rank,
    previous_stage_sessions,
    current_stage_sessions,
    (previous_stage_sessions - current_stage_sessions) AS dropped_sessions,
    ROUND(((previous_stage_sessions - current_stage_sessions) * 100.0) / previous_stage_sessions, 2) AS drop_off_pct
FROM funnel_lag
ORDER BY stage_rank;
📊 Key DAX Measures
Total Sessions: DISTINCTCOUNT(clean_ecommerce_events[session_id])

Total Orders: DISTINCTCOUNT(clean_ecommerce_orders[order_id])

Total Net Revenue: SUM(clean_ecommerce_orders[net_revenue])

Overall Conversion Rate %: DIVIDE([Total Orders], [Total Sessions], 0)

Average Order Value (AOV): DIVIDE([Total Net Revenue], [Total Orders], 0)

🛠️ How to Run Locally
Clone this repository:
git clone https://github.com/sapphirechrist98-cell/ecommerce-funnel-customer-analytics.git

Run the ETL pipeline:
python ecommerce_etl_pipeline.py

Load clean CSVs into MySQL and execute Project1_Ecommerce_Funnel.sql.

Open Project1_Ecommerce_Funnel_Dashboard.pbix in Power BI Desktop to interact with the visual dashboard.

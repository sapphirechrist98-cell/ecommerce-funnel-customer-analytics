"""
Project 1: E-Commerce Product Funnel & Customer Analytics
Script: ecommerce_etl_pipeline.py
Author: Sunil Kumar S
"""

import os
import re
import numpy as np
import pandas as pd

# =============================================================================
# [ETL STEP 1]: Data Ingestion & Deduplication
# =============================================================================
print("=" * 70)
print(">>> [ETL STEP 1]: Ingesting raw datasets...")
print("=" * 70)

events_file = "raw_ecommerce_events.csv"
orders_file = "raw_ecommerce_orders.csv"

df_events = pd.read_csv(events_file)
df_orders = pd.read_csv(orders_file)

initial_events_len = len(df_events)
initial_orders_len = len(df_orders)

df_events = df_events.drop_duplicates().copy()
df_orders = df_orders.drop_duplicates().copy()

print(f"   Deduplicated Events: {initial_events_len:,} -> {len(df_events):,} clean rows")
print(f"   Deduplicated Orders: {initial_orders_len:,} -> {len(df_orders):,} clean rows")


# =============================================================================
# [ETL STEP 2]: Categorical Standardization
# =============================================================================
print("\n" + "=" * 70)
print(">>> [ETL STEP 2]: Standardizing categorical dimensions...")
print("=" * 70)

df_events["device_type"] = df_events["device_type"].astype(str).str.strip().str.capitalize()
df_events["user_type"] = df_events["user_type"].astype(str).str.strip().str.capitalize()

channel_lookup = {
    "organic": "Organic Search",
    "organic search": "Organic Search",
    "direct": "Direct",
    "cpc": "Paid Search",
    "paid search": "Paid Search",
    "social": "Social Media",
    "email": "Email Newsletter",
    "referral": "Referral",
}

df_events["traffic_channel"] = (
    df_events["traffic_channel"]
    .astype(str)
    .str.strip()
    .str.lower()
    .map(lambda x: channel_lookup.get(x, x.title()))
)


# =============================================================================
# [ETL STEP 3]: Timestamp Parsing & Missing Data
# =============================================================================
print("\n" + "=" * 70)
print(">>> [ETL STEP 3]: Parsing timestamps and handling missing data...")
print("=" * 70)

df_events["event_timestamp"] = pd.to_datetime(df_events["event_timestamp"], format="mixed")

df_events["region"] = (
    df_events["region"]
    .fillna("Unknown")
    .replace("", "Unknown")
    .astype(str)
    .str.strip()
    .str.title()
)

df_events.loc[df_events["funnel_stage"].str.lower().str.contains("homepage"), "product_id"] = np.nan


# =============================================================================
# [ETL STEP 4]: Orders Cleaning (Prices, Discounts, Revenues)
# =============================================================================
print("\n" + "=" * 70)
print(">>> [ETL STEP 4]: Cleaning orders table...")
print("=" * 70)

df_orders["unit_price"] = (
    df_orders["raw_unit_price"]
    .astype(str)
    .str.replace(r"[^\d.]", "", regex=True)
    .astype(float)
)

df_orders["discount_rate"] = (
    df_orders["raw_discount"]
    .astype(str)
    .str.replace("%", "", regex=False)
    .str.strip()
    .astype(float)
)
df_orders.loc[df_orders["discount_rate"] > 1.0, "discount_rate"] = (
    df_orders["discount_rate"] / 100.0
)

df_orders["quantity"] = pd.to_numeric(df_orders["quantity"], errors="coerce").fillna(1).astype(int)
df_orders["gross_revenue"] = (df_orders["unit_price"] * df_orders["quantity"]).round(2)
df_orders["net_revenue"] = (df_orders["gross_revenue"] * (1 - df_orders["discount_rate"])).round(2)

payment_map = {
    "upi": "UPI",
    "cc": "Credit Card",
    "credit card": "Credit Card",
    "cod": "Cash on Delivery",
    "dc": "Debit Card",
    "debit card": "Debit Card",
}
df_orders["payment_method"] = (
    df_orders["payment_method"]
    .astype(str)
    .str.strip()
    .str.lower()
    .map(payment_map)
    .fillna("Other")
)

df_orders["order_status"] = df_orders["order_status"].astype(str).str.strip().str.capitalize()
df_orders["order_date"] = pd.to_datetime(df_orders["order_date"], format="mixed")


# =============================================================================
# [ETL STEP 5]: Funnel Feature Engineering
# =============================================================================
print("\n" + "=" * 70)
print(">>> [ETL STEP 5]: Engineering funnel sequence and stage progression...")
print("=" * 70)

stage_hierarchy = {
    "homepage_view": 1,
    "product_detail_view": 2,
    "add_to_cart": 3,
    "initiate_checkout": 4,
    "purchase_success": 5,
    "homepage": 1,
    "product_page": 2,
    "cart": 3,
    "checkout": 4,
    "purchase": 5,
}

df_events["stage_rank"] = (
    df_events["funnel_stage"]
    .astype(str)
    .str.lower()
    .str.strip()
    .map(stage_hierarchy)
)

df_events = df_events.sort_values(by=["session_id", "event_timestamp"]).reset_index(drop=True)
df_events["event_sequence"] = df_events.groupby("session_id").cumcount() + 1

session_max_stage = df_events.groupby("session_id")["stage_rank"].max().rename("max_session_stage")
df_events = df_events.merge(session_max_stage, on="session_id", how="left")

df_events["converted_to_purchase"] = (df_events["max_session_stage"] == 5).astype(int)

total_sessions = df_events["session_id"].nunique()
converted_sessions = df_events[df_events["converted_to_purchase"] == 1]["session_id"].nunique()
overall_conversion_rate = (converted_sessions / total_sessions) * 100

print(f"   Total Unique Sessions: {total_sessions:,}")
print(f"   Converted Sessions (Stage 5): {converted_sessions:,}")
print(f"   Overall Funnel Conversion Rate: {overall_conversion_rate:.2f}%")


# =============================================================================
# [ETL STEP 6]: Export Clean Tables to CSV
# =============================================================================
print("\n" + "=" * 70)
print(">>> [ETL STEP 6]: Exporting clean tables to CSV...")
print("=" * 70)

df_events.to_csv("clean_ecommerce_events.csv", index=False)
df_orders.to_csv("clean_ecommerce_orders.csv", index=False)

print(f"   Successfully exported 'clean_ecommerce_events.csv' ({len(df_events):,} rows)")
print(f"   Successfully exported 'clean_ecommerce_orders.csv' ({len(df_orders):,} rows)")
print("=" * 70)
print(">>> ETL PIPELINE COMPLETED SUCCESSFULLY!")
print("=" * 70)
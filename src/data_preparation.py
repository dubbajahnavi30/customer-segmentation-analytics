"""
Data Preparation and Cleaning Module.
Loads raw transaction records, validates schema, cleans invalid/cancelled orders,
and calculates transaction totals using Pandas.
"""

import os
from typing import Tuple, Dict, Any
import pandas as pd
import numpy as np

def load_and_clean_data(file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Loads raw transaction CSV, performs data validation, cleaning, and preparation.

    Parameters:
        file_path (str): Path to customer_purchase_data.csv.

    Returns:
        clean_df (pd.DataFrame): Validated and cleaned line-item transactions.
        summary_stats (dict): Metadata and cleaning statistics.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Transaction data file not found at: {file_path}")

    # Load dataset
    raw_df = pd.read_csv(file_path)
    initial_rows = len(raw_df)

    # 1. Validate required columns exist
    required_cols = [
        "order_id", "customer_id", "customer_code", "order_date",
        "order_status", "product_id", "quantity", "unit_price"
    ]
    missing_cols = [col for col in required_cols if col not in raw_df.columns]
    if missing_cols:
        raise ValueError(f"Dataset missing required columns: {missing_cols}")

    # 2. Check and remove null values in primary identifying columns
    clean_df = raw_df.dropna(subset=["order_id", "customer_id", "order_date"]).copy()
    null_rows_removed = initial_rows - len(clean_df)

    # 3. Parse order_date to datetime
    clean_df["order_date"] = pd.to_datetime(clean_df["order_date"], errors="coerce")
    clean_df = clean_df.dropna(subset=["order_date"])

    # 4. Filter for valid quantities and unit prices (must be positive)
    invalid_numerical = len(clean_df[(clean_df["quantity"] <= 0) | (clean_df["unit_price"] <= 0)])
    clean_df = clean_df[(clean_df["quantity"] > 0) & (clean_df["unit_price"] > 0)].copy()

    # 5. Filter for fulfilled orders (Completed / Delivered)
    # RFM monetary and frequency should be based on actual fulfilled revenue
    unfulfilled_mask = ~clean_df["order_status"].isin(["Completed", "Delivered"])
    unfulfilled_count = unfulfilled_mask.sum()
    clean_df = clean_df[~unfulfilled_mask].copy()

    # 6. Calculate total line item amount
    clean_df["total_amount"] = clean_df["quantity"] * clean_df["unit_price"]

    # 7. Collect data summary
    summary_stats = {
        "raw_record_count": initial_rows,
        "clean_record_count": len(clean_df),
        "null_rows_removed": null_rows_removed,
        "invalid_numerical_rows_removed": invalid_numerical,
        "unfulfilled_orders_filtered": int(unfulfilled_count),
        "unique_customers": int(clean_df["customer_id"].nunique()),
        "unique_orders": int(clean_df["order_id"].nunique()),
        "earliest_order_date": clean_df["order_date"].min().strftime("%Y-%m-%d %H:%M:%S"),
        "latest_order_date": clean_df["order_date"].max().strftime("%Y-%m-%d %H:%M:%S"),
        "total_revenue": float(np.round(clean_df["total_amount"].sum(), 2))
    }

    return clean_df, summary_stats

if __name__ == "__main__":
    df, stats = load_and_clean_data("data/customer_purchase_data.csv")
    print("--- Data Preparation Summary ---")
    for k, v in stats.items():
        print(f"  {k}: {v}")

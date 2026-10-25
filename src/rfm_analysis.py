"""
RFM Analysis Module.
Calculates Recency, Frequency, and Monetary (RFM) values for each customer
and assigns quantile-based RFM scores (1-5).
"""

from typing import Optional
import pandas as pd
import numpy as np

def calculate_rfm_metrics(
    df: pd.DataFrame,
    snapshot_date: Optional[pd.Timestamp] = None
) -> pd.DataFrame:
    """
    Computes Recency, Frequency, and Monetary (RFM) values for every customer.

    Definitions:
    - RECENCY: Number of days between customer's most recent purchase and reference snapshot date.
               Lower recency indicates a more recent active customer.
    - FREQUENCY: Total count of unique completed orders placed by the customer.
                 Higher frequency indicates repeated engagement.
    - MONETARY: Total sum spent across all valid orders by the customer.
                Higher monetary value indicates greater revenue contribution.

    Parameters:
        df (pd.DataFrame): Cleaned transaction data.
        snapshot_date (pd.Timestamp, optional): Reference date. Defaults to max(order_date) + 1 day.

    Returns:
        rfm_df (pd.DataFrame): Table containing customer_id, customer_code,
                               Recency, Frequency, and Monetary.
    """
    if snapshot_date is None:
        snapshot_date = df["order_date"].max() + pd.Timedelta(days=1)

    # Aggregations per customer
    rfm = df.groupby(["customer_id", "customer_code"]).agg(
        recency=("order_date", lambda x: int((snapshot_date - x.max()).days)),
        frequency=("order_id", "nunique"),
        monetary=("total_amount", "sum")
    ).reset_index()

    rfm["monetary"] = rfm["monetary"].round(2)
    return rfm

def compute_rfm_scores(rfm_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates quintile-based scores (1 to 5) for Recency, Frequency, and Monetary.

    Scoring Logic:
    - Recency Score (R_Score):
      Customers with the lowest recency days get the highest score (5),
      while those with the highest recency days get the lowest score (1).
      Labels: [5, 4, 3, 2, 1] across ascending percentiles.

    - Frequency Score (F_Score):
      Customers with the highest order counts get the highest score (5).
      Ties are handled gracefully using rank-based percentile binning.
      Labels: [1, 2, 3, 4, 5] across ascending percentiles.

    - Monetary Score (M_Score):
      Customers with the highest cumulative spending get the highest score (5).
      Labels: [1, 2, 3, 4, 5] across ascending percentiles.

    Returns:
        df_scored (pd.DataFrame): RFM table enriched with R_Score, F_Score, M_Score,
                                  RFM_Score (string e.g. '543'), and RFM_Mean (float).
    """
    df_scored = rfm_df.copy()

    # Recency: lower is better -> inverse score
    # Using rank(pct=True) to handle duplicate values deterministically
    r_pct = df_scored["recency"].rank(method="first", pct=True)
    df_scored["R_Score"] = pd.cut(
        r_pct,
        bins=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
        labels=[5, 4, 3, 2, 1],
        include_lowest=True
    ).astype(int)

    # Frequency: higher is better
    f_pct = df_scored["frequency"].rank(method="first", pct=True)
    df_scored["F_Score"] = pd.cut(
        f_pct,
        bins=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
        labels=[1, 2, 3, 4, 5],
        include_lowest=True
    ).astype(int)

    # Monetary: higher is better
    m_pct = df_scored["monetary"].rank(method="first", pct=True)
    df_scored["M_Score"] = pd.cut(
        m_pct,
        bins=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
        labels=[1, 2, 3, 4, 5],
        include_lowest=True
    ).astype(int)

    # String composite (e.g., '543') and numerical average
    df_scored["RFM_Score"] = (
        df_scored["R_Score"].astype(str) +
        df_scored["F_Score"].astype(str) +
        df_scored["M_Score"].astype(str)
    )
    df_scored["RFM_Mean"] = (
        (df_scored["R_Score"] + df_scored["F_Score"] + df_scored["M_Score"]) / 3.0
    ).round(2)

    return df_scored

if __name__ == "__main__":
    from data_preparation import load_and_clean_data
    clean_df, _ = load_and_clean_data("data/customer_purchase_data.csv")
    rfm = calculate_rfm_metrics(clean_df)
    rfm_scored = compute_rfm_scores(rfm)
    print("--- Sample Scored RFM Table ---")
    print(rfm_scored.head(10))

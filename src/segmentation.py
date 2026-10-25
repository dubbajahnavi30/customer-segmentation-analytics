"""
Rule-Based Customer Segmentation Module.
Applies transparent, interpretable business rules on RFM scores to segment customers,
generates detailed segment profiles, and documents threshold limitations.
"""

from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np

# Segment characteristics and narrative explanations
SEGMENT_DESCRIPTIONS: Dict[str, Dict[str, str]] = {
    "Champions": {
        "spending_pattern": "High cumulative spend and high order frequency.",
        "characteristics": "Bought recently, purchase often, and spend heavily. Core high-value customer base.",
        "recommendation_hint": "Reward with exclusive loyalty perks, early access to new products, and advocate programs."
    },
    "Loyal Customers": {
        "spending_pattern": "Above-average spend across steady, recurring orders.",
        "characteristics": "Consistent repeat purchasers with good recency and healthy engagement.",
        "recommendation_hint": "Maintain engagement with tailored up-selling, cross-selling, and loyalty incentives."
    },
    "Big Spenders": {
        "spending_pattern": "Substantial monetary spend per transaction despite low overall frequency.",
        "characteristics": "Infrequent buyers who purchase premium, high-ticket items when they do order.",
        "recommendation_hint": "Target with premium product launches, luxury bundles, and high-value offers."
    },
    "New Customers": {
        "spending_pattern": "Low to moderate initial spend on introductory purchases.",
        "characteristics": "Transacted very recently (1-2 purchases total). Fresh additions to the customer base.",
        "recommendation_hint": "Provide seamless onboarding, welcome discounts, and educational product guidance."
    },
    "At Risk": {
        "spending_pattern": "Historically significant spending and frequency, now inactive.",
        "characteristics": "Previously frequent or high-value shoppers who have not purchased in recent months.",
        "recommendation_hint": "Deploy win-back campaigns, reactivation discounts, and feedback surveys."
    },
    "Lost Customers": {
        "spending_pattern": "Minimal cumulative monetary contribution.",
        "characteristics": "Purchased long ago with low frequency and low spend; likely churned entirely.",
        "recommendation_hint": "Low marketing priority; standard seasonal reactivation or remove from costly direct outreach."
    },
    "Potential Loyalists": {
        "spending_pattern": "Moderate spending with steady potential.",
        "characteristics": "Recent buyers with moderate frequency and spending; balanced intermediate profile.",
        "recommendation_hint": "Nurture with membership programs and personalized recommendations to convert to Loyal."
    }
}

def assign_rule_based_segment(row: pd.Series) -> str:
    """
    Assigns an interpretable segment label to a customer row based on R, F, and M scores.

    Rules Hierarchy:
    1. Champions:           R_Score >= 4 AND F_Score >= 4 AND M_Score >= 4
    2. Loyal Customers:     R_Score >= 3 AND F_Score >= 3 AND M_Score >= 3
    3. Big Spenders:        M_Score >= 4 AND F_Score < 3
    4. New Customers:       R_Score >= 4 AND F_Score <= 2
    5. At Risk:             R_Score <= 2 AND (F_Score >= 3 OR M_Score >= 3)
    6. Lost Customers:      R_Score <= 2 AND F_Score <= 2 AND M_Score <= 2
    7. Potential Loyalists: All remaining intermediate combinations
    """
    r = row["R_Score"]
    f = row["F_Score"]
    m = row["M_Score"]

    # Rule 1: Champions
    if r >= 4 and f >= 4 and m >= 4:
        return "Champions"

    # Rule 2: Loyal Customers
    if r >= 3 and f >= 3 and m >= 3:
        return "Loyal Customers"

    # Rule 3: Big Spenders
    if m >= 4 and f < 3:
        return "Big Spenders"

    # Rule 4: New Customers
    if r >= 4 and f <= 2:
        return "New Customers"

    # Rule 5: At Risk
    if r <= 2 and (f >= 3 or m >= 3):
        return "At Risk"

    # Rule 6: Lost Customers
    if r <= 2 and f <= 2 and m <= 2:
        return "Lost Customers"

    # Rule 7: Potential Loyalists
    return "Potential Loyalists"

def apply_rule_based_segmentation(rfm_df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies the rule-based segmentation function across all rows of the scored RFM DataFrame.
    """
    df = rfm_df.copy()
    df["segment_label"] = df.apply(assign_rule_based_segment, axis=1)
    return df

def generate_segment_profiles(segmented_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates detailed summary profile metrics for every customer segment:
    - Customer Count
    - % Customers
    - Avg Recency (days)
    - Avg Frequency (orders)
    - Avg Monetary ($)
    - Total Spending ($)
    - Spending Patterns
    - General Characteristics
    """
    total_customers = len(segmented_df)

    profile_records = []
    # Ensure consistent segment ordering
    segment_order = [
        "Champions", "Loyal Customers", "Big Spenders",
        "Potential Loyalists", "New Customers", "At Risk", "Lost Customers"
    ]

    for segment in segment_order:
        sub = segmented_df[segmented_df["segment_label"] == segment]
        count = len(sub)
        if count == 0:
            continue

        pct = (count / total_customers) * 100.0
        avg_r = sub["recency"].mean()
        avg_f = sub["frequency"].mean()
        avg_m = sub["monetary"].mean()
        tot_m = sub["monetary"].sum()

        desc_info = SEGMENT_DESCRIPTIONS.get(segment, {
            "spending_pattern": "Standard spending pattern.",
            "characteristics": "Standard segment behavior."
        })

        profile_records.append({
            "Segment": segment,
            "Customer Count": int(count),
            "% Customers": round(pct, 2),
            "Avg Recency": round(avg_r, 1),
            "Avg Frequency": round(avg_f, 1),
            "Avg Monetary": round(avg_m, 2),
            "Total Spending": round(tot_m, 2),
            "Spending Patterns": desc_info["spending_pattern"],
            "General Characteristics": desc_info["characteristics"]
        })

    profile_df = pd.DataFrame(profile_records)
    return profile_df

def get_rule_based_limitations() -> str:
    """
    Returns an academic explanation of the inherent limitations of rule-based segmentation.
    """
    return (
        "LIMITATIONS OF RULE-BASED RFM SEGMENTATION:\n"
        "1. Heuristic & Arbitrary Boundaries: Quintile or threshold cutoffs (e.g., R >= 4 vs R = 3) "
        "are chosen by business analysts and do not adapt automatically to underlying natural clusters.\n"
        "2. Boundary Sensitivity: A customer with a score of 3.99 may fall into a different bucket "
        "than one with 4.01 despite nearly identical real-world purchasing behavior.\n"
        "3. Equal Weighting Assumption: RFM rules often assume R, F, and M have equal categorical "
        "importance, whereas in certain industries, Recency or Monetary value may be far more decisive.\n"
        "4. Non-Universal Truth: Segment labels provide a helpful operational heuristic, but they are "
        "not absolute behavioral truths. They must be validated against real campaign outcomes."
    )

if __name__ == "__main__":
    from data_preparation import load_and_clean_data
    from rfm_analysis import calculate_rfm_metrics, compute_rfm_scores

    clean_df, _ = load_and_clean_data("data/customer_purchase_data.csv")
    rfm = calculate_rfm_metrics(clean_df)
    rfm_scored = compute_rfm_scores(rfm)
    segmented = apply_rule_based_segmentation(rfm_scored)
    profiles = generate_segment_profiles(segmented)

    print("--- Customer Segment Profiles Table ---")
    print(profiles[["Segment", "Customer Count", "% Customers", "Avg Recency", "Avg Frequency", "Avg Monetary"]])

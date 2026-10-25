"""
================================================================================
Customer Segmentation and Predictive Analytics System
Main Driver Script
================================================================================
Strictly follows the academic specification:
1. Data Preparation & Cleaning (Pandas, NumPy)
2. RFM Metrics & Scoring (Reproducible Quantiles)
3. Rule-Based RFM Customer Segmentation & Profiles
4. K-Means Clustering (StandardScaler, KMeans, Silhouette Evaluation)
5. Comprehensive RFM vs. K-Means Comparison & Limitations
6. Publication-Quality Visualizations (Matplotlib)
7. MySQL Relational Database Persistence (Customers, Orders, Items, Runs, Segments)
================================================================================
"""

import os
import sys
import pandas as pd
import numpy as np

# Ensure src modules can be imported
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.data_preparation import load_and_clean_data
from src.rfm_analysis import calculate_rfm_metrics, compute_rfm_scores
from src.segmentation import (
    apply_rule_based_segmentation,
    generate_segment_profiles,
    get_rule_based_limitations
)
from src.clustering import (
    explain_kmeans_rationale,
    prepare_and_scale_features,
    evaluate_optimal_k,
    apply_kmeans_clustering,
    generate_cluster_profiles,
    compare_rfm_vs_kmeans,
    get_comparison_limitations
)
from src.visualization import generate_all_visualizations
from src.database import (
    initialize_database,
    store_raw_data_to_mysql,
    record_segmentation_run,
    test_mysql_connection
)

def print_section_header(title: str):
    """Prints a clean, formatted terminal header."""
    print("\n" + "=" * 78)
    print(f" {title}")
    print("=" * 78)

def main():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    data_path = os.path.join(base_dir, "data", "customer_purchase_data.csv")
    schema_path = os.path.join(base_dir, "database", "schema.sql")
    output_dir = os.path.join(base_dir, "output")
    charts_dir = os.path.join(output_dir, "charts")
    os.makedirs(charts_dir, exist_ok=True)

    print_section_header("CUSTOMER SEGMENTATION & PREDICTIVE ANALYTICS SYSTEM")
    print("Academic Pipeline: Rule-Based RFM + K-Means Comparative Analysis")

    # --------------------------------------------------------------------------
    # Step 1: Data Preparation & Cleaning
    # --------------------------------------------------------------------------
    print_section_header("STEP 1: DATA PREPARATION & VALIDATION")
    clean_df, data_stats = load_and_clean_data(data_path)
    print(f"Loaded raw transaction dataset from: {data_path}")
    print(f"Total Transactions:      {data_stats['raw_record_count']:,}")
    print(f"Cleaned Transactions:    {data_stats['clean_record_count']:,}")
    print(f"Unique Customers:        {data_stats['unique_customers']:,}")
    print(f"Unique Orders:           {data_stats['unique_orders']:,}")
    print(f"Date Range:              {data_stats['earliest_order_date']} to {data_stats['latest_order_date']}")
    print(f"Total Net Revenue:       ${data_stats['total_revenue']:,.2f}")

    # --------------------------------------------------------------------------
    # Step 2: MySQL Database Persistence Check
    # --------------------------------------------------------------------------
    print_section_header("STEP 2: MYSQL DATABASE STORAGE")
    mysql_active = test_mysql_connection()
    if mysql_active:
        print("[DATABASE] MySQL connection detected! Initializing schema and tables...")
        initialize_database(schema_path)
        store_raw_data_to_mysql(clean_df)
    else:
        print("[DATABASE NOTE] Local MySQL server not currently reachable on localhost:3306.")
        print("                (Schema is ready in 'database/schema.sql'. Analysis proceeds seamlessly via Pandas).")

    # --------------------------------------------------------------------------
    # Step 3: RFM Calculation & Scoring
    # --------------------------------------------------------------------------
    print_section_header("STEP 3: RFM METRIC COMPUTATION & SCORING")
    rfm_df = calculate_rfm_metrics(clean_df)
    rfm_scored = compute_rfm_scores(rfm_df)
    print(f"Computed R, F, M metrics and quintile scores for {len(rfm_scored)} customers.")
    print("\nSample RFM Table (First 5 records):")
    cols_to_show = ["customer_id", "customer_code", "recency", "frequency", "monetary", "R_Score", "F_Score", "M_Score", "RFM_Score"]
    print(rfm_scored[cols_to_show].head(5).to_string(index=False))

    # --------------------------------------------------------------------------
    # Step 4: Rule-Based RFM Segmentation
    # --------------------------------------------------------------------------
    print_section_header("STEP 4: RULE-BASED RFM SEGMENTATION")
    segmented_rfm = apply_rule_based_segmentation(rfm_scored)
    segment_profiles = generate_segment_profiles(segmented_rfm)

    print("Customer Segment Profiles Table:")
    profile_display_cols = ["Segment", "Customer Count", "% Customers", "Avg Recency", "Avg Frequency", "Avg Monetary", "Total Spending"]
    print(segment_profiles[profile_display_cols].to_string(index=False))

    print("\n" + get_rule_based_limitations())

    # --------------------------------------------------------------------------
    # Step 5: Optional K-Means Clustering
    # --------------------------------------------------------------------------
    print_section_header("STEP 5: K-MEANS CLUSTERING ON RFM FEATURES")
    print(explain_kmeans_rationale())

    print("\n[SCALING] Applying np.log1p transformation and StandardScaler to (R, F, M)...")
    scaled_features, scaler = prepare_and_scale_features(segmented_rfm)

    print("[EVALUATION] Calculating Elbow Inertia and Silhouette Scores for K = 2 to 8...")
    eval_results = evaluate_optimal_k(scaled_features, k_range=range(2, 9), random_state=42)

    eval_df = pd.DataFrame({
        "K (Clusters)": eval_results["k_values"],
        "Inertia (SSE)": [round(i, 2) for i in eval_results["inertias"]],
        "Silhouette Score": eval_results["silhouette_scores"]
    })
    print("\nCluster Diagnostic Evaluation:")
    print(eval_df.to_string(index=False))

    chosen_k = eval_results["recommended_k"]
    print(f"\nOptimal Cluster Count Selected: K = {chosen_k} (Highest Silhouette Score: {max(eval_results['silhouette_scores'])})")

    final_clustered_df, kmeans_model = apply_kmeans_clustering(
        segmented_rfm, scaled_features, n_clusters=chosen_k, random_state=42
    )

    cluster_profiles = generate_cluster_profiles(final_clustered_df)
    print("\nK-Means Cluster Profiles Table:")
    cluster_cols = ["Cluster", "Customer Count", "% Customers", "Avg Recency", "Avg Frequency", "Avg Monetary", "Total Spending", "Cluster Characterization"]
    print(cluster_profiles[cluster_cols].to_string(index=False))

    # --------------------------------------------------------------------------
    # Step 6: RFM vs. K-Means Comparison
    # --------------------------------------------------------------------------
    print_section_header("STEP 6: COMPARATIVE ANALYSIS (RULE-BASED RFM vs. K-MEANS)")
    cross_tab, comparison_summary = compare_rfm_vs_kmeans(final_clustered_df)

    print("Cross-Tabulation Matrix (Overlap of Customer Assignments):")
    print(cross_tab.to_string())

    print("\nSide-by-Side Group Characteristics Comparison:")
    print(comparison_summary.to_string(index=False))

    print("\n" + get_comparison_limitations())

    # --------------------------------------------------------------------------
    # Step 7: Record Runs in MySQL (if connected)
    # --------------------------------------------------------------------------
    if mysql_active:
        print_section_header("STEP 7: PERSISTING RUNS IN MYSQL")
        rfm_run_params = {"rules": "Standard RFM Quintiles Hierarchy", "snapshot_date": "auto"}
        record_segmentation_run("Rule-Based RFM", rfm_run_params, final_clustered_df.set_index("customer_id")["segment_label"])

        kmeans_params = {"k": chosen_k, "scaling": "log1p + StandardScaler", "algorithm": "k-means++", "random_state": 42}
        record_segmentation_run("K-Means", kmeans_params, final_clustered_df.set_index("customer_id")["kmeans_cluster"])

    # --------------------------------------------------------------------------
    # Step 8: Visualizations
    # --------------------------------------------------------------------------
    print_section_header("STEP 8: GENERATING VISUALIZATIONS")
    generate_all_visualizations(
        profiles_df=segment_profiles,
        eval_results=eval_results,
        clustered_df=final_clustered_df,
        cross_tab_df=cross_tab,
        output_dir=charts_dir
    )

    # --------------------------------------------------------------------------
    # Step 9: Save Output CSV Files
    # --------------------------------------------------------------------------
    print_section_header("STEP 9: EXPORTING OUTPUT FILES")
    rfm_table_path = os.path.join(output_dir, "rfm_table.csv")
    profiles_path = os.path.join(output_dir, "segment_profiles.csv")
    cluster_profiles_path = os.path.join(output_dir, "kmeans_cluster_profiles.csv")
    comparison_path = os.path.join(output_dir, "rfm_vs_kmeans_comparison.csv")

    final_clustered_df.to_csv(rfm_table_path, index=False)
    segment_profiles.to_csv(profiles_path, index=False)
    cluster_profiles.to_csv(cluster_profiles_path, index=False)
    cross_tab.to_csv(comparison_path)

    print(f" [1] RFM Table:                   {rfm_table_path}")
    print(f" [2] Segment Profiles:            {profiles_path}")
    print(f" [3] K-Means Cluster Profiles:    {cluster_profiles_path}")
    print(f" [4] RFM vs K-Means Comparison:   {comparison_path}")
    print(f" [5] Visualization Figures:       {charts_dir} (9 high-resolution charts)")

    print_section_header("PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    main()

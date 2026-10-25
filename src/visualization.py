"""
Visualization Module.
Generates academic-quality, publication-grade Matplotlib charts
that directly support customer segmentation analysis.
"""

import os
from typing import Dict, Any, List
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Professional, colorblind-friendly academic color palette
SEGMENT_COLORS = {
    "Champions": "#2E7D32",           # Deep Forest Green
    "Loyal Customers": "#1976D2",     # Cobalt Blue
    "Big Spenders": "#7B1FA2",        # Royal Purple
    "Potential Loyalists": "#0288D1", # Teal / Cyan Blue
    "New Customers": "#F57C00",       # Vibrant Amber
    "At Risk": "#D32F2F",             # Crimson Red
    "Lost Customers": "#757575"       # Charcoal Gray
}

def ensure_output_dir(directory: str):
    """Ensures that the output charts directory exists."""
    os.makedirs(directory, exist_ok=True)

def plot_customer_count_by_segment(profiles_df: pd.DataFrame, output_dir: str):
    """1. Customer count by segment bar chart."""
    ensure_output_dir(output_dir)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    
    segments = profiles_df["Segment"]
    counts = profiles_df["Customer Count"]
    colors = [SEGMENT_COLORS.get(s, "#333333") for s in segments]

    bars = ax.bar(segments, counts, color=colors, edgecolor="black", linewidth=0.8, width=0.6)
    ax.set_title("Customer Count by Segment", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Customer Segment", fontsize=11, fontweight="semibold")
    ax.set_ylabel("Number of Customers", fontsize=11, fontweight="semibold")
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    # Annotate bar values
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f"{int(height)}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 4),
                    textcoords="offset points",
                    ha="center", va="bottom", fontsize=10, fontweight="bold")

    plt.xticks(rotation=25, ha="right", fontsize=10)
    plt.tight_layout()
    file_path = os.path.join(output_dir, "01_customer_count_by_segment.png")
    plt.savefig(file_path, dpi=300)
    plt.close()

def plot_segment_distribution_pie(profiles_df: pd.DataFrame, output_dir: str):
    """2. Segment distribution pie chart."""
    ensure_output_dir(output_dir)
    fig, ax = plt.subplots(figsize=(8, 7))

    segments = profiles_df["Segment"]
    percentages = profiles_df["% Customers"]
    colors = [SEGMENT_COLORS.get(s, "#333333") for s in segments]

    wedges, texts, autotexts = ax.pie(
        percentages,
        labels=segments,
        autopct="%1.1f%%",
        startangle=140,
        colors=colors,
        wedgeprops=dict(width=0.6, edgecolor="white", linewidth=1.5),
        pctdistance=0.75
    )

    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_fontweight("bold")
        autotext.set_fontsize(10)

    for text in texts:
        text.set_fontsize(10)
        text.set_fontweight("semibold")

    ax.set_title("Customer Segment Distribution (% Share)", fontsize=14, fontweight="bold", pad=12)
    plt.tight_layout()
    file_path = os.path.join(output_dir, "02_segment_distribution.png")
    plt.savefig(file_path, dpi=300)
    plt.close()

def plot_spending_by_segment(profiles_df: pd.DataFrame, output_dir: str):
    """3. Spending by segment bar chart (Total Revenue Contribution)."""
    ensure_output_dir(output_dir)
    fig, ax = plt.subplots(figsize=(10, 5.5))

    segments = profiles_df["Segment"]
    spend = profiles_df["Total Spending"]
    colors = [SEGMENT_COLORS.get(s, "#333333") for s in segments]

    bars = ax.bar(segments, spend, color=colors, edgecolor="black", linewidth=0.8, width=0.6)
    ax.set_title("Total Revenue / Spending by Customer Segment ($)", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Customer Segment", fontsize=11, fontweight="semibold")
    ax.set_ylabel("Total Spending ($)", fontsize=11, fontweight="semibold")
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    for bar in bars:
        height = bar.get_height()
        ax.annotate(f"${height:,.0f}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 4),
                    textcoords="offset points",
                    ha="center", va="bottom", fontsize=9, fontweight="bold")

    plt.xticks(rotation=25, ha="right", fontsize=10)
    plt.tight_layout()
    file_path = os.path.join(output_dir, "03_total_spending_by_segment.png")
    plt.savefig(file_path, dpi=300)
    plt.close()

def plot_avg_monetary_by_segment(profiles_df: pd.DataFrame, output_dir: str):
    """4. Average monetary value by segment bar chart."""
    ensure_output_dir(output_dir)
    fig, ax = plt.subplots(figsize=(10, 5.5))

    segments = profiles_df["Segment"]
    avg_m = profiles_df["Avg Monetary"]
    colors = [SEGMENT_COLORS.get(s, "#333333") for s in segments]

    bars = ax.bar(segments, avg_m, color=colors, edgecolor="black", linewidth=0.8, width=0.6)
    ax.set_title("Average Monetary Value by Segment ($)", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Customer Segment", fontsize=11, fontweight="semibold")
    ax.set_ylabel("Mean Spend per Customer ($)", fontsize=11, fontweight="semibold")
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    for bar in bars:
        height = bar.get_height()
        ax.annotate(f"${height:,.2f}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 4),
                    textcoords="offset points",
                    ha="center", va="bottom", fontsize=9, fontweight="bold")

    plt.xticks(rotation=25, ha="right", fontsize=10)
    plt.tight_layout()
    file_path = os.path.join(output_dir, "04_avg_monetary_by_segment.png")
    plt.savefig(file_path, dpi=300)
    plt.close()

def plot_avg_frequency_by_segment(profiles_df: pd.DataFrame, output_dir: str):
    """5. Average frequency by segment bar chart."""
    ensure_output_dir(output_dir)
    fig, ax = plt.subplots(figsize=(10, 5.5))

    segments = profiles_df["Segment"]
    avg_f = profiles_df["Avg Frequency"]
    colors = [SEGMENT_COLORS.get(s, "#333333") for s in segments]

    bars = ax.bar(segments, avg_f, color=colors, edgecolor="black", linewidth=0.8, width=0.6)
    ax.set_title("Average Purchase Frequency by Segment (Orders)", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Customer Segment", fontsize=11, fontweight="semibold")
    ax.set_ylabel("Mean Completed Orders", fontsize=11, fontweight="semibold")
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    for bar in bars:
        height = bar.get_height()
        ax.annotate(f"{height:.1f}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 4),
                    textcoords="offset points",
                    ha="center", va="bottom", fontsize=10, fontweight="bold")

    plt.xticks(rotation=25, ha="right", fontsize=10)
    plt.tight_layout()
    file_path = os.path.join(output_dir, "05_avg_frequency_by_segment.png")
    plt.savefig(file_path, dpi=300)
    plt.close()

def plot_avg_recency_by_segment(profiles_df: pd.DataFrame, output_dir: str):
    """6. Average recency by segment bar chart."""
    ensure_output_dir(output_dir)
    fig, ax = plt.subplots(figsize=(10, 5.5))

    segments = profiles_df["Segment"]
    avg_r = profiles_df["Avg Recency"]
    colors = [SEGMENT_COLORS.get(s, "#333333") for s in segments]

    bars = ax.bar(segments, avg_r, color=colors, edgecolor="black", linewidth=0.8, width=0.6)
    ax.set_title("Average Purchase Recency by Segment (Days Elapsed)", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Customer Segment", fontsize=11, fontweight="semibold")
    ax.set_ylabel("Mean Days Since Last Purchase (Lower = More Recent)", fontsize=11, fontweight="semibold")
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    for bar in bars:
        height = bar.get_height()
        ax.annotate(f"{height:.1f} d",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 4),
                    textcoords="offset points",
                    ha="center", va="bottom", fontsize=10, fontweight="bold")

    plt.xticks(rotation=25, ha="right", fontsize=10)
    plt.tight_layout()
    file_path = os.path.join(output_dir, "06_avg_recency_by_segment.png")
    plt.savefig(file_path, dpi=300)
    plt.close()

def plot_kmeans_elbow_and_silhouette(eval_results: Dict[str, Any], output_dir: str):
    """K-Means diagnostic chart: Elbow Method & Silhouette Score curves."""
    ensure_output_dir(output_dir)
    k_vals = eval_results["k_values"]
    inertias = eval_results["inertias"]
    sil_scores = eval_results["silhouette_scores"]
    recommended_k = eval_results["recommended_k"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # 1. Elbow Curve
    ax1.plot(k_vals, inertias, marker="o", color="#1976D2", linewidth=2.2, markersize=7)
    ax1.set_title("Elbow Method (Inertia vs. Number of Clusters)", fontsize=12, fontweight="bold")
    ax1.set_xlabel("Number of Clusters (K)", fontsize=10, fontweight="semibold")
    ax1.set_ylabel("Within-Cluster Sum of Squares (Inertia)", fontsize=10, fontweight="semibold")
    ax1.grid(True, linestyle="--", alpha=0.5)
    ax1.axvline(x=recommended_k, color="#D32F2F", linestyle=":", label=f"Selected K={recommended_k}")
    ax1.legend()

    # 2. Silhouette Score Curve
    ax2.plot(k_vals, sil_scores, marker="s", color="#388E3C", linewidth=2.2, markersize=7)
    ax2.set_title("Silhouette Score vs. Number of Clusters", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Number of Clusters (K)", fontsize=10, fontweight="semibold")
    ax2.set_ylabel("Average Silhouette Coefficient", fontsize=10, fontweight="semibold")
    ax2.grid(True, linestyle="--", alpha=0.5)
    ax2.axvline(x=recommended_k, color="#D32F2F", linestyle=":", label=f"Max Silhouette K={recommended_k}")
    ax2.legend()

    plt.tight_layout()
    file_path = os.path.join(output_dir, "07_kmeans_elbow_and_silhouette.png")
    plt.savefig(file_path, dpi=300)
    plt.close()

def plot_kmeans_clusters_scatter(clustered_df: pd.DataFrame, output_dir: str):
    """K-Means cluster multi-dimensional scatter visual."""
    ensure_output_dir(output_dir)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    clusters = sorted(clustered_df["kmeans_cluster"].unique())
    cluster_palette = ["#1976D2", "#388E3C", "#F57C00", "#7B1FA2", "#D32F2F", "#0097A7"]

    # Left: Recency vs Frequency
    for i, cl in enumerate(clusters):
        sub = clustered_df[clustered_df["kmeans_cluster"] == cl]
        color = cluster_palette[i % len(cluster_palette)]
        ax1.scatter(sub["recency"], sub["frequency"], label=cl, color=color, alpha=0.75, s=60, edgecolors="white")

    ax1.set_title("K-Means Clusters: Recency vs. Frequency", fontsize=12, fontweight="bold")
    ax1.set_xlabel("Recency (Days)", fontsize=10, fontweight="semibold")
    ax1.set_ylabel("Frequency (Orders)", fontsize=10, fontweight="semibold")
    ax1.grid(True, linestyle="--", alpha=0.5)
    ax1.legend(loc="upper right")

    # Right: Frequency vs Monetary
    for i, cl in enumerate(clusters):
        sub = clustered_df[clustered_df["kmeans_cluster"] == cl]
        color = cluster_palette[i % len(cluster_palette)]
        ax2.scatter(sub["frequency"], sub["monetary"], label=cl, color=color, alpha=0.75, s=60, edgecolors="white")

    ax2.set_title("K-Means Clusters: Frequency vs. Monetary Spending", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Frequency (Orders)", fontsize=10, fontweight="semibold")
    ax2.set_ylabel("Monetary Spending ($)", fontsize=10, fontweight="semibold")
    ax2.grid(True, linestyle="--", alpha=0.5)
    ax2.legend(loc="upper left")

    plt.tight_layout()
    file_path = os.path.join(output_dir, "08_kmeans_clusters_scatter.png")
    plt.savefig(file_path, dpi=300)
    plt.close()

def plot_rfm_vs_kmeans_cross_tab(cross_tab_df: pd.DataFrame, output_dir: str):
    """Visual cross-tabulation matrix comparing Rule-Based Segments vs K-Means Clusters."""
    ensure_output_dir(output_dir)
    fig, ax = plt.subplots(figsize=(10, 6.5))

    # Exclude 'Total' margins for visualization
    matrix_data = cross_tab_df.drop(index="Total", columns="Total", errors="ignore")

    cax = ax.matshow(matrix_data.values, cmap="Blues", alpha=0.85)
    fig.colorbar(cax)

    # Set tick labels
    ax.set_xticks(range(len(matrix_data.columns)))
    ax.set_yticks(range(len(matrix_data.index)))
    ax.set_xticklabels(matrix_data.columns, rotation=30, ha="left", fontsize=10, fontweight="semibold")
    ax.set_yticklabels(matrix_data.index, fontsize=10, fontweight="semibold")

    # Display cell values
    for i in range(len(matrix_data.index)):
        for j in range(len(matrix_data.columns)):
            val = matrix_data.values[i, j]
            ax.text(j, i, f"{val}", ha="center", va="center",
                    color="black" if val < matrix_data.values.max() / 2 else "white",
                    fontsize=11, fontweight="bold")

    ax.set_title("Cross-Tabulation Matrix: Rule-Based Segments vs. K-Means Clusters",
                 fontsize=13, fontweight="bold", pad=20)
    ax.set_xlabel("K-Means Clusters", fontsize=11, fontweight="bold", labelpad=10)
    ax.set_ylabel("Rule-Based RFM Segments", fontsize=11, fontweight="bold")

    plt.tight_layout()
    file_path = os.path.join(output_dir, "09_rfm_vs_kmeans_heatmap.png")
    plt.savefig(file_path, dpi=300)
    plt.close()

def generate_all_visualizations(
    profiles_df: pd.DataFrame,
    eval_results: Dict[str, Any],
    clustered_df: pd.DataFrame,
    cross_tab_df: pd.DataFrame,
    output_dir: str
):
    """Master routine that generates and saves all required charts."""
    print("[VISUALIZATION] Generating required segmentation charts...")
    plot_customer_count_by_segment(profiles_df, output_dir)
    plot_segment_distribution_pie(profiles_df, output_dir)
    plot_spending_by_segment(profiles_df, output_dir)
    plot_avg_monetary_by_segment(profiles_df, output_dir)
    plot_avg_frequency_by_segment(profiles_df, output_dir)
    plot_avg_recency_by_segment(profiles_df, output_dir)
    plot_kmeans_elbow_and_silhouette(eval_results, output_dir)
    plot_kmeans_clusters_scatter(clustered_df, output_dir)
    plot_rfm_vs_kmeans_cross_tab(cross_tab_df, output_dir)
    print(f"[VISUALIZATION] All 9 charts successfully saved to '{output_dir}'.")

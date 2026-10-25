"""
K-Means Clustering and Comparative Analytics Module.
Uses scikit-learn ONLY for StandardScaler, KMeans, and silhouette_score.
Performs feature scaling, optimal K evaluation, data-driven clustering,
cluster profiling, and detailed comparison against rule-based RFM segments.
"""

from typing import Dict, Any, Tuple, List
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

def explain_kmeans_rationale() -> str:
    """
    Returns an academic explanation of why K-Means is used and why scaling is required.
    """
    return (
        "ACADEMIC JUSTIFICATION FOR K-MEANS & FEATURE SCALING:\n\n"
        "1. Why K-Means is Used:\n"
        "   K-Means is an unsupervised, centroid-based machine learning algorithm that partitions\n"
        "   data into K distinct, non-overlapping clusters by minimizing within-cluster sum of squares\n"
        "   (inertia). Unlike rule-based segmentation which relies on fixed, subjective threshold cutoffs,\n"
        "   K-Means autonomously discovers mathematical groupings and multi-dimensional geometric\n"
        "   relationships directly from the empirical distribution of Recency, Frequency, and Monetary metrics.\n\n"
        "2. Why Feature Scaling is Essential:\n"
        "   K-Means relies strictly on Euclidean distance: d(x, y) = sqrt(sum((x_i - y_i)^2)).\n"
        "   In RFM analysis, the three features have drastically different numerical magnitudes:\n"
        "   - Recency spans 1 to ~500 days.\n"
        "   - Frequency spans 1 to ~15 orders.\n"
        "   - Monetary spans $20 to ~$4,000+.\n"
        "   Without normalization, the feature with the largest scale (Monetary) would completely dominate\n"
        "   the distance calculations, rendering Recency and Frequency virtually irrelevant.\n"
        "   Logarithmic transformation log(x + 1) is first applied to mitigate extreme positive skewness,\n"
        "   followed by StandardScaler (z = (x - mean) / std), ensuring every dimension contributes\n"
        "   equitably with zero mean and unit variance."
    )

def prepare_and_scale_features(rfm_df: pd.DataFrame) -> Tuple[np.ndarray, StandardScaler]:
    """
    Prepares RFM features for clustering using log-transformation and StandardScaler.

    Parameters:
        rfm_df (pd.DataFrame): DataFrame containing 'recency', 'frequency', 'monetary'.

    Returns:
        scaled_features (np.ndarray): Transformed and standardized feature matrix.
        scaler (StandardScaler): Fitted scaler instance.
    """
    # Extract only the 3 core features
    rfm_matrix = rfm_df[["recency", "frequency", "monetary"]].copy()

    # Apply log transformation log(x + 1) to eliminate heavy right tails
    rfm_log = np.log1p(rfm_matrix)

    # Standardize to zero mean and unit variance
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(rfm_log)

    return scaled_features, scaler

def evaluate_optimal_k(
    scaled_features: np.ndarray,
    k_range: range = range(2, 9),
    random_state: int = 42
) -> Dict[str, Any]:
    """
    Evaluates cluster numbers using the Elbow Method (Inertia) and Silhouette Scores.

    Definitions:
    - Elbow Method: Tracks the within-cluster Sum of Squared Errors (Inertia) as K increases.
      The optimal point represents an 'elbow' where marginal reduction in error diminishes.
    - Silhouette Score: Quantifies cluster cohesion and separation, varying between -1 and +1.
      Scores close to +1 indicate dense, well-separated clusters; scores near 0 indicate overlapping boundaries.

    Returns:
        eval_dict containing 'k_values', 'inertias', 'silhouette_scores', and 'recommended_k'.
    """
    inertias: List[float] = []
    sil_scores: List[float] = []
    k_values = list(k_range)

    for k in k_values:
        kmeans = KMeans(n_clusters=k, init="k-means++", n_init=10, random_state=random_state)
        cluster_labels = kmeans.fit_predict(scaled_features)
        inertias.append(float(kmeans.inertia_))
        score = float(silhouette_score(scaled_features, cluster_labels))
        sil_scores.append(round(score, 4))

    # Pick K with highest silhouette score as recommendation
    best_k = k_values[int(np.argmax(sil_scores))]

    return {
        "k_values": k_values,
        "inertias": inertias,
        "silhouette_scores": sil_scores,
        "recommended_k": best_k
    }

def apply_kmeans_clustering(
    rfm_df: pd.DataFrame,
    scaled_features: np.ndarray,
    n_clusters: int = 4,
    random_state: int = 42
) -> Tuple[pd.DataFrame, KMeans]:
    """
    Fits K-Means model and assigns cluster labels (e.g., 'Cluster 0', 'Cluster 1') to each customer.
    """
    kmeans = KMeans(
        n_clusters=n_clusters,
        init="k-means++",
        n_init=10,
        random_state=random_state
    )
    labels = kmeans.fit_predict(scaled_features)

    df_clustered = rfm_df.copy()
    df_clustered["kmeans_cluster_id"] = labels
    df_clustered["kmeans_cluster"] = [f"Cluster {lbl}" for lbl in labels]

    return df_clustered, kmeans

def generate_cluster_profiles(clustered_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates statistical characteristics for each K-Means cluster:
    - Customer Count
    - % Customers
    - Avg Recency
    - Avg Frequency
    - Avg Monetary
    - Total Monetary
    - Cluster Interpretation / Characterization
    """
    total_customers = len(clustered_df)
    cluster_order = sorted(clustered_df["kmeans_cluster"].unique())

    records = []
    for cl in cluster_order:
        sub = clustered_df[clustered_df["kmeans_cluster"] == cl]
        cnt = len(sub)
        pct = (cnt / total_customers) * 100.0
        avg_r = sub["recency"].mean()
        avg_f = sub["frequency"].mean()
        avg_m = sub["monetary"].mean()
        tot_m = sub["monetary"].sum()

        # Data-driven characterization based on relative averages
        # (Compare to overall dataset medians)
        med_r = clustered_df["recency"].median()
        med_f = clustered_df["frequency"].median()
        med_m = clustered_df["monetary"].median()

        traits = []
        if avg_r < med_r:
            traits.append("High Recency (Active)")
        else:
            traits.append("Low Recency (Dormant)")

        if avg_f >= med_f:
            traits.append("High Frequency")
        else:
            traits.append("Low Frequency")

        if avg_m >= med_m:
            traits.append("High Monetary")
        else:
            traits.append("Low Monetary")

        interpretation = ", ".join(traits)

        records.append({
            "Cluster": cl,
            "Customer Count": int(cnt),
            "% Customers": round(pct, 2),
            "Avg Recency": round(avg_r, 1),
            "Avg Frequency": round(avg_f, 1),
            "Avg Monetary": round(avg_m, 2),
            "Total Spending": round(tot_m, 2),
            "Cluster Characterization": interpretation
        })

    return pd.DataFrame(records)

def compare_rfm_vs_kmeans(df_combined: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Compares Rule-Based RFM Segments with K-Means Clusters.

    Returns:
        cross_tab (pd.DataFrame): Contingency table showing customer overlap.
        comparison_summary (pd.DataFrame): Metric-by-metric comparison.
    """
    cross_tab = pd.crosstab(
        df_combined["segment_label"],
        df_combined["kmeans_cluster"],
        margins=True,
        margins_name="Total"
    )

    # Aggregated metrics for side-by-side comparison
    rfm_summary = df_combined.groupby("segment_label").agg(
        Count=("customer_id", "count"),
        Avg_Recency=("recency", "mean"),
        Avg_Frequency=("frequency", "mean"),
        Avg_Monetary=("monetary", "mean"),
        Total_Monetary=("monetary", "sum")
    ).round(2).reset_index().rename(columns={"segment_label": "Group"})
    rfm_summary["Type"] = "Rule-Based RFM"

    kmeans_summary = df_combined.groupby("kmeans_cluster").agg(
        Count=("customer_id", "count"),
        Avg_Recency=("recency", "mean"),
        Avg_Frequency=("frequency", "mean"),
        Avg_Monetary=("monetary", "mean"),
        Total_Monetary=("monetary", "sum")
    ).round(2).reset_index().rename(columns={"kmeans_cluster": "Group"})
    kmeans_summary["Type"] = "K-Means Cluster"

    comparison_summary = pd.concat([rfm_summary, kmeans_summary], ignore_index=True)

    return cross_tab, comparison_summary

def get_comparison_limitations() -> str:
    """
    Returns an academic critique detailing the differences and limitations of both approaches.
    """
    return (
        "COMPARISON & METHODOLOGICAL LIMITATIONS (RFM vs. K-MEANS):\n\n"
        "1. K-Means Clusters are NOT Objectively Correct:\n"
        "   Clustering algorithms will partition any multi-dimensional space even if true clusters\n"
        "   do not exist. A cluster assignment is a data-driven heuristic dependent on the distance metric,\n"
        "   scaling technique, and user-specified K. Cluster boundaries must be critically interpreted.\n\n"
        "2. Interpretability vs. Mathematical Geometry:\n"
        "   - Rule-Based RFM is highly intuitive, transparent, and directly actionable for marketing teams.\n"
        "     Business stakeholders understand exactly why a customer is labeled 'Champion' or 'At Risk'.\n"
        "   - K-Means discovers spherical geometric groupings in scaled feature space without imposing human bias,\n"
        "     revealing natural sub-patterns that rigid quintiles might obscure.\n\n"
        "3. Core Limitations of Rule-Based RFM:\n"
        "   - Thresholds are hardcoded and subjective.\n"
        "   - Highly sensitive to boundary edges (e.g. 79th vs 81st percentile).\n"
        "   - Ignores correlation structures between Frequency and Monetary value.\n\n"
        "4. Core Limitations of K-Means:\n"
        "   - Assumes spherical, equally-sized clusters with uniform variance.\n"
        "   - Requires manual selection of K; different K values yield entirely different customer groupings.\n"
        "   - Sensitive to initialization and outliers, even after scaling.\n"
        "   - Cluster labels ('Cluster 0', 'Cluster 1') lack intrinsic business meaning until manually interpreted."
    )

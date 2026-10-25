# Customer Segmentation and Predictive Analytics System

[![Live Demo](https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-6366f1?style=for-the-badge&logo=github)](https://dubbajahnavi30.github.io/customer-segmentation-analytics/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-orange?style=for-the-badge&logo=scikit-learn)](https://scikit-learn.org/)
[![MySQL Ready](https://img.shields.io/badge/Database-MySQL-00758F?style=for-the-badge&logo=mysql)](https://www.mysql.com/)

> **🌐 Live Interactive Web Dashboard:** [https://dubbajahnavi30.github.io/customer-segmentation-analytics/](https://dubbajahnavi30.github.io/customer-segmentation-analytics/)

An academically rigorous, reproducible Python data analytics project implementing **Rule-Based RFM Segmentation**, **K-Means Clustering Comparative Analytics**, and **MySQL Database Integration**.

---

## 1. Project Title
**Customer Segmentation and Predictive Analytics System**

---

## 2. Project Objective
The primary objective of this project is to group customers into meaningful behavioral segments using their transaction histories and describe their core characteristics. Specifically, the system:
1. Calculates **Purchase Recency**, **Purchase Frequency**, and **Spending / Monetary Value** (RFM) for every individual customer from raw transaction records.
2. Implements transparent, interpretable **Rule-Based RFM Segmentation** to categorize customers into operational business archetypes (e.g., Champions, Loyal Customers, Big Spenders, New Customers, At Risk, Lost Customers).
3. Applies unsupervised **K-Means Clustering** as a comparative data-driven model on appropriately scaled RFM features.
4. Generates comprehensive segment profiles, statistical spending comparisons, and publication-quality diagnostic visualizations.
5. Integrates with a relational **MySQL Database** to persist transactional entities, segmentation execution runs, and customer assignments.

---

## 3. Problem Statement
Modern businesses generate massive transaction logs containing orders, items, and timestamps. However, treating all customers uniformly results in inefficient marketing budgets, high customer churn, and missed revenue opportunities. 

Traditional heuristic segmentation often relies on arbitrary manual rules, while unsupervised machine learning models can produce mathematically sound clusters that are difficult to interpret operationally. This project addresses the challenge by building a dual-method customer analytics pipeline: pairing transparent **Rule-Based RFM Analysis** with mathematical **K-Means Clustering** to evaluate the strengths, alignments, and trade-offs of both approaches.

---

## 4. Key Features
- **Anonymized Transaction Ingestion & Cleaning:** Validates records, handles missing data, filters out non-fulfilled/cancelled orders, and aggregates multi-item transactions.
- **Reproducible RFM Computation:** Establishes a reference snapshot date to compute exact Recency (days), Frequency (unique orders), and Monetary value (total spend), followed by quantile scoring (1–5).
- **Interpretable Rule-Based Segmentation:** Applies unambiguous rule hierarchies to assign business labels to 100% of the customer base.
- **Segment Profiling Suite:** Calculates customer count, percentage distribution, mean recency, mean frequency, mean monetary spend, and aggregate revenue per segment.
- **Data-Driven K-Means Clustering:** Features log-transformation and `StandardScaler` normalization, cluster evaluation via the Elbow Method (Inertia) and Silhouette Scores, and automated selection of optimal cluster count $K$.
- **Comparative Analysis Engine:** Generates cross-tabulation matrices and side-by-side metric tables comparing Rule-Based Segments vs. K-Means Clusters.
- **Academic Visualization Suite:** Produces 9 high-resolution Matplotlib charts covering distributions, spend patterns, clustering diagnostics, and correlation heatmaps.
- **MySQL Relational Storage:** Implements 5 structured entities with foreign key constraints to store customers, orders, order items, segmentation runs, and customer segment assignments.

---

## 5. Technologies Used
- **Language:** Python (3.10+)
- **Data Manipulation:** `pandas`
- **Numerical Computation:** `numpy`
- **Data Visualization:** `matplotlib`
- **Unsupervised Machine Learning & Preprocessing:** `scikit-learn` (`StandardScaler`, `KMeans`, `silhouette_score`)
- **Database Engine:** MySQL
- **Database Connector:** `mysql-connector-python`

> *Note: In accordance with project specifications, no extraneous web frameworks (Flask, Django, FastAPI, Streamlit), deep learning, or unnecessary third-party packages are used.*

---

## 6. Project Structure

```
customer_segmentation_project/
│
├── data/
│   └── customer_purchase_data.csv        # Realistic, anonymized transaction records
│
├── database/
│   └── schema.sql                        # MySQL DDL schema for the 5 required tables
│
├── src/
│   ├── __init__.py                       # Package initializer
│   ├── database.py                       # MySQL connection, table loading, and run logging
│   ├── data_preparation.py               # Data loading, validation, and cleaning
│   ├── rfm_analysis.py                   # R, F, M calculation and quantile scoring
│   ├── segmentation.py                   # Rule-based segmentation and segment profiling
│   ├── clustering.py                     # K-Means clustering, scaling, and comparative analysis
│   ├── visualization.py                  # Matplotlib chart generation routines
│   └── generate_dataset.py               # Deterministic sample dataset generator
│
├── output/
│   ├── rfm_table.csv                     # Per-customer RFM metrics and scores
│   ├── segment_profiles.csv              # Rule-based segment characteristics
│   ├── kmeans_cluster_profiles.csv       # K-Means cluster statistics
│   ├── rfm_vs_kmeans_comparison.csv      # Cross-tabulation comparison matrix
│   └── charts/                           # High-resolution (300 DPI) visualization figures
│       ├── 01_customer_count_by_segment.png
│       ├── 02_segment_distribution.png
│       ├── 03_total_spending_by_segment.png
│       ├── 04_avg_monetary_by_segment.png
│       ├── 05_avg_frequency_by_segment.png
│       ├── 06_avg_recency_by_segment.png
│       ├── 07_kmeans_elbow_and_silhouette.png
│       ├── 08_kmeans_clusters_scatter.png
│       └── 09_rfm_vs_kmeans_heatmap.png
│
├── main.py                               # Master end-to-end execution pipeline
├── requirements.txt                      # Minimum explicit required dependencies
└── README.md                             # Comprehensive project documentation
```

---

## 7. Database Setup (MySQL)

The project includes `database/schema.sql`, defining exactly the 5 required entities:
1. `customers`: `customer_id` (PK), `customer_code` (Unique), `signup_date`.
2. `orders`: `order_id` (PK), `customer_id` (FK), `order_date`, `order_status`.
3. `order_items`: `item_id` (PK Auto-Increment), `order_id` (FK), `product_identifier`, `quantity`, `unit_price`.
4. `segment_runs`: `run_id` (PK Auto-Increment), `method`, `run_date`, `parameters`.
5. `customer_segments`: `run_id` (FK), `customer_id` (FK), `segment_label`, composite PK (`run_id`, `customer_id`).

### Setting up MySQL:
1. Ensure your MySQL Server is running (e.g., via MySQL Workbench, XAMPP, or Windows Service).
2. Create the database and execute the schema:
   ```bash
   mysql -u root -p < database/schema.sql
   ```
3. Database connection parameters can be configured via environment variables:
   - `MYSQL_HOST` (default: `localhost`)
   - `MYSQL_PORT` (default: `3306`)
   - `MYSQL_USER` (default: `root`)
   - `MYSQL_PASSWORD` (default: `""`)
   - `MYSQL_DATABASE` (default: `customer_segmentation_db`)

*(Note: If MySQL is not currently running, the system will output a clear notice and execute the full analysis pipeline using Pandas and CSV files without crashing).*

---

## 8. Python Environment Setup

1. Open your terminal or VS Code in the project root directory.
2. (Recommended) Create and activate a Python virtual environment:
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

---

## 9. Required Packages
Install the required packages using `pip`:
```bash
python -m pip install -r requirements.txt
```

---

## 10. How to Run the Project

Run the end-to-end execution pipeline with a single command:
```bash
python main.py
```

The script will sequentially execute:
1. Raw dataset validation and data cleaning.
2. MySQL connection check and schema population (if reachable).
3. RFM feature calculation and quintile scoring.
4. Rule-based customer segmentation and profile table generation.
5. Log-transformation, scaling, Elbow/Silhouette analysis, and K-Means clustering.
6. Rule-Based vs. K-Means cross-tabulation and comparative evaluation.
7. Export of all 4 CSV summaries to `output/` and all 9 charts to `output/charts/`.

---

## 11. RFM Methodology

### Core Metric Definitions
- **Recency ($R$):**
  $$\text{Recency}_i = \text{Date}_{\text{snapshot}} - \max(\text{Date}_{\text{order}, i})$$
  The number of days between the customer's most recent purchase and the reference snapshot date ($\max(\text{order\_date}) + 1\text{ day}$). Lower recency indicates active engagement.
- **Frequency ($F$):**
  $$\text{Frequency}_i = \text{Count}(\text{Unique Order IDs}_i)$$
  Total count of unique fulfilled transactions placed by the customer. Higher frequency indicates habitual buying behavior.
- **Monetary ($M$):**
  $$\text{Monetary}_i = \sum_{j} (\text{Quantity}_{i, j} \times \text{UnitPrice}_{i, j})$$
  Cumulative monetary spend across all valid orders. Higher monetary value indicates greater revenue contribution.

### Scoring Logic (Quintiles 1 to 5)
Customers are binned into percentiles (0–20%, 20–40%, 40–60%, 60–80%, 80–100%):
- **$R$-Score:** Inverted rank. Score 5 = Lowest recency (top 20% most recent); Score 1 = Highest recency (>80% oldest).
- **$F$-Score:** Direct rank. Score 5 = Highest purchase counts; Score 1 = Lowest purchase counts (single orders).
- **$M$-Score:** Direct rank. Score 5 = Highest total spend; Score 1 = Lowest total spend.

---

## 12. Rule-Based Segmentation Methodology

Customers are categorized according to their composite RFM scores using the following hierarchical rules:

| Segment | Rule Definition | Customer Profile & Strategy |
| :--- | :--- | :--- |
| **Champions** | $R \ge 4$, $F \ge 4$, $M \ge 4$ | Highest value: purchased recently, buy often, and spend heavily. Reward with exclusive perks. |
| **Loyal Customers** | $R \ge 3$, $F \ge 3$, $M \ge 3$ *(excl. Champions)* | Consistent repeat buyers with steady spend and recent activity. Target with cross-selling. |
| **Big Spenders** | $M \ge 4$, $F < 3$ | High spend per transaction but low purchase count. Target with high-ticket luxury items. |
| **New Customers** | $R \ge 4$, $F \le 2$ | Freshly acquired customers who bought recently (1–2 orders). Onboard with welcome sequences. |
| **At Risk** | $R \le 2$, ($F \ge 3$ or $M \ge 3$) | Formerly high-value/frequent buyers who have become dormant. Deploy win-back promotions. |
| **Lost Customers** | $R \le 2$, $F \le 2$, $M \le 2$ | Lowest recency, frequency, and spend; churned buyers. Deprioritize expensive marketing. |
| **Potential Loyalists** | All remaining combinations | Intermediate buyers with solid potential. Nurture into Loyal Customers. |

---

## 13. K-Means Methodology

### Rationale & Feature Scaling
K-Means minimizes the Euclidean distance between data points and cluster centroids:
$$d(x, y) = \sqrt{\sum_{j=1}^{d} (x_j - y_j)^2}$$
- **Why Scaling is Critical:** In raw RFM data, Monetary values span hundreds to thousands of dollars, while Frequency spans single-digit integers. Without normalization, Monetary value would dominate the objective function, rendering Recency and Frequency negligible.
- **Transformation Pipeline:**
  1. **Log-Transformation:** $\tilde{x} = \log(x + 1)$ stabilizes variance and reduces severe right-skewness.
  2. **StandardScaler:** $z = (x - \mu) / \sigma$ standardizes all dimensions to zero mean and unit variance.

### Cluster Evaluation & Selection ($K$)
- **Elbow Method:** Evaluates within-cluster Sum of Squared Errors (Inertia) across $K \in [2, 8]$. The "elbow" marks where adding another cluster yields diminishing returns.
- **Silhouette Coefficient:** Measures cohesion within clusters versus separation from neighboring clusters ($s \in [-1, 1]$). The cluster count with the highest average silhouette score ($K = 4$, score $\approx 0.485$) is selected.

---

## 14. Expected Outputs

| Output File | Description |
| :--- | :--- |
| `output/rfm_table.csv` | Full table containing per-customer Recency, Frequency, Monetary values, quintile scores, rule-based segment labels, and K-Means cluster assignments. |
| `output/segment_profiles.csv` | Summary profile table containing Customer Count, % Share, Mean $R$, Mean $F$, Mean $M$, Total Spending, and General Characteristics for each rule-based segment. |
| `output/kmeans_cluster_profiles.csv` | Profile table of K-Means clusters with customer counts, average RFM metrics, and data-driven behavioral characterizations. |
| `output/rfm_vs_kmeans_comparison.csv` | Contingency cross-tabulation matrix mapping Rule-Based RFM segments directly against K-Means clusters. |
| `output/charts/01_customer_count_by_segment.png` | Bar chart of customer counts per rule-based segment with exact value labels. |
| `output/charts/02_segment_distribution.png` | Pie chart displaying percentage customer share per segment. |
| `output/charts/03_total_spending_by_segment.png` | Bar chart showing total gross revenue contribution by customer segment. |
| `output/charts/04_avg_monetary_by_segment.png` | Bar chart illustrating mean spend per customer across segments. |
| `output/charts/05_avg_frequency_by_segment.png` | Bar chart illustrating average order frequency across segments. |
| `output/charts/06_avg_recency_by_segment.png` | Bar chart illustrating average days elapsed since last purchase per segment. |
| `output/charts/07_kmeans_elbow_and_silhouette.png` | Dual-panel diagnostic figure displaying Elbow Inertia curve and Silhouette Score curve. |
| `output/charts/08_kmeans_clusters_scatter.png` | Multi-panel scatter plot illustrating K-Means cluster boundaries across RFM dimensions. |
| `output/charts/09_rfm_vs_kmeans_heatmap.png` | Heatmap cross-tabulation matrix showing customer distribution between Rule-Based and K-Means groupings. |

---

## 15. Methodological Limitations

### Limitations of Rule-Based RFM Segmentation:
1. **Heuristic & Subjective Thresholds:** Quintile cutoffs (e.g., top 20% vs. 40%) are arbitrary rules of thumb. They do not automatically adapt to real clusters in customer behavior.
2. **Boundary Sensitivity:** A customer near a cutoff (e.g., $R$-percentile of 0.39 vs. 0.41) may be assigned to different segments despite having almost identical transactional habits.
3. **Non-Universal Business Truth:** Segment labels provide operational heuristics; they do not represent absolute behavioral laws.

### Limitations of K-Means Clustering:
1. **Clusters are Not "Objective Truth":** K-Means will partition any data into $K$ groups regardless of whether true natural clusters exist.
2. **Spherical Cluster Assumption:** K-Means assumes spherical clusters with uniform variance, which may distort non-spherical customer groupings.
3. **Sensitivity to Hyperparameters & Outliers:** Results depend on the choice of $K$ and initialization seeds.
4. **Lack of Inherent Interpretability:** Cluster labels (`Cluster 0`, `Cluster 1`) require manual post-hoc interpretation, whereas rule-based labels are immediately actionable.

---

## 16. Interactive Web Application & Executive Dashboard

The repository includes a modern, glassmorphic interactive web dashboard (`index.html`) providing real-time exploration, visualization, and simulation:

### Core Features:
- **Executive KPI Bar:** Real-time metrics for net revenue ($291,490.82), customer count (147), average spend ($1,982.93), and risk exposure.
- **Rule-Based RFM Studio:** Dynamic Chart.js donut and spend breakdown charts, segment cards, and marketing action playbooks.
- **K-Means ML Studio:** Interactive dual-axis Elbow & Silhouette curve ($K=4$), 2D/3D scatter plot, and cluster centroid metrics.
- **Comparative Contingency Heatmap:** Interactive matrix mapping Rule-Based labels against K-Means clusters with click-to-filter.
- **What-If RFM Simulator:** Real-time sliders for Recency, Frequency, and Monetary spend that dynamically calculate quintile scores, predict segments, and display tailored business playbooks.
- **Live Customer Directory:** 147 customer accounts with search, multi-filter, column sorting, pagination, CSV export, and detailed profile modal views.
- **Academic Visualization Gallery:** Lightbox inspection and downloads for all 9 high-resolution (300 DPI) Matplotlib figures.
- **Relational Architecture Viewer:** Interactive MySQL schema cards and one-click SQL copying.

### How to Launch:
- **Option 1 (One-Click Batch):** Double-click `start_dashboard.bat` (Windows).
- **Option 2 (Python Launcher):** Run `python start_dashboard.py`.
- **Option 3 (Direct File):** Double-click `index.html` in your file explorer to open directly in any browser (100% self-contained data, zero server dependency).


# Functionality 17: Product Recommendation System

## Overview
This module implements a complete, modular product recommendation system for the Real-Time E-Commerce Data Engineering & AI Analytics Platform. It combines implicit-feedback collaborative filtering, text/metadata content-based filtering, hybrid weighted scoring, and explicit popularity-based cold-start fallbacks.

---

## System Architecture

```
recommendation_system/
│
├── config.py                 # File paths, weights, and directory configurations
├── data_loader.py            # Loads users, products, orders, events, reviews (excluding PII)
├── interaction_builder.py    # Builds weighted implicit user-product interaction dataset
├── content_features.py       # TF-IDF text features & normalized numerical product vectors
├── collaborative.py          # Sparse user-item matrix & item-item cosine similarity
├── content_based.py          # Item & user content-based similarity recommenders
├── hybrid.py                 # Min-Max normalized weighted hybrid recommendation engine
├── candidate_generation.py   # Candidate retrieval helpers
├── ranking.py                # Validation, deduplication, stock filtering & popularity fallback
├── evaluation.py             # Temporal holdout split & evaluation (Precision, Recall, MAP, NDCG)
├── recommend.py              # High-level public recommendation API
├── visualization.py          # Matplotlib performance & distribution chart generation
├── reporting.py              # Summary reports & sample user recommendation outputs
└── main.py                   # Full end-to-end CLI execution pipeline
```

---

## Key Features

1. **Implicit Interaction Aggregation**:
   - `product_view` (Weight = 1.0)
   - `search` (Weight = 1.0)
   - `add_to_cart` (Weight = 3.0)
   - `purchase` (Weight = 5.0)
   - `review` (Weight = 4.0)

2. **Item-Item Collaborative Filtering**:
   - Uses `scipy.sparse.csr_matrix` for high memory efficiency.
   - Computes item-item cosine similarity via normalized sparse matrix dot products.

3. **Content-Based Filtering**:
   - Computes TF-IDF vectors on combined product name and category metadata using `scikit-learn`.
   - Incorporates scaled numerical features (price, rating, discount percent).

4. **Hybrid Scoring Engine**:
   - Min-Max normalizes collaborative scores [0, 1] and content-based scores [0, 1].
   - Combines scores with configurable weights (Default: Collaborative = 0.6, Content = 0.4).

5. **Cold-Start Strategy**:
   - **New / Unknown Users**: Evaluates composite popularity score derived from purchase frequency, interaction intensity, and product ratings.
   - **New Products**: Recommended via content-based similarity using product metadata.

6. **Evaluation & Metrics**:
   - Temporal holdout split (holds out latest interaction per user).
   - Evaluates at K = [5, 10, 20]:
     - Precision@K
     - Recall@K
     - Hit Rate@K
     - MAP@K
     - NDCG@K
     - Catalog Coverage

---

## Model Artifacts & Outputs

All generated artifacts are saved to `data/recommendations/`:

```
data/recommendations/
├── interactions/
│   ├── user_product_interactions.parquet
│   └── user_product_interactions.csv
├── models/
│   ├── interaction_matrix.npz
│   ├── item_similarity.npz
│   ├── product_tfidf.joblib
│   ├── product_similarity.npz
│   └── model_metadata.json
├── recommendations/
│   ├── hybrid_recommendations.csv
│   ├── collaborative_recommendations.csv
│   ├── content_recommendations.csv
│   └── popular_recommendations.csv
├── evaluation/
│   ├── evaluation_metrics.csv
│   ├── evaluation_metrics.json
│   └── recommendation_examples.csv
├── visualizations/
│   ├── interaction_distribution.png
│   ├── popular_products.png
│   ├── recommendation_coverage.png
│   └── model_comparison.png
└── reports/
    ├── recommendation_summary.json
    └── recommendation_summary.txt
```

---

## Installation & Requirements

Ensure Python dependencies are installed:
```powershell
pip install numpy pandas scipy scikit-learn matplotlib seaborn joblib pytest
```

---

## Execution & Usage

### 1. Run Tests
Run unit tests with synthetic fixtures:
```powershell
python -m pytest recommendation_system/tests -v
```

### 2. Run Full Recommendation Pipeline
Execute end-to-end data processing, model training, evaluation, visualization, and report generation:
```powershell
python -m recommendation_system.main
```

### 3. Generate Recommendations for a Specific User
```powershell
python -m recommendation_system.main --user-id USER001 --top-n 10 --method hybrid
```

Supported methods: `hybrid`, `collaborative`, `content`, `popular`.

---

## Python API Usage Example

```python
from recommendation_system.recommend import recommend

# Generate Top-10 Hybrid Recommendations for USER001
recs_df = recommend(
    user_id="USER001",
    n=10,
    method="hybrid",
    exclude_purchased=True
)

print(recs_df)
```

---

## Limitations
- Collaborative filtering relies on user-item interaction co-occurrence. Extremely sparse interaction matrices default to content-based or popularity fallbacks.
- Temporal evaluation requires users to have at least 2 distinct interactions.

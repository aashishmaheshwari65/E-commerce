import os
import json
import numpy as np
import pandas as pd
from recommendation_system import config
from recommendation_system.collaborative import build_interaction_matrix, build_item_similarity, recommend_collaborative
from recommendation_system.content_features import build_content_similarity
from recommendation_system.content_based import recommend_content_based
from recommendation_system.hybrid import recommend_hybrid
from recommendation_system.ranking import recommend_popular

def precision_at_k(actual, recommended, k):
    """Calculate Precision@K."""
    if not recommended or k <= 0:
        return 0.0
    rec_k = recommended[:k]
    hits = sum(1 for p in rec_k if p in actual)
    return hits / k

def recall_at_k(actual, recommended, k):
    """Calculate Recall@K."""
    if not actual or k <= 0:
        return 0.0
    rec_k = recommended[:k]
    hits = sum(1 for p in rec_k if p in actual)
    return hits / len(actual)

def hit_rate_at_k(actual, recommended, k):
    """Calculate Hit Rate@K."""
    if not recommended or k <= 0:
        return 0.0
    rec_k = recommended[:k]
    return 1.0 if any(p in actual for p in rec_k) else 0.0

def map_at_k(actual, recommended, k):
    """Calculate Mean Average Precision@K."""
    if not actual or not recommended or k <= 0:
        return 0.0
    rec_k = recommended[:k]
    score = 0.0
    num_hits = 0.0
    for i, p in enumerate(rec_k):
        if p in actual:
            num_hits += 1.0
            score += num_hits / (i + 1.0)
    return score / min(len(actual), k)

def ndcg_at_k(actual, recommended, k):
    """Calculate Normalized Discounted Cumulative Gain@K."""
    if not actual or not recommended or k <= 0:
        return 0.0
    rec_k = recommended[:k]
    dcg = 0.0
    for i, p in enumerate(rec_k):
        if p in actual:
            dcg += 1.0 / np.log2(i + 2) # i+2 because 1-indexed rank in formula
    idcg = sum(1.0 / np.log2(i + 2) for i in range(min(len(actual), k)))
    return dcg / idcg if idcg > 0 else 0.0

def evaluate_models(interactions_df, products_df, k_values=[5, 10, 20]):
    """
    Perform temporal holdout evaluation across Popularity, Collaborative, Content, and Hybrid models.
    """
    if interactions_df.empty or len(interactions_df["user_id"].unique()) < 2:
        print("Warning: Interaction dataset is too small for meaningful holdout evaluation.")
        empty_res = {"status": "insufficient_data", "metrics": []}
        return pd.DataFrame(), empty_res

    df = interactions_df.copy()
    df["user_id"] = df["user_id"].astype(str)
    df["product_id"] = df["product_id"].astype(str)

    # Filter users with at least 2 interactions
    user_counts = df["user_id"].value_counts()
    eligible_users = user_counts[user_counts >= 2].index.tolist()

    if not eligible_users:
        print("Warning: No users with >= 2 interactions for holdout evaluation.")
        return pd.DataFrame(), {"status": "no_eligible_users", "metrics": []}

    train_records = []
    test_dict = {} # user_id -> set of held-out product_ids

    # Train / Test temporal/index holdout split
    for u in eligible_users:
        u_df = df[df["user_id"] == u]
        # Keep last interaction for test, earlier for train
        train_part = u_df.iloc[:-1]
        test_part = u_df.iloc[-1:]

        train_records.append(train_part)
        test_dict[u] = set(test_part["product_id"].tolist())

    # Include single-interaction users in training data
    single_users = user_counts[user_counts == 1].index.tolist()
    if single_users:
        train_records.append(df[df["user_id"].isin(single_users)])

    train_df = pd.concat(train_records, ignore_index=True)

    # Train models on train_df
    user_item_mat, u2i, i2u, p2i, i2p = build_interaction_matrix(train_df)
    item_sim = build_item_similarity(user_item_mat)
    cnt_sim, c_p2i, c_i2p, _ = build_content_similarity(products_df)

    methods = ["popular", "collaborative", "content", "hybrid"]
    metrics_results = []

    catalog_products = set(products_df["product_id"].astype(str).tolist()) if not products_df.empty else set(df["product_id"].unique())
    num_catalog = len(catalog_products) or 1

    for method in methods:
        for k in k_values:
            prec_list, rec_list, hit_list, map_list, ndcg_list = [], [], [], [], []
            recommended_products_all = set()

            for u in test_dict:
                actual = test_dict[u]
                recs = []

                if method == "popular":
                    pop_recs = recommend_popular(products_df, train_df, n=k)
                    recs = [r["product_id"] for r in pop_recs]
                elif method == "collaborative":
                    collab_recs = recommend_collaborative(
                        user_id=u, user_item_matrix=user_item_mat, item_similarity=item_sim,
                        user_to_idx=u2i, idx_to_user=i2u, product_to_idx=p2i, idx_to_product=i2p,
                        n=k, exclude_purchased=True
                    )
                    recs = [r["product_id"] for r in collab_recs]
                elif method == "content":
                    cnt_recs = recommend_content_based(
                        user_id=u, interactions_df=train_df, similarity_matrix=cnt_sim,
                        product_to_idx=c_p2i, idx_to_product=c_i2p, n=k, exclude_purchased=True
                    )
                    recs = [r["product_id"] for r in cnt_recs]
                elif method == "hybrid":
                    hyb_recs = recommend_hybrid(
                        user_id=u, user_item_matrix=user_item_mat, item_similarity=item_sim,
                        content_similarity=cnt_sim, user_to_idx=u2i, idx_to_user=i2u,
                        product_to_idx=p2i, idx_to_product=i2p, interactions_df=train_df,
                        n=k, exclude_purchased=True, content_p2i=c_p2i, content_i2p=c_i2p
                    )
                    recs = [r["product_id"] for r in hyb_recs]

                # Fallback to popular if model gave empty recommendations
                if not recs:
                    pop_recs = recommend_popular(products_df, train_df, n=k)
                    recs = [r["product_id"] for r in pop_recs]

                recommended_products_all.update(recs[:k])

                prec_list.append(precision_at_k(actual, recs, k))
                rec_list.append(recall_at_k(actual, recs, k))
                hit_list.append(hit_rate_at_k(actual, recs, k))
                map_list.append(map_at_k(actual, recs, k))
                ndcg_list.append(ndcg_at_k(actual, recs, k))

            coverage = len(recommended_products_all) / num_catalog

            metrics_results.append({
                "method": method,
                "k": k,
                "precision": float(np.mean(prec_list)),
                "recall": float(np.mean(rec_list)),
                "hit_rate": float(np.mean(hit_list)),
                "map": float(np.mean(map_list)),
                "ndcg": float(np.mean(ndcg_list)),
                "catalog_coverage": float(coverage),
                "unique_recommended_count": len(recommended_products_all)
            })

    metrics_df = pd.DataFrame(metrics_results)
    return metrics_df, {"status": "success", "metrics": metrics_results}

def save_evaluation_results(metrics_df, metrics_json, output_dir=None):
    """Save evaluation metrics to CSV and JSON files."""
    if output_dir is None:
        output_dir = config.EVALUATION_DIR
    os.makedirs(output_dir, exist_ok=True)

    csv_path = os.path.join(output_dir, "evaluation_metrics.csv")
    json_path = os.path.join(output_dir, "evaluation_metrics.json")

    metrics_df.to_csv(csv_path, index=False)
    with open(json_path, "w") as f:
        json.dump(metrics_json, f, indent=2)

    return csv_path, json_path

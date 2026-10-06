import numpy as np
import pandas as pd
from recommendation_system import config
from recommendation_system.collaborative import recommend_collaborative
from recommendation_system.content_based import recommend_content_based

def normalize_scores(scores_dict):
    """
    Min-Max normalize dictionary of product_id -> score to [0, 1].
    If max == min, return 1.0 for positive scores or 0.0.
    """
    if not scores_dict:
        return {}
    vals = list(scores_dict.values())
    min_val, max_val = min(vals), max(vals)
    if max_val == min_val:
        return {k: (1.0 if max_val > 0 else 0.0) for k, v in scores_dict.items()}
    
    return {k: (v - min_val) / (max_val - min_val) for k, v in scores_dict.items()}

def recommend_hybrid(
    user_id,
    user_item_matrix,
    item_similarity,
    content_similarity,
    user_to_idx,
    idx_to_user,
    product_to_idx,
    idx_to_product,
    interactions_df,
    n=10,
    collaborative_weight=0.6,
    content_weight=0.4,
    exclude_purchased=True,
    content_p2i=None,
    content_i2p=None
):
    """
    Generate hybrid recommendations combining normalized collaborative and content-based scores.
    """
    u_str = str(user_id)
    c_p2i = content_p2i if content_p2i is not None else product_to_idx
    c_i2p = content_i2p if content_i2p is not None else idx_to_product

    # Fetch candidate recommendations from both models
    collab_recs = recommend_collaborative(
        user_id=u_str,
        user_item_matrix=user_item_matrix,
        item_similarity=item_similarity,
        user_to_idx=user_to_idx,
        idx_to_user=idx_to_user,
        product_to_idx=product_to_idx,
        idx_to_product=idx_to_product,
        n=max(n * 5, 50),
        exclude_purchased=exclude_purchased
    )

    content_recs = recommend_content_based(
        user_id=u_str,
        interactions_df=interactions_df,
        similarity_matrix=content_similarity,
        product_to_idx=c_p2i,
        idx_to_product=c_i2p,
        n=max(n * 5, 50),
        exclude_purchased=exclude_purchased
    )

    collab_dict = {r["product_id"]: r["score"] for r in collab_recs}
    content_dict = {r["product_id"]: r["score"] for r in content_recs}

    # Normalize scores
    norm_collab = normalize_scores(collab_dict)
    norm_content = normalize_scores(content_dict)

    all_products = set(norm_collab.keys()).union(set(norm_content.keys()))

    if not all_products:
        return []

    # Normalize weights so they sum to 1.0
    total_w = collaborative_weight + content_weight
    c_w = collaborative_weight / total_w if total_w > 0 else 0.5
    cnt_w = content_weight / total_w if total_w > 0 else 0.5

    hybrid_results = []
    for pid in all_products:
        c_score = norm_collab.get(pid, 0.0)
        cnt_score = norm_content.get(pid, 0.0)

        h_score = c_w * c_score + cnt_w * cnt_score

        hybrid_results.append({
            "user_id": u_str,
            "product_id": pid,
            "recommendation_score": float(h_score),
            "collaborative_score": float(c_score),
            "content_score": float(cnt_score),
            "recommendation_method": "hybrid"
        })

    # Sort descending by hybrid recommendation_score
    hybrid_results.sort(key=lambda x: (-x["recommendation_score"], x["product_id"]))

    return hybrid_results[:n]

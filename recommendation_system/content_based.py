import numpy as np
import pandas as pd
from recommendation_system import config

def recommend_content_based_for_product(product_id, similarity_matrix, product_to_idx, idx_to_product, n=10):
    """Generate content-based recommendations given a target product_id."""
    p_str = str(product_id)
    if p_str not in product_to_idx or similarity_matrix is None or similarity_matrix.size == 0:
        return []

    p_idx = product_to_idx[p_str]
    sim_scores = similarity_matrix[p_idx].toarray().ravel() if hasattr(similarity_matrix[p_idx], "toarray") else np.array(similarity_matrix[p_idx]).ravel()

    # Zero out target product self similarity
    sim_scores[p_idx] = -np.inf

    top_indices = np.argsort(-sim_scores)
    recs = []
    for idx in top_indices:
        score = sim_scores[idx]
        if score <= 0.0 or score == -np.inf:
            break
        recs.append({
            "product_id": idx_to_product[idx],
            "score": float(score),
            "method": "content"
        })
        if len(recs) >= n:
            break

    return recs

def recommend_content_based(user_id, interactions_df, similarity_matrix, product_to_idx, idx_to_product, n=10, exclude_purchased=True):
    """
    Generate content-based recommendations for a user based on products they interacted with.
    Calculates weighted sum of content similarity vectors for user's interacted products.
    """
    u_str = str(user_id)
    if interactions_df.empty or similarity_matrix is None or similarity_matrix.size == 0:
        return []

    user_df = interactions_df[interactions_df["user_id"].astype(str) == u_str]
    if user_df.empty:
        return []

    num_products = similarity_matrix.shape[0]
    user_content_scores = np.zeros(num_products, dtype=np.float32)
    interacted_indices = []

    for _, row in user_df.iterrows():
        pid = str(row["product_id"])
        weight = float(row["interaction_score"])
        if pid in product_to_idx:
            idx = product_to_idx[pid]
            if idx < num_products:
                interacted_indices.append(idx)
                row_sim = similarity_matrix[idx].toarray().ravel() if hasattr(similarity_matrix[idx], "toarray") else np.array(similarity_matrix[idx]).ravel()
                user_content_scores += weight * row_sim

    if exclude_purchased and interacted_indices:
        user_content_scores[interacted_indices] = -np.inf

    valid_mask = user_content_scores > 0.0
    if not np.any(valid_mask):
        return []

    top_indices = np.argsort(-user_content_scores)
    recs = []
    for idx in top_indices:
        score = user_content_scores[idx]
        if score <= 0.0 or score == -np.inf:
            break
        pid = idx_to_product.get(idx, idx_to_product.get(int(idx), None))
        if pid is None:
            continue
        recs.append({
            "product_id": str(pid),
            "score": float(score),
            "method": "content"
        })
        if len(recs) >= n:
            break

    return recs

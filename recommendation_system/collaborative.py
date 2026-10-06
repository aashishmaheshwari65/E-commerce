import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.preprocessing import normalize
import os
from recommendation_system import config

def build_interaction_matrix(interactions_df):
    """
    Build scipy sparse user-item interaction matrix and index mappings.
    Returns:
        user_item_matrix: csr_matrix (n_users, n_products)
        user_to_idx: dict mapping user_id to row index
        idx_to_user: dict mapping row index to user_id
        product_to_idx: dict mapping product_id to col index
        idx_to_product: dict mapping col index to product_id
    """
    if interactions_df.empty:
        empty_mat = sparse.csr_matrix((0, 0), dtype=np.float32)
        return empty_mat, {}, {}, {}, {}

    df = interactions_df.copy()
    df["user_id"] = df["user_id"].astype(str)
    df["product_id"] = df["product_id"].astype(str)

    unique_users = sorted(df["user_id"].unique())
    unique_products = sorted(df["product_id"].unique())

    user_to_idx = {u: i for i, u in enumerate(unique_users)}
    idx_to_user = {i: u for i, u in enumerate(unique_users)}
    product_to_idx = {p: i for i, p in enumerate(unique_products)}
    idx_to_product = {i: p for i, p in enumerate(unique_products)}

    row_indices = df["user_id"].map(user_to_idx).values
    col_indices = df["product_id"].map(product_to_idx).values
    data = df["interaction_score"].values.astype(np.float32)

    user_item_matrix = sparse.csr_matrix(
        (data, (row_indices, col_indices)),
        shape=(len(unique_users), len(unique_products)),
        dtype=np.float32
    )

    return user_item_matrix, user_to_idx, idx_to_user, product_to_idx, idx_to_product

def build_item_similarity(user_item_matrix):
    """
    Compute item-item cosine similarity using sparse normalized matrix dot products.
    Item vectors are columns of user_item_matrix (transpose: shape (n_products, n_users)).
    """
    if user_item_matrix.shape[0] == 0 or user_item_matrix.shape[1] == 0:
        return sparse.csr_matrix((0, 0), dtype=np.float32)

    # Transpose to get item-user matrix of shape (n_products, n_users)
    item_user_matrix = user_item_matrix.T.tocsr()

    # Normalize rows (items) to L2 unit norm for cosine similarity
    item_user_norm = normalize(item_user_matrix, norm='l2', axis=1)

    # Compute cosine similarity: S = norm * norm.T
    item_similarity = item_user_norm.dot(item_user_norm.T).tocsr()

    # Zero out self-similarity on diagonal
    item_similarity.setdiag(0.0)
    item_similarity.eliminate_zeros()

    return item_similarity

def recommend_collaborative(user_id, user_item_matrix, item_similarity, user_to_idx, idx_to_user, product_to_idx, idx_to_product, n=10, exclude_purchased=True):
    """
    Generate collaborative filtering recommendations for a given user.
    Returns list of dicts: [{'product_id': p, 'score': score}, ...]
    """
    user_str = str(user_id)
    if user_str not in user_to_idx:
        # Cold start user: no interactions in matrix
        return []

    u_idx = user_to_idx[user_str]
    user_vector = user_item_matrix[u_idx] # shape (1, n_products)

    if user_vector.nnz == 0:
        return []

    # Score candidates: scores = user_vector * item_similarity (1, n_products)
    scores = user_vector.dot(item_similarity).toarray().ravel()

    # Exclude already interacted products if requested
    if exclude_purchased:
        interacted_indices = user_vector.indices
        scores[interacted_indices] = -np.inf

    # Filter invalid/zero scores
    valid_mask = scores > 0.0
    if not np.any(valid_mask):
        return []

    # Get top candidate indices
    top_indices = np.argsort(-scores)
    
    recs = []
    for idx in top_indices:
        if scores[idx] <= 0.0 or scores[idx] == -np.inf:
            break
        recs.append({
            "product_id": idx_to_product[idx],
            "score": float(scores[idx]),
            "method": "collaborative"
        })
        if len(recs) >= n:
            break

    return recs

def save_collaborative_model(user_item_matrix, item_similarity, output_dir=None):
    """Save interaction matrix and item similarity sparse artifacts."""
    if output_dir is None:
        output_dir = config.MODELS_DIR
    os.makedirs(output_dir, exist_ok=True)

    if user_item_matrix is not None and user_item_matrix.shape[0] > 0:
        sparse.save_npz(os.path.join(output_dir, "interaction_matrix.npz"), user_item_matrix)
    if item_similarity is not None and item_similarity.shape[0] > 0:
        sparse.save_npz(os.path.join(output_dir, "item_similarity.npz"), item_similarity)

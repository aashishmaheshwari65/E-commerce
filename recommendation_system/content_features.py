import pandas as pd
import numpy as np
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import os
from recommendation_system import config

def build_product_features(products_df):
    """
    Build combined text and numerical product features using TF-IDF + normalized numerical metrics.
    """
    if products_df.empty:
        return None, None, None

    p_df = products_df.copy()
    p_df["product_id"] = p_df["product_id"].astype(str)

    # 1. Textual feature: product_name + category
    p_df["product_name"] = p_df["product_name"].fillna("").astype(str)
    p_df["category"] = p_df["category"].fillna("").astype(str)
    p_df["text_content"] = p_df["product_name"] + " " + p_df["category"]

    tfidf = TfidfVectorizer(stop_words="english")
    tfidf_matrix = tfidf.fit_transform(p_df["text_content"])

    # 2. Numerical features: price, rating, discount_percent
    num_cols = []
    for col in ["price", "rating", "discount_percent"]:
        if col in p_df.columns:
            num_cols.append(col)

    if num_cols:
        scaler = MinMaxScaler()
        num_matrix = scaler.fit_transform(p_df[num_cols].fillna(0.0).values)
        # Scale down numerical features (weight=0.2) so text dominates text-based content similarity
        num_sparse = sparse.csr_matrix(num_matrix * 0.2)
        combined_matrix = sparse.hstack([tfidf_matrix, num_sparse]).tocsr()
    else:
        combined_matrix = tfidf_matrix

    return tfidf, tfidf_matrix, combined_matrix

def build_content_similarity(products_df):
    """
    Compute pairwise cosine similarity between all products based on content features.
    Returns:
        similarity_matrix: np.ndarray / scipy sparse matrix
        product_to_idx: dict mapping product_id to matrix row index
        idx_to_product: dict mapping matrix row index to product_id
    """
    if products_df.empty:
        return np.array([]), {}, {}

    products_df = products_df.copy()
    products_df["product_id"] = products_df["product_id"].astype(str)
    
    product_ids = products_df["product_id"].tolist()
    product_to_idx = {pid: idx for idx, pid in enumerate(product_ids)}
    idx_to_product = {idx: pid for idx, pid in enumerate(product_ids)}

    tfidf, tfidf_matrix, combined_matrix = build_product_features(products_df)

    if combined_matrix is None:
        return np.array([]), {}, {}

    similarity_matrix = cosine_similarity(combined_matrix)

    return similarity_matrix, product_to_idx, idx_to_product, tfidf

def save_content_model(similarity_matrix, tfidf_vectorizer, output_dir=None):
    """Save content similarity matrix and TF-IDF artifact."""
    if output_dir is None:
        output_dir = config.MODELS_DIR
    os.makedirs(output_dir, exist_ok=True)

    if tfidf_vectorizer is not None:
        joblib.dump(tfidf_vectorizer, os.path.join(output_dir, "product_tfidf.joblib"))

    if isinstance(similarity_matrix, np.ndarray) and similarity_matrix.size > 0:
        sparse_sim = sparse.csr_matrix(similarity_matrix)
        sparse.save_npz(os.path.join(output_dir, "product_similarity.npz"), sparse_sim)

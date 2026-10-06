import numpy as np
import pandas as pd
from recommendation_system import config

def recommend_popular(products_df, interactions_df=None, n=10):
    """
    Calculate popularity score for products based on purchase count, interaction score, and rating.
    Provides robust cold-start fallback for new or unknown users.
    """
    if products_df.empty:
        return []

    p_df = products_df.copy()
    p_df["product_id"] = p_df["product_id"].astype(str)

    if interactions_df is not None and not interactions_df.empty:
        i_agg = interactions_df.groupby("product_id").agg(
            total_purchases=("purchase_count", "sum") if "purchase_count" in interactions_df.columns else ("interaction_score", "count"),
            total_score=("interaction_score", "sum")
        ).reset_index()
        i_agg["product_id"] = i_agg["product_id"].astype(str)
        p_df = p_df.merge(i_agg, on="product_id", how="left")
    else:
        p_df["total_purchases"] = 0.0
        p_df["total_score"] = 0.0

    p_df["total_purchases"] = p_df["total_purchases"].fillna(0.0)
    p_df["total_score"] = p_df["total_score"].fillna(0.0)
    p_df["rating"] = p_df["rating"].fillna(0.0) if "rating" in p_df.columns else 0.0

    # Max normalization for composite popularity score
    max_p = p_df["total_purchases"].max() or 1.0
    max_s = p_df["total_score"].max() or 1.0
    max_r = p_df["rating"].max() or 5.0

    p_df["popularity_score"] = (
        0.5 * (p_df["total_purchases"] / max_p) +
        0.3 * (p_df["total_score"] / max_s) +
        0.2 * (p_df["rating"] / max_r)
    )

    p_df["score"] = p_df["popularity_score"]
    p_df["method"] = "popular"

    # Filter out of stock if stock column exists
    if "stock" in p_df.columns:
        p_df = p_df[p_df["stock"].fillna(1) > 0]

    # Deterministic sort
    p_df = p_df.sort_values(by=["score", "product_id"], ascending=[False, True])

    recs = []
    for _, row in p_df.head(n).iterrows():
        recs.append({
            "product_id": str(row["product_id"]),
            "recommendation_score": float(row["score"]),
            "recommendation_method": "popular"
        })

    return recs

def rank_recommendations(
    raw_recommendations,
    products_df,
    user_id="UNKNOWN",
    interactions_df=None,
    n=10,
    exclude_purchased=True,
    filter_out_of_stock=True
):
    """
    Format, validate, rank, and enrich raw recommendation dicts into final ranking output DataFrame.
    """
    u_str = str(user_id)

    # 1. Fallback to popular if raw_recommendations is empty (Cold-start user)
    if not raw_recommendations:
        raw_recommendations = recommend_popular(products_df, interactions_df, n=n * 2)

    # 2. Build DataFrame
    rec_df = pd.DataFrame(raw_recommendations)

    if rec_df.empty or "product_id" not in rec_df.columns:
        pop_recs = recommend_popular(products_df, interactions_df, n=n * 2)
        rec_df = pd.DataFrame(pop_recs)

    rec_df["product_id"] = rec_df["product_id"].astype(str)

    # 3. Clean score column
    score_col = "recommendation_score" if "recommendation_score" in rec_df.columns else "score"
    rec_df["recommendation_score"] = rec_df[score_col].apply(
        lambda x: 0.0 if (pd.isna(x) or np.isinf(x)) else float(x)
    )

    method_col = "recommendation_method" if "recommendation_method" in rec_df.columns else "method"
    rec_df["recommendation_method"] = rec_df[method_col].fillna("unknown")

    # 4. Filter invalid product IDs
    rec_df = rec_df[
        rec_df["product_id"].notna() &
        (rec_df["product_id"] != "") &
        (rec_df["product_id"] != "nan") &
        (rec_df["product_id"] != "None")
    ].copy()

    # 5. Remove duplicates (keep highest score)
    rec_df = rec_df.sort_values(by=["recommendation_score", "product_id"], ascending=[False, True])
    rec_df = rec_df.drop_duplicates(subset=["product_id"], keep="first")

    # 6. Exclude purchased products if configured
    if exclude_purchased and interactions_df is not None and not interactions_df.empty:
        user_purchases = interactions_df[
            (interactions_df["user_id"].astype(str) == u_str) &
            (interactions_df.get("purchase_count", 0) > 0)
        ]["product_id"].astype(str).tolist()
        if user_purchases:
            rec_df = rec_df[~rec_df["product_id"].isin(user_purchases)]

    # 7. Merge product metadata
    if not products_df.empty:
        p_meta = products_df.copy()
        p_meta["product_id"] = p_meta["product_id"].astype(str)
        meta_cols = ["product_id", "product_name", "category", "price", "rating"]
        if "stock" in p_meta.columns:
            meta_cols.append("stock")
        meta_cols = [c for c in meta_cols if c in p_meta.columns]
        rec_df = rec_df.merge(p_meta[meta_cols], on="product_id", how="left")

    # 8. Filter out-of-stock
    if filter_out_of_stock and "stock" in rec_df.columns:
        rec_df = rec_df[rec_df["stock"].fillna(1) > 0]

    # 9. Fill missing metadata fields
    rec_df["product_name"] = rec_df.get("product_name", pd.Series(dtype=str)).fillna("Unknown Product")
    rec_df["category"] = rec_df.get("category", pd.Series(dtype=str)).fillna("General")
    rec_df["price"] = rec_df.get("price", pd.Series(dtype=float)).fillna(0.0)
    rec_df["rating"] = rec_df.get("rating", pd.Series(dtype=float)).fillna(0.0)

    # If top-n candidates fell short, pad with popular
    if len(rec_df) < n:
        pop_recs = recommend_popular(products_df, interactions_df, n=n * 2)
        pop_df = pd.DataFrame(pop_recs)
        if not pop_df.empty:
            pop_df["product_id"] = pop_df["product_id"].astype(str)
            existing_pids = set(rec_df["product_id"].tolist())
            pop_df = pop_df[~pop_df["product_id"].isin(existing_pids)]
            if not products_df.empty:
                pop_df = pop_df.merge(p_meta[meta_cols], on="product_id", how="left")
            rec_df = pd.concat([rec_df, pop_df], ignore_index=True)

    # 10. Final deterministic sorting
    rec_df = rec_df.sort_values(by=["recommendation_score", "product_id"], ascending=[False, True]).head(n)

    # 11. Add rank and user_id columns
    rec_df["rank"] = range(1, len(rec_df) + 1)
    rec_df["user_id"] = u_str

    final_cols = [
        "rank", "user_id", "product_id", "product_name", "category",
        "price", "rating", "recommendation_score", "recommendation_method"
    ]
    
    return rec_df[[c for c in final_cols if c in rec_df.columns]]

import os
import pandas as pd
import numpy as np
from recommendation_system import config

def build_interactions(data_dict=None, weights=None, valid_users=None, valid_products=None):
    """
    Build user-product interaction dataset from purchases, reviews, and events.
    """
    if weights is None:
        weights = config.DEFAULT_INTERACTION_WEIGHTS

    if data_dict is None:
        from recommendation_system.data_loader import load_all_data
        data_dict = load_all_data()

    purchases = data_dict.get("purchases", pd.DataFrame())
    reviews = data_dict.get("reviews", pd.DataFrame())
    events = data_dict.get("events", pd.DataFrame())

    interaction_records = []

    # 1. Process Purchases
    if not purchases.empty and "user_id" in purchases.columns and "product_id" in purchases.columns:
        # Filter valid purchase rows
        p_df = purchases.dropna(subset=["user_id", "product_id"]).copy()
        p_df["user_id"] = p_df["user_id"].astype(str)
        p_df["product_id"] = p_df["product_id"].astype(str)
        
        # Quantity & spend calculation
        if "quantity" not in p_df.columns:
            p_df["quantity"] = 1
        if "line_total" in p_df.columns:
            p_df["spend"] = p_df["line_total"]
        elif "net_sales" in p_df.columns:
            p_df["spend"] = p_df["net_sales"]
        elif "unit_price" in p_df.columns:
            p_df["spend"] = p_df["quantity"] * p_df["unit_price"]
        else:
            p_df["spend"] = 0.0

        purchase_agg = p_df.groupby(["user_id", "product_id"]).agg(
            purchase_count=("user_id", "count"),
            total_quantity=("quantity", "sum"),
            total_spend=("spend", "sum")
        ).reset_index()
        
        purchase_agg["purchase_score"] = purchase_agg["purchase_count"] * weights.get("purchase", 5.0)
    else:
        purchase_agg = pd.DataFrame(columns=["user_id", "product_id", "purchase_count", "total_quantity", "total_spend", "purchase_score"])

    # 2. Process Reviews
    if not reviews.empty and "user_id" in reviews.columns and "product_id" in reviews.columns:
        r_df = reviews.dropna(subset=["user_id", "product_id"]).copy()
        r_df["user_id"] = r_df["user_id"].astype(str)
        r_df["product_id"] = r_df["product_id"].astype(str)

        review_agg = r_df.groupby(["user_id", "product_id"]).agg(
            review_count=("user_id", "count"),
            avg_review_rating=("rating", "mean") if "rating" in r_df.columns else ("user_id", lambda x: 0.0)
        ).reset_index()

        review_agg["review_score"] = review_agg["review_count"] * weights.get("review", 4.0)
    else:
        review_agg = pd.DataFrame(columns=["user_id", "product_id", "review_count", "avg_review_rating", "review_score"])

    # 3. Process Events
    if not events.empty and "user_id" in events.columns and "product_id" in events.columns:
        e_df = events.dropna(subset=["user_id", "product_id"]).copy()
        e_df["user_id"] = e_df["user_id"].astype(str)
        e_df["product_id"] = e_df["product_id"].astype(str)

        # Map event types
        view_w = weights.get("product_view", 1.0)
        search_w = weights.get("search", 1.0)
        cart_w = weights.get("add_to_cart", 3.0)

        e_df["view_cnt"] = np.where(e_df["event_type"].isin(["product_view", "view"]), 1, 0)
        e_df["search_cnt"] = np.where(e_df["event_type"] == "search", 1, 0)
        e_df["cart_cnt"] = np.where(e_df["event_type"] == "add_to_cart", 1, 0)

        event_agg = e_df.groupby(["user_id", "product_id"]).agg(
            view_count=("view_cnt", "sum"),
            search_count=("search_cnt", "sum"),
            cart_count=("cart_cnt", "sum"),
            event_count=("user_id", "count")
        ).reset_index()

        event_agg["event_score"] = (
            event_agg["view_count"] * view_w +
            event_agg["search_count"] * search_w +
            event_agg["cart_count"] * cart_w
        )
    else:
        event_agg = pd.DataFrame(columns=["user_id", "product_id", "view_count", "search_count", "cart_count", "event_count", "event_score"])

    # Merge all aggregations into unified dataset
    all_pairs = pd.concat([
        purchase_agg[["user_id", "product_id"]],
        review_agg[["user_id", "product_id"]],
        event_agg[["user_id", "product_id"]]
    ]).drop_duplicates()

    if all_pairs.empty:
        # Fallback if no interactions exist
        interactions = pd.DataFrame(columns=[
            "user_id", "product_id", "interaction_score",
            "purchase_count", "total_quantity", "total_spend",
            "review_count", "avg_review_rating",
            "view_count", "search_count", "cart_count", "event_count"
        ])
        return interactions

    merged = all_pairs.merge(purchase_agg, on=["user_id", "product_id"], how="left")
    merged = merged.merge(review_agg, on=["user_id", "product_id"], how="left")
    merged = merged.merge(event_agg, on=["user_id", "product_id"], how="left")

    # Fill NaNs
    fill_zeros = ["purchase_count", "total_quantity", "total_spend", "purchase_score",
                  "review_count", "avg_review_rating", "review_score",
                  "view_count", "search_count", "cart_count", "event_count", "event_score"]
    for col in fill_zeros:
        if col in merged.columns:
            merged[col] = merged[col].fillna(0.0)

    # Compute final interaction score
    merged["interaction_score"] = (
        merged["purchase_score"] + merged["review_score"] + merged["event_score"]
    )

    # Ensure non-negative
    merged["interaction_score"] = merged["interaction_score"].clip(lower=0.0)

    # Clean invalid IDs (empty string, nan, 'nan')
    merged = merged[
        (merged["user_id"].notna()) & (merged["user_id"] != "") & (merged["user_id"] != "nan") &
        (merged["product_id"].notna()) & (merged["product_id"] != "") & (merged["product_id"] != "nan")
    ].copy()

    # Filter against valid users/products if provided
    if valid_users is not None:
        valid_u_set = set(map(str, valid_users))
        merged = merged[merged["user_id"].isin(valid_u_set)]

    if valid_products is not None:
        valid_p_set = set(map(str, valid_products))
        merged = merged[merged["product_id"].isin(valid_p_set)]

    cols_order = [
        "user_id", "product_id", "interaction_score",
        "purchase_count", "total_quantity", "total_spend",
        "review_count", "avg_review_rating",
        "view_count", "search_count", "cart_count", "event_count"
    ]
    interactions = merged[[c for c in cols_order if c in merged.columns]]

    return interactions

def save_interactions(interactions_df, output_dir=None):
    """Save interactions dataset to parquet and csv."""
    if output_dir is None:
        output_dir = config.INTERACTIONS_DIR
    os.makedirs(output_dir, exist_ok=True)

    pq_path = os.path.join(output_dir, "user_product_interactions.parquet")
    csv_path = os.path.join(output_dir, "user_product_interactions.csv")

    interactions_df.to_parquet(pq_path, index=False)
    interactions_df.to_csv(csv_path, index=False)
    return pq_path, csv_path

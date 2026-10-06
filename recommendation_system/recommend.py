import pandas as pd
from recommendation_system import config
from recommendation_system.data_loader import load_all_data
from recommendation_system.interaction_builder import build_interactions
from recommendation_system.collaborative import build_interaction_matrix, build_item_similarity, recommend_collaborative
from recommendation_system.content_features import build_content_similarity
from recommendation_system.content_based import recommend_content_based
from recommendation_system.hybrid import recommend_hybrid
from recommendation_system.ranking import rank_recommendations, recommend_popular

def recommend(
    user_id,
    n=config.DEFAULT_TOP_N,
    method="hybrid",
    exclude_purchased=True,
    data_dict=None,
    models_dict=None
):
    """
    High-level API for generating Top-N product recommendations for a user.
    
    Supported methods: 'collaborative', 'content', 'hybrid', 'popular'
    Returns DataFrame with columns:
        [rank, user_id, product_id, product_name, category, price, rating, recommendation_score, recommendation_method]
    """
    if data_dict is None:
        data_dict = load_all_data()

    products_df = data_dict.get("products", pd.DataFrame())
    
    if models_dict is None:
        interactions_df = build_interactions(data_dict)
        user_item_matrix, u2i, i2u, p2i, i2p = build_interaction_matrix(interactions_df)
        item_similarity = build_item_similarity(user_item_matrix)
        content_similarity, c_p2i, c_i2p, _ = build_content_similarity(products_df)

        models_dict = {
            "interactions_df": interactions_df,
            "user_item_matrix": user_item_matrix,
            "user_to_idx": u2i,
            "idx_to_user": i2u,
            "product_to_idx": p2i,
            "idx_to_product": i2p,
            "item_similarity": item_similarity,
            "content_similarity": content_similarity,
            "content_p2i": c_p2i,
            "content_i2p": c_i2p
        }

    interactions_df = models_dict["interactions_df"]
    u_str = str(user_id)
    method = str(method).lower()

    raw_recs = []

    if method == "collaborative":
        raw_recs = recommend_collaborative(
            user_id=u_str,
            user_item_matrix=models_dict["user_item_matrix"],
            item_similarity=models_dict["item_similarity"],
            user_to_idx=models_dict["user_to_idx"],
            idx_to_user=models_dict["idx_to_user"],
            product_to_idx=models_dict["product_to_idx"],
            idx_to_product=models_dict["idx_to_product"],
            n=n * 2,
            exclude_purchased=exclude_purchased
        )

    elif method == "content":
        raw_recs = recommend_content_based(
            user_id=u_str,
            interactions_df=interactions_df,
            similarity_matrix=models_dict["content_similarity"],
            product_to_idx=models_dict["content_p2i"],
            idx_to_product=models_dict["content_i2p"],
            n=n * 2,
            exclude_purchased=exclude_purchased
        )

    elif method == "hybrid":
        raw_recs = recommend_hybrid(
            user_id=u_str,
            user_item_matrix=models_dict["user_item_matrix"],
            item_similarity=models_dict["item_similarity"],
            content_similarity=models_dict["content_similarity"],
            user_to_idx=models_dict["user_to_idx"],
            idx_to_user=models_dict["idx_to_user"],
            product_to_idx=models_dict["product_to_idx"],
            idx_to_product=models_dict["idx_to_product"],
            interactions_df=interactions_df,
            n=n * 2,
            exclude_purchased=exclude_purchased,
            content_p2i=models_dict["content_p2i"],
            content_i2p=models_dict["content_i2p"]
        )

    elif method == "popular":
        raw_recs = recommend_popular(
            products_df=products_df,
            interactions_df=interactions_df,
            n=n * 2
        )

    else:
        print(f"Warning: Unknown method '{method}'. Falling back to popular recommendations.")
        raw_recs = recommend_popular(products_df=products_df, interactions_df=interactions_df, n=n * 2)

    ranked_df = rank_recommendations(
        raw_recommendations=raw_recs,
        products_df=products_df,
        user_id=u_str,
        interactions_df=interactions_df,
        n=n,
        exclude_purchased=exclude_purchased
    )

    return ranked_df

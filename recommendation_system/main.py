import argparse
import sys
import os
import pandas as pd
from recommendation_system import config
from recommendation_system.data_loader import load_all_data
from recommendation_system.interaction_builder import build_interactions, save_interactions
from recommendation_system.collaborative import build_interaction_matrix, build_item_similarity, save_collaborative_model
from recommendation_system.content_features import build_content_similarity, save_content_model
from recommendation_system.evaluation import evaluate_models, save_evaluation_results
from recommendation_system.recommend import recommend
from recommendation_system.visualization import generate_visualizations
from recommendation_system.reporting import generate_sample_recommendations, generate_reports

def run_pipeline(user_id=None, method="hybrid", top_n=10, exclude_purchased=True):
    """
    Execute full recommendation system end-to-end pipeline.
    """
    print("=== Step 1: Loading Data ===")
    config.ensure_directories()
    data_dict = load_all_data()

    products_df = data_dict.get("products", pd.DataFrame())
    users_df = data_dict.get("users", pd.DataFrame())

    print(f"Loaded {len(products_df)} products, {len(users_df)} users.")

    print("\n=== Step 2: Building Interaction Dataset ===")
    interactions_df = build_interactions(
        data_dict,
        valid_users=users_df["user_id"].unique() if "user_id" in users_df.columns else None,
        valid_products=products_df["product_id"].unique() if "product_id" in products_df.columns else None
    )
    save_interactions(interactions_df)
    print(f"Built {len(interactions_df)} user-product interactions.")

    print("\n=== Step 3: Training Collaborative Filtering Model ===")
    user_item_matrix, u2i, i2u, p2i, i2p = build_interaction_matrix(interactions_df)
    item_similarity = build_item_similarity(user_item_matrix)
    save_collaborative_model(user_item_matrix, item_similarity)
    print("Collaborative model artifacts saved.")

    print("\n=== Step 4: Training Content-Based Filtering Model ===")
    content_similarity, c_p2i, c_i2p, tfidf_vectorizer = build_content_similarity(products_df)
    save_content_model(content_similarity, tfidf_vectorizer)
    print("Content-based model artifacts saved.")

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

    print("\n=== Step 5: Evaluating Recommendation Models ===")
    eval_df, eval_json = evaluate_models(interactions_df, products_df)
    save_evaluation_results(eval_df, eval_json)
    print("Evaluation completed and metrics saved.")

    print("\n=== Step 6: Generating Recommendations & Saving Output Files ===")
    real_users = interactions_df["user_id"].unique().tolist() if not interactions_df.empty else []
    sample_users = real_users[:10] if real_users else ["USER001", "USER002"]

    sample_recs_df, _ = generate_sample_recommendations(
        users_list=sample_users,
        products_df=products_df,
        models_dict=models_dict,
        n=top_n,
        method=method
    )

    # Save method-specific recommendations files
    for m in ["hybrid", "collaborative", "content", "popular"]:
        m_recs = []
        for uid in sample_users[:5]:
            r_df = recommend(
                user_id=uid,
                n=top_n,
                method=m,
                exclude_purchased=exclude_purchased,
                data_dict=data_dict,
                models_dict=models_dict
            )
            if not r_df.empty:
                m_recs.append(r_df)
        if m_recs:
            m_combined = pd.concat(m_recs, ignore_index=True)
            m_combined.to_csv(os.path.join(config.RECOMMENDATIONS_OUTPUT_DIR, f"{m}_recommendations.csv"), index=False)

    print("\n=== Step 7: Generating Visualizations ===")
    viz_files = generate_visualizations(
        interactions_df=interactions_df,
        products_df=products_df,
        evaluation_df=eval_df,
        sample_recommendations_df=sample_recs_df
    )
    print(f"Generated {len(viz_files)} visualization figures.")

    print("\n=== Step 8: Generating Summary Reports ===")
    json_rep, txt_rep = generate_reports(
        interactions_df=interactions_df,
        products_df=products_df,
        evaluation_json=eval_json,
        sample_recs_df=sample_recs_df,
        models_dict=models_dict
    )
    print(f"Reports generated: {txt_rep}")

    # Specific user request handling
    if user_id:
        print(f"\n=====================================================")
        print(f" Recommendations for Specified User: {user_id}")
        print(f"=====================================================")
        user_recs = recommend(
            user_id=user_id,
            n=top_n,
            method=method,
            exclude_purchased=exclude_purchased,
            data_dict=data_dict,
            models_dict=models_dict
        )
        print(user_recs.to_string(index=False))

    print("\n=== Recommendation Pipeline Execution Completed Successfully ===")

def main():
    parser = argparse.ArgumentParser(description="Product Recommendation System CLI")
    parser.add_argument("--user-id", type=str, default=None, help="Target User ID for recommendations")
    parser.add_argument("--method", type=str, default="hybrid", choices=["hybrid", "collaborative", "content", "popular"], help="Recommendation method")
    parser.add_argument("--top-n", type=int, default=10, help="Number of recommendations to return")
    parser.add_argument("--exclude-purchased", action="store_true", default=True, help="Exclude purchased products")
    parser.add_argument("--include-purchased", dest="exclude_purchased", action="store_false", help="Do not exclude purchased products")

    args = parser.parse_args()
    run_pipeline(
        user_id=args.user_id,
        method=args.method,
        top_n=args.top_n,
        exclude_purchased=args.exclude_purchased
    )

if __name__ == "__main__":
    main()

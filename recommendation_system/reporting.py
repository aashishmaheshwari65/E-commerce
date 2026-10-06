import os
import json
import pandas as pd
from recommendation_system import config
from recommendation_system.recommend import recommend

def generate_sample_recommendations(users_list, products_df, models_dict, n=10, method="hybrid"):
    """
    Generate actual recommendations for a sample of real users from the dataset.
    Saves output to data/recommendations/evaluation/recommendation_examples.csv
    """
    if not users_list:
        users_list = ["USER001", "USER002", "USER003"]

    all_sample_recs = []
    for uid in users_list[:10]:
        recs_df = recommend(
            user_id=uid,
            n=n,
            method=method,
            exclude_purchased=True,
            data_dict={"products": products_df},
            models_dict=models_dict
        )
        if not recs_df.empty:
            all_sample_recs.append(recs_df)

    if all_sample_recs:
        combined_df = pd.concat(all_sample_recs, ignore_index=True)
    else:
        combined_df = pd.DataFrame(columns=[
            "rank", "user_id", "product_id", "product_name", "category",
            "price", "rating", "recommendation_score", "recommendation_method"
        ])

    csv_path = os.path.join(config.EVALUATION_DIR, "recommendation_examples.csv")
    os.makedirs(config.EVALUATION_DIR, exist_ok=True)
    combined_df.to_csv(csv_path, index=False)
    return combined_df, csv_path

def generate_reports(interactions_df, products_df, evaluation_json, sample_recs_df, models_dict):
    """
    Generate recommendation_summary.json and recommendation_summary.txt reports.
    """
    os.makedirs(config.REPORTS_DIR, exist_ok=True)
    os.makedirs(config.MODELS_DIR, exist_ok=True)

    n_users = interactions_df["user_id"].nunique() if not interactions_df.empty else 0
    n_products = products_df["product_id"].nunique() if not products_df.empty else 0
    n_interactions = len(interactions_df)

    summary_data = {
        "model_version": "1.0.0",
        "dataset_statistics": {
            "num_users": int(n_users),
            "num_products": int(n_products),
            "num_interactions": int(n_interactions)
        },
        "interaction_weights": config.DEFAULT_INTERACTION_WEIGHTS,
        "hybrid_weights": config.DEFAULT_HYBRID_WEIGHTS,
        "cold_start_strategy": {
            "new_user": "Popularity score based on purchase count, interaction score, and rating",
            "new_product": "Content-based similarity using TF-IDF text and numerical metadata",
            "unknown_user": "Popularity fallback"
        },
        "evaluation_summary": evaluation_json.get("metrics", [])
    }

    # Save model_metadata.json to models dir
    metadata_path = os.path.join(config.MODELS_DIR, "model_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(summary_data, f, indent=2)

    # Save recommendation_summary.json to reports dir
    json_report_path = os.path.join(config.REPORTS_DIR, "recommendation_summary.json")
    with open(json_report_path, "w") as f:
        json.dump(summary_data, f, indent=2)

    # Save recommendation_summary.txt to reports dir
    txt_report_path = os.path.join(config.REPORTS_DIR, "recommendation_summary.txt")
    with open(txt_report_path, "w") as f:
        f.write("=====================================================\n")
        f.write("      PRODUCT RECOMMENDATION SYSTEM SUMMARY REPORT   \n")
        f.write("=====================================================\n\n")
        f.write(f"Model Version      : {summary_data['model_version']}\n")
        f.write(f"Total Users        : {summary_data['dataset_statistics']['num_users']}\n")
        f.write(f"Total Products     : {summary_data['dataset_statistics']['num_products']}\n")
        f.write(f"Total Interactions : {summary_data['dataset_statistics']['num_interactions']}\n\n")
        f.write("Cold-Start Strategy:\n")
        f.write(f"  - New User    : {summary_data['cold_start_strategy']['new_user']}\n")
        f.write(f"  - New Product : {summary_data['cold_start_strategy']['new_product']}\n")
        f.write(f"  - Unknown User: {summary_data['cold_start_strategy']['unknown_user']}\n\n")
        f.write("Evaluation Results:\n")
        for m in summary_data["evaluation_summary"]:
            f.write(f"  - Method: {m.get('method')}, K={m.get('k')} | Precision: {m.get('precision'):.4f}, Recall: {m.get('recall'):.4f}, Coverage: {m.get('catalog_coverage'):.4f}\n")
        f.write("\n=====================================================\n")

    return json_report_path, txt_report_path

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from recommendation_system import config

def generate_visualizations(interactions_df, products_df, evaluation_df, sample_recommendations_df=None, output_dir=None):
    """
    Generate and save visualization plots for interaction distributions, top products,
    catalog coverage, model evaluation comparisons, and score distributions.
    """
    if output_dir is None:
        output_dir = config.VISUALIZATIONS_DIR
    os.makedirs(output_dir, exist_ok=True)

    plt.style.use('ggplot')
    generated_files = []

    # 1. Interaction Score Distribution
    if not interactions_df.empty and "interaction_score" in interactions_df.columns:
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(interactions_df["interaction_score"], bins=30, color="#4C72B0", edgecolor="white")
        ax.set_title("Interaction Score Distribution", fontsize=14, pad=10)
        ax.set_xlabel("Interaction Score", fontsize=12)
        ax.set_ylabel("User-Product Pair Count", fontsize=12)
        plt.tight_layout()
        path1 = os.path.join(output_dir, "interaction_distribution.png")
        plt.savefig(path1, dpi=300)
        plt.close()
        generated_files.append(path1)

    # 2. Most Interacted Products
    if not interactions_df.empty and "product_id" in interactions_df.columns:
        fig, ax = plt.subplots(figsize=(10, 6))
        top_interacted = interactions_df.groupby("product_id")["interaction_score"].sum().nlargest(10).reset_index()
        
        if not products_df.empty and "product_name" in products_df.columns:
            p_map = dict(zip(products_df["product_id"].astype(str), products_df["product_name"]))
            top_interacted["product_name"] = top_interacted["product_id"].astype(str).map(p_map).fillna(top_interacted["product_id"])
            label_col = "product_name"
        else:
            label_col = "product_id"

        ax.barh(top_interacted[label_col].astype(str), top_interacted["interaction_score"], color="#55A868")
        ax.set_title("Top 10 Most Interacted Products", fontsize=14, pad=10)
        ax.set_xlabel("Total Interaction Score", fontsize=12)
        ax.invert_yaxis()
        plt.tight_layout()
        path2 = os.path.join(output_dir, "popular_products.png")
        plt.savefig(path2, dpi=300)
        plt.close()
        generated_files.append(path2)

    # 3. Recommendation Coverage
    if not evaluation_df.empty and "catalog_coverage" in evaluation_df.columns:
        fig, ax = plt.subplots(figsize=(8, 5))
        k10_eval = evaluation_df[evaluation_df["k"] == 10] if "k" in evaluation_df.columns else evaluation_df
        if k10_eval.empty:
            k10_eval = evaluation_df

        ax.bar(k10_eval["method"], k10_eval["catalog_coverage"] * 100, color="#C44E52", width=0.5)
        ax.set_title("Catalog Coverage by Method (K=10)", fontsize=14, pad=10)
        ax.set_xlabel("Recommendation Method", fontsize=12)
        ax.set_ylabel("Catalog Coverage (%)", fontsize=12)
        ax.set_ylim(0, 100)
        plt.tight_layout()
        path3 = os.path.join(output_dir, "recommendation_coverage.png")
        plt.savefig(path3, dpi=300)
        plt.close()
        generated_files.append(path3)

    # 4. Model Evaluation Comparison (Precision & Recall @ K=10)
    if not evaluation_df.empty and "precision" in evaluation_df.columns:
        fig, ax = plt.subplots(figsize=(9, 5))
        k10_eval = evaluation_df[evaluation_df["k"] == 10] if "k" in evaluation_df.columns else evaluation_df
        if k10_eval.empty:
            k10_eval = evaluation_df

        x = np.arange(len(k10_eval["method"]))
        width = 0.35

        ax.bar(x - width/2, k10_eval["precision"], width, label="Precision@10", color="#8172B0")
        ax.bar(x + width/2, k10_eval["recall"], width, label="Recall@10", color="#CCB974")

        ax.set_title("Model Performance Comparison (K=10)", fontsize=14, pad=10)
        ax.set_xticks(x)
        ax.set_xticklabels(k10_eval["method"])
        ax.set_ylabel("Metric Value", fontsize=12)
        ax.legend()
        plt.tight_layout()
        path4 = os.path.join(output_dir, "model_comparison.png")
        plt.savefig(path4, dpi=300)
        plt.close()
        generated_files.append(path4)

    # 5. Recommendation Score Distribution
    if sample_recommendations_df is not None and not sample_recommendations_df.empty and "recommendation_score" in sample_recommendations_df.columns:
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(sample_recommendations_df["recommendation_score"], bins=20, color="#64B5CD", edgecolor="white")
        ax.set_title("Distribution of Recommendation Scores", fontsize=14, pad=10)
        ax.set_xlabel("Recommendation Score", fontsize=12)
        ax.set_ylabel("Frequency", fontsize=12)
        plt.tight_layout()
        path5 = os.path.join(output_dir, "recommendation_score_distribution.png")
        plt.savefig(path5, dpi=300)
        plt.close()
        generated_files.append(path5)

    return generated_files

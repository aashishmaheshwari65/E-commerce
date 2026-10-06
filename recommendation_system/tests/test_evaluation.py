import pytest
import pandas as pd
from recommendation_system.evaluation import precision_at_k, recall_at_k, hit_rate_at_k, map_at_k, ndcg_at_k, evaluate_models

def test_metrics_calculation():
    actual = {"P1", "P2"}
    recommended = ["P1", "P3", "P2", "P4"]

    assert precision_at_k(actual, recommended, 2) == 0.5 # 1 hit in top 2 (P1)
    assert recall_at_k(actual, recommended, 2) == 0.5    # 1 of 2 actual items hit
    assert hit_rate_at_k(actual, recommended, 2) == 1.0  # Has at least 1 hit
    assert map_at_k(actual, recommended, 2) == 0.5       # (1/1)/2 = 0.5
    assert ndcg_at_k(actual, recommended, 2) > 0.0

def test_evaluate_models_synthetic():
    products = pd.DataFrame({
        "product_id": ["P1", "P2", "P3", "P4"],
        "product_name": ["W1", "W2", "W3", "W4"],
        "category": ["C1", "C1", "C2", "C2"],
        "price": [10, 20, 30, 40],
        "rating": [4, 4, 5, 5]
    })
    interactions = pd.DataFrame({
        "user_id": ["U1", "U1", "U2", "U2"],
        "product_id": ["P1", "P2", "P1", "P3"],
        "interaction_score": [5.0, 4.0, 5.0, 3.0]
    })

    eval_df, eval_json = evaluate_models(interactions, products, k_values=[2])
    assert not eval_df.empty
    assert "precision" in eval_df.columns
    assert "catalog_coverage" in eval_df.columns
    assert eval_json["status"] == "success"

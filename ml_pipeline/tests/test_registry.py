import pytest
import os
from sklearn.linear_model import LogisticRegression
from ml_pipeline import model_registry, config

def test_save_and_load_model():
    dummy_model = LogisticRegression()
    dummy_model.fit([[1, 2, 3, 4], [5, 6, 7, 8]], [0, 1])

    version = "20261006_999999"
    metadata = {"model_name": "logistic_regression", "test_key": "val"}
    metrics = {"roc_auc": 0.85}

    save_info = model_registry.save_model(
        model_type="churn",
        model_obj=dummy_model,
        version=version,
        metadata=metadata,
        metrics=metrics
    )

    assert save_info["version"] == version

    # List models
    models = model_registry.list_models("churn")
    assert any(m["version"] == version for m in models)

    # Get latest
    latest = model_registry.get_latest_model("churn")
    assert latest is not None

    # Load model
    loaded = model_registry.load_model("churn", version=version)
    assert loaded["version"] == version
    assert loaded["metadata"]["test_key"] == "val"
    assert hasattr(loaded["model"], "predict")

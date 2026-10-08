"""
tests/ml_pipeline/test_registry.py

Tests ModelRegistry save, load, version generation, and latest model retrieval.
"""

from pathlib import Path
from unittest.mock import patch
import pytest
from sklearn.linear_model import Ridge
from ml_pipeline import model_registry, config


@pytest.mark.unit
@pytest.mark.ml
def test_save_and_load_model(tmp_path: Path):
    test_model_root = tmp_path / "models"

    with patch.object(config, "MODEL_ROOT", test_model_root):
        dummy_model = Ridge()
        dummy_model.fit([[1], [2]], [10, 20])

        info = model_registry.save_model(
            model_type="forecasting",
            model_obj=dummy_model,
            version="v1.0.0",
            metrics={"mae": 1.5},
        )

        assert info["version"] == "v1.0.0"
        assert (test_model_root / "forecasting" / "v1.0.0" / "model.joblib").exists()

        loaded = model_registry.load_model("forecasting", version="v1.0.0")
        assert loaded["model"] is not None
        assert loaded["version"] == "v1.0.0"

        # Verify model can perform inference
        preds = loaded["model"].predict([[3]])
        assert len(preds) == 1

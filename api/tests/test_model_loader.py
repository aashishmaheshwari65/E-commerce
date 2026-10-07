import pytest
from unittest.mock import patch
from api.services import model_loader
from api.utils.errors import ModelUnavailableError

def test_model_loader_missing_model():
    with patch("ml_pipeline.model_registry.get_latest_model", return_value=None):
        model_loader.clear_model_cache()
        assert model_loader.is_model_available("non_existent_model_type") is False
        with pytest.raises(ModelUnavailableError):
            model_loader.load_latest_model("non_existent_model_type")

def test_model_loader_caching():
    dummy_latest = {
        "version": "20261007_000000",
        "path": "/dummy/path",
        "metadata": {"model_type": "churn", "test": True}
    }
    dummy_model_dict = {
        "model": "dummy_model_obj",
        "metadata": {"model_type": "churn", "test": True},
        "version": "20261007_000000"
    }

    with patch("ml_pipeline.model_registry.get_latest_model", return_value=dummy_latest):
        with patch("ml_pipeline.model_registry.load_model", return_value=dummy_model_dict):
            model_loader.clear_model_cache()
            
            # First load -> disk read
            loaded1 = model_loader.load_latest_model("churn")
            assert loaded1["version"] == "20261007_000000"

            # Second load -> returns cached dict
            loaded2 = model_loader.load_latest_model("churn")
            assert loaded2 is loaded1

import pytest
from ml_pipeline import pipeline, config, pipeline_utils

def test_pipeline_features_only():
    res = pipeline.run_pipeline(features_only=True)
    assert res["status"] == "success"
    assert res["feature_status"] == "success"

def test_pipeline_run_all():
    res = pipeline.run_pipeline(run_all=True)
    assert res["status"] == "success"
    assert res["feature_status"] == "success"
    assert res["training_status"] == "success"
    assert res["evaluation_status"] == "success"
    assert res["model_save_status"] == "success"
    assert len(res["selected_models"]) == 4

def test_pipeline_runs_record():
    runs = pipeline_utils.load_json(config.PIPELINE_ROOT / "pipeline_runs.json")
    assert isinstance(runs, list)
    assert len(runs) >= 1
    assert "run_id" in runs[0]
    assert "selected_models" in runs[0]

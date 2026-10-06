import os
import json
from pathlib import Path
from datetime import datetime
import joblib
from ml_pipeline import config
from ml_pipeline.pipeline_utils import get_logger, save_json, load_json

logger = get_logger("model_registry")

def save_model(model_type, model_obj, version=None, metadata=None, metrics=None):
    """
    Save trained model artifact, metadata, and evaluation metrics under a versioned directory.
    Path: data/models/<model_type>/<version>/
    """
    config.ensure_directories()
    if model_type not in config.MODEL_TYPES:
        raise ValueError(f"Invalid model_type '{model_type}'. Must be one of {config.MODEL_TYPES}")

    if version is None:
        version = config.generate_version()

    model_dir = config.MODEL_ROOT / model_type / version
    os.makedirs(model_dir, exist_ok=True)

    model_path = model_dir / "model.joblib"
    joblib.dump(model_obj, model_path)

    timestamp = datetime.now().isoformat()

    if metadata is None:
        metadata = {}

    metadata.update({
        "model_type": model_type,
        "version": version,
        "training_timestamp": timestamp,
        "status": "selected"
    })

    if metrics is not None:
        metadata["metrics"] = metrics
        save_metrics(model_type, version, metrics)

    save_metadata(model_type, version, metadata)
    logger.info(f"Successfully saved {model_type} model version '{version}' to {model_dir}")

    return {
        "model_type": model_type,
        "version": version,
        "model_path": str(model_path),
        "dir": str(model_dir)
    }

def save_metadata(model_type, version, metadata):
    """Save metadata.json for a model version."""
    model_dir = config.MODEL_ROOT / model_type / version
    os.makedirs(model_dir, exist_ok=True)
    meta_path = model_dir / "metadata.json"
    save_json(meta_path, metadata)
    return str(meta_path)

def save_metrics(model_type, version, metrics):
    """Save metrics.json for a model version."""
    model_dir = config.MODEL_ROOT / model_type / version
    os.makedirs(model_dir, exist_ok=True)
    metrics_path = model_dir / "metrics.json"
    save_json(metrics_path, metrics)
    return str(metrics_path)

def list_models(model_type=None):
    """
    List all saved model versions in the model registry.
    Returns list of dicts: [{'model_type': m, 'version': v, 'path': p}, ...]
    """
    config.ensure_directories()
    types_to_check = [model_type] if model_type else config.MODEL_TYPES
    registered = []

    for mtype in types_to_check:
        type_dir = config.MODEL_ROOT / mtype
        if type_dir.exists():
            for v_dir in sorted(type_dir.iterdir(), reverse=True):
                if v_dir.is_dir() and (v_dir / "model.joblib").exists():
                    meta = load_json(v_dir / "metadata.json")
                    registered.append({
                        "model_type": mtype,
                        "version": v_dir.name,
                        "path": str(v_dir / "model.joblib"),
                        "metadata": meta
                    })
    return registered

def get_latest_model(model_type):
    """
    Retrieve the latest model version directory and path for a given model type.
    """
    models = list_models(model_type)
    if not models:
        return None
    # Latest version (sorted chronologically descending)
    return models[0]

def load_model(model_type, version=None):
    """
    Load model artifact object and metadata from the registry.
    If version is None, loads the latest version.
    """
    if version is None:
        latest = get_latest_model(model_type)
        if not latest:
            raise FileNotFoundError(f"No registered model found for model_type '{model_type}'")
        version = latest["version"]

    model_file = config.MODEL_ROOT / model_type / version / "model.joblib"
    meta_file = config.MODEL_ROOT / model_type / version / "metadata.json"

    if not model_file.exists():
        raise FileNotFoundError(f"Model file not found: {model_file}")

    model_obj = joblib.load(model_file)
    metadata = load_json(meta_file)

    return {
        "model": model_obj,
        "metadata": metadata,
        "version": version
    }

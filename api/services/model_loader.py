import logging
from typing import Dict, Any, Optional
from ml_pipeline import model_registry, config as ml_config
from api.utils.errors import ModelUnavailableError

logger = logging.getLogger("api.model_loader")

# In-memory singleton model cache: {model_type: {"model": model_obj, "metadata": meta, "version": v}}
_MODEL_CACHE: Dict[str, Dict[str, Any]] = {}

def is_model_available(model_type: str) -> bool:
    """
    Check if a trained model artifact is registered and available on disk for a given domain.
    """
    try:
        latest = model_registry.get_latest_model(model_type)
        return latest is not None and "path" in latest
    except Exception as e:
        logger.warning(f"Error checking model availability for '{model_type}': {e}")
        return False

def get_model_metadata(model_type: str) -> Dict[str, Any]:
    """
    Retrieve metadata for the latest registered model version.
    """
    if model_type in _MODEL_CACHE:
        return _MODEL_CACHE[model_type].get("metadata", {})

    latest = model_registry.get_latest_model(model_type)
    if not latest:
        raise ModelUnavailableError(model_type)

    meta = latest.get("metadata", {})
    return meta

def load_latest_model(model_type: str) -> Dict[str, Any]:
    """
    Lazy load and cache the latest registered model for a given domain.
    Returns dict: {"model": model_obj, "metadata": metadata, "version": version}
    """
    if model_type in _MODEL_CACHE:
        return _MODEL_CACHE[model_type]

    if not is_model_available(model_type):
        raise ModelUnavailableError(model_type)

    try:
        logger.info(f"Loading '{model_type}' model from disk into cache...")
        loaded = model_registry.load_model(model_type)
        _MODEL_CACHE[model_type] = loaded
        logger.info(f"Successfully cached '{model_type}' model (version: {loaded.get('version')}).")
        return loaded
    except Exception as e:
        logger.error(f"Failed to load '{model_type}' model: {e}", exc_info=True)
        raise ModelUnavailableError(model_type, detail=f"Failed to load model artifact: {str(e)}")

def clear_model_cache():
    """Clear in-memory model cache."""
    _MODEL_CACHE.clear()

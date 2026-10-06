import pytest
from pathlib import Path
from ml_pipeline import config

def test_config_paths():
    assert isinstance(config.DATA_ROOT, Path)
    assert isinstance(config.MODEL_ROOT, Path)
    assert isinstance(config.PIPELINE_ROOT, Path)
    assert isinstance(config.FEATURE_ROOT, Path)

def test_generate_version():
    v = config.generate_version()
    assert isinstance(v, str)
    assert len(v) == 15 # YYYYMMDD_HHMMSS
    assert "_" in v

def test_ensure_directories():
    config.ensure_directories()
    assert config.MODEL_ROOT.exists()
    assert config.PIPELINE_ROOT.exists()
    assert config.FEATURE_ROOT.exists()

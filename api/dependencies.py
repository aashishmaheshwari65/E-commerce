from api.services import model_loader
from api.utils.errors import ModelUnavailableError

def require_churn_model():
    """Dependency that ensures churn model is loaded or available."""
    if not model_loader.is_model_available("churn"):
        raise ModelUnavailableError("churn")
    return model_loader.load_latest_model("churn")

def require_forecasting_model():
    """Dependency that ensures forecasting model is loaded or available."""
    if not model_loader.is_model_available("forecasting"):
        raise ModelUnavailableError("forecasting")
    return model_loader.load_latest_model("forecasting")

def require_recommendation_model():
    """Dependency that ensures recommendation model is loaded or available."""
    if not model_loader.is_model_available("recommendation"):
        raise ModelUnavailableError("recommendation")
    return model_loader.load_latest_model("recommendation")

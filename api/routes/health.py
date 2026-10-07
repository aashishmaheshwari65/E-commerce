from fastapi import APIRouter
from api.services.model_loader import is_model_available
from api import config

router = APIRouter(tags=["Health"])

@router.get("/health", summary="API Health Check")
def health_check():
    """Returns basic service health status."""
    return {
        "status": "ok",
        "service": "ecommerce-ml-api",
        "version": config.API_VERSION
    }

@router.get("/health/models", summary="ML Model Availability Check")
def model_health_check():
    """Returns model artifact availability for churn, forecasting, and recommendations."""
    churn_avail = is_model_available("churn")
    forecast_avail = is_model_available("forecasting")
    rec_avail = is_model_available("recommendation")

    return {
        "status": "ok",
        "models": {
            "churn": churn_avail,
            "forecasting": forecast_avail,
            "recommendation": rec_avail
        }
    }

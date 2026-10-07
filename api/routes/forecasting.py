from typing import Dict, Any
from fastapi import APIRouter, Depends
from api.schemas.common import APIResponse
from api.schemas.forecasting import ForecastRequest, ForecastData
from api.services import forecasting_service, model_loader
from api.dependencies import require_forecasting_model

router = APIRouter(prefix="/forecast", tags=["Sales Forecasting"])

@router.post("", response_model=APIResponse[ForecastData], summary="Generate Sales Forecast")
def generate_forecast(request: ForecastRequest, model_info: Dict[str, Any] = Depends(require_forecasting_model)):
    """Generate daily sales revenue forecast for 7, 14, or 30 days ahead."""
    forecast_data = forecasting_service.generate_sales_forecast(request.horizon)
    version = model_info.get("version", "unknown")
    return APIResponse[ForecastData](
        success=True,
        model_version=version,
        data=forecast_data
    )

@router.get("/model", response_model=APIResponse[Dict[str, Any]], summary="Forecasting Model Metadata")
def get_forecasting_model_metadata(model_info: Dict[str, Any] = Depends(require_forecasting_model)):
    """Retrieve metadata, metrics, and training details for the active forecasting model."""
    meta = model_loader.get_model_metadata("forecasting")
    version = model_info.get("version", "unknown")
    return APIResponse[Dict[str, Any]](
        success=True,
        model_version=version,
        data=meta
    )

from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from api.schemas.common import APIResponse
from api.schemas.churn import ChurnPredictionRequest, BatchChurnPredictionRequest, ChurnPredictionData, BatchChurnPredictionResponseData
from api.services import churn_service, model_loader
from api.dependencies import require_churn_model

router = APIRouter(prefix="/churn", tags=["Churn Prediction"])

@router.post("/predict", response_model=APIResponse[ChurnPredictionData], summary="Single Customer Churn Prediction")
def predict_churn(request: ChurnPredictionRequest, model_info: Dict[str, Any] = Depends(require_churn_model)):
    """Predict churn probability and risk category for a customer or feature payload."""
    pred_data = churn_service.predict_single_churn(request)
    version = model_info.get("version", "unknown")
    return APIResponse[ChurnPredictionData](
        success=True,
        model_version=version,
        data=pred_data
    )

@router.post("/predict/batch", response_model=APIResponse[BatchChurnPredictionResponseData], summary="Batch Customer Churn Prediction")
def predict_churn_batch(request: BatchChurnPredictionRequest, model_info: Dict[str, Any] = Depends(require_churn_model)):
    """Predict churn probability for multiple customers in batch."""
    batch_res = churn_service.predict_batch_churn(request)
    version = model_info.get("version", "unknown")
    payload = BatchChurnPredictionResponseData(
        count=len(batch_res),
        data=batch_res
    )
    return APIResponse[BatchChurnPredictionResponseData](
        success=True,
        model_version=version,
        data=payload
    )

@router.get("/model", response_model=APIResponse[Dict[str, Any]], summary="Churn Model Metadata")
def get_churn_model_metadata(model_info: Dict[str, Any] = Depends(require_churn_model)):
    """Retrieve metadata, metrics, and training details for the active churn model."""
    meta = model_loader.get_model_metadata("churn")
    version = model_info.get("version", "unknown")
    return APIResponse[Dict[str, Any]](
        success=True,
        model_version=version,
        data=meta
    )

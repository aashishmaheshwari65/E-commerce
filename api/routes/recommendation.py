from typing import Dict, Any
from fastapi import APIRouter, Depends, Query
from api.schemas.common import APIResponse
from api.schemas.recommendation import RecommendationData
from api.services import recommendation_service, model_loader
from api.dependencies import require_recommendation_model

router = APIRouter(prefix="/recommendations", tags=["Product Recommendations"])

@router.get("/model", response_model=APIResponse[Dict[str, Any]], summary="Recommendation Model Metadata")
def get_recommendation_model_metadata(model_info: Dict[str, Any] = Depends(require_recommendation_model)):
    """Retrieve metadata, metrics, and training details for the active recommendation model."""
    meta = model_loader.get_model_metadata("recommendation")
    version = model_info.get("version", "unknown")
    return APIResponse[Dict[str, Any]](
        success=True,
        model_version=version,
        data=meta
    )

@router.get("/{user_id}", response_model=APIResponse[RecommendationData], summary="Get User Product Recommendations")
def get_recommendations(
    user_id: str,
    n: int = Query(10, ge=1, le=100, description="Top-N recommendations count"),
    method: str = Query("hybrid", description="Method: hybrid, collaborative, content, popular"),
    exclude_purchased: bool = Query(True, description="Exclude already purchased items"),
    model_info: Dict[str, Any] = Depends(require_recommendation_model)
):
    """Generate Top-N product recommendations for a user."""
    rec_data = recommendation_service.get_user_recommendations(
        user_id=user_id,
        n=n,
        method=method,
        exclude_purchased=exclude_purchased
    )
    version = model_info.get("version", "unknown")
    return APIResponse[RecommendationData](
        success=True,
        model_version=version,
        data=rec_data
    )

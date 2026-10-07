from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

class RecommendationParams(BaseModel):
    n: int = Field(10, ge=1, le=100, description="Number of recommendations (1 to 100)")
    method: str = Field("hybrid", description="Recommendation method (hybrid, collaborative, content, popular)")
    exclude_purchased: bool = Field(True, description="Exclude already purchased products")

    @field_validator("method")

    def validate_method(cls, v):
        allowed = {"hybrid", "collaborative", "content", "popular"}
        if v.lower() not in allowed:
            raise ValueError(f"Method must be one of {allowed}")
        return v.lower()

class RecommendationItemData(BaseModel):
    product_id: str
    score: float
    product_name: Optional[str] = None
    category: Optional[str] = None

class RecommendationData(BaseModel):
    user_id: str
    method: str
    recommendations: List[RecommendationItemData]

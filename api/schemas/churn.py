from typing import List, Optional
from pydantic import BaseModel, Field

class ChurnPredictionRequest(BaseModel):
    customer_id: Optional[str] = Field(None, description="Target customer ID for dataset lookup", json_schema_extra={"example": "USER001"})
    total_orders: Optional[int] = Field(None, description="Total order count", json_schema_extra={"example": 5})
    total_spend: Optional[float] = Field(None, description="Total customer spend amount", json_schema_extra={"example": 250.0})
    recency_days: Optional[int] = Field(None, description="Days since last purchase", json_schema_extra={"example": 30})
    average_items_per_order: Optional[float] = Field(None, description="Average items per order", json_schema_extra={"example": 2.5})

class BatchChurnPredictionRequest(BaseModel):
    customer_ids: List[str] = Field(..., description="List of target customer IDs", json_schema_extra={"example": ["USER001", "USER002"]})

class ChurnPredictionData(BaseModel):
    customer_id: str
    churn_probability: float
    risk_category: str

class BatchChurnPredictionResponseData(BaseModel):
    count: int
    data: List[ChurnPredictionData]

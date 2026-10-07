from typing import List
from pydantic import BaseModel, Field, field_validator

class ForecastRequest(BaseModel):
    horizon: int = Field(..., description="Forecast horizon in days (must be 7, 14, or 30)", json_schema_extra={"example": 7})

    @field_validator("horizon")

    def validate_horizon(cls, v):
        if v not in (7, 14, 30):
            raise ValueError("Horizon must be 7, 14, or 30 days.")
        return v

class ForecastItemData(BaseModel):
    date: str
    predicted_revenue: float

class ForecastData(BaseModel):
    horizon: int
    forecast: List[ForecastItemData]

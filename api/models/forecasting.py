from dataclasses import dataclass
from typing import List

@dataclass
class ForecastItem:
    date: str
    predicted_revenue: float

@dataclass
class ForecastResult:
    horizon: int
    forecast: List[ForecastItem]

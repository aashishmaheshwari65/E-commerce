from dataclasses import dataclass
from typing import List, Optional

@dataclass
class RecommendationItem:
    product_id: str
    score: float
    product_name: Optional[str] = None
    category: Optional[str] = None

@dataclass
class RecommendationResult:
    user_id: str
    method: str
    recommendations: List[RecommendationItem]

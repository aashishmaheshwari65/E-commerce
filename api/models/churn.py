from dataclasses import dataclass
from typing import Optional

@dataclass
class ChurnResult:
    customer_id: str
    churn_probability: float
    risk_category: str

from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")

class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    model_version: Optional[str] = None
    data: T

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[Any] = None

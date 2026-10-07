import logging
import json
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

logger = logging.getLogger("api.errors")

class ModelUnavailableError(HTTPException):
    def __init__(self, model_type: str, detail: str = None):
        msg = detail or f"Model '{model_type}' artifact is currently unavailable. Run Functionality 18 training pipeline first."
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=msg)

class ResourceNotFoundError(HTTPException):
    def __init__(self, resource: str, identifier: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f"{resource} '{identifier}' not found.")

class InvalidInputError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP Exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom Pydantic Request Validation Exception handler."""
    logger.warning(f"Validation error on {request.url}: {exc.errors()}")
    # Convert error objects to serializable dicts/strings
    serializable_errors = json.loads(json.dumps(exc.errors(), default=str))
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "Validation Error",
            "detail": serializable_errors
        }
    )

async def unhandled_exception_handler(request: Request, exc: Exception):
    """Server-side exception logger for 500 errors."""
    logger.error(f"Unhandled exception on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Internal Server Error",
            "detail": str(exc)
        }
    )

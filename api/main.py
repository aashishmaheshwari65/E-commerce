import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from api import config
from api.routes import health, churn, forecasting, recommendation, monitoring
from api.utils.errors import http_exception_handler, validation_exception_handler, unhandled_exception_handler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"
)
logger = logging.getLogger("api.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {config.API_TITLE} v{config.API_VERSION}...")
    logger.info(f"CORS Allowed Origins: {config.CORS_ORIGINS}")
    yield
    logger.info("Shutting down API...")

app = FastAPI(
    title=config.API_TITLE,
    version=config.API_VERSION,
    description=config.API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Exception Handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# Include API Routers
app.include_router(health.router)
app.include_router(churn.router)
app.include_router(forecasting.router)
app.include_router(recommendation.router)
app.include_router(monitoring.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)

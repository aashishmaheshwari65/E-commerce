# Base image: Python 3.11 slim (stable, lightweight, compatible with all dependencies)
FROM python:3.11-slim

# Labels
LABEL maintainer="E-Commerce ML Team"
LABEL description="Production-ready container for E-Commerce Data Engineering & AI Platform FastAPI Service"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PORT=8000

# Install runtime system dependencies (libgomp for scikit-learn OpenMP, curl for health checks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Create non-root user and group
RUN groupadd -r appuser && useradd -r -g appuser -u 1000 -d /app appuser

# Copy requirements files first to leverage Docker layer caching
COPY requirements.txt requirements-api.txt ./

# Install Python packages
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-api.txt

# Copy application source code (ignoring paths specified in .dockerignore)
COPY --chown=appuser:appuser . .

# Ensure data and models directory structure exists with appropriate permissions
RUN mkdir -p /app/data/models /app/data/ml_pipeline/features /app/data/testing && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose FastAPI service port
EXPOSE 8000

# Container health check querying the actual FastAPI /health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command to run FastAPI via Uvicorn
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

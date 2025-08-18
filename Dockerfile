# Multi-stage Docker build for FastAPI S3 middleware
FROM python:3.13.7-slim as builder

# Install uv for fast package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-cache

# Production stage
FROM python:3.13.7-slim

# Install security updates and clean up
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        curl \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# Create non-root user for security
RUN groupadd -g 1000 appuser && \
    useradd -r -u 1000 -g appuser appuser

# Set working directory
WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Copy application code
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser pyproject.toml ./

# Make sure scripts in .venv are usable
ENV PATH="/app/.venv/bin:$PATH"

# Create logs directory
RUN mkdir -p /app/logs && chown appuser:appuser /app/logs

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Set default environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
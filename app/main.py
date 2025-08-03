"""FastAPI application with S3 logging middleware."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.config.settings import settings
from app.middleware.s3_logging import create_s3_logging_middleware
from app.services.endpoint_matcher import EndpointMatcher
from app.services.s3_client import s3_service

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting FastAPI application")
    
    # Test S3 connection on startup
    try:
        async with s3_service as service:
            connection_ok = await service.test_connection()
            if connection_ok:
                logger.info("S3 connection test passed")
            else:
                logger.warning("S3 connection test failed - logging may not work")
    except Exception as e:
        logger.error(f"Failed to test S3 connection: {e}")
    
    yield
    
    logger.info("Shutting down FastAPI application")


# Create FastAPI app
app = FastAPI(
    title="Atlan Requests Middleware",
    description="Lightweight middleware for logging requests and responses to S3",
    version="0.1.0",
    lifespan=lifespan
)

# Add S3 logging middleware
app.add_middleware(create_s3_logging_middleware(enable_logging=settings.enable_middleware))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    matcher = EndpointMatcher()
    return {
        "status": "healthy", 
        "middleware_enabled": settings.enable_middleware,
        "logging_config": matcher.get_matching_info()
    }


@app.get("/health/s3")
async def s3_health_check():
    """S3 connection health check."""
    try:
        async with s3_service as service:
            connection_ok = await service.test_connection()
            if connection_ok:
                return {"status": "healthy", "s3_connection": "ok"}
            else:
                raise HTTPException(status_code=503, detail="S3 connection failed")
    except Exception as e:
        logger.error(f"S3 health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"S3 health check failed: {str(e)}")


@app.post("/api/example")
async def example_endpoint(request: Request, data: dict = None):
    """
    Example endpoint to test the middleware.
    
    This endpoint will be logged if x-request-id header is provided.
    """
    request_id = request.headers.get("x-request-id")
    
    return {
        "message": "Request processed successfully",
        "request_id": request_id,
        "received_data": data,
        "middleware_active": settings.enable_middleware
    }


@app.get("/api/example/{item_id}")
async def get_item(item_id: int, request: Request):
    """
    Example GET endpoint with path parameter.
    """
    request_id = request.headers.get("x-request-id")
    
    return {
        "item_id": item_id,
        "request_id": request_id,
        "status": "found"
    }


@app.post("/search/indexsearch")
async def index_search(request: Request, query: dict = None):
    """
    Example search endpoint that WILL be logged (configured endpoint + POST method).
    """
    request_id = request.headers.get("x-request-id")
    
    return {
        "message": "Search completed",
        "request_id": request_id,
        "query": query,
        "results": ["result1", "result2"],
        "logged_to_s3": True
    }


@app.post("/entity/lineage")
async def entity_lineage(request: Request, entity_data: dict = None):
    """
    Example lineage endpoint that WILL be logged (configured endpoint + POST method).
    """
    request_id = request.headers.get("x-request-id")
    
    return {
        "message": "Lineage retrieved",
        "request_id": request_id,
        "entity_data": entity_data,
        "lineage": {"upstream": [], "downstream": []},
        "logged_to_s3": True
    }


@app.get("/search/indexsearch")
async def index_search_get(request: Request):
    """
    Example search endpoint that will NOT be logged (GET method not configured).
    """
    request_id = request.headers.get("x-request-id")
    
    return {
        "message": "Search metadata",
        "request_id": request_id,
        "logged_to_s3": False,
        "reason": "GET method not configured for logging"
    }


@app.post("/other/endpoint")
async def other_endpoint(request: Request, data: dict = None):
    """
    Example endpoint that will NOT be logged (endpoint not configured).
    """
    request_id = request.headers.get("x-request-id")
    
    return {
        "message": "Other endpoint processed",
        "request_id": request_id,
        "data": data,
        "logged_to_s3": False,
        "reason": "Endpoint not configured for logging"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower()
    )
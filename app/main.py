"""Main FastAPI application."""

import logging
import uuid
from datetime import datetime
from typing import Dict

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config.settings import settings
from app.models.schemas import HealthResponse, ErrorResponse, LogEntry, RequestData, ResponseData
from app.services.s3_client import s3_service

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format=settings.log_format
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Lightweight FastAPI middleware for storing requests/responses in S3",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Middleware to log requests and responses to S3."""
    request_id = str(uuid.uuid4())
    start_time = datetime.utcnow()
    
    # Add request ID to request state
    request.state.request_id = request_id
    
    # Create request data
    request_data = RequestData(
        method=request.method,
        url=str(request.url),
        headers=dict(request.headers),
        query_params=dict(request.query_params),
        client_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    
    # Try to get request body if it's small enough
    if settings.enable_request_logging:
        try:
            body = await request.body()
            if len(body) <= settings.max_body_size:
                request_data.body = body.decode("utf-8", errors="ignore")
        except Exception as e:
            logger.warning(f"Failed to read request body: {e}")
    
    # Process the request
    response = await call_next(request)
    
    # Calculate processing time
    end_time = datetime.utcnow()
    processing_time_ms = (end_time - start_time).total_seconds() * 1000
    
    # Create response data
    response_data = ResponseData(
        status_code=response.status_code,
        headers=dict(response.headers),
        processing_time_ms=processing_time_ms,
    )
    
    # Create log entry
    log_entry = LogEntry(
        request_id=request_id,
        timestamp=start_time,
        request=request_data,
        response=response_data,
    )
    
    # Log to S3 asynchronously (don't block the response)
    if settings.enable_request_logging or settings.enable_response_logging:
        try:
            async with s3_service as s3:
                await s3.upload_log_entry(log_entry)
        except Exception as e:
            logger.error(f"Failed to log request to S3: {e}")
    
    # Add request ID to response headers
    response.headers["X-Request-ID"] = request_id
    
    return response


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    services = {}
    
    # Test S3 connection
    try:
        async with s3_service as s3:
            s3_status = await s3.test_connection()
        services["s3"] = "healthy" if s3_status else "unhealthy"
    except Exception as e:
        services["s3"] = f"error: {str(e)}"
        logger.error(f"S3 health check failed: {e}")
    
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        services=services,
    )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Atlan Requests Middleware API",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/ping")
async def ping():
    """Simple ping endpoint for testing."""
    return {"message": "pong", "timestamp": datetime.utcnow().isoformat()}


@app.post("/echo")
async def echo(request: Request):
    """Echo endpoint that returns the request data (useful for testing)."""
    try:
        body = await request.body()
        return {
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "query_params": dict(request.query_params),
            "body": body.decode("utf-8", errors="ignore") if body else None,
            "request_id": getattr(request.state, "request_id", None),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process request: {str(e)}")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    request_id = getattr(request.state, "request_id", None)
    
    logger.error(f"Unhandled exception for request {request_id}: {exc}", exc_info=True)
    
    error_response = ErrorResponse(
        error="Internal server error",
        detail=str(exc) if settings.debug else "An unexpected error occurred",
        request_id=request_id,
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response.model_dump(),
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
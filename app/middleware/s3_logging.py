"""FastAPI middleware for logging requests and responses to S3."""

import asyncio
import logging
import time
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import StreamingResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config.settings import settings
from app.services.data_processor import DataProcessor
from app.services.endpoint_matcher import EndpointMatcher
from app.services.s3_client import s3_service

logger = logging.getLogger(__name__)


class S3LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that logs requests and responses to S3."""
    
    def __init__(self, app, enable_logging: bool = True):
        """
        Initialize the middleware.
        
        Args:
            app: FastAPI application
            enable_logging: Whether to enable S3 logging
        """
        super().__init__(app)
        self.enable_logging = enable_logging and settings.enable_middleware
        self.data_processor = DataProcessor()
        self.endpoint_matcher = EndpointMatcher()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and response, logging to S3.
        
        Args:
            request: Incoming request
            call_next: Next middleware/route handler
            
        Returns:
            Response from downstream
        """
        # Skip logging if disabled
        if not self.enable_logging:
            return await call_next(request)
        
        # Check if this endpoint/method should be logged
        should_log = self.endpoint_matcher.should_log_request(
            request.method, str(request.url.path)
        )
        
        if not should_log:
            # Skip logging for this endpoint/method combination
            return await call_next(request)
        
        # Get request ID from headers (user provided)
        request_id = request.headers.get("x-request-id")
        if not request_id:
            logger.warning(
                f"No x-request-id header found for {request.method} {request.url.path}, "
                "skipping S3 logging"
            )
            return await call_next(request)
        
        # Record start time
        start_time = time.time()
        
        # Extract request data
        try:
            request_data = await self.data_processor.extract_request_data(request)
        except Exception as e:
            logger.error(f"Failed to extract request data: {e}")
            return await call_next(request)
        
        # Call downstream service
        response = await call_next(request)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Extract response data
        try:
            response_body = await self._extract_response_body(response)
            response_data = self.data_processor.extract_response_data(
                response, response_body, processing_time
            )
            
            # Create log entry
            log_entry = self.data_processor.create_log_entry(
                request_id, request_data, response_data
            )
            
            # Upload to S3 asynchronously (fire and forget)
            asyncio.create_task(self._upload_log_safely(log_entry))
            
        except Exception as e:
            logger.error(f"Failed to process response data: {e}")
        
        return response
    
    async def _extract_response_body(self, response: Response) -> bytes:
        """
        Extract response body without consuming it.
        
        Args:
            response: FastAPI response
            
        Returns:
            Response body as bytes
        """
        if isinstance(response, StreamingResponse):
            # Handle streaming responses
            response_body = b""
            body_chunks = []
            
            async for chunk in response.body_iterator:
                body_chunks.append(chunk)
                response_body += chunk
            
            # Recreate the response with the collected body
            response.body_iterator = self._create_iterator(body_chunks)
            return response_body
        else:
            # Handle regular responses
            if hasattr(response, 'body') and response.body:
                return response.body
            return b""
    
    def _create_iterator(self, chunks):
        """Create an async iterator from chunks."""
        async def generate():
            for chunk in chunks:
                yield chunk
        return generate()
    
    async def _upload_log_safely(self, log_entry):
        """
        Safely upload log entry to S3 with timeout and error handling.
        
        Args:
            log_entry: Log entry to upload
        """
        try:
            async with asyncio.timeout(settings.s3_upload_timeout):
                async with s3_service as service:
                    success = await service.upload_log_entry(log_entry)
                    if not success:
                        logger.warning(f"Failed to upload log entry for request {log_entry.request_id}")
        except asyncio.TimeoutError:
            logger.warning(f"S3 upload timeout for request {log_entry.request_id}")
        except Exception as e:
            logger.error(f"Unexpected error during S3 upload: {e}")


def create_s3_logging_middleware(enable_logging: bool = True) -> type:
    """
    Factory function to create S3 logging middleware.
    
    Args:
        enable_logging: Whether to enable S3 logging
        
    Returns:
        Configured middleware class
    """
    class ConfiguredS3LoggingMiddleware(S3LoggingMiddleware):
        def __init__(self, app):
            super().__init__(app, enable_logging=enable_logging)
    
    return ConfiguredS3LoggingMiddleware
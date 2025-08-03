"""Data processing utilities for request/response handling."""

import json
import time
from typing import Any, Dict, Optional

from fastapi import Request, Response

from app.config.settings import settings
from app.models.schemas import LogEntry, RequestData, ResponseData


class DataProcessor:
    """Processes request and response data for logging."""
    
    # Headers to filter out for security
    FILTERED_HEADERS = {"authorization", "cookie"}
    
    @staticmethod
    def filter_headers(headers: Dict[str, str]) -> Dict[str, str]:
        """
        Filter sensitive headers.
        
        Args:
            headers: Original headers dict
            
        Returns:
            Filtered headers dict
        """
        return {
            key: value for key, value in headers.items()
            if key.lower() not in DataProcessor.FILTERED_HEADERS
        }
    
    @staticmethod
    async def extract_request_data(request: Request) -> RequestData:
        """
        Extract data from FastAPI request.
        
        Args:
            request: FastAPI request object
            
        Returns:
            RequestData object
        """
        # Get client IP
        client_ip = None
        if hasattr(request, 'client') and request.client:
            client_ip = request.client.host
        
        # Extract headers (filtered)
        headers = DataProcessor.filter_headers(dict(request.headers))
        
        # Extract body (with size limit)
        body = None
        try:
            raw_body = await request.body()
            if raw_body and len(raw_body) <= settings.max_body_size:
                body = raw_body.decode('utf-8', errors='ignore')
        except Exception:
            body = "[Body could not be decoded]"
        
        return RequestData(
            method=request.method,
            path=str(request.url.path),
            query_params=dict(request.query_params),
            headers=headers,
            body=body,
            client_ip=client_ip
        )
    
    @staticmethod
    def extract_response_data(
        response: Response,
        response_body: bytes,
        processing_time: float
    ) -> ResponseData:
        """
        Extract data from FastAPI response.
        
        Args:
            response: FastAPI response object
            response_body: Response body bytes
            processing_time: Processing time in seconds
            
        Returns:
            ResponseData object
        """
        # Extract headers (filtered)
        headers = DataProcessor.filter_headers(dict(response.headers))
        
        # Extract body (with size limit)
        body = None
        if response_body and len(response_body) <= settings.max_body_size:
            try:
                body = response_body.decode('utf-8', errors='ignore')
            except Exception:
                body = "[Body could not be decoded]"
        
        return ResponseData(
            status_code=response.status_code,
            headers=headers,
            body=body,
            processing_time_ms=processing_time * 1000  # Convert to milliseconds
        )
    
    @staticmethod
    def create_log_entry(
        request_id: str,
        request_data: RequestData,
        response_data: ResponseData
    ) -> LogEntry:
        """
        Create a complete log entry.
        
        Args:
            request_id: Unique request identifier
            request_data: Request data
            response_data: Response data
            
        Returns:
            LogEntry object
        """
        return LogEntry(
            request_id=request_id,
            request=request_data,
            response=response_data
        )
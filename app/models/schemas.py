"""Pydantic models for request/response logging."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RequestData(BaseModel):
    """Model for HTTP request data."""
    
    method: str = Field(..., description="HTTP method")
    url: str = Field(..., description="Request URL")
    headers: Dict[str, str] = Field(default_factory=dict, description="Request headers")
    query_params: Dict[str, Any] = Field(default_factory=dict, description="Query parameters")
    path_params: Dict[str, Any] = Field(default_factory=dict, description="Path parameters")
    body: Optional[str] = Field(default=None, description="Request body")
    client_ip: Optional[str] = Field(default=None, description="Client IP address")
    user_agent: Optional[str] = Field(default=None, description="User agent")


class ResponseData(BaseModel):
    """Model for HTTP response data."""
    
    status_code: int = Field(..., description="HTTP status code")
    headers: Dict[str, str] = Field(default_factory=dict, description="Response headers")
    body: Optional[str] = Field(default=None, description="Response body")
    processing_time_ms: Optional[float] = Field(default=None, description="Request processing time in milliseconds")


class LogEntry(BaseModel):
    """Model for complete request/response log entry."""
    
    request_id: str = Field(..., description="Unique request identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Request timestamp")
    request: RequestData = Field(..., description="Request data")
    response: Optional[ResponseData] = Field(default=None, description="Response data")
    error: Optional[str] = Field(default=None, description="Error message if any")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: str = Field(..., description="Health status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")
    version: str = Field(..., description="Application version")
    services: Dict[str, str] = Field(default_factory=dict, description="Service status")


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Error details")
    request_id: Optional[str] = Field(default=None, description="Request ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
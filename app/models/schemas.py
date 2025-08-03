"""Pydantic models for request/response data structures."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class RequestData(BaseModel):
    """Model for HTTP request data."""
    
    method: str = Field(..., description="HTTP method")
    path: str = Field(..., description="Request path")
    query_params: Dict[str, Any] = Field(default_factory=dict, description="Query parameters")
    headers: Dict[str, str] = Field(default_factory=dict, description="Request headers")
    body: Optional[str] = Field(None, description="Request body (if any)")
    client_ip: Optional[str] = Field(None, description="Client IP address")


class ResponseData(BaseModel):
    """Model for HTTP response data."""
    
    status_code: int = Field(..., description="HTTP status code")
    headers: Dict[str, str] = Field(default_factory=dict, description="Response headers")
    body: Optional[str] = Field(None, description="Response body (if any)")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


class LogEntry(BaseModel):
    """Complete log entry for request/response pair."""
    
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="UTC timestamp")
    request_id: str = Field(..., description="Unique request identifier")
    request: RequestData = Field(..., description="Request data")
    response: ResponseData = Field(..., description="Response data")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z"
        }
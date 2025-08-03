"""Configuration settings for the FastAPI S3 middleware."""

from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # AWS Configuration
    aws_role_arn: str = Field(..., description="AWS Role ARN for S3 access")
    aws_region: str = Field(default="us-east-1", description="AWS region")
    
    # S3 Configuration
    s3_bucket_name: str = Field(..., description="S3 bucket name for storing logs")
    s3_key_prefix: str = Field(default="request-logs/", description="S3 key prefix")
    
    # Application Configuration
    log_level: str = Field(default="INFO", description="Application log level")
    max_body_size: int = Field(
        default=1048576, description="Maximum body size to log (1MB)"
    )
    enable_middleware: bool = Field(
        default=True, description="Enable/disable S3 logging middleware"
    )
    
    # Request timeout for S3 uploads
    s3_upload_timeout: int = Field(
        default=30, description="S3 upload timeout in seconds"
    )
    
    # Selective logging configuration
    log_endpoints: List[str] = Field(
        default=["/search/indexsearch", "/entity/lineage"],
        description="List of endpoint patterns to log"
    )
    log_methods: List[str] = Field(
        default=["POST"], 
        description="List of HTTP methods to log"
    )
    endpoint_match_type: str = Field(
        default="exact",
        description="Endpoint matching type: 'exact', 'prefix', or 'regex'"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
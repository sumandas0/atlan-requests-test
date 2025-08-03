"""Application settings and configuration."""

import os
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application settings
    app_name: str = Field(default="Atlan Requests Middleware", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    
    # AWS Settings
    aws_region: str = Field(default="us-east-1", description="AWS region")
    aws_role_arn: Optional[str] = Field(default=None, description="AWS IAM role ARN to assume")
    
    # S3 Settings
    s3_bucket_name: str = Field(..., description="S3 bucket name for storing logs")
    s3_key_prefix: str = Field(default="request-logs/", description="S3 key prefix")
    
    # Logging Settings
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )
    
    # Middleware Settings
    enable_request_logging: bool = Field(default=True, description="Enable request logging")
    enable_response_logging: bool = Field(default=True, description="Enable response logging")
    max_body_size: int = Field(default=1024 * 1024, description="Maximum body size to log (bytes)")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
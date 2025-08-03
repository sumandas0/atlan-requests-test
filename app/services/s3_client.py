"""Async S3 client service for uploading request/response logs."""

import json
import logging
from datetime import datetime
from typing import Optional

import aioboto3
from botocore.exceptions import ClientError, NoCredentialsError

from app.config.settings import settings
from app.models.schemas import LogEntry

logger = logging.getLogger(__name__)


class S3LoggingService:
    """Service for uploading request/response logs to S3."""
    
    def __init__(self):
        self.session = aioboto3.Session()
        self._s3_client: Optional[object] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._get_s3_client()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._s3_client:
            await self._s3_client.__aexit__(exc_type, exc_val, exc_tb)
    
    async def _get_s3_client(self):
        """Get or create async S3 client with role assumption."""
        if not self._s3_client:
            try:
                # Create STS client to assume role
                sts_client = self.session.client('sts', region_name=settings.aws_region)
                
                async with sts_client as sts:
                    # Assume the specified role
                    response = await sts.assume_role(
                        RoleArn=settings.aws_role_arn,
                        RoleSessionName=f"s3-logging-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
                    )
                    
                    credentials = response['Credentials']
                    
                    # Create S3 client with assumed role credentials
                    self._s3_client = self.session.client(
                        's3',
                        region_name=settings.aws_region,
                        aws_access_key_id=credentials['AccessKeyId'],
                        aws_secret_access_key=credentials['SecretAccessKey'],
                        aws_session_token=credentials['SessionToken']
                    )
                    
                logger.info("Successfully assumed AWS role and created S3 client")
                
            except (ClientError, NoCredentialsError) as e:
                logger.error(f"Failed to create S3 client: {e}")
                raise
    
    async def upload_log_entry(self, log_entry: LogEntry) -> bool:
        """
        Upload a log entry to S3.
        
        Args:
            log_entry: The log entry to upload
            
        Returns:
            True if upload succeeded, False otherwise
        """
        try:
            # Generate S3 key with date-only pattern (no nested folders)
            date_only = log_entry.timestamp.strftime('%Y-%m-%d')
            s3_key = f"{settings.s3_key_prefix}{date_only}/{log_entry.request_id}.json"
            
            # Convert to JSON
            log_data = log_entry.model_dump_json(indent=2)
            
            # Upload to S3
            async with self._s3_client as s3:
                await s3.put_object(
                    Bucket=settings.s3_bucket_name,
                    Key=s3_key,
                    Body=log_data,
                    ContentType='application/json',
                    ServerSideEncryption='AES256'
                )
            
            logger.debug(f"Successfully uploaded log entry to s3://{settings.s3_bucket_name}/{s3_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload log entry to S3: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """
        Test S3 connection by listing bucket.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            async with self._s3_client as s3:
                await s3.head_bucket(Bucket=settings.s3_bucket_name)
            logger.info("S3 connection test successful")
            return True
        except Exception as e:
            logger.error(f"S3 connection test failed: {e}")
            return False


# Global S3 service instance
s3_service = S3LoggingService()
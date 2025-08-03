"""Tests for S3 client service."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from botocore.exceptions import ClientError

from app.models.schemas import LogEntry, RequestData, ResponseData
from app.services.s3_client import S3LoggingService


@pytest.fixture
def sample_log_entry():
    """Create sample log entry for testing."""
    request_data = RequestData(
        method="POST",
        path="/api/test",
        query_params={"param": "value"},
        headers={"content-type": "application/json"},
        body='{"test": "data"}',
        client_ip="127.0.0.1"
    )
    
    response_data = ResponseData(
        status_code=200,
        headers={"content-type": "application/json"},
        body='{"result": "success"}',
        processing_time_ms=150.5
    )
    
    return LogEntry(
        request_id="test-123",
        request=request_data,
        response=response_data
    )


@pytest.mark.asyncio
@patch('app.services.s3_client.aioboto3')
async def test_s3_service_upload_success(mock_aioboto3, sample_log_entry):
    """Test successful S3 upload."""
    # Mock session and clients
    mock_session = MagicMock()
    mock_sts_client = AsyncMock()
    mock_s3_client = AsyncMock()
    
    mock_aioboto3.Session.return_value = mock_session
    mock_session.client.side_effect = [mock_sts_client, mock_s3_client]
    
    # Mock STS assume role response
    mock_sts_client.__aenter__.return_value = mock_sts_client
    mock_sts_client.assume_role.return_value = {
        'Credentials': {
            'AccessKeyId': 'test-key',
            'SecretAccessKey': 'test-secret',
            'SessionToken': 'test-token'
        }
    }
    
    # Mock S3 put_object
    mock_s3_client.__aenter__.return_value = mock_s3_client
    mock_s3_client.put_object.return_value = None
    
    # Test upload
    service = S3LoggingService()
    async with service:
        result = await service.upload_log_entry(sample_log_entry)
    
    assert result is True
    mock_s3_client.put_object.assert_called_once()


@pytest.mark.asyncio
@patch('app.services.s3_client.aioboto3')
async def test_s3_service_upload_failure(mock_aioboto3, sample_log_entry):
    """Test S3 upload failure."""
    # Mock session and clients
    mock_session = MagicMock()
    mock_sts_client = AsyncMock()
    mock_s3_client = AsyncMock()
    
    mock_aioboto3.Session.return_value = mock_session
    mock_session.client.side_effect = [mock_sts_client, mock_s3_client]
    
    # Mock STS assume role response
    mock_sts_client.__aenter__.return_value = mock_sts_client
    mock_sts_client.assume_role.return_value = {
        'Credentials': {
            'AccessKeyId': 'test-key',
            'SecretAccessKey': 'test-secret',
            'SessionToken': 'test-token'
        }
    }
    
    # Mock S3 put_object failure
    mock_s3_client.__aenter__.return_value = mock_s3_client
    mock_s3_client.put_object.side_effect = ClientError(
        {'Error': {'Code': 'AccessDenied', 'Message': 'Access denied'}},
        'PutObject'
    )
    
    # Test upload
    service = S3LoggingService()
    async with service:
        result = await service.upload_log_entry(sample_log_entry)
    
    assert result is False


@pytest.mark.asyncio
@patch('app.services.s3_client.aioboto3')
async def test_s3_service_connection_test(mock_aioboto3):
    """Test S3 connection test."""
    # Mock session and clients
    mock_session = MagicMock()
    mock_sts_client = AsyncMock()
    mock_s3_client = AsyncMock()
    
    mock_aioboto3.Session.return_value = mock_session
    mock_session.client.side_effect = [mock_sts_client, mock_s3_client]
    
    # Mock STS assume role response
    mock_sts_client.__aenter__.return_value = mock_sts_client
    mock_sts_client.assume_role.return_value = {
        'Credentials': {
            'AccessKeyId': 'test-key',
            'SecretAccessKey': 'test-secret',
            'SessionToken': 'test-token'
        }
    }
    
    # Mock S3 head_bucket
    mock_s3_client.__aenter__.return_value = mock_s3_client
    mock_s3_client.head_bucket.return_value = None
    
    # Test connection
    service = S3LoggingService()
    async with service:
        result = await service.test_connection()
    
    assert result is True
    mock_s3_client.head_bucket.assert_called_once()
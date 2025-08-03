"""Tests for S3 logging middleware."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.main import app
from app.middleware.s3_logging import S3LoggingMiddleware


@pytest.fixture
def test_app():
    """Create test FastAPI app."""
    test_app = FastAPI()
    
    @test_app.get("/test")
    async def test_endpoint():
        return {"message": "test"}
    
    return test_app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "middleware_enabled" in data


def test_example_endpoint_without_request_id(client):
    """Test example endpoint without request ID header."""
    response = client.post("/api/example", json={"test": "data"})
    assert response.status_code == 200
    data = response.json()
    assert data["request_id"] is None


def test_example_endpoint_with_request_id(client):
    """Test example endpoint with request ID header."""
    request_id = "test-request-123"
    headers = {"x-request-id": request_id}
    response = client.post("/api/example", json={"test": "data"}, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["request_id"] == request_id


def test_get_item_endpoint(client):
    """Test GET endpoint with path parameter."""
    request_id = "test-get-456"
    headers = {"x-request-id": request_id}
    response = client.get("/api/example/123", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["item_id"] == 123
    assert data["request_id"] == request_id


@pytest.mark.asyncio
async def test_middleware_with_disabled_logging(test_app):
    """Test middleware behavior when logging is disabled."""
    # Add middleware with logging disabled
    test_app.add_middleware(S3LoggingMiddleware, enable_logging=False)
    
    with TestClient(test_app) as client:
        response = client.get("/test")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_middleware_without_request_id(test_app):
    """Test middleware behavior without request ID."""
    test_app.add_middleware(S3LoggingMiddleware, enable_logging=True)
    
    with TestClient(test_app) as client:
        response = client.get("/test")
        assert response.status_code == 200


@pytest.mark.asyncio
@patch('app.middleware.s3_logging.s3_service')
async def test_middleware_with_request_id(mock_s3_service, test_app):
    """Test middleware behavior with request ID."""
    # Mock S3 service
    mock_s3_service.__aenter__ = AsyncMock(return_value=mock_s3_service)
    mock_s3_service.__aexit__ = AsyncMock(return_value=None)
    mock_s3_service.upload_log_entry = AsyncMock(return_value=True)
    
    test_app.add_middleware(S3LoggingMiddleware, enable_logging=True)
    
    with TestClient(test_app) as client:
        headers = {"x-request-id": "test-123"}
        response = client.get("/test", headers=headers)
        assert response.status_code == 200
"""Tests for the main FastAPI application."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["message"] == "Atlan Requests Middleware API"


def test_ping_endpoint():
    """Test the ping endpoint."""
    response = client.get("/ping")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "pong"
    assert "timestamp" in data


def test_echo_endpoint():
    """Test the echo endpoint."""
    test_data = {"test": "data", "number": 123}
    response = client.post("/echo", json=test_data)
    assert response.status_code == 200
    data = response.json()
    assert data["method"] == "POST"
    assert "/echo" in data["url"]
    assert "headers" in data
    assert "body" in data


def test_health_endpoint():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "services" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_request_id_header():
    """Test that request ID is added to response headers."""
    response = client.get("/ping")
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) > 0
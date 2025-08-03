#!/usr/bin/env python3
"""
Example usage of the Atlan Requests Middleware.

This script demonstrates how to use the middleware and test it.
"""

import asyncio
import json
from datetime import datetime

import httpx


async def test_middleware():
    """Test the middleware with sample requests."""
    base_url = "http://localhost:8000"
    
    print("🚀 Testing Atlan Requests Middleware")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        # Test 1: Health check
        print("\n1. Testing health endpoints...")
        health_response = await client.get(f"{base_url}/health")
        print(f"   Health check: {health_response.status_code}")
        print(f"   Response: {health_response.json()}")
        
        # Test 2: Request without x-request-id (should NOT be logged)
        print("\n2. Testing request without x-request-id (NOT logged)...")
        response = await client.post(
            f"{base_url}/api/example",
            json={"message": "This won't be logged", "timestamp": datetime.now().isoformat()}
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        # Test 3: Request with x-request-id (WILL be logged)
        print("\n3. Testing request with x-request-id (WILL be logged)...")
        request_id = f"example-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        headers = {"x-request-id": request_id}
        response = await client.post(
            f"{base_url}/api/example",
            json={
                "message": "This will be logged to S3",
                "timestamp": datetime.now().isoformat(),
                "data": {"user_id": 123, "action": "test"}
            },
            headers=headers
        )
        print(f"   Status: {response.status_code}")
        print(f"   Request ID: {request_id}")
        print(f"   Response: {response.json()}")
        
        # Test 4: GET request with path parameter
        print("\n4. Testing GET request with path parameter...")
        request_id = f"get-example-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        headers = {"x-request-id": request_id}
        response = await client.get(
            f"{base_url}/api/example/456",
            headers=headers
        )
        print(f"   Status: {response.status_code}")
        print(f"   Request ID: {request_id}")
        print(f"   Response: {response.json()}")
        
        # Test 5: Request with sensitive headers (should be filtered)
        print("\n5. Testing request with sensitive headers (filtered)...")
        request_id = f"sensitive-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        headers = {
            "x-request-id": request_id,
            "authorization": "Bearer secret-token-123",
            "cookie": "session=abc123; user=john",
            "user-agent": "test-client/1.0"
        }
        response = await client.post(
            f"{base_url}/api/example",
            json={"message": "Testing header filtering"},
            headers=headers
        )
        print(f"   Status: {response.status_code}")
        print(f"   Request ID: {request_id}")
        print(f"   Response: {response.json()}")
        print("   Note: Authorization and Cookie headers will be filtered in S3 logs")
    
    print("\n" + "=" * 50)
    print("✅ Testing completed!")
    print("\nTo verify S3 logging:")
    print("1. Check your S3 bucket for log files")
    print("2. Look for files in: request-logs/YYYY/MM/DD/HH/{request-id}.json")
    print("3. Only requests with x-request-id headers will be logged")


async def check_s3_connection():
    """Check S3 connection health."""
    base_url = "http://localhost:8000"
    
    print("🔍 Checking S3 connection...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{base_url}/health/s3")
            if response.status_code == 200:
                print("✅ S3 connection is healthy")
                print(f"   Response: {response.json()}")
            else:
                print("❌ S3 connection failed")
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"❌ Failed to check S3 connection: {e}")


if __name__ == "__main__":
    print("Atlan Requests Middleware - Example Usage")
    print("Make sure the FastAPI server is running on http://localhost:8000")
    print("Start it with: uv run uvicorn app.main:app --reload")
    print()
    
    # Check S3 connection first
    asyncio.run(check_s3_connection())
    
    print()
    input("Press Enter to continue with testing...")
    
    # Run middleware tests
    asyncio.run(test_middleware())
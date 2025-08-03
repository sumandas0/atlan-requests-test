#!/usr/bin/env python3
"""
Example usage demonstrating selective logging functionality.

This script shows how different endpoints and methods are handled
based on the configuration.
"""

import asyncio
import json
from datetime import datetime

import httpx


async def test_selective_logging():
    """Test selective logging with different endpoints and methods."""
    base_url = "http://localhost:8000"
    
    print("🎯 Testing Selective Logging Configuration")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        # Test 1: Check current logging configuration
        print("\n1. Checking logging configuration...")
        health_response = await client.get(f"{base_url}/health")
        config = health_response.json()
        print(f"   Status: {config['status']}")
        print(f"   Middleware enabled: {config['middleware_enabled']}")
        print(f"   Logging config: {json.dumps(config['logging_config'], indent=6)}")
        
        # Test 2: POST to configured endpoint (WILL be logged)
        print("\n2. Testing POST /search/indexsearch (WILL be logged)...")
        request_id = f"search-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        headers = {"x-request-id": request_id}
        response = await client.post(
            f"{base_url}/search/indexsearch",
            json={"query": "test search", "filters": {"type": "document"}},
            headers=headers
        )
        print(f"   Status: {response.status_code}")
        print(f"   Request ID: {request_id}")
        print(f"   Response: {response.json()}")
        
        # Test 3: POST to configured endpoint (WILL be logged)
        print("\n3. Testing POST /entity/lineage (WILL be logged)...")
        request_id = f"lineage-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        headers = {"x-request-id": request_id}
        response = await client.post(
            f"{base_url}/entity/lineage",
            json={"entity_id": "table_123", "depth": 2},
            headers=headers
        )
        print(f"   Status: {response.status_code}")
        print(f"   Request ID: {request_id}")
        print(f"   Response: {response.json()}")
        
        # Test 4: GET to configured endpoint (will NOT be logged - wrong method)
        print("\n4. Testing GET /search/indexsearch (NOT logged - wrong method)...")
        request_id = f"search-get-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        headers = {"x-request-id": request_id}
        response = await client.get(
            f"{base_url}/search/indexsearch",
            headers=headers
        )
        print(f"   Status: {response.status_code}")
        print(f"   Request ID: {request_id}")
        print(f"   Response: {response.json()}")
        
        # Test 5: POST to non-configured endpoint (will NOT be logged - wrong endpoint)
        print("\n5. Testing POST /other/endpoint (NOT logged - wrong endpoint)...")
        request_id = f"other-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        headers = {"x-request-id": request_id}
        response = await client.post(
            f"{base_url}/other/endpoint",
            json={"test": "data"},
            headers=headers
        )
        print(f"   Status: {response.status_code}")
        print(f"   Request ID: {request_id}")
        print(f"   Response: {response.json()}")
        
        # Test 6: POST to original example endpoint (will NOT be logged - wrong endpoint)
        print("\n6. Testing POST /api/example (NOT logged - wrong endpoint)...")
        request_id = f"example-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        headers = {"x-request-id": request_id}
        response = await client.post(
            f"{base_url}/api/example",
            json={"message": "This won't be logged"},
            headers=headers
        )
        print(f"   Status: {response.status_code}")
        print(f"   Request ID: {request_id}")
        print(f"   Response: {response.json()}")
        
        # Test 7: Request without x-request-id to configured endpoint
        print("\n7. Testing POST /search/indexsearch without x-request-id...")
        response = await client.post(
            f"{base_url}/search/indexsearch",
            json={"query": "test without request id"}
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        print("   Note: Even for configured endpoints, x-request-id header is required")
    
    print("\n" + "=" * 60)
    print("✅ Selective logging testing completed!")
    print("\n🔍 Summary:")
    print("- Requests LOGGED to S3:")
    print("  ✓ POST /search/indexsearch (with x-request-id)")
    print("  ✓ POST /entity/lineage (with x-request-id)")
    print("\n- Requests NOT logged:")
    print("  ✗ GET /search/indexsearch (wrong method)")
    print("  ✗ POST /other/endpoint (wrong endpoint)")
    print("  ✗ POST /api/example (wrong endpoint)")
    print("  ✗ Any request without x-request-id header")
    print("\n📝 Check your S3 bucket for log files only from the logged requests!")


async def demonstrate_configuration_options():
    """Demonstrate different configuration options."""
    print("\n🔧 Configuration Options Demo")
    print("=" * 40)
    
    print("\n1. Current Configuration (from defaults):")
    print("   LOG_ENDPOINTS=['/search/indexsearch', '/entity/lineage']")
    print("   LOG_METHODS=['POST']")
    print("   ENDPOINT_MATCH_TYPE='exact'")
    
    print("\n2. Alternative Configurations:")
    print("\n   a) Prefix matching:")
    print("      LOG_ENDPOINTS=['/api/', '/search/']")
    print("      ENDPOINT_MATCH_TYPE='prefix'")
    print("      → Logs any endpoint starting with /api/ or /search/")
    
    print("\n   b) Multiple methods:")
    print("      LOG_METHODS=['POST', 'PUT', 'PATCH']")
    print("      → Logs POST, PUT, and PATCH requests")
    
    print("\n   c) Regex matching:")
    print("      LOG_ENDPOINTS=['/search/.*', '/entity/(lineage|metadata)']")
    print("      ENDPOINT_MATCH_TYPE='regex'")
    print("      → Uses regex patterns for flexible matching")
    
    print("\n   d) Log everything:")
    print("      LOG_ENDPOINTS=['.*']")
    print("      LOG_METHODS=['GET', 'POST', 'PUT', 'PATCH', 'DELETE']")
    print("      ENDPOINT_MATCH_TYPE='regex'")
    print("      → Logs all requests (not recommended for production)")


if __name__ == "__main__":
    print("Atlan Requests Middleware - Selective Logging Demo")
    print("Make sure the FastAPI server is running on http://localhost:8000")
    print("Start it with: uv run uvicorn app.main:app --reload")
    print()
    
    asyncio.run(demonstrate_configuration_options())
    
    print()
    input("Press Enter to start testing...")
    
    # Run selective logging tests
    asyncio.run(test_selective_logging())
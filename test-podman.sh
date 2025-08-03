#!/bin/bash

# Quick Podman test script for Atlan Requests Middleware

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_info "🐳 Testing Atlan Requests Middleware with Podman"
echo "================================================="

# Build the image
log_info "Building container image..."
podman build -t atlan-requests-middleware:test .

# Run the container
log_info "Starting container..."
CONTAINER_ID=$(podman run -d -p 8001:8000 \
  -e AWS_ROLE_ARN="arn:aws:iam::123456789012:role/test-role" \
  -e S3_BUCKET_NAME="test-bucket" \
  --name atlan-test \
  atlan-requests-middleware:test)

log_info "Container started with ID: ${CONTAINER_ID:0:12}"

# Wait for startup
log_info "Waiting for application to start..."
sleep 8

# Test health endpoint
log_info "Testing health endpoint..."
if curl -s http://localhost:8001/health > /dev/null; then
    log_success "Health endpoint responding"
    curl -s http://localhost:8001/health | jq .
else
    echo "❌ Health endpoint not responding"
    podman logs atlan-test
    exit 1
fi

# Test configured endpoint
log_info "Testing configured search endpoint..."
RESPONSE=$(curl -s -X POST http://localhost:8001/search/indexsearch \
  -H "x-request-id: podman-test-$(date +%s)" \
  -H "Content-Type: application/json" \
  -d '{"query": "podman test"}')

echo "$RESPONSE" | jq .

if echo "$RESPONSE" | jq -r '.logged_to_s3' | grep -q "true"; then
    log_success "Selective logging working correctly"
else
    echo "❌ Selective logging not working"
    exit 1
fi

# Test non-configured endpoint
log_info "Testing non-configured endpoint..."
RESPONSE=$(curl -s -X POST http://localhost:8001/other/endpoint \
  -H "x-request-id: podman-test-$(date +%s)" \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}')

if echo "$RESPONSE" | jq -r '.logged_to_s3' | grep -q "false"; then
    log_success "Non-configured endpoint correctly not logged"
else
    echo "❌ Non-configured endpoint logging behavior incorrect"
    exit 1
fi

# Cleanup
log_info "Cleaning up..."
podman stop atlan-test
podman rm atlan-test
podman rmi atlan-requests-middleware:test

echo ""
log_success "🎉 All Podman tests passed!"
echo ""
log_info "Your FastAPI middleware is ready for production deployment!"
echo "Next steps:"
echo "1. Configure your AWS credentials and S3 bucket"
echo "2. Update k8s/secret.yaml with your actual values"
echo "3. Deploy to Kubernetes with: ./deploy.sh --build --engine podman"
# Atlan Requests Middleware

A lightweight FastAPI middleware that intercepts HTTP requests, calls downstream services, and stores request/response data in S3 using AWS Role ARN authentication.

## Features

- 🚀 **FastAPI Integration**: Seamless middleware for FastAPI applications
- 🔒 **Secure S3 Storage**: AWS Role ARN authentication for S3 access
- 🔄 **Async Operations**: Non-blocking S3 uploads for optimal performance
- 🛡️ **Security Focused**: Filters sensitive headers (Authorization, Cookie)
- 📊 **Structured Logging**: JSON format with timestamps and request tracing
- ⚡ **Lightweight**: Minimal overhead on request processing
- 🎯 **Selective Logging**: Configurable endpoint and method filtering
- 🔧 **Flexible Matching**: Exact, prefix, or regex endpoint matching

## Quick Start

### Prerequisites

- Python 3.11+
- uv package manager
- AWS account with S3 bucket and IAM role

### Installation

1. Clone and install dependencies:
```bash
cd atlan-requests-test
uv sync
```

2. Set up environment variables:
```bash
# Copy example and edit
cp .env.example .env

# Required variables:
AWS_ROLE_ARN=arn:aws:iam::123456789012:role/YourS3AccessRole
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-request-logs-bucket
```

3. Run the application:
```bash
uv run uvicorn app.main:app --reload
```

## Usage

### Selective Request Logging

The middleware only logs requests that match configured endpoints and HTTP methods. By default, it logs POST requests to `/search/indexsearch` and `/entity/lineage`:

```bash
# ✅ Request WILL be logged (configured endpoint + method + x-request-id header)
curl -X POST http://localhost:8000/search/indexsearch \
  -H "x-request-id: search-123" \
  -H "Content-Type: application/json" \
  -d '{"query": "test search"}'

# ✅ Request WILL be logged (configured endpoint + method + x-request-id header)
curl -X POST http://localhost:8000/entity/lineage \
  -H "x-request-id: lineage-456" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "table_123"}'

# ❌ Request will NOT be logged (wrong method - GET instead of POST)
curl -X GET http://localhost:8000/search/indexsearch \
  -H "x-request-id: search-get-789"

# ❌ Request will NOT be logged (endpoint not configured)
curl -X POST http://localhost:8000/api/example \
  -H "x-request-id: example-999" \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'

# ❌ Request will NOT be logged (no x-request-id header)
curl -X POST http://localhost:8000/search/indexsearch \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'
```

### Health Checks

```bash
# Application health
curl http://localhost:8000/health

# S3 connection health
curl http://localhost:8000/health/s3
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AWS_ROLE_ARN` | AWS Role ARN for S3 access | **Required** |
| `AWS_REGION` | AWS region | `us-east-1` |
| `S3_BUCKET_NAME` | S3 bucket for logs | **Required** |
| `S3_KEY_PREFIX` | S3 key prefix | `request-logs/` |
| `LOG_LEVEL` | Application log level | `INFO` |
| `MAX_BODY_SIZE` | Max body size to log (bytes) | `1048576` (1MB) |
| `ENABLE_MIDDLEWARE` | Enable/disable middleware | `true` |
| `S3_UPLOAD_TIMEOUT` | S3 upload timeout (seconds) | `30` |
| `LOG_ENDPOINTS` | Endpoints to log (JSON array) | `["/search/indexsearch", "/entity/lineage"]` |
| `LOG_METHODS` | HTTP methods to log (JSON array) | `["POST"]` |
| `ENDPOINT_MATCH_TYPE` | Matching type: exact/prefix/regex | `exact` |

### S3 Key Structure

Logs are stored with the following S3 key pattern:
```
{S3_KEY_PREFIX}{YYYY}/{MM}/{DD}/{HH}/{request-id}.json
```

Example: `request-logs/2024/01/15/14/my-unique-id-123.json`

## Data Format

### Log Entry Structure

```json
{
  "timestamp": "2024-01-15T14:30:45Z",
  "request_id": "my-unique-id-123",
  "request": {
    "method": "POST",
    "path": "/api/example",
    "query_params": {"param": "value"},
    "headers": {
      "content-type": "application/json",
      "user-agent": "curl/7.68.0"
    },
    "body": "{\"test\": \"data\"}",
    "client_ip": "127.0.0.1"
  },
  "response": {
    "status_code": 200,
    "headers": {
      "content-type": "application/json"
    },
    "body": "{\"message\": \"success\"}",
    "processing_time_ms": 150.5
  }
}
```

### Security Features

- **Header Filtering**: `Authorization` and `Cookie` headers are automatically filtered
- **Body Size Limits**: Request/response bodies are limited to prevent large uploads
- **Role-based Access**: Uses AWS IAM roles for secure S3 access

## AWS Setup

### Required IAM Role Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl"
      ],
      "Resource": "arn:aws:s3:::your-bucket-name/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:HeadBucket"
      ],
      "Resource": "arn:aws:s3:::your-bucket-name"
    }
  ]
}
```

### Trust Relationship

Ensure your role has the appropriate trust relationship for your execution environment (EC2, ECS, Lambda, etc.).

## Testing

Run tests:
```bash
uv run pytest tests/ -v
```

Run with coverage:
```bash
uv run pytest tests/ --cov=app --cov-report=html
```

### Selective Logging Configuration

You can configure which endpoints and methods to log:

```bash
# Log specific endpoints with exact matching (default)
export LOG_ENDPOINTS='["/search/indexsearch", "/entity/lineage"]'
export LOG_METHODS='["POST"]'
export ENDPOINT_MATCH_TYPE='exact'

# Log all endpoints starting with /api/ or /search/ (prefix matching)
export LOG_ENDPOINTS='["/api/", "/search/"]'
export ENDPOINT_MATCH_TYPE='prefix'

# Log multiple HTTP methods
export LOG_METHODS='["POST", "PUT", "PATCH"]'

# Use regex patterns for complex matching
export LOG_ENDPOINTS='["/search/.*", "/entity/(lineage|metadata)"]'
export ENDPOINT_MATCH_TYPE='regex'
```

### Configuration Examples

1. **Log only search operations:**
```bash
LOG_ENDPOINTS='["/search/indexsearch", "/search/query"]'
LOG_METHODS='["POST"]'
ENDPOINT_MATCH_TYPE='exact'
```

2. **Log all API endpoints:**
```bash
LOG_ENDPOINTS='["/api/"]'
LOG_METHODS='["POST", "PUT", "PATCH", "DELETE"]'
ENDPOINT_MATCH_TYPE='prefix'
```

3. **Complex regex patterns:**
```bash
LOG_ENDPOINTS='["^/search/.*", "^/entity/(lineage|metadata|bulk)$"]'
LOG_METHODS='["POST"]'
ENDPOINT_MATCH_TYPE='regex'
```

## Docker Deployment

### Using Pre-built Images (Recommended)

**Pull from GitHub Container Registry:**
```bash
# Pull the latest version
docker pull ghcr.io/your-org/atlan-requests-test:latest
# OR with podman
podman pull ghcr.io/your-org/atlan-requests-test:latest

# Run directly
docker run -p 8000:8000 \
  -e AWS_ROLE_ARN="arn:aws:iam::123456789012:role/YourS3AccessRole" \
  -e S3_BUCKET_NAME="your-request-logs-bucket" \
  ghcr.io/your-org/atlan-requests-test:latest
```

**Available Tags:**
- `latest` - Latest stable release
- `main` - Latest from main branch
- `v1.0.0` - Specific version tags
- `main-abc1234` - Commit-specific builds

### Building the Container Image (Development)

**Using Docker:**
```bash
# Build the image
docker build -t atlan-requests-middleware:latest .

# Run locally for testing
docker run -p 8000:8000 \
  -e AWS_ROLE_ARN="arn:aws:iam::123456789012:role/YourS3AccessRole" \
  -e S3_BUCKET_NAME="your-request-logs-bucket" \
  atlan-requests-middleware:latest
```

**Using Podman:**
```bash
# Build the image
podman build -t atlan-requests-middleware:latest .

# Run locally for testing
podman run -p 8000:8000 \
  -e AWS_ROLE_ARN="arn:aws:iam::123456789012:role/YourS3AccessRole" \
  -e S3_BUCKET_NAME="your-request-logs-bucket" \
  atlan-requests-middleware:latest
```

### Multi-Architecture Build

**Using Docker:**
```bash
# Build for multiple architectures
docker buildx build --platform linux/amd64,linux/arm64 \
  -t atlan-requests-middleware:latest .
```

**Using Podman:**
```bash
# Build for multiple architectures
podman build --platform linux/amd64,linux/arm64 \
  -t atlan-requests-middleware:latest .
```

## Kubernetes Deployment

### Quick Deployment

**Option 1: Using Pre-built Images (Recommended)**
```bash
# Deploy from GitHub Container Registry
./deploy-from-ghcr.sh --tag latest

# Or with specific version
./deploy-from-ghcr.sh --tag v1.0.0
```

**Option 2: Build and Deploy**
```bash
# Build and deploy locally
./deploy.sh --build --tag latest

# Or deploy manually with kubectl
kubectl apply -k k8s/
```

### Prerequisites

1. **Kubernetes cluster** (v1.19+)
2. **AWS IAM role** with S3 permissions
3. **Ingress controller** (nginx recommended)
4. **Metrics server** (for auto-scaling)

### Configuration Steps

1. **Update Secret Values** in `k8s/secret.yaml`:
```bash
# Encode your AWS Role ARN
echo -n "arn:aws:iam::YOUR_ACCOUNT:role/YOUR_ROLE" | base64

# Encode your S3 bucket name  
echo -n "your-s3-bucket-name" | base64
```

2. **Update Ingress Domain** in `k8s/ingress.yaml`:
```yaml
rules:
- host: atlan-middleware.yourdomain.com  # Replace with your domain
```

3. **Deploy the Application**:
```bash
# Build and deploy with script
./deploy.sh --build --tag v1.0.0

# Or deploy manually
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/serviceaccount.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml
```

### Deployment Features

- **High Availability**: 3 replicas with anti-affinity
- **Auto-scaling**: HPA based on CPU/memory usage (2-10 replicas)
- **Security**: Non-root containers, network policies, RBAC
- **Monitoring**: Health checks, readiness/liveness probes
- **AWS Integration**: IRSA (IAM Roles for Service Accounts)

### Monitoring & Troubleshooting

```bash
# Check deployment status
kubectl get all -n atlan-middleware

# View logs
kubectl logs -f deployment/atlan-middleware -n atlan-middleware

# Test health endpoint
kubectl port-forward svc/atlan-middleware-service 8080:80 -n atlan-middleware
curl http://localhost:8080/health

# Check auto-scaling
kubectl get hpa -n atlan-middleware
```

For detailed Kubernetes deployment instructions, see [k8s/README.md](k8s/README.md).

## CI/CD and Container Registry

### GitHub Container Registry (GHCR)

This project automatically builds and publishes container images to GitHub Container Registry:

- **Registry**: `ghcr.io/your-org/atlan-requests-test`
- **Auto-built on**: Push to main, tags, and PRs
- **Multi-architecture**: AMD64 and ARM64 support
- **Security scanning**: Trivy vulnerability scanning

### Available Images

```bash
# Latest stable release
ghcr.io/your-org/atlan-requests-test:latest

# Specific versions
ghcr.io/your-org/atlan-requests-test:v1.0.0

# Branch builds
ghcr.io/your-org/atlan-requests-test:main

# Commit-specific builds
ghcr.io/your-org/atlan-requests-test:main-abc1234
```

### GitHub Actions Workflows

- **🔨 Build & Publish** - Builds and publishes container images
- **✅ Test** - Runs unit tests, linting, and container tests
- **🔒 Security** - Trivy scanning and dependency review
- **📦 Dependabot** - Automated dependency updates

For detailed Kubernetes deployment instructions, see [k8s/README.md](k8s/README.md).

## Development

### Testing Selective Logging

Use the provided example script to test selective logging:

```bash
# Test selective logging functionality
uv run python example_selective_usage.py
```

### Code Quality

```bash
# Format code
uv run black app/ tests/

# Lint code
uv run ruff check app/ tests/

# Type checking (if using mypy)
uv run mypy app/
```

### Project Structure

```
app/
├── main.py              # FastAPI application
├── middleware/
│   └── s3_logging.py    # S3 logging middleware
├── services/
│   ├── s3_client.py     # S3 operations
│   └── data_processor.py # Data processing
├── config/
│   └── settings.py      # Configuration
└── models/
    └── schemas.py       # Data models
```

## License

MIT License - see LICENSE file for details.
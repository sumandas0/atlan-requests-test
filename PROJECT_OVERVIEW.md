# Atlan Requests Middleware - Project Overview

## 🎯 Project Summary

A production-ready FastAPI middleware that selectively logs HTTP requests and responses to AWS S3, designed for high-throughput applications with configurable endpoint filtering.

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   HTTP Client   │───▶│  FastAPI App     │───▶│   Downstream    │
│                 │    │  + S3 Middleware │    │   Services      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   AWS S3        │
                       │   (Logs)        │
                       └─────────────────┘
```

## 🔧 Core Components

### 1. Selective Logging Middleware
- **Purpose**: Intercept and log specific HTTP requests/responses
- **Location**: `app/middleware/s3_logging.py`
- **Features**:
  - Configurable endpoint patterns (exact/prefix/regex)
  - HTTP method filtering
  - Request ID requirement
  - Async S3 uploads (non-blocking)

### 2. Endpoint Matcher
- **Purpose**: Determine which requests to log
- **Location**: `app/services/endpoint_matcher.py`
- **Matching Strategies**:
  - `exact`: Match exact paths
  - `prefix`: Match path prefixes
  - `regex`: Use regex patterns

### 3. S3 Client Service
- **Purpose**: Handle AWS S3 operations
- **Location**: `app/services/s3_client.py`
- **Features**:
  - AWS IAM role authentication
  - Async uploads with timeout
  - Structured JSON storage

### 4. Data Processor
- **Purpose**: Process and sanitize request/response data
- **Location**: `app/services/data_processor.py`
- **Security**: Filters sensitive headers (Authorization, Cookie)

## 📊 Data Flow

```
1. Request arrives at FastAPI
2. Middleware checks endpoint against patterns
3. If match: Extract request data (sanitized)
4. Call downstream service
5. Extract response data (sanitized)
6. Async upload to S3 (with timeout)
7. Return response to client
```

## 🔒 Security Features

### Container Security
- Non-root user (UID 1000)
- Read-only root filesystem
- Dropped capabilities
- Security context constraints

### Application Security
- Header filtering (Authorization, Cookie)
- Input validation with Pydantic
- Request/response size limits
- AWS IAM role-based access

### Infrastructure Security
- Kubernetes Network Policies
- RBAC configurations
- Encrypted S3 storage
- TLS termination at ingress

## 🚀 Deployment Options

### 1. Container Deployment
```bash
# Using Docker
docker run -p 8000:8000 ghcr.io/your-org/atlan-requests-test:latest

# Using Podman
podman run -p 8000:8000 ghcr.io/your-org/atlan-requests-test:latest
```

### 2. Kubernetes Deployment
```bash
# From GHCR (recommended)
./deploy-from-ghcr.sh --tag v1.0.0

# Build and deploy
./deploy.sh --build --engine podman
```

### 3. Docker Compose
```yaml
services:
  atlan-middleware:
    image: ghcr.io/your-org/atlan-requests-test:latest
    ports: ["8000:8000"]
    environment:
      - AWS_ROLE_ARN=arn:aws:iam::123456789012:role/S3Role
```

## ⚙️ Configuration

### Required Environment Variables
- `AWS_ROLE_ARN`: AWS IAM role for S3 access
- `S3_BUCKET_NAME`: S3 bucket for storing logs

### Optional Configuration
- `LOG_ENDPOINTS`: JSON array of endpoints to log
- `LOG_METHODS`: JSON array of HTTP methods to log
- `ENDPOINT_MATCH_TYPE`: Matching strategy (exact/prefix/regex)

### Example Configuration
```bash
# Log specific API endpoints with POST method
LOG_ENDPOINTS='["/api/search", "/api/lineage"]'
LOG_METHODS='["POST"]'
ENDPOINT_MATCH_TYPE='prefix'
```

## 📈 Performance Characteristics

### Scalability
- **Horizontal scaling**: 2-10 replicas (HPA)
- **CPU target**: 70% utilization
- **Memory target**: 80% utilization
- **Non-blocking**: Async S3 uploads

### Resource Usage
- **Memory**: 256Mi request, 512Mi limit
- **CPU**: 100m request, 500m limit
- **Startup time**: ~10 seconds
- **Request overhead**: <10ms (when not logging)

## 🔍 Monitoring

### Health Endpoints
- `/health` - Application health + configuration
- `/health/s3` - S3 connection health

### Metrics (Ready for Prometheus)
- Request count and duration
- S3 upload success/failure rates
- Memory and CPU usage
- Custom business metrics

### Logging
- Structured JSON logs
- Request tracing with ID
- Error correlation
- Performance metrics

## 🧪 Testing

### Test Coverage
- Unit tests: Core business logic
- Integration tests: End-to-end workflows
- Container tests: Image functionality
- Security tests: Vulnerability scanning

### Automated Testing
- **GitHub Actions**: CI/CD pipeline
- **Dependency scanning**: Dependabot + Trivy
- **Multi-architecture**: AMD64 + ARM64
- **Performance testing**: Load test scenarios

## 📦 Distribution

### GitHub Container Registry
- **Public images**: Available on GHCR
- **Multi-arch**: AMD64 and ARM64
- **Automated builds**: On every commit/tag
- **Security scanning**: Trivy integration

### Versioning
- **Semantic versioning**: v1.0.0 format
- **Git tags**: Automatic image tagging
- **Branch builds**: Development images
- **Commit tracking**: SHA-based tags

## 🛠️ Development

### Local Development
```bash
# Install dependencies
uv sync --group dev

# Run tests
uv run pytest tests/ -v

# Start development server
uv run uvicorn app.main:app --reload

# Test with container
./test-podman.sh
```

### Code Quality
- **Linting**: Ruff
- **Formatting**: Black
- **Type checking**: MyPy (optional)
- **Testing**: Pytest with async support

## 🔄 CI/CD Pipeline

### Workflow Triggers
- Push to main/develop branches
- Pull requests
- Git tags (releases)
- Manual workflow dispatch

### Pipeline Stages
1. **Test**: Unit tests, linting, formatting
2. **Security**: Vulnerability scanning
3. **Build**: Multi-architecture container build
4. **Publish**: Push to GHCR
5. **Deploy**: Kubernetes deployment (optional)

## 📋 Production Readiness

### ✅ Completed Features
- Selective request/response logging
- AWS S3 integration with IAM roles
- Container packaging (Docker/Podman)
- Kubernetes manifests
- CI/CD pipeline
- Security scanning
- Multi-architecture support
- Comprehensive documentation

### 🔮 Future Enhancements
- Prometheus metrics endpoint
- Grafana dashboards
- Log aggregation integration
- Request sampling for high traffic
- Custom storage backends
- Advanced filtering rules

## 📚 Documentation

- **README.md**: Quick start and usage
- **DEPLOYMENT.md**: Detailed deployment guide
- **CONTRIBUTING.md**: Development guidelines
- **k8s/README.md**: Kubernetes specifics
- **API Documentation**: FastAPI auto-generated docs

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup
- Code style guidelines
- Testing requirements
- Pull request process
- Security reporting
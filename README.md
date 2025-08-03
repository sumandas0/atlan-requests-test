# Atlan Requests Middleware

A lightweight FastAPI application for logging HTTP requests and responses to AWS S3.

## Use Case

### What Problem Does This Solve?

This middleware addresses critical needs in modern API management:

- **🔍 API Audit Trail** - Track all incoming requests and outgoing responses for compliance and debugging
- **📈 Analytics & Monitoring** - Collect data for API usage analytics, performance monitoring, and business intelligence
- **🛡️ Security & Compliance** - Maintain detailed logs for security audits, regulatory compliance (GDPR, SOX, etc.)
- **🐛 Debugging & Troubleshooting** - Capture request/response data to diagnose issues in production
- **📊 Data Lake Integration** - Feed API interaction data into data lakes for machine learning and analytics

### When to Use This

**Perfect for:**
- **API Gateways** - Deploy as a sidecar or proxy to log all API traffic
- **Microservices Architecture** - Track inter-service communication patterns
- **Customer-Facing APIs** - Monitor user interactions and API consumption
- **Financial Services** - Maintain transaction logs for regulatory compliance
- **Healthcare Systems** - Track data access for HIPAA compliance
- **E-commerce Platforms** - Log user interactions for analytics and fraud detection

### Real-World Scenarios

1. **Compliance Logging**: A financial institution needs to log all API calls for regulatory audits
2. **API Analytics**: A SaaS company wants to understand how customers use their API endpoints
3. **Debugging Production Issues**: Developers need detailed request/response logs to troubleshoot customer issues
4. **Security Monitoring**: Security teams need to track suspicious API usage patterns
5. **Data Science**: Data teams need API interaction data for user behavior analysis

### Benefits

- **🚀 Non-Intrusive** - Works as middleware without modifying existing application code
- **⚡ High Performance** - Asynchronous logging doesn't block API responses
- **🔧 Configurable** - Selectively log requests, responses, or both
- **📦 Production Ready** - Includes health checks, monitoring, and containerization
- **💰 Cost-Effective** - Uses S3 for affordable, scalable log storage
- **🔒 Secure** - Supports AWS IAM roles and encryption

## Features

- 🚀 **FastAPI** - Modern, fast web framework
- 📊 **Request/Response Logging** - Automatic logging to S3
- 🔒 **AWS IAM Role Support** - Secure credential management
- 🏥 **Health Checks** - Built-in health monitoring
- 🧪 **Testing** - Comprehensive test suite
- 🐳 **Docker Ready** - Production-ready containerization

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

### 2. Configure Environment

Create a `.env` file with your configuration:

```bash
# AWS Settings
AWS_REGION=us-east-1
AWS_ROLE_ARN=arn:aws:iam::123456789012:role/YourS3LoggingRole

# S3 Settings
S3_BUCKET_NAME=your-s3-bucket-name
S3_KEY_PREFIX=request-logs/

# Optional settings
DEBUG=false
LOG_LEVEL=INFO
ENABLE_REQUEST_LOGGING=true
ENABLE_RESPONSE_LOGGING=true
```

### 3. Run the Application

```bash
# Development mode (with auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python
python -m app.main
```

### 4. Test the API

Visit http://localhost:8000/docs for the interactive API documentation.

Try these endpoints:
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /ping` - Simple ping/pong
- `POST /echo` - Echo back request data

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint with API info |
| GET | `/health` | Health check with service status |
| GET | `/ping` | Simple ping endpoint |
| POST | `/echo` | Echo request data back |
| GET | `/docs` | Interactive API documentation |

## Running Tests

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=app
```

## Docker Usage

```bash
# Build the image
docker build -t atlan-middleware .

# Run the container
docker run -p 8000:8000 \
  -e S3_BUCKET_NAME=your-bucket \
  -e AWS_ROLE_ARN=your-role-arn \
  atlan-middleware
```

## Kubernetes Deployment

### Quick Deploy

```bash
# Deploy everything (namespace, deployment, services, ingress)
kubectl apply -f k8s/

# Or deploy individually
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
```

### Service Types Available

1. **ClusterIP Service** (`atlan-middleware-service`)
   - Internal cluster access only
   - Port: 80 → 8000

2. **NodePort Service** (`atlan-middleware-nodeport`)
   - External access via node IP
   - Port: 8000 → 8000 (NodePort: 30080)

3. **Ingress** (Optional)
   - HTTP/HTTPS access via domain names
   - Local: `atlan-middleware.local`
   - Production: `api.atlan-middleware.com`

### Testing the Service

```bash
# Port forward for local testing
kubectl port-forward -n atlas svc/atlan-middleware-service 8080:80

# Test the API
curl http://localhost:8080/
curl http://localhost:8080/health
curl http://localhost:8080/docs

# Or access via NodePort (if available)
curl http://<node-ip>:30080/
```

### Service Endpoints

| Service | Type | Internal | External | Description |
|---------|------|----------|----------|-------------|
| `atlan-middleware-service` | ClusterIP | `atlas-middleware-service.atlas.svc.cluster.local:80` | - | Internal cluster access |
| `atlan-middleware-nodeport` | NodePort | - | `<node-ip>:30080` | External node access |
| Ingress | HTTP/HTTPS | - | `atlan-middleware.local` | Domain-based access |

## Development

### Code Formatting

```bash
# Format code
black app/ tests/

# Lint code
ruff check app/ tests/
```

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `S3_BUCKET_NAME` | Yes | - | S3 bucket for storing logs |
| `AWS_ROLE_ARN` | No | - | IAM role to assume |
| `AWS_REGION` | No | `us-east-1` | AWS region |
| `S3_KEY_PREFIX` | No | `request-logs/` | S3 key prefix |
| `DEBUG` | No | `false` | Enable debug mode |
| `LOG_LEVEL` | No | `INFO` | Logging level |

## Architecture

### Deployment Patterns

**1. Reverse Proxy / API Gateway**
```
Client → Load Balancer → Atlan Middleware → Your API → Response
                            ↓
                        S3 Storage
```

**2. Sidecar Pattern (Kubernetes)**
```
Pod: [Your App Container] + [Atlan Sidecar Container]
                                    ↓
                               S3 Storage
```

**3. Standalone Proxy**
```
Client → Atlan Middleware → Upstream API
              ↓
          S3 Storage
```

### Components

The application consists of:

- **FastAPI App** (`app/main.py`) - Main application with middleware
- **S3 Service** (`app/services/s3_client.py`) - Async S3 logging with IAM role support
- **Models** (`app/models/schemas.py`) - Pydantic data models for structured logging
- **Config** (`app/config/settings.py`) - Environment-based configuration
- **Middleware** - Automatic request/response interception and logging

### Data Flow

1. **Request Interception** - Middleware captures incoming HTTP requests
2. **Request Processing** - Forwards request to your application/upstream service
3. **Response Capture** - Intercepts the response before returning to client
4. **Async Logging** - Logs structured data to S3 without blocking the response
5. **Request ID Tracking** - Adds unique request IDs for tracing

## License

MIT License
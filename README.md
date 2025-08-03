# Atlan Requests Middleware

A lightweight FastAPI application for logging HTTP requests and responses to AWS S3.

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

```bash
# Apply the deployment
kubectl apply -f k8s/deployment.yaml
```

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

The application consists of:

- **FastAPI App** (`app/main.py`) - Main application with middleware
- **S3 Service** (`app/services/s3_client.py`) - Async S3 logging
- **Models** (`app/models/schemas.py`) - Pydantic data models
- **Config** (`app/config/settings.py`) - Environment-based configuration

## License

MIT License
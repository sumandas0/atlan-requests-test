# Deployment Guide for Atlan Requests Middleware

This document provides comprehensive deployment instructions for the Atlan Requests Middleware using Docker and Kubernetes.

## 📋 Overview

The deployment includes:
- **Dockerfile**: Multi-stage optimized container image
- **Kubernetes Manifests**: Production-ready deployment with security, scaling, and monitoring
- **Automated Scripts**: One-command deployment with `deploy.sh`

## 🐳 Docker Deployment

### Building the Image

**Using Docker:**
```bash
# Standard build
docker build -t atlan-requests-middleware:latest .

# Multi-architecture build (for ARM64/AMD64)
docker buildx build --platform linux/amd64,linux/arm64 \
  -t atlan-requests-middleware:latest .
```

**Using Podman:**
```bash
# Standard build
podman build -t atlan-requests-middleware:latest .

# Multi-architecture build (for ARM64/AMD64)
podman build --platform linux/amd64,linux/arm64 \
  -t atlan-requests-middleware:latest .
```

> **Note**: When using Podman, you may see warnings about HEALTHCHECK not being supported for OCI image format. This is normal and doesn't affect functionality.

### Running Locally

**Using Docker:**
```bash
# Basic run
docker run -p 8000:8000 \
  -e AWS_ROLE_ARN="arn:aws:iam::123456789012:role/YourS3AccessRole" \
  -e S3_BUCKET_NAME="your-request-logs-bucket" \
  atlan-requests-middleware:latest

# With custom configuration
docker run -p 8000:8000 \
  -e AWS_ROLE_ARN="arn:aws:iam::123456789012:role/YourS3AccessRole" \
  -e S3_BUCKET_NAME="your-request-logs-bucket" \
  -e LOG_ENDPOINTS='["/api/search", "/api/lineage"]' \
  -e LOG_METHODS='["POST", "PUT"]' \
  -e ENDPOINT_MATCH_TYPE="prefix" \
  atlan-requests-middleware:latest
```

**Using Podman:**
```bash
# Basic run
podman run -p 8000:8000 \
  -e AWS_ROLE_ARN="arn:aws:iam::123456789012:role/YourS3AccessRole" \
  -e S3_BUCKET_NAME="your-request-logs-bucket" \
  atlan-requests-middleware:latest

# With custom configuration
podman run -p 8000:8000 \
  -e AWS_ROLE_ARN="arn:aws:iam::123456789012:role/YourS3AccessRole" \
  -e S3_BUCKET_NAME="your-request-logs-bucket" \
  -e LOG_ENDPOINTS='["/api/search", "/api/lineage"]' \
  -e LOG_METHODS='["POST", "PUT"]' \
  -e ENDPOINT_MATCH_TYPE="prefix" \
  atlan-requests-middleware:latest
```

### Docker Compose (Optional)

```yaml
version: '3.8'
services:
  atlan-middleware:
    build: .
    ports:
      - "8000:8000"
    environment:
      - AWS_ROLE_ARN=arn:aws:iam::123456789012:role/YourS3AccessRole
      - S3_BUCKET_NAME=your-request-logs-bucket
      - LOG_ENDPOINTS=["\/search\/indexsearch", "\/entity\/lineage"]
      - LOG_METHODS=["POST"]
      - ENDPOINT_MATCH_TYPE=exact
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## ☸️ Kubernetes Deployment

### Quick Start

```bash
# Clone and navigate to project
cd atlan-requests-test

# Configure secrets (required)
# Edit k8s/secret.yaml with your base64 encoded values:
echo -n "arn:aws:iam::YOUR_ACCOUNT:role/YOUR_ROLE" | base64
echo -n "your-s3-bucket-name" | base64

# Deploy everything with one command
./deploy.sh --build --tag v1.0.0
```

### Manual Deployment

```bash
# 1. Build and push image (if needed)
docker build -t atlan-requests-middleware:v1.0.0 .
docker tag atlan-requests-middleware:v1.0.0 your-registry/atlan-requests-middleware:v1.0.0
docker push your-registry/atlan-requests-middleware:v1.0.0

# 2. Update k8s/kustomization.yaml with new image tag
# 3. Deploy to Kubernetes
kubectl apply -k k8s/

# 4. Check deployment
kubectl get all -n atlan-middleware
```

### Production Checklist

Before deploying to production:

- [ ] **Update Secret Values** in `k8s/secret.yaml`
- [ ] **Configure Domain** in `k8s/ingress.yaml`
- [ ] **Set Resource Limits** in `k8s/deployment.yaml`
- [ ] **Configure SSL** in `k8s/ingress.yaml`
- [ ] **Set up Monitoring** (Prometheus/Grafana)
- [ ] **Configure Backup** for S3 bucket
- [ ] **Test Disaster Recovery** procedures

## 🔧 Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AWS_ROLE_ARN` | ✅ | - | AWS IAM Role ARN for S3 access |
| `S3_BUCKET_NAME` | ✅ | - | S3 bucket for storing logs |
| `AWS_REGION` | ❌ | `us-east-1` | AWS region |
| `LOG_ENDPOINTS` | ❌ | `["/search/indexsearch", "/entity/lineage"]` | Endpoints to log |
| `LOG_METHODS` | ❌ | `["POST"]` | HTTP methods to log |
| `ENDPOINT_MATCH_TYPE` | ❌ | `exact` | Matching strategy |

### Kubernetes Resources

| Resource | Purpose | Replicas | Resources |
|----------|---------|----------|-----------|
| **Deployment** | Main application | 3 | 256Mi-512Mi, 100m-500m |
| **Service** | Internal communication | - | ClusterIP |
| **Ingress** | External access | - | SSL, Rate limiting |
| **HPA** | Auto-scaling | 2-10 | CPU 70%, Memory 80% |

## 🔒 Security Features

### Container Security
- Non-root user (UID 1000)
- Read-only root filesystem where possible
- Dropped capabilities
- Security context constraints

### Network Security
- NetworkPolicy for traffic isolation
- Ingress rate limiting
- CORS configuration
- Security headers

### AWS Security
- IAM Roles for Service Accounts (IRSA)
- No hardcoded credentials
- Least privilege access
- Encrypted S3 storage

## 📊 Monitoring

### Health Checks

```bash
# Application health
curl http://your-domain/health

# Kubernetes health
kubectl get pods -n atlan-middleware
kubectl logs -f deployment/atlan-middleware -n atlan-middleware
```

### Metrics

The application exposes metrics at `/metrics` for Prometheus:
- Request count and duration
- S3 upload success/failure rates
- Memory and CPU usage
- Custom business metrics

### Alerts

Recommended alerts:
- Pod restart rate > 5/hour
- S3 upload failure rate > 5%
- Response time > 1s (95th percentile)
- Memory usage > 80%
- CPU usage > 80%

## 🚀 Scaling

### Horizontal Pod Autoscaler (HPA)

```yaml
# Automatic scaling based on:
- CPU utilization: 70%
- Memory utilization: 80%
- Min replicas: 2
- Max replicas: 10
```

### Manual Scaling

```bash
# Scale deployment
kubectl scale deployment atlan-middleware --replicas=5 -n atlan-middleware

# Update HPA limits
kubectl patch hpa atlan-middleware-hpa -n atlan-middleware \
  -p '{"spec":{"maxReplicas":20}}'
```

## 🔄 Updates

### Rolling Updates

```bash
# Update image version
kubectl set image deployment/atlan-middleware \
  atlan-middleware=atlan-requests-middleware:v1.1.0 \
  -n atlan-middleware

# Check rollout status
kubectl rollout status deployment/atlan-middleware -n atlan-middleware

# Rollback if needed
kubectl rollout undo deployment/atlan-middleware -n atlan-middleware
```

### Configuration Updates

```bash
# Update ConfigMap
kubectl apply -f k8s/configmap.yaml

# Restart deployment to pick up changes
kubectl rollout restart deployment/atlan-middleware -n atlan-middleware
```

## 🆘 Troubleshooting

### Common Issues

#### Pods Not Starting
```bash
kubectl describe pod POD_NAME -n atlan-middleware
kubectl logs POD_NAME -n atlan-middleware
```

#### AWS/S3 Connection Issues
```bash
# Check ServiceAccount
kubectl describe sa atlan-middleware-sa -n atlan-middleware

# Check AWS credentials
kubectl get secret atlan-middleware-secret -n atlan-middleware -o yaml

# Test S3 access
kubectl exec -it POD_NAME -n atlan-middleware -- \
  python -c "import boto3; print(boto3.client('s3').list_buckets())"
```

#### Ingress Issues
```bash
# Check ingress status
kubectl describe ingress atlan-middleware-ingress -n atlan-middleware

# Check ingress controller
kubectl logs -f deployment/ingress-nginx-controller -n ingress-nginx
```

#### HPA Not Working
```bash
# Check metrics server
kubectl get deployment metrics-server -n kube-system

# Check HPA status
kubectl describe hpa atlan-middleware-hpa -n atlan-middleware

# Check resource requests
kubectl describe deployment atlan-middleware -n atlan-middleware
```

### Performance Tuning

#### For High Traffic
- Increase replica count
- Optimize S3 upload timeout
- Enable request compression
- Use SSD storage classes

#### For Cost Optimization
- Use spot instances for worker nodes
- Implement intelligent request filtering
- Optimize S3 storage classes
- Use resource limits effectively

## 🧹 Cleanup

```bash
# Delete everything
kubectl delete -k k8s/

# Or delete namespace (removes all resources)
kubectl delete namespace atlan-middleware

# Remove Docker images
docker rmi atlan-requests-middleware:latest
```

## 📚 Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [AWS IAM Roles for Service Accounts](https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Nginx Ingress Controller](https://kubernetes.github.io/ingress-nginx/)

---

For more information, see:
- [Main README.md](README.md) - Application overview and local development
- [k8s/README.md](k8s/README.md) - Detailed Kubernetes deployment guide
# Kubernetes Deployment for Atlan Requests Middleware

This directory contains Kubernetes manifests for deploying the Atlan Requests Middleware application.

## Architecture

The deployment includes:

- **Namespace**: Isolated environment for the application
- **ConfigMap**: Non-sensitive configuration (endpoints, methods, etc.)
- **Secret**: Sensitive configuration (AWS credentials, S3 bucket)
- **ServiceAccount**: For AWS IAM role binding (IRSA)
- **Deployment**: Main application deployment with 3 replicas
- **Service**: ClusterIP service for internal communication
- **Ingress**: External access with SSL and rate limiting
- **HPA**: Horizontal Pod Autoscaler for automatic scaling
- **NetworkPolicy**: Security policies for network access

## Prerequisites

1. **Kubernetes cluster** (v1.19+)
2. **kubectl** configured to access your cluster
3. **AWS IAM role** with S3 permissions
4. **Ingress controller** (nginx recommended)
5. **Metrics server** (for HPA)

## Configuration

### 1. Update Secret Values

Edit `secret.yaml` and replace the base64 encoded values:

```bash
# Encode your AWS Role ARN
echo -n "arn:aws:iam::YOUR_ACCOUNT:role/YOUR_ROLE" | base64

# Encode your S3 bucket name
echo -n "your-s3-bucket-name" | base64
```

### 2. Update ConfigMap (Optional)

Edit `configmap.yaml` to customize:
- Logging endpoints
- HTTP methods
- Matching strategy
- AWS region
- Application settings

### 3. Update Ingress

Edit `ingress.yaml` to set:
- Your domain name
- SSL certificate settings
- Rate limiting rules

### 4. Update ServiceAccount

Edit `serviceaccount.yaml` to set your actual IAM role ARN for IRSA.

## Deployment

### Quick Deployment

```bash
# Deploy everything
kubectl apply -k k8s/

# Check deployment status
kubectl get all -n atlan-middleware
```

### Step-by-Step Deployment

```bash
# 1. Create namespace
kubectl apply -f k8s/namespace.yaml

# 2. Create ServiceAccount (for AWS permissions)
kubectl apply -f k8s/serviceaccount.yaml

# 3. Create ConfigMap and Secret
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml

# 4. Deploy the application
kubectl apply -f k8s/deployment.yaml

# 5. Create service
kubectl apply -f k8s/service.yaml

# 6. Create ingress (optional)
kubectl apply -f k8s/ingress.yaml

# 7. Create HPA for autoscaling
kubectl apply -f k8s/hpa.yaml

# 8. Apply network policy
kubectl apply -f k8s/networkpolicy.yaml
```

## Verification

### Check Pod Status

```bash
kubectl get pods -n atlan-middleware
kubectl logs -f deployment/atlan-middleware -n atlan-middleware
```

### Test Health Endpoint

```bash
# Port-forward for testing
kubectl port-forward svc/atlan-middleware-service 8080:80 -n atlan-middleware

# Test health endpoint
curl http://localhost:8080/health
```

### Check HPA Status

```bash
kubectl get hpa -n atlan-middleware
kubectl describe hpa atlan-middleware-hpa -n atlan-middleware
```

## Monitoring

### View Logs

```bash
# All pods
kubectl logs -f deployment/atlan-middleware -n atlan-middleware

# Specific pod
kubectl logs -f pod/POD_NAME -n atlan-middleware
```

### Check Metrics

```bash
# Resource usage
kubectl top pods -n atlan-middleware

# HPA metrics
kubectl describe hpa atlan-middleware-hpa -n atlan-middleware
```

## Scaling

### Manual Scaling

```bash
# Scale deployment
kubectl scale deployment atlan-middleware --replicas=5 -n atlan-middleware
```

### Auto Scaling

The HPA will automatically scale based on:
- CPU utilization (target: 70%)
- Memory utilization (target: 80%)
- Min replicas: 2
- Max replicas: 10

## Troubleshooting

### Common Issues

1. **Pods not starting**
   ```bash
   kubectl describe pod POD_NAME -n atlan-middleware
   ```

2. **AWS credentials issues**
   ```bash
   # Check if ServiceAccount has correct annotations
   kubectl describe sa atlan-middleware-sa -n atlan-middleware
   
   # Check secret values
   kubectl get secret atlan-middleware-secret -n atlan-middleware -o yaml
   ```

3. **S3 connection issues**
   ```bash
   # Check logs for AWS/S3 errors
   kubectl logs deployment/atlan-middleware -n atlan-middleware | grep -i "s3\|aws"
   ```

4. **Ingress not working**
   ```bash
   # Check ingress status
   kubectl describe ingress atlan-middleware-ingress -n atlan-middleware
   
   # Check ingress controller logs
   kubectl logs -f deployment/ingress-nginx-controller -n ingress-nginx
   ```

## Security Considerations

- Pods run as non-root user (UID 1000)
- ReadOnlyRootFilesystem enabled where possible
- Network policies restrict traffic
- Secrets are base64 encoded (consider using sealed-secrets or external secrets operator)
- IRSA used for AWS authentication instead of access keys

## Updates

### Rolling Updates

```bash
# Update deployment with new image
kubectl set image deployment/atlan-middleware atlan-middleware=atlan-requests-middleware:v1.1.0 -n atlan-middleware

# Check rollout status
kubectl rollout status deployment/atlan-middleware -n atlan-middleware
```

### Configuration Updates

```bash
# Update ConfigMap
kubectl apply -f k8s/configmap.yaml

# Restart deployment to pick up changes
kubectl rollout restart deployment/atlan-middleware -n atlan-middleware
```

## Cleanup

```bash
# Delete everything
kubectl delete -k k8s/

# Or delete namespace (removes everything in the namespace)
kubectl delete namespace atlan-middleware
```
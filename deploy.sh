#!/bin/bash

# Deployment script for Atlan Requests Middleware
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
NAMESPACE="atlan-middleware"
BUILD_IMAGE=${BUILD_IMAGE:-false}
IMAGE_TAG=${IMAGE_TAG:-latest}
REGISTRY=${REGISTRY:-""}
CONTAINER_ENGINE=${CONTAINER_ENGINE:-"auto"}

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    log_info "Checking dependencies..."
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed or not in PATH"
        exit 1
    fi
    
    # Check if cluster is accessible
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    # Check if metrics server is installed (for HPA)
    if ! kubectl get deployment metrics-server -n kube-system &> /dev/null; then
        log_warning "Metrics server not found. HPA may not work properly."
    fi
    
    # Determine container engine
    if [[ "$CONTAINER_ENGINE" == "auto" ]]; then
        if command -v podman &> /dev/null; then
            CONTAINER_ENGINE="podman"
        elif command -v docker &> /dev/null; then
            CONTAINER_ENGINE="docker"
        else
            log_error "Neither Docker nor Podman found. Please install one of them."
            exit 1
        fi
    fi
    
    log_info "Using container engine: $CONTAINER_ENGINE"
    log_success "Dependencies check passed"
}

build_image() {
    if [[ "$BUILD_IMAGE" == "true" ]]; then
        log_info "Building container image using $CONTAINER_ENGINE..."
        $CONTAINER_ENGINE build -t atlan-requests-middleware:${IMAGE_TAG} .
        
        if [[ -n "$REGISTRY" ]]; then
            log_info "Tagging and pushing to registry..."
            $CONTAINER_ENGINE tag atlan-requests-middleware:${IMAGE_TAG} ${REGISTRY}/atlan-requests-middleware:${IMAGE_TAG}
            $CONTAINER_ENGINE push ${REGISTRY}/atlan-requests-middleware:${IMAGE_TAG}
        fi
        
        log_success "Image built successfully"
    fi
}

deploy_application() {
    log_info "Deploying Atlan Requests Middleware..."
    
    # Create namespace if it doesn't exist
    if ! kubectl get namespace $NAMESPACE &> /dev/null; then
        log_info "Creating namespace: $NAMESPACE"
        kubectl apply -f k8s/namespace.yaml
    fi
    
    # Apply all manifests
    log_info "Applying Kubernetes manifests..."
    kubectl apply -k k8s/
    
    # Wait for deployment to be ready
    log_info "Waiting for deployment to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/atlan-middleware -n $NAMESPACE
    
    log_success "Deployment completed successfully"
}

verify_deployment() {
    log_info "Verifying deployment..."
    
    # Check pod status
    log_info "Pod status:"
    kubectl get pods -n $NAMESPACE
    
    # Check service status
    log_info "Service status:"
    kubectl get services -n $NAMESPACE
    
    # Check HPA status
    if kubectl get hpa atlan-middleware-hpa -n $NAMESPACE &> /dev/null; then
        log_info "HPA status:"
        kubectl get hpa -n $NAMESPACE
    fi
    
    # Test health endpoint
    log_info "Testing health endpoint..."
    kubectl port-forward svc/atlan-middleware-service 8080:80 -n $NAMESPACE &
    PORT_FORWARD_PID=$!
    sleep 5
    
    if curl -f http://localhost:8080/health &> /dev/null; then
        log_success "Health endpoint is responding"
    else
        log_warning "Health endpoint not responding (this might be normal if ingress is not configured)"
    fi
    
    # Cleanup port-forward
    kill $PORT_FORWARD_PID 2>/dev/null || true
    
    log_success "Verification completed"
}

show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -b, --build           Build container image before deploying"
    echo "  -t, --tag TAG         Container image tag (default: latest)"
    echo "  -r, --registry REG    Container registry for pushing image"
    echo "  -n, --namespace NS    Kubernetes namespace (default: atlan-middleware)"
    echo "  -e, --engine ENGINE   Container engine (docker/podman/auto) (default: auto)"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Deploy with default settings"
    echo "  $0 --build --tag v1.0.0              # Build and deploy with tag v1.0.0"
    echo "  $0 --build --registry myregistry.com # Build and push to registry"
    echo "  $0 --build --engine podman           # Build using Podman specifically"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -b|--build)
            BUILD_IMAGE=true
            shift
            ;;
        -t|--tag)
            IMAGE_TAG="$2"
            shift 2
            ;;
        -r|--registry)
            REGISTRY="$2"
            shift 2
            ;;
        -n|--namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        -e|--engine)
            CONTAINER_ENGINE="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
main() {
    log_info "Starting deployment of Atlan Requests Middleware"
    log_info "Namespace: $NAMESPACE"
    log_info "Image tag: $IMAGE_TAG"
    
    check_dependencies
    build_image
    deploy_application
    verify_deployment
    
    echo ""
    log_success "Deployment completed successfully!"
    echo ""
    log_info "Next steps:"
    echo "1. Update the ingress domain in k8s/ingress.yaml"
    echo "2. Configure SSL certificates if needed"
    echo "3. Update ConfigMap values for your environment"
    echo "4. Monitor the application: kubectl logs -f deployment/atlan-middleware -n $NAMESPACE"
}

# Run main function
main
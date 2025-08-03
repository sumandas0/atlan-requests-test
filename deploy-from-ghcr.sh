#!/bin/bash

# Deployment script for Atlan Requests Middleware using GHCR images
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
NAMESPACE="atlan-middleware"
IMAGE_TAG=${IMAGE_TAG:-latest}
GHCR_REPO=${GHCR_REPO:-"ghcr.io/your-org/atlan-requests-test"}

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

check_prerequisites() {
    log_info "Checking prerequisites..."
    
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
    
    # Check if namespace exists
    if ! kubectl get namespace $NAMESPACE &> /dev/null; then
        log_warning "Namespace $NAMESPACE does not exist, it will be created"
    fi
    
    log_success "Prerequisites check passed"
}

update_image_references() {
    log_info "Updating image references to use GHCR..."
    
    # Create temporary kustomization file
    cat > k8s/kustomization-ghcr.yaml << EOF
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: $NAMESPACE

resources:
- namespace.yaml
- serviceaccount.yaml
- configmap.yaml
- secret.yaml
- deployment.yaml
- service.yaml
- ingress.yaml
- hpa.yaml
- networkpolicy.yaml

# Common labels applied to all resources
commonLabels:
  app.kubernetes.io/name: atlan-requests-middleware
  app.kubernetes.io/part-of: atlan-platform
  
# Use GHCR image
images:
- name: ghcr.io/your-org/atlan-requests-test
  newName: ${GHCR_REPO}
  newTag: ${IMAGE_TAG}
EOF
    
    log_success "Image references updated"
}

deploy_application() {
    log_info "Deploying Atlan Requests Middleware from GHCR..."
    log_info "Using image: ${GHCR_REPO}:${IMAGE_TAG}"
    
    # Apply manifests with updated image
    kubectl apply -k k8s/ --kustomization=k8s/kustomization-ghcr.yaml
    
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
    
    # Check if image is pulled correctly
    log_info "Checking container image..."
    kubectl describe deployment atlan-middleware -n $NAMESPACE | grep Image: || true
    
    # Check service status
    log_info "Service status:"
    kubectl get services -n $NAMESPACE
    
    log_success "Verification completed"
}

cleanup_temp_files() {
    log_info "Cleaning up temporary files..."
    rm -f k8s/kustomization-ghcr.yaml
}

show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Deploy Atlan Requests Middleware using pre-built GHCR images"
    echo ""
    echo "Options:"
    echo "  -t, --tag TAG         Container image tag (default: latest)"
    echo "  -r, --repo REPO       GHCR repository (default: ghcr.io/your-org/atlan-requests-test)"
    echo "  -n, --namespace NS    Kubernetes namespace (default: atlan-middleware)"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  IMAGE_TAG             Container image tag"
    echo "  GHCR_REPO            GHCR repository path"
    echo ""
    echo "Examples:"
    echo "  $0                                          # Deploy latest image"
    echo "  $0 --tag v1.0.0                           # Deploy specific version"
    echo "  $0 --repo ghcr.io/myorg/atlan-middleware  # Use custom repo"
    echo ""
    echo "Prerequisites:"
    echo "  1. kubectl configured for your cluster"
    echo "  2. Update k8s/secret.yaml with your AWS credentials"
    echo "  3. Update k8s/ingress.yaml with your domain"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--tag)
            IMAGE_TAG="$2"
            shift 2
            ;;
        -r|--repo)
            GHCR_REPO="$2"
            shift 2
            ;;
        -n|--namespace)
            NAMESPACE="$2"
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
    log_info "🚀 Deploying Atlan Requests Middleware from GHCR"
    log_info "Namespace: $NAMESPACE"
    log_info "Image: ${GHCR_REPO}:${IMAGE_TAG}"
    echo ""
    
    check_prerequisites
    update_image_references
    deploy_application
    verify_deployment
    cleanup_temp_files
    
    echo ""
    log_success "🎉 Deployment completed successfully!"
    echo ""
    log_info "Next steps:"
    echo "1. Check pod logs: kubectl logs -f deployment/atlan-middleware -n $NAMESPACE"
    echo "2. Test health endpoint: kubectl port-forward svc/atlan-middleware-service 8080:80 -n $NAMESPACE"
    echo "3. Configure ingress domain if needed"
    echo "4. Monitor the application with: kubectl get all -n $NAMESPACE"
}

# Set trap to cleanup on exit
trap cleanup_temp_files EXIT

# Run main function
main
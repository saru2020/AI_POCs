#!/bin/bash

# Movies GraphRAG Demo - Deploy Script
# This script deploys the Movies GraphRAG Demo to production

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking deployment prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        print_error "Environment file (.env) not found"
        print_status "Please copy env.example to .env and configure it"
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Function to run tests
run_tests() {
    print_status "Running tests before deployment..."
    ./scripts/test.sh --all
    print_success "Tests passed"
}

# Function to build Docker images
build_images() {
    print_status "Building Docker images..."
    
    if command -v docker-compose &> /dev/null; then
        docker-compose build --no-cache
    else
        docker compose build --no-cache
    fi
    
    print_success "Docker images built"
}

# Function to deploy to production
deploy_production() {
    print_status "Deploying to production..."
    
    # Stop existing containers
    if command -v docker-compose &> /dev/null; then
        docker-compose down
    else
        docker compose down
    fi
    
    # Start production containers
    if command -v docker-compose &> /dev/null; then
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
    else
        docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
    fi
    
    print_success "Production deployment completed"
}

# Function to deploy to staging
deploy_staging() {
    print_status "Deploying to staging..."
    
    # Stop existing containers
    if command -v docker-compose &> /dev/null; then
        docker-compose down
    else
        docker compose down
    fi
    
    # Start staging containers
    if command -v docker-compose &> /dev/null; then
        docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d
    else
        docker compose -f docker-compose.yml -f docker-compose.staging.yml up -d
    fi
    
    print_success "Staging deployment completed"
}

# Function to deploy locally
deploy_local() {
    print_status "Deploying locally..."
    
    # Stop existing containers
    if command -v docker-compose &> /dev/null; then
        docker-compose down
    else
        docker compose down
    fi
    
    # Start local containers
    if command -v docker-compose &> /dev/null; then
        docker-compose up -d
    else
        docker compose up -d
    fi
    
    print_success "Local deployment completed"
}

# Function to check deployment health
check_health() {
    print_status "Checking deployment health..."
    
    # Wait for services to start
    sleep 30
    
    # Check application health
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        print_success "Application is healthy"
    else
        print_error "Application health check failed"
        exit 1
    fi
    
    # Check Neo4j health
    if curl -f http://localhost:7474 >/dev/null 2>&1; then
        print_success "Neo4j is healthy"
    else
        print_warning "Neo4j health check failed"
    fi
    
    # Check Redis health
    if redis-cli -h localhost -p 6379 ping >/dev/null 2>&1; then
        print_success "Redis is healthy"
    else
        print_warning "Redis health check failed"
    fi
}

# Function to show deployment status
show_status() {
    print_status "Deployment status:"
    echo ""
    
    if command -v docker-compose &> /dev/null; then
        docker-compose ps
    else
        docker compose ps
    fi
    
    echo ""
    echo "🌐 Application: http://localhost:8000"
    echo "📚 API Docs: http://localhost:8000/docs"
    echo "🔍 Neo4j Browser: http://localhost:7474"
    echo "📊 Grafana: http://localhost:3001"
    echo ""
}

# Function to rollback deployment
rollback() {
    print_status "Rolling back deployment..."
    
    # Stop current containers
    if command -v docker-compose &> /dev/null; then
        docker-compose down
    else
        docker compose down
    fi
    
    # Start previous version (if available)
    if [ -f "docker-compose.backup.yml" ]; then
        if command -v docker-compose &> /dev/null; then
            docker-compose -f docker-compose.backup.yml up -d
        else
            docker compose -f docker-compose.backup.yml up -d
        fi
        print_success "Rollback completed"
    else
        print_warning "No backup found for rollback"
    fi
}

# Function to show help
show_help() {
    echo "Movies GraphRAG Demo - Deploy Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help              Show this help message"
    echo "  -e, --env ENV           Deployment environment (local|staging|production)"
    echo "  -t, --test              Run tests before deployment"
    echo "  -b, --build             Build Docker images"
    echo "  -c, --check             Check deployment health"
    echo "  -s, --status            Show deployment status"
    echo "  -r, --rollback          Rollback deployment"
    echo "  --no-test               Skip tests"
    echo "  --no-build              Skip building images"
    echo ""
    echo "Examples:"
    echo "  $0 --env local          # Deploy locally"
    echo "  $0 --env staging        # Deploy to staging"
    echo "  $0 --env production     # Deploy to production"
    echo "  $0 --test --build       # Run tests and build images"
    echo "  $0 --status             # Show deployment status"
    echo "  $0 --rollback           # Rollback deployment"
    echo ""
}

# Main function
main() {
    # Parse command line arguments
    ENVIRONMENT="local"
    RUN_TESTS=true
    BUILD_IMAGES=true
    CHECK_HEALTH=true
    SHOW_STATUS=false
    ROLLBACK=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -e|--env)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -t|--test)
                RUN_TESTS=true
                shift
                ;;
            -b|--build)
                BUILD_IMAGES=true
                shift
                ;;
            -c|--check)
                CHECK_HEALTH=true
                shift
                ;;
            -s|--status)
                SHOW_STATUS=true
                shift
                ;;
            -r|--rollback)
                ROLLBACK=true
                shift
                ;;
            --no-test)
                RUN_TESTS=false
                shift
                ;;
            --no-build)
                BUILD_IMAGES=false
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    echo "🚀 Movies GraphRAG Demo - Deployment"
    echo "===================================="
    echo ""
    
    # Check prerequisites
    check_prerequisites
    
    # Rollback if requested
    if [ "$ROLLBACK" = true ]; then
        rollback
        exit 0
    fi
    
    # Show status if requested
    if [ "$SHOW_STATUS" = true ]; then
        show_status
        exit 0
    fi
    
    # Run tests if requested
    if [ "$RUN_TESTS" = true ]; then
        run_tests
    fi
    
    # Build images if requested
    if [ "$BUILD_IMAGES" = true ]; then
        build_images
    fi
    
    # Deploy based on environment
    case $ENVIRONMENT in
        local)
            deploy_local
            ;;
        staging)
            deploy_staging
            ;;
        production)
            deploy_production
            ;;
        *)
            print_error "Invalid environment: $ENVIRONMENT"
            print_status "Valid environments: local, staging, production"
            exit 1
            ;;
    esac
    
    # Check health if requested
    if [ "$CHECK_HEALTH" = true ]; then
        check_health
    fi
    
    # Show status
    show_status
    
    print_success "Deployment completed successfully!"
}

# Run main function
main "$@"

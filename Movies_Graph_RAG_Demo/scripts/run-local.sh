#!/bin/bash

# Movies GraphRAG Demo - Run Local Script
# This script runs the Movies GraphRAG Demo locally with minimal setup

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

# Function to check if services are running
check_services() {
    print_status "Checking if required services are running..."
    
    # Check Neo4j
    if curl -s http://localhost:7474 >/dev/null 2>&1; then
        print_success "Neo4j is running"
    else
        print_warning "Neo4j is not running, starting it..."
        if command -v docker-compose >/dev/null 2>&1; then
            docker-compose up -d neo4j redis
        else
            docker compose up -d neo4j redis
        fi
        print_status "Waiting for services to be ready..."
        sleep 30
    fi
    
    # Check Redis
    if redis-cli -h localhost -p 6379 ping >/dev/null 2>&1; then
        print_success "Redis is running"
    else
        print_warning "Redis is not running, starting it..."
        if command -v docker-compose >/dev/null 2>&1; then
            docker-compose up -d redis
        else
            docker compose up -d redis
        fi
        print_status "Waiting for Redis to be ready..."
        sleep 10
    fi
}

# Function to activate virtual environment
activate_venv() {
    if [ -d "venv" ]; then
        print_status "Activating virtual environment..."
        source venv/bin/activate
        print_success "Virtual environment activated"
    else
        print_warning "Virtual environment not found, creating it..."
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        print_success "Virtual environment created and activated"
    fi
}

# Function to check environment variables
check_env() {
    print_status "Checking environment configuration..."
    
    if [ ! -f ".env" ]; then
        print_warning "Environment file not found, creating default..."
        cat > .env << EOF
# Database Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=movies123

# Redis Configuration
REDIS_URL=redis://localhost:6379

# API Keys (Add your actual keys here)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
TMDB_API_KEY=your_tmdb_api_key_here

# Application Configuration
LOG_LEVEL=INFO
ENVIRONMENT=development
DEBUG=True
EOF
        print_warning "Please update .env file with your actual API keys"
    fi
    
    # Source environment variables
    source .env
    print_success "Environment configuration loaded"
}

# Function to run database migrations
run_migrations() {
    print_status "Running database migrations..."
    python -m src.database.migrate
    print_success "Database migrations completed"
}

# Function to start the application
start_app() {
    print_status "Starting Movies GraphRAG Demo application..."
    
    # Check if port 8000 is available
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "Port 8000 is already in use"
        print_status "Stopping existing process on port 8000..."
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
    
    # Start the application
    print_status "Starting FastAPI application..."
    python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload &
    APP_PID=$!
    
    # Wait for application to start
    print_status "Waiting for application to start..."
    sleep 5
    
    # Check if application is running
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        print_success "Application started successfully!"
        echo ""
        echo "=========================================="
        echo "🎬 Movies GraphRAG Demo is running!"
        echo "=========================================="
        echo ""
        echo "🌐 Application: http://localhost:8000"
        echo "📚 API Docs: http://localhost:8000/docs"
        echo "🔍 Neo4j Browser: http://localhost:7474"
        echo "📊 Grafana: http://localhost:3001"
        echo ""
        echo "Press Ctrl+C to stop the application"
        echo ""
        
        # Wait for user to stop
        wait $APP_PID
    else
        print_error "Failed to start application"
        exit 1
    fi
}

# Function to start with monitoring
start_with_monitoring() {
    print_status "Starting with monitoring services..."
    
    # Start monitoring services
    if command -v docker-compose >/dev/null 2>&1; then
        docker-compose up -d prometheus grafana
    else
        docker compose up -d prometheus grafana
    fi
    
    print_success "Monitoring services started"
    print_status "Grafana: http://localhost:3001 (admin/admin123)"
    print_status "Prometheus: http://localhost:9090"
}

# Function to show help
show_help() {
    echo "Movies GraphRAG Demo - Run Local Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help              Show this help message"
    echo "  -m, --monitoring        Start with monitoring services"
    echo "  -s, --skip-services     Skip service checks"
    echo "  -d, --daemon            Run in background"
    echo ""
    echo "Examples:"
    echo "  $0                      # Start normally"
    echo "  $0 --monitoring         # Start with monitoring"
    echo "  $0 --daemon             # Start in background"
    echo ""
}

# Main function
main() {
    # Parse command line arguments
    SKIP_SERVICES=false
    WITH_MONITORING=false
    DAEMON=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -m|--monitoring)
                WITH_MONITORING=true
                shift
                ;;
            -s|--skip-services)
                SKIP_SERVICES=true
                shift
                ;;
            -d|--daemon)
                DAEMON=true
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    echo "🎬 Movies GraphRAG Demo - Run Local"
    echo "=================================="
    echo ""
    
    # Check services if not skipped
    if [ "$SKIP_SERVICES" = false ]; then
        check_services
    fi
    
    # Activate virtual environment
    activate_venv
    
    # Check environment
    check_env
    
    # Run migrations
    run_migrations
    
    # Start monitoring if requested
    if [ "$WITH_MONITORING" = true ]; then
        start_with_monitoring
    fi
    
    # Start application
    if [ "$DAEMON" = true ]; then
        print_status "Starting application in background..."
        nohup python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 > logs/app.log 2>&1 &
        print_success "Application started in background (PID: $!)"
        print_status "Logs: tail -f logs/app.log"
    else
        start_app
    fi
}

# Run main function
main "$@"

#!/bin/bash

# Movies GraphRAG Demo - Setup Script
# This script sets up the development environment for the Movies GraphRAG Demo project

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
    if command_exists python3; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        if [[ $(echo "$PYTHON_VERSION >= 3.11" | bc -l) -eq 1 ]]; then
            print_success "Python $PYTHON_VERSION is installed"
            return 0
        else
            print_error "Python 3.11+ is required. Found: $PYTHON_VERSION"
            return 1
        fi
    else
        print_error "Python 3 is not installed"
        return 1
    fi
}

# Function to check Docker
check_docker() {
    if command_exists docker; then
        print_success "Docker is installed"
        if command_exists docker-compose; then
            print_success "Docker Compose is installed"
        else
            print_warning "Docker Compose not found, trying 'docker compose'"
            if docker compose version >/dev/null 2>&1; then
                print_success "Docker Compose (new version) is available"
            else
                print_error "Docker Compose is required"
                return 1
            fi
        fi
    else
        print_error "Docker is not installed"
        return 1
    fi
}

# Function to create virtual environment
create_venv() {
    print_status "Creating Python virtual environment..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
}

# Function to activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    source venv/bin/activate
    print_success "Virtual environment activated"
}

# Function to install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    print_success "Python dependencies installed"
}

# Function to create environment file
create_env_file() {
    print_status "Creating environment configuration..."
    if [ ! -f ".env" ]; then
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

# Monitoring
PROMETHEUS_ENABLED=True
GRAFANA_ENABLED=True
EOF
        print_success "Environment file created (.env)"
        print_warning "Please update .env file with your actual API keys"
    else
        print_warning "Environment file already exists"
    fi
}

# Function to create logs directory
create_logs_dir() {
    print_status "Creating logs directory..."
    mkdir -p logs
    print_success "Logs directory created"
}

# Function to start services
start_services() {
    print_status "Starting Docker services..."
    if command_exists docker-compose; then
        docker-compose up -d neo4j redis
    else
        docker compose up -d neo4j redis
    fi
    
    print_status "Waiting for services to be ready..."
    sleep 30
    
    print_success "Services started successfully"
}

# Function to run database migrations
run_migrations() {
    print_status "Running database migrations..."
    python -m src.database.migrate
    print_success "Database migrations completed"
}

# Function to run tests
run_tests() {
    print_status "Running tests..."
    python -m pytest tests/ -v --cov=src --cov-report=html
    print_success "Tests completed"
}

# Function to display next steps
display_next_steps() {
    echo ""
    echo "=========================================="
    echo "🎬 Movies GraphRAG Demo Setup Complete!"
    echo "=========================================="
    echo ""
    echo "Next steps:"
    echo "1. Update .env file with your API keys"
    echo "2. Run: ./scripts/run-local.sh"
    echo "3. Open: http://localhost:8000"
    echo "4. Neo4j Browser: http://localhost:7474"
    echo "5. Grafana: http://localhost:3001 (admin/admin123)"
    echo ""
    echo "Useful commands:"
    echo "- Start services: docker-compose up -d"
    echo "- Stop services: docker-compose down"
    echo "- View logs: docker-compose logs -f app"
    echo "- Run tests: ./scripts/test.sh"
    echo "- Deploy: ./scripts/deploy.sh"
    echo ""
}

# Main setup function
main() {
    echo "🎬 Movies GraphRAG Demo - Setup Script"
    echo "======================================"
    echo ""
    
    # Check prerequisites
    print_status "Checking prerequisites..."
    check_python_version || exit 1
    check_docker || exit 1
    
    # Setup Python environment
    create_venv
    activate_venv
    install_dependencies
    
    # Setup configuration
    create_env_file
    create_logs_dir
    
    # Start services
    start_services
    
    # Run migrations
    run_migrations
    
    # Run tests
    run_tests
    
    # Display next steps
    display_next_steps
}

# Run main function
main "$@"

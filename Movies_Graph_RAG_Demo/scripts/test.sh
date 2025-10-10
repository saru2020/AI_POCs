#!/bin/bash

# Movies GraphRAG Demo - Test Script
# This script runs the test suite for the Movies GraphRAG Demo project

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

# Function to check if virtual environment exists
check_venv() {
    if [ ! -d "venv" ]; then
        print_error "Virtual environment not found. Please run ./scripts/setup.sh first."
        exit 1
    fi
}

# Function to activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    source venv/bin/activate
    print_success "Virtual environment activated"
}

# Function to install test dependencies
install_test_deps() {
    print_status "Installing test dependencies..."
    pip install -r requirements-dev.txt
    print_success "Test dependencies installed"
}

# Function to run linting
run_linting() {
    print_status "Running code quality checks..."
    
    # Black formatting check
    print_status "Checking code formatting with Black..."
    black --check src tests
    
    # Flake8 linting
    print_status "Running Flake8 linting..."
    flake8 src tests
    
    # MyPy type checking
    print_status "Running MyPy type checking..."
    mypy src
    
    # Import sorting check
    print_status "Checking import sorting with isort..."
    isort --check-only src tests
    
    print_success "Code quality checks passed"
}

# Function to run security checks
run_security_checks() {
    print_status "Running security checks..."
    
    # Bandit security linting
    print_status "Running Bandit security analysis..."
    bandit -r src -f json -o security-report.json || true
    
    # Safety dependency check
    print_status "Checking for known security vulnerabilities..."
    safety check --json --output safety-report.json || true
    
    print_success "Security checks completed"
}

# Function to run unit tests
run_unit_tests() {
    print_status "Running unit tests..."
    pytest tests/ -m "unit" -v --cov=src --cov-report=html --cov-report=term-missing
    print_success "Unit tests completed"
}

# Function to run integration tests
run_integration_tests() {
    print_status "Running integration tests..."
    pytest tests/ -m "integration" -v --cov=src --cov-report=html --cov-report=term-missing
    print_success "Integration tests completed"
}

# Function to run all tests
run_all_tests() {
    print_status "Running all tests..."
    pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing --cov-fail-under=90
    print_success "All tests completed"
}

# Function to run specific test file
run_specific_test() {
    local test_file="$1"
    print_status "Running specific test: $test_file"
    pytest "$test_file" -v --cov=src --cov-report=html --cov-report=term-missing
    print_success "Test $test_file completed"
}

# Function to run performance tests
run_performance_tests() {
    print_status "Running performance tests..."
    pytest tests/ -m "performance" -v --durations=10
    print_success "Performance tests completed"
}

# Function to run GraphRAG specific tests
run_graphrag_tests() {
    print_status "Running GraphRAG specific tests..."
    pytest tests/ -m "graphrag" -v --cov=src --cov-report=html --cov-report=term-missing
    print_success "GraphRAG tests completed"
}

# Function to run evaluation tests
run_evaluation_tests() {
    print_status "Running evaluation framework tests..."
    pytest tests/ -m "evaluation" -v --cov=src --cov-report=html --cov-report=term-missing
    print_success "Evaluation tests completed"
}

# Function to generate test report
generate_test_report() {
    print_status "Generating test report..."
    
    # Create reports directory
    mkdir -p reports
    
    # Run tests with HTML report
    pytest tests/ -v --cov=src --cov-report=html:reports/coverage --cov-report=xml:reports/coverage.xml --junitxml=reports/junit.xml
    
    # Generate coverage badge
    coverage-badge -o reports/coverage-badge.svg
    
    print_success "Test report generated in reports/ directory"
}

# Function to clean up
cleanup() {
    print_status "Cleaning up test artifacts..."
    rm -rf .pytest_cache
    rm -rf htmlcov
    rm -rf .coverage
    print_success "Cleanup completed"
}

# Function to show help
show_help() {
    echo "Movies GraphRAG Demo - Test Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help              Show this help message"
    echo "  -u, --unit              Run unit tests only"
    echo "  -i, --integration       Run integration tests only"
    echo "  -a, --all               Run all tests (default)"
    echo "  -l, --lint              Run linting only"
    echo "  -s, --security          Run security checks only"
    echo "  -p, --performance       Run performance tests only"
    echo "  -g, --graphrag          Run GraphRAG specific tests"
    echo "  -e, --evaluation        Run evaluation framework tests"
    echo "  -f, --file FILE         Run specific test file"
    echo "  -r, --report            Generate test report"
    echo "  -c, --clean             Clean up test artifacts"
    echo "  --no-cov               Skip coverage reporting"
    echo "  --no-lint              Skip linting"
    echo "  --no-security          Skip security checks"
    echo ""
    echo "Examples:"
    echo "  $0                      # Run all tests"
    echo "  $0 --unit               # Run unit tests only"
    echo "  $0 --lint               # Run linting only"
    echo "  $0 --file test_api.py   # Run specific test file"
    echo "  $0 --report             # Generate test report"
    echo ""
}

# Main function
main() {
    # Parse command line arguments
    RUN_UNIT=false
    RUN_INTEGRATION=false
    RUN_ALL=true
    RUN_LINT=true
    RUN_SECURITY=true
    RUN_PERFORMANCE=false
    RUN_GRAPHRAG=false
    RUN_EVALUATION=false
    RUN_REPORT=false
    RUN_CLEAN=false
    NO_COV=false
    NO_LINT=false
    NO_SECURITY=false
    SPECIFIC_FILE=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -u|--unit)
                RUN_UNIT=true
                RUN_ALL=false
                shift
                ;;
            -i|--integration)
                RUN_INTEGRATION=true
                RUN_ALL=false
                shift
                ;;
            -a|--all)
                RUN_ALL=true
                shift
                ;;
            -l|--lint)
                RUN_LINT=true
                RUN_ALL=false
                shift
                ;;
            -s|--security)
                RUN_SECURITY=true
                RUN_ALL=false
                shift
                ;;
            -p|--performance)
                RUN_PERFORMANCE=true
                RUN_ALL=false
                shift
                ;;
            -g|--graphrag)
                RUN_GRAPHRAG=true
                RUN_ALL=false
                shift
                ;;
            -e|--evaluation)
                RUN_EVALUATION=true
                RUN_ALL=false
                shift
                ;;
            -f|--file)
                SPECIFIC_FILE="$2"
                RUN_ALL=false
                shift 2
                ;;
            -r|--report)
                RUN_REPORT=true
                RUN_ALL=false
                shift
                ;;
            -c|--clean)
                RUN_CLEAN=true
                RUN_ALL=false
                shift
                ;;
            --no-cov)
                NO_COV=true
                shift
                ;;
            --no-lint)
                NO_LINT=true
                shift
                ;;
            --no-security)
                NO_SECURITY=false
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    echo "🧪 Movies GraphRAG Demo - Test Suite"
    echo "===================================="
    echo ""
    
    # Check virtual environment
    check_venv
    
    # Activate virtual environment
    activate_venv
    
    # Install test dependencies
    install_test_deps
    
    # Run specific test file
    if [ -n "$SPECIFIC_FILE" ]; then
        run_specific_test "$SPECIFIC_FILE"
        exit 0
    fi
    
    # Run linting
    if [ "$RUN_LINT" = true ] && [ "$NO_LINT" = false ]; then
        run_linting
    fi
    
    # Run security checks
    if [ "$RUN_SECURITY" = true ] && [ "$NO_SECURITY" = false ]; then
        run_security_checks
    fi
    
    # Run unit tests
    if [ "$RUN_UNIT" = true ]; then
        run_unit_tests
    fi
    
    # Run integration tests
    if [ "$RUN_INTEGRATION" = true ]; then
        run_integration_tests
    fi
    
    # Run performance tests
    if [ "$RUN_PERFORMANCE" = true ]; then
        run_performance_tests
    fi
    
    # Run GraphRAG tests
    if [ "$RUN_GRAPHRAG" = true ]; then
        run_graphrag_tests
    fi
    
    # Run evaluation tests
    if [ "$RUN_EVALUATION" = true ]; then
        run_evaluation_tests
    fi
    
    # Run all tests
    if [ "$RUN_ALL" = true ]; then
        run_all_tests
    fi
    
    # Generate test report
    if [ "$RUN_REPORT" = true ]; then
        generate_test_report
    fi
    
    # Clean up
    if [ "$RUN_CLEAN" = true ]; then
        cleanup
    fi
    
    print_success "Test suite completed successfully!"
}

# Run main function
main "$@"

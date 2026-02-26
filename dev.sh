#!/bin/bash

# Development helper script for OCR Service

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

echo_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Setup virtual environment
setup_venv() {
    echo_info "Setting up Python virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo_info "Virtual environment created"
    else
        echo_info "Virtual environment already exists"
    fi
    
    source venv/bin/activate
    echo_info "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    echo_info "✓ Virtual environment ready"
}

# Initialize database
init_db() {
    echo_info "Initializing database..."
    source venv/bin/activate
    python -c "from app.db.session import init_db; init_db(); print('Database initialized')"
    echo_info "✓ Database ready"
}

# Run development server
run_dev() {
    echo_info "Starting development server..."
    source venv/bin/activate
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}

# Run tests
run_tests() {
    echo_info "Running tests..."
    source venv/bin/activate
    pytest tests/ -v --cov=app --cov-report=term-missing
}

# Format code
format_code() {
    echo_info "Formatting code with black..."
    source venv/bin/activate
    black app/ tests/
    echo_info "✓ Code formatted"
}

# Lint code
lint_code() {
    echo_info "Linting code..."
    source venv/bin/activate
    flake8 app/ tests/ --max-line-length=100 --exclude=venv
    echo_info "✓ Linting complete"
}

# Docker commands
docker_build() {
    echo_info "Building Docker image..."
    docker build -t ocr-service:latest .
    echo_info "✓ Docker image built"
}

docker_up() {
    echo_info "Starting Docker containers..."
    docker-compose up -d
    echo_info "✓ Containers started"
    echo_info "API available at: http://localhost:8000"
    echo_info "API docs at: http://localhost:8000/docs"
}

docker_down() {
    echo_info "Stopping Docker containers..."
    docker-compose down
    echo_info "✓ Containers stopped"
}

docker_logs() {
    docker-compose logs -f
}

# Show help
show_help() {
    cat << EOF
OCR Service Development Helper

Usage: ./dev.sh [command]

Commands:
    setup       Set up Python virtual environment and install dependencies
    db-init     Initialize database tables
    run         Run development server (with hot reload)
    test        Run test suite with coverage
    format      Format code with black
    lint        Lint code with flake8
    
Docker Commands:
    docker-build    Build Docker image
    docker-up       Start Docker containers (app + database)
    docker-down     Stop Docker containers
    docker-logs     Show container logs
    
Examples:
    ./dev.sh setup       # First time setup
    ./dev.sh run         # Start development server
    ./dev.sh test        # Run tests
    ./dev.sh docker-up   # Start with Docker

EOF
}

# Main script
case "$1" in
    setup)
        setup_venv
        ;;
    db-init)
        init_db
        ;;
    run)
        run_dev
        ;;
    test)
        run_tests
        ;;
    format)
        format_code
        ;;
    lint)
        lint_code
        ;;
    docker-build)
        docker_build
        ;;
    docker-up)
        docker_up
        ;;
    docker-down)
        docker_down
        ;;
    docker-logs)
        docker_logs
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac

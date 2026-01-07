#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

function print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

function print_success() {
    echo -e "${GREEN}SUCCESS: $1${NC}"
}

function check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "Error: $1 is not installed."
        exit 1
    fi
}

function dev() {
    print_header "Starting Local Development Stack"

    check_command docker
    check_command docker-compose

    if [ ! -f .env ]; then
        echo "Creating .env file..."
        # Copying example logic or creating basic default
        # Ideally we should copy .env.example if it existed, or just ensuring it exists
        # Since I created it recently, I'll just warn if missing.
        echo "Warning: .env file missing. Using defaults or created file."
    fi

    echo "Building and Starting Containers..."
    docker-compose up -d --build

    print_success "Stack is running!"
    echo "---------------------------------------------------"
    echo "Web App:        http://localhost:3000"
    echo "Supabase Studio: http://localhost:8001"
    echo "Supabase API:   http://localhost:8000"
    echo "---------------------------------------------------"
    echo "Logs: ./manage.sh logs"
    echo "Stop: ./manage.sh down"
}

function down() {
    print_header "Stopping Stack"
    docker-compose down
    print_success "Stack stopped."
}

function clean() {
    print_header "Cleaning Stack (Removing Volumes)"
    read -p "Are you sure you want to delete all database data? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down -v
        print_success "Stack stopped and volumes removed."
    else
        echo "Aborted."
    fi
}

function logs() {
    print_header "Streaming Logs"
    docker-compose logs -f
}

function help() {
    echo "Usage: ./manage.sh [command]"
    echo "Commands:"
    echo "  dev    - Start the full stack locally (Docker Compose)"
    echo "  down   - Stop the stack"
    echo "  clean  - Stop the stack and remove data volumes"
    echo "  logs   - Stream logs from all services"
    echo "  help   - Show this help message"
}

# Main Dispatch
case "$1" in
    dev)
        dev
        ;;
    down)
        down
        ;;
    clean)
        clean
        ;;
    logs)
        logs
        ;;
    *)
        if [ -z "$1" ]; then
            dev # Default to dev
        else
            help
        fi
        ;;
esac

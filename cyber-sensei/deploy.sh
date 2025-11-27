#!/bin/bash

# Deployment script for CYBER-SENSEI (Linux/macOS)
# This script deploys the application locally using Docker Compose

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$SCRIPT_DIR"

echo
echo "========================================"
echo "  CYBER-SENSEI Local Deployment"
echo "========================================"
echo

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "[ERROR] Docker is not installed or not in PATH"
    echo "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "[ERROR] Docker Compose is not installed"
    echo "Please install Docker Compose from https://docs.docker.com/compose/install/"
    exit 1
fi

echo "[INFO] Docker and Docker Compose are installed"
echo

# Default command
COMMAND=${1:-start}

case "$COMMAND" in
    start)
        echo "[INFO] Starting CYBER-SENSEI..."
        echo

        # Create necessary directories
        mkdir -p data/knowledge_db data/transcripts

        echo "[INFO] Building Docker images..."
        docker-compose -f docker-compose.prod.yml build --no-cache

        echo
        echo "[INFO] Starting services..."
        docker-compose -f docker-compose.prod.yml up -d

        echo
        echo "[INFO] Waiting for services to be healthy..."
        sleep 15

        echo
        echo "[SUCCESS] CYBER-SENSEI is starting up!"
        echo
        echo "Available services:"
        echo "  - Frontend:    http://localhost"
        echo "  - Backend API: http://localhost:8000"
        echo "  - Kibana:      http://localhost:5601"
        echo "  - PostgreSQL:  localhost:5432"
        echo "  - Redis:       localhost:6379"
        echo
        echo "[INFO] Use './deploy.sh logs' to view logs"
        echo "[INFO] Use './deploy.sh stop' to stop services"
        echo
        ;;

    stop)
        echo "[INFO] Stopping CYBER-SENSEI..."
        docker-compose -f docker-compose.prod.yml down
        echo "[SUCCESS] CYBER-SENSEI stopped"
        ;;

    restart)
        echo "[INFO] Restarting CYBER-SENSEI..."
        docker-compose -f docker-compose.prod.yml restart
        echo "[SUCCESS] CYBER-SENSEI restarted"
        ;;

    logs)
        echo "[INFO] Showing logs (Press Ctrl+C to stop)..."
        docker-compose -f docker-compose.prod.yml logs -f --tail=100
        ;;

    status)
        echo "[INFO] Service status:"
        docker-compose -f docker-compose.prod.yml ps
        ;;

    clean)
        echo "[WARNING] This will remove all containers, volumes, and data!"
        read -p "Continue? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "[INFO] Cleaning up..."
            docker-compose -f docker-compose.prod.yml down -v

            echo "[INFO] Removing data directories..."
            rm -rf data

            echo "[SUCCESS] Cleanup complete"
        fi
        ;;

    help)
        echo "Usage: ./deploy.sh [COMMAND]"
        echo
        echo "Commands:"
        echo "  start       - Start CYBER-SENSEI (default)"
        echo "  stop        - Stop CYBER-SENSEI"
        echo "  restart     - Restart CYBER-SENSEI"
        echo "  logs        - View service logs"
        echo "  status      - Show service status"
        echo "  clean       - Remove all containers, volumes, and data"
        echo "  help        - Show this help message"
        echo
        ;;

    *)
        echo "[ERROR] Unknown command: $COMMAND"
        echo "Use './deploy.sh help' for usage information"
        exit 1
        ;;
esac

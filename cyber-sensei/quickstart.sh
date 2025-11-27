#!/bin/bash

# Quick start script for CYBER-SENSEI development
# This script sets up the development environment

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$SCRIPT_DIR"

echo
echo "=========================================="
echo "  CYBER-SENSEI Quick Start Setup"
echo "=========================================="
echo

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    echo "📥 Install Docker Desktop from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

echo "✅ Docker is installed"

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed"
    echo "📥 Install Docker Compose from: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker Compose is installed"
echo

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/knowledge_db data/transcripts
echo "✅ Directories created"
echo

# Create .env files if they don't exist
if [ ! -f ".env.development" ]; then
    echo "📝 Creating .env.development..."
    cp .env.development .env.development 2>/dev/null || true
fi

if [ ! -f ".env.production" ]; then
    echo "📝 Creating .env.production..."
    cp .env.production .env.production 2>/dev/null || true
fi

echo
echo "=========================================="
echo "  ✅ Setup Complete!"
echo "=========================================="
echo
echo "🚀 Next steps:"
echo
echo "   Option 1: Start development (quick, hot-reload)"
echo "   $ docker-compose up"
echo
echo "   Option 2: Start production (optimized, background)"
echo "   $ ./deploy.sh start"
echo "   Windows: deploy.bat start"
echo
echo "📚 For full guide, see: DEPLOYMENT_GUIDE.md"
echo
echo "Access services at:"
echo "  • Frontend:  http://localhost:3000 (dev) or http://localhost (prod)"
echo "  • API:       http://localhost:8000"
echo "  • Docs:      http://localhost:8000/docs"
echo "  • Kibana:    http://localhost:5601"
echo

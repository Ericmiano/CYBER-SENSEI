@echo off
REM Quick start script for CYBER-SENSEI development
REM This script sets up the development environment

setlocal enabledelayedexpansion

echo.
echo ==========================================
echo   CYBER-SENSEI Quick Start Setup
echo ==========================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo.❌ Docker is not installed
    echo.📥 Install Docker Desktop from: https://www.docker.com/products/docker-desktop
    exit /b 1
)

echo.✅ Docker is installed

REM Check if Docker Compose is available
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo.❌ Docker Compose is not installed
    echo.📥 Install Docker Compose from: https://docs.docker.com/compose/install/
    exit /b 1
)

echo.✅ Docker Compose is installed
echo.

REM Create necessary directories
echo.📁 Creating directories...
if not exist data mkdir data
if not exist data\knowledge_db mkdir data\knowledge_db
if not exist data\transcripts mkdir data\transcripts
echo.✅ Directories created
echo.

REM Create .env files if they don't exist
if not exist ".env.development" (
    echo.📝 Creating .env.development...
    copy ".env.development" ".env.development" >nul 2>&1
)

if not exist ".env.production" (
    echo.📝 Creating .env.production...
    copy ".env.production" ".env.production" >nul 2>&1
)

echo.
echo ==========================================
echo   ✅ Setup Complete!
echo ==========================================
echo.
echo.🚀 Next steps:
echo.
echo.   Option 1: Start development (quick, hot-reload)
echo.   docker-compose up
echo.
echo.   Option 2: Start production (optimized, background)
echo.   deploy.bat start
echo.
echo.📚 For full guide, see: DEPLOYMENT_GUIDE.md
echo.
echo.Access services at:
echo.  • Frontend:  http://localhost:3000 (dev) or http://localhost (prod)
echo.  • API:       http://localhost:8000
echo.  • Docs:      http://localhost:8000/docs
echo.  • Kibana:    http://localhost:5601
echo.

endlocal

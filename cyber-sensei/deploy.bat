@echo off
REM Deployment script for CYBER-SENSEI (Windows)
REM This script deploys the application locally using Docker Compose

setlocal enabledelayedexpansion
set SCRIPT_DIR=%~dp0
set PROJECT_DIR=%SCRIPT_DIR%

echo.
echo ========================================
echo   CYBER-SENSEI Local Deployment
echo ========================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed or not in PATH
    echo Please install Docker Desktop from https://www.docker.com/products/docker-desktop
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose is not installed
    echo Please install Docker Desktop which includes Docker Compose
    exit /b 1
)

echo [INFO] Docker and Docker Compose are installed
echo.

REM Parse command line arguments
set COMMAND=%1
if "%COMMAND%"=="" set COMMAND=start

if "%COMMAND%"=="start" goto start
if "%COMMAND%"=="stop" goto stop
if "%COMMAND%"=="restart" goto restart
if "%COMMAND%"=="logs" goto logs
if "%COMMAND%"=="status" goto status
if "%COMMAND%"=="clean" goto clean
if "%COMMAND%"=="help" goto help

echo [ERROR] Unknown command: %COMMAND%
goto help

:start
echo [INFO] Starting CYBER-SENSEI...
echo.

REM Create necessary directories
if not exist data mkdir data
if not exist data\knowledge_db mkdir data\knowledge_db
if not exist data\transcripts mkdir data\transcripts

echo [INFO] Building Docker images...
docker-compose -f docker-compose.prod.yml build --no-cache

if errorlevel 1 (
    echo [ERROR] Failed to build Docker images
    exit /b 1
)

echo.
echo [INFO] Starting services...
docker-compose -f docker-compose.prod.yml up -d

if errorlevel 1 (
    echo [ERROR] Failed to start services
    exit /b 1
)

echo.
echo [INFO] Waiting for services to be healthy...
timeout /t 15 /nobreak

echo.
echo [SUCCESS] CYBER-SENSEI is starting up!
echo.
echo Available services:
echo   - Frontend:    http://localhost
echo   - Backend API: http://localhost:8000
echo   - Kibana:      http://localhost:5601
echo   - PostgreSQL:  localhost:5432
echo   - Redis:       localhost:6379
echo.
echo [INFO] Use 'deploy.bat logs' to view logs
echo [INFO] Use 'deploy.bat stop' to stop services
echo.
goto end

:stop
echo [INFO] Stopping CYBER-SENSEI...
docker-compose -f docker-compose.prod.yml down

if errorlevel 1 (
    echo [ERROR] Failed to stop services
    exit /b 1
)

echo [SUCCESS] CYBER-SENSEI stopped
goto end

:restart
echo [INFO] Restarting CYBER-SENSEI...
docker-compose -f docker-compose.prod.yml restart

if errorlevel 1 (
    echo [ERROR] Failed to restart services
    exit /b 1
)

echo [SUCCESS] CYBER-SENSEI restarted
goto end

:logs
echo [INFO] Showing logs (Press Ctrl+C to stop)...
docker-compose -f docker-compose.prod.yml logs -f --tail=100
goto end

:status
echo [INFO] Service status:
docker-compose -f docker-compose.prod.yml ps
goto end

:clean
echo [WARNING] This will remove all containers, volumes, and data!
set /p confirm="Continue? (y/n): "
if /i not "%confirm%"=="y" goto end

echo [INFO] Cleaning up...
docker-compose -f docker-compose.prod.yml down -v

echo [INFO] Removing data directories...
if exist data rmdir /s /q data

echo [SUCCESS] Cleanup complete
goto end

:help
echo Usage: deploy.bat [COMMAND]
echo.
echo Commands:
echo   start       - Start CYBER-SENSEI (default)
echo   stop        - Stop CYBER-SENSEI
echo   restart     - Restart CYBER-SENSEI
echo   logs        - View service logs
echo   status      - Show service status
echo   clean       - Remove all containers, volumes, and data
echo   help        - Show this help message
echo.
goto end

:end
endlocal

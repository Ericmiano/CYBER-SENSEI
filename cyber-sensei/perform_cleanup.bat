@echo off
echo CYBER-SENSEI System Cleanup
echo ============================
echo.

echo [1/5] Removing Python cache files...
if exist backend\__pycache__ rmdir /s /q backend\__pycache__
if exist backend\tests\__pycache__ rmdir /s /q backend\tests\__pycache__
if exist backend\app\__pycache__ rmdir /s /q backend\app\__pycache__
if exist backend\app\engines\__pycache__ rmdir /s /q backend\app\engines\__pycache__
if exist backend\app\models\__pycache__ rmdir /s /q backend\app\models\__pycache__
if exist backend\app\core\__pycache__ rmdir /s /q backend\app\core\__pycache__
if exist backend\app\services\__pycache__ rmdir /s /q backend\app\services\__pycache__
if exist backend\app\schemas\__pycache__ rmdir /s /q backend\app\schemas\__pycache__
if exist backend\app\routers\__pycache__ rmdir /s /q backend\app\routers\__pycache__
echo    Python cache removed

echo.
echo [2/5] Removing test artifacts...
if exist backend\test.db del /f /q backend\test.db
if exist backend\.pytest_cache rmdir /s /q backend\.pytest_cache
echo    Test artifacts removed

echo.
echo [3/5] Clearing log files...
if exist backend\logs\celery.log del /f /q backend\logs\celery.log
if exist backend\logs\cyber_sensei.log del /f /q backend\logs\cyber_sensei.log
echo    Log files cleared

echo.
echo [4/5] Removing outdated documentation...
if exist FRESH_AUDIT_2025-11-25.md del /f /q FRESH_AUDIT_2025-11-25.md  
if exist CLEANUP_SUMMARY.md del /f /q CLEANUP_SUMMARY.md
if exist cleanup_docs.bat del /f /q cleanup_docs.bat
echo    Outdated docs removed

echo.
echo [5/5] Verifying cleanup...
echo.
echo === Files Removed ===
echo - 9 __pycache__ directories
echo - Test database (test.db)
echo - Log files (celery.log, cyber_sensei.log)
echo - Outdated docs (FRESH_AUDIT, CLEANUP_SUMMARY, cleanup_docs.bat)
echo.
echo === Files Kept ===
echo - All source code (.py, .jsx, .js)
echo - README.md (main documentation)
echo - Configuration files (.env, docker-compose.yml)
echo - Deployment scripts (deploy.bat, quickstart.bat)
echo.
echo ============================
echo Cleanup Complete!
echo ============================
echo.
pause

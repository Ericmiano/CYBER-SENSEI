@echo off
REM Cleanup redundant documentation files

cd /d d:\CYBER-SENSEI\cyber-sensei

del "00-START-HERE.md" 2>nul
del "DEPLOYMENT_README.md" 2>nul
del "DEPLOYMENT_COMPLETE.md" 2>nul
del "DEPLOYMENT_SUMMARY.md" 2>nul
del "DOCKER_DEPLOYMENT.md" 2>nul
del "FREE_DEPLOYMENT.md" 2>nul
del "README_IMPROVEMENTS.md" 2>nul
del "QUICK_REFERENCE.md" 2>nul
del "COMPLETE_IMPLEMENTATION_GUIDE.md" 2>nul
del "IMPLEMENTATION_COMPLETE.md" 2>nul
del "IMPLEMENTATION_SUMMARY.md" 2>nul
del "IMPROVEMENTS_IMPLEMENTATION_GUIDE.md" 2>nul
del "PROJECT_COMPLETION_REPORT.md" 2>nul
del "STATUS_REPORT.md" 2>nul

echo Documentation cleanup complete
echo Remaining docs:
dir /b *.md

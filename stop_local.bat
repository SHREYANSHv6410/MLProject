@echo off
echo ========================================================
echo        Stopping ReplySense Services...
echo ========================================================

taskkill /F /FI "WINDOWTITLE eq ReplySense*" /T 2>nul
taskkill /F /IM node.exe 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173') do taskkill /F /PID %%a 2>nul

echo.
echo ReplySense backend (port 8000) and frontend (port 5173) have been stopped.
echo ========================================================
pause

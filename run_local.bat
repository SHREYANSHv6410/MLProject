@echo off
echo ========================================================
echo        Starting ReplySense (Local Native Mode)
echo ========================================================
echo.

start "ReplySense Backend (Port 8000)" cmd /k "python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000"

echo Backend started on http://127.0.0.1:8000
echo Starting Frontend...
echo.

cd frontend
start "ReplySense Frontend (Port 5173)" cmd /k "npm run dev"

timeout /t 3 >nul
start http://localhost:5173

echo ReplySense is opening in your browser at http://localhost:5173!
echo.

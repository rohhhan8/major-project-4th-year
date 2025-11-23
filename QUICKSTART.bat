@echo off
REM Quick Start Script for Adaptive Learning Platform

echo.
echo ========================================
echo Adaptive Learning Platform - Quick Start
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Download from: https://www.python.org/
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Download from: https://nodejs.org/
    pause
    exit /b 1
)

echo [✓] Python and Node.js found
echo.

REM Setup Backend
echo ========================================
echo Setting up Backend...
echo ========================================
cd backend

if not exist venv (
    echo Creating Python virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing backend dependencies...
pip install -r requirements.txt

if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo [!] Please configure .env with your MongoDB connection string
)

echo Loading quiz data...
python load_quizzes.py

echo.
echo Backend setup complete!
echo To start the backend server: cd backend && venv\Scripts\activate.bat && python main.py
echo.

REM Setup Frontend
echo ========================================
echo Setting up Frontend...
echo ========================================
cd ..\frontend

echo Installing frontend dependencies...
call npm install

echo.
echo Frontend setup complete!
echo To start the frontend server: cd frontend && npm run dev
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Open two terminals
echo 2. Terminal 1 - Backend:
echo    cd backend
echo    venv\Scripts\activate
echo    python main.py
echo.
echo 3. Terminal 2 - Frontend:
echo    cd frontend
echo    npm run dev
echo.
echo Frontend will open at: http://localhost:5173
echo Backend API docs: http://localhost:8000/docs
echo.
pause

# Adaptive Learning Platform - Quick Start Script (PowerShell)
# Run as: .\QUICKSTART.ps1

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Adaptive Learning Platform - Quick Start" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[✓] Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[✗] Python not found. Download from: https://www.python.org/" -ForegroundColor Red
    exit 1
}

# Check Node.js
try {
    $nodeVersion = node --version
    $npmVersion = npm --version
    Write-Host "[✓] Node.js found: $nodeVersion" -ForegroundColor Green
    Write-Host "[✓] npm found: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "[✗] Node.js not found. Download from: https://nodejs.org/" -ForegroundColor Red
    exit 1
}

# Setup Backend
Write-Host "`n========================================" -ForegroundColor Yellow
Write-Host "Setting up Backend..." -ForegroundColor Yellow
Write-Host "========================================`n" -ForegroundColor Yellow

Set-Location backend

if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Cyan
    python -m venv venv
}

Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& .\venv\Scripts\Activate.ps1

Write-Host "Installing backend dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt

if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "[!] Configure .env with your MongoDB connection string" -ForegroundColor Yellow
}

Write-Host "Loading quiz data..." -ForegroundColor Cyan
python load_quizzes.py

Write-Host "`n[✓] Backend setup complete!" -ForegroundColor Green
Write-Host "To start backend: cd backend && .\venv\Scripts\Activate.ps1 && python main.py`n" -ForegroundColor Cyan

# Setup Frontend
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "Setting up Frontend..." -ForegroundColor Yellow
Write-Host "========================================`n" -ForegroundColor Yellow

Set-Location ..\frontend

Write-Host "Installing frontend dependencies..." -ForegroundColor Cyan
npm install

Write-Host "`n[✓] Frontend setup complete!" -ForegroundColor Green
Write-Host "To start frontend: cd frontend && npm run dev`n" -ForegroundColor Cyan

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Open two PowerShell terminals`n" -ForegroundColor White

Write-Host "2. Terminal 1 - Backend:" -ForegroundColor White
Write-Host "   cd backend" -ForegroundColor Gray
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "   python main.py`n" -ForegroundColor Gray

Write-Host "3. Terminal 2 - Frontend:" -ForegroundColor White
Write-Host "   cd frontend" -ForegroundColor Gray
Write-Host "   npm run dev`n" -ForegroundColor Gray

Write-Host "Frontend: http://localhost:5173" -ForegroundColor Green
Write-Host "Backend Docs: http://localhost:8000/docs`n" -ForegroundColor Green

@echo off
REM Quick start script for Care Triage (Windows)

echo 🏥 Care Triage - Quick Start Setup
echo ==================================

REM Check prerequisites
echo Checking prerequisites...

python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.11+
    exit /b 1
)

node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found. Please install Node.js 20+
    exit /b 1
)

echo ✅ Prerequisites OK

REM Backend setup
echo.
echo Setting up backend...
cd backend

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt

if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
    echo ⚠️  Please edit backend\.env with your Azure credentials
)

echo ✅ Backend setup complete

REM Frontend setup
echo.
echo Setting up frontend...
cd ..\frontend

if not exist "node_modules" (
    echo Installing npm dependencies...
    call npm install
)

echo ✅ Frontend setup complete

REM Summary
echo.
echo 🎉 Setup Complete!
echo ==================
echo.
echo Next steps:
echo 1. Edit backend\.env with your Azure credentials
echo 2. Start backend:  cd backend ^&^& venv\Scripts\activate ^&^& python app.py
echo 3. Start frontend: cd frontend ^&^& npm run dev
echo 4. Open browser:   http://localhost:5173
echo.
echo For detailed instructions, see SETUP.md

pause

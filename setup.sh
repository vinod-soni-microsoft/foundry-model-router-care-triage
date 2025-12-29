#!/bin/bash
# Quick start script for Care Triage

echo "🏥 Care Triage - Quick Start Setup"
echo "=================================="

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.11+"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 20+"
    exit 1
fi

echo "✅ Prerequisites OK"

# Backend setup
echo ""
echo "Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit backend/.env with your Azure credentials"
fi

echo "✅ Backend setup complete"

# Frontend setup
echo ""
echo "Setting up frontend..."
cd ../frontend

if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install
fi

echo "✅ Frontend setup complete"

# Summary
echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "Next steps:"
echo "1. Edit backend/.env with your Azure credentials"
echo "2. Start backend:  cd backend && source venv/bin/activate && python app.py"
echo "3. Start frontend: cd frontend && npm run dev"
echo "4. Open browser:   http://localhost:5173"
echo ""
echo "For detailed instructions, see SETUP.md"

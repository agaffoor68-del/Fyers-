#!/usr/bin/env bash
set -e

echo "========================================"
echo "  Grok AI Trading Platform Setup"
echo "========================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Python3 not found. Please install Python 3.10+"
    exit 1
fi

# Check Node
if ! command -v node &> /dev/null; then
    echo "Node.js not found. Please install Node 18+"
    exit 1
fi

# Backend Setup
echo ""
echo "[1/3] Setting up Backend..."
cd backend

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Copy .env
if [ ! -f ".env" ]; then
    cp ../.env.example .env
    echo "Please edit backend/.env with your API keys"
fi

# Initialize DB
python -c "from app.db.init_db import init_db; init_db()"

echo "Backend setup complete!"

# Frontend Setup
echo ""
echo "[2/3] Setting up Frontend..."
cd ../frontend

if [ ! -d "node_modules" ]; then
    npm install
fi

echo "Frontend setup complete!"

# Final
echo ""
echo "[3/3] Setup Complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your API keys (XAI_API_KEY, FYERS_CLIENT_ID, FYERS_ACCESS_TOKEN)"
echo "  2. Run: ./start.sh"
echo ""

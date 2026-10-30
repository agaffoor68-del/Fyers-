#!/usr/bin/env bash
set -e

echo "========================================"
echo "  Starting Grok AI Trading Platform"
echo "========================================"

# Start Backend
echo "[1/2] Starting Backend (FastAPI)..."
cd /workspaces/Fyers-/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to be ready
echo "Waiting for backend to start..."
sleep 3

# Start Frontend
echo "[2/2] Starting Frontend (Next.js)..."
cd /workspaces/Fyers-/frontend
npm run dev &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

echo ""
echo "========================================"
echo "  Platform is running!"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "========================================"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID

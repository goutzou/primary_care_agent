#!/bin/bash

echo "🚀 Starting Primary Care Agent..."

# Start backend
echo "▶️ Starting backend on port 8000..."
uvicorn backend.server:app --reload --port 8000 &
BACKEND_PID=$!

# Start frontend
echo "▶️ Starting frontend on port 5173..."
cd frontend
npm run dev &
FRONTEND_PID=$!

# Kill both on exit
trap "kill $BACKEND_PID $FRONTEND_PID" EXIT

wait

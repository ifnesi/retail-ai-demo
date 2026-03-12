#!/bin/bash

echo "🏪 UrbanStreet Retail AI Demo - Startup Script"
echo "=============================================="
echo ""

echo "🚀 Starting demo application..."
echo ""
echo "Backend will run on: http://localhost:8000"
echo "Frontend will run on: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    deactivate 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Extract system prompts from SQL files
echo "📝 Extracting system prompts from SQL files..."
source .venv/bin/activate
python backend/utils/extract_prompts.py
if [ $? -ne 0 ]; then
    echo "❌ Failed to extract system prompts"
    exit 1
fi
echo ""

# Start backend
python backend/app.py &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 3

# Start frontend
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

# Wait for both processes
wait

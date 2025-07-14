#!/bin/bash

# Activate virtual environment and start the Flask backend
echo "Starting Flask backend..."
source venv/bin/activate && python app.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

# Start the React frontend
echo "Starting React frontend..."
cd frontend && npm start &
FRONTEND_PID=$!

# Function to cleanup on exit
cleanup() {
    echo "Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Trap Ctrl+C and call cleanup
trap cleanup SIGINT

# Wait for both processes
wait 
#!/bin/bash

# Start the FastAPI backend
echo "Starting FastAPI backend..."
uvicorn src.infrastructure.api.main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait a bit for the backend to start
sleep 2

# Start the React frontend
echo "Starting React frontend..."
cd frontend && npm start &
FRONTEND_PID=$!

# Function to handle script termination
cleanup() {
    echo "Shutting down servers..."
    kill $BACKEND_PID
    kill $FRONTEND_PID
    exit 0
}

# Register the cleanup function for script termination
trap cleanup SIGINT SIGTERM

# Keep the script running
wait

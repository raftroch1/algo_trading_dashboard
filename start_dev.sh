#!/bin/bash

# Install any missing packages
pip install -r requirements.txt

# Setup frontend environment if needed
if [ ! -f frontend/.env ]; then
    echo "Setting up frontend environment..."
    cp frontend/.env.template frontend/.env
    echo "Created frontend/.env from template"
fi

# Start the FastAPI backend on port 8080
echo "Starting FastAPI backend on port 8080..."
uvicorn src.infrastructure.api.main:app --reload --port 8080 --log-level info &
BACKEND_PID=$!

# Wait a bit for the backend to start and show status
sleep 2
echo "Backend should be running at http://localhost:8080"
echo "API documentation available at http://localhost:8080/docs"

# Start the React frontend on port 3001
echo "Starting React frontend on port 3001..."
cd frontend && npm start &
FRONTEND_PID=$!

echo "Frontend should be available at http://localhost:3001"

# Function to handle script termination
cleanup() {
    echo "Shutting down servers..."
    kill $BACKEND_PID
    kill $FRONTEND_PID
    exit 0
}

# Register the cleanup function for script termination
trap cleanup SIGINT SIGTERM

# Keep the script running and show status every 30 seconds
while true; do
    echo "Services status check ($(date)):"
    if ps -p $BACKEND_PID > /dev/null; then
        echo "✅ Backend is running (PID: $BACKEND_PID)"
    else
        echo "❌ Backend is not running"
    fi
    if ps -p $FRONTEND_PID > /dev/null; then
        echo "✅ Frontend is running (PID: $FRONTEND_PID)"
    else
        echo "❌ Frontend is not running"
    fi
    sleep 30
done

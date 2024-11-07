#!/bin/bash

# Function to check if a port is available
check_port() {
    local port=$1
    if ! lsof -i :$port > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to find next available port starting from a base port
find_available_port() {
    local port=$1
    while ! check_port $port; do
        echo "Port $port is in use, trying next port..."
        port=$((port + 1))
    done
    echo $port
}

# Install any missing packages
pip install -r requirements.txt

# Find available ports
BACKEND_PORT=$(find_available_port 8080)
FRONTEND_PORT=$(find_available_port 3000)

echo "Using ports: Backend=$BACKEND_PORT, Frontend=$FRONTEND_PORT"

# Create or update frontend environment file
cat > frontend/.env << EOL
REACT_APP_API_URL=http://localhost:${BACKEND_PORT}
REACT_APP_WS_URL=ws://localhost:${BACKEND_PORT}
PORT=${FRONTEND_PORT}
EOL

# Start the FastAPI backend
echo "Starting FastAPI backend on port ${BACKEND_PORT}..."
uvicorn src.infrastructure.api.main:app --reload --port $BACKEND_PORT --log-level info &
BACKEND_PID=$!

# Wait a bit for the backend to start and show status
sleep 2
echo "Backend should be running at http://localhost:${BACKEND_PORT}"
echo "API documentation available at http://localhost:${BACKEND_PORT}/docs"

# Start the React frontend
echo "Starting React frontend on port ${FRONTEND_PORT}..."
cd frontend && npm start &
FRONTEND_PID=$!

echo "Frontend should be available at http://localhost:${FRONTEND_PORT}"

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
        echo "✅ Backend is running on port ${BACKEND_PORT} (PID: $BACKEND_PID)"
    else
        echo "❌ Backend is not running"
    fi
    if ps -p $FRONTEND_PID > /dev/null; then
        echo "✅ Frontend is running on port ${FRONTEND_PORT} (PID: $FRONTEND_PID)"
    else
        echo "❌ Frontend is not running"
    fi
    sleep 30
done

#!/bin/bash

echo "Stopping and removing all Docker containers..."
docker stop $(docker ps -aq) 2>/dev/null
docker rm $(docker ps -aq) 2>/dev/null

echo "Checking for processes using common development ports..."
for port in 3000 3001 3002 8000 8080 8086; do
    pid=$(lsof -ti :$port)
    if [ ! -z "$pid" ]; then
        echo "Killing process using port $port (PID: $pid)..."
        kill -9 $pid 2>/dev/null
    fi
done

echo "Starting fresh InfluxDB container..."
docker run -d --name influxdb -p 8086:8086 influxdb:latest

echo "Waiting for InfluxDB to start..."
sleep 5

echo "Environment cleaned up and ready!"
echo "You can now run ./start_dev.sh to start the application."

#!/bin/bash

# StudyBuddy Development Server Stop Script
echo "🛑 Stopping StudyBuddy development servers..."

# Function to stop process by PID file
stop_process() {
    local pid_file=$1
    local service_name=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            echo "✅ Stopped $service_name (PID: $pid)"
        else
            echo "⚠️  $service_name process not found"
        fi
        rm -f "$pid_file"
    else
        echo "⚠️  No PID file found for $service_name"
    fi
}

# Stop backend
stop_process ".backend.pid" "Backend"

# Stop frontend
stop_process ".frontend.pid" "Frontend"

# Kill any remaining processes on our ports
echo "🔧 Cleaning up remaining processes..."

# Kill processes on port 8000 (backend)
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Kill processes on port 3000 (frontend)
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

echo "✅ All servers stopped"

# Optionally stop MongoDB and Redis (commented out by default)
# echo "🔧 Stopping MongoDB and Redis..."
# pkill mongod
# pkill redis-server
# echo "✅ MongoDB and Redis stopped"

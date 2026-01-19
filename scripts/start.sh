#!/bin/bash

# StudyBuddy Development Server Startup Script
echo "🚀 Starting StudyBuddy development servers..."

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Port $1 is already in use"
        return 1
    fi
    return 0
}

# Check required ports
check_port 3000 || exit 1  # Frontend
check_port 8000 || exit 1  # Backend
check_port 27017 || echo "⚠️  MongoDB port 27017 in use (this is expected if MongoDB is running)"
check_port 6379 || echo "⚠️  Redis port 6379 in use (this is expected if Redis is running)"

# Start MongoDB if not running
if ! pgrep mongod > /dev/null; then
    echo "🔧 Starting MongoDB..."
    mongod --dbpath ./data/db --fork --logpath ./data/mongodb.log
    sleep 2
fi

# Start Redis if not running
if ! pgrep redis-server > /dev/null; then
    echo "🔧 Starting Redis..."
    redis-server --daemonize yes
    sleep 1
fi

# Create log directory
mkdir -p logs

echo "🔧 Starting backend server..."
cd backend
source venv/bin/activate
nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

echo "🔧 Starting frontend server..."
cd frontend
nohup npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait for servers to start
echo "⏳ Waiting for servers to start..."
sleep 5

# Check if servers are running
if kill -0 $BACKEND_PID 2>/dev/null; then
    echo "✅ Backend server running (PID: $BACKEND_PID)"
else
    echo "❌ Backend server failed to start"
    exit 1
fi

if kill -0 $FRONTEND_PID 2>/dev/null; then
    echo "✅ Frontend server running (PID: $FRONTEND_PID)"
else
    echo "❌ Frontend server failed to start"
    exit 1
fi

# Save PIDs for cleanup
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

echo ""
echo "🎉 All servers started successfully!"
echo ""
echo "📋 Server URLs:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📊 Logs:"
echo "   Backend:  tail -f logs/backend.log"
echo "   Frontend: tail -f logs/frontend.log"
echo ""
echo "🛑 To stop servers: ./scripts/stop.sh"

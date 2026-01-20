#!/bin/bash

echo "🔄 Starting Study Buddy servers..."

# Kill processes on ports 8000 and 3000
echo "🛑 Killing existing processes..."
fuser -k 8000/tcp 2>/dev/null || true
fuser -k 3000/tcp 2>/dev/null || true

# Wait for ports to be free
sleep 2

echo "🚀 Starting backend server..."
cd "/home/unknown/Documents/hackathon application/dynamous-kiro-hackathon/backend"
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "🚀 Starting frontend server..."
cd "/home/unknown/Documents/hackathon application/dynamous-kiro-hackathon/frontend"
npm run dev &
FRONTEND_PID=$!

# Wait for servers to start
sleep 5

echo "✅ Checking server status..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend: Running on http://localhost:8000"
else
    echo "❌ Backend: Failed to start"
fi

if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend: Running on http://localhost:3000"
else
    echo "⏳ Frontend: Still starting... (check http://localhost:3000)"
fi

echo "🎉 Both servers started!"
echo "📊 Backend API: http://localhost:8000"
echo "🌐 Frontend App: http://localhost:3000"
echo "📚 API Docs: http://localhost:8000/docs"

# Keep script running
wait

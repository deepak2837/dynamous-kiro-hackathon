#!/bin/bash

# StudyBuddy Development Setup Script
echo "🚀 Setting up StudyBuddy development environment..."

# Check if MongoDB is installed
if ! command -v mongod &> /dev/null; then
    echo "❌ MongoDB not found. Please install MongoDB 6.0+"
    echo "   Ubuntu/Debian: sudo apt install mongodb"
    echo "   macOS: brew install mongodb/brew/mongodb-community"
    exit 1
fi

# Check if Redis is installed
if ! command -v redis-server &> /dev/null; then
    echo "❌ Redis not found. Please install Redis 7.0+"
    echo "   Ubuntu/Debian: sudo apt install redis-server"
    echo "   macOS: brew install redis"
    exit 1
fi

# Check if Python 3.10+ is installed
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
if [[ $(echo "$python_version < 3.10" | bc -l) -eq 1 ]]; then
    echo "❌ Python 3.10+ required. Current version: $python_version"
    exit 1
fi

# Check if Node.js 18+ is installed
node_version=$(node --version 2>&1 | grep -oP '\d+' | head -1)
if [[ $node_version -lt 18 ]]; then
    echo "❌ Node.js 18+ required. Current version: $node_version"
    exit 1
fi

echo "✅ All prerequisites found"

# Create uploads directory
mkdir -p backend/uploads
echo "✅ Created uploads directory"

# Setup backend
echo "🔧 Setting up backend..."
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
echo "✅ Backend dependencies installed"

# Go back to root
cd ..

# Setup frontend
echo "🔧 Setting up frontend..."
cd frontend

# Dependencies already installed during commit
echo "✅ Frontend dependencies already installed"

# Go back to root
cd ..

echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Start MongoDB: mongod --dbpath /path/to/data"
echo "2. Start Redis: redis-server"
echo "3. Configure API keys in backend/.env"
echo "4. Start backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "5. Start frontend: cd frontend && npm run dev"
echo ""
echo "🌐 Access the application at http://localhost:3000"

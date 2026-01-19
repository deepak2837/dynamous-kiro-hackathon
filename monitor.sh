#!/bin/bash

echo "📊 StudyBuddy Server Monitor"
echo "============================"

# Function to check server status
check_servers() {
    echo -e "\n⏰ $(date '+%H:%M:%S') - Server Status Check"
    echo "----------------------------------------"
    
    # Check Backend
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ Backend (8000): Running"
    else
        echo "❌ Backend (8000): Down"
    fi
    
    # Check Frontend
    if curl -s http://localhost:3001/ > /dev/null; then
        echo "✅ Frontend (3001): Running"
    else
        echo "❌ Frontend (3001): Down"
    fi
    
    # Check recent logs
    echo -e "\n📋 Recent Backend Logs:"
    tail -n 3 logs/backend.log 2>/dev/null || echo "No backend logs found"
    
    echo -e "\n📋 Recent Frontend Logs:"
    tail -n 3 logs/frontend.log 2>/dev/null || echo "No frontend logs found"
}

# Initial check
check_servers

echo -e "\n🔄 Monitoring every 30 seconds... (Press Ctrl+C to stop)"

# Monitor loop
while true; do
    sleep 30
    check_servers
done

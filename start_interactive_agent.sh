#!/bin/bash

# Quick launcher for the interactive server agent
echo "🚀 Starting Interactive Server Management Agent..."
echo "📝 This agent will:"
echo "   - Monitor both frontend and backend servers"
echo "   - Auto-fix common errors"
echo "   - Accept your manual issue reports"
echo "   - Restart servers when needed"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Install required Python packages if not available
python3 -c "import requests, threading, queue" 2>/dev/null || {
    echo "📦 Installing required Python packages..."
    pip3 install requests
}

# Run the interactive agent
python3 interactive_server_agent.py

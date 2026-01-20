#!/bin/bash

# Enhanced Server Agent Launcher
# Runs the server monitoring agent with proper error handling

echo "🚀 Starting Enhanced Server Management Agent..."

# Make sure we're in the right directory
cd "$(dirname "$0")"

# Create logs directory if it doesn't exist
mkdir -p logs

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Make the agent executable
chmod +x enhanced_server_agent.py

# Run the agent with proper error handling
python3 enhanced_server_agent.py 2>&1 | tee logs/agent_output.log

echo "🛑 Server agent stopped"

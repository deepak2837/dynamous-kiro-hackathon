#!/bin/bash

# Server Management and Error Monitoring Agent
# Usage: ./server_agent.sh

BACKEND_PID_FILE=".backend.pid"
FRONTEND_PID_FILE=".frontend.pid"
BACKEND_LOG="logs/backend.log"
FRONTEND_LOG="logs/frontend.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%H:%M:%S')] ERROR:${NC} $1"
}

success() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')] SUCCESS:${NC} $1"
}

warning() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')] WARNING:${NC} $1"
}

# Kill existing servers
kill_servers() {
    log "Killing existing servers..."
    fuser -k 3000/tcp 8000/tcp 2>/dev/null || true
    pkill -f "npm run dev" 2>/dev/null || true
    pkill -f "uvicorn" 2>/dev/null || true
    sleep 2
}

# Start backend server
start_backend() {
    log "Starting backend server..."
    cd backend
    source venv/bin/activate
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../$BACKEND_LOG 2>&1 &
    echo $! > ../$BACKEND_PID_FILE
    cd ..
    sleep 3
    
    if curl -s http://localhost:8000/health > /dev/null; then
        success "Backend server started successfully"
        return 0
    else
        error "Backend server failed to start"
        return 1
    fi
}

# Start frontend server
start_frontend() {
    log "Starting frontend server..."
    cd frontend
    npm run dev > ../$FRONTEND_LOG 2>&1 &
    echo $! > ../$FRONTEND_PID_FILE
    cd ..
    sleep 5
    
    if curl -s http://localhost:3000 > /dev/null; then
        success "Frontend server started successfully"
        return 0
    else
        error "Frontend server failed to start"
        return 1
    fi
}

# Fix common backend errors
fix_backend_error() {
    local error_msg="$1"
    
    if [[ "$error_msg" == *"ModuleNotFoundError"* ]]; then
        warning "Missing Python module detected, installing..."
        cd backend
        source venv/bin/activate
        
        if [[ "$error_msg" == *"slowapi"* ]]; then
            pip install slowapi
        elif [[ "$error_msg" == *"pytesseract"* ]]; then
            pip install pytesseract
        elif [[ "$error_msg" == *"pdf2image"* ]]; then
            pip install pdf2image
        elif [[ "$error_msg" == *"python-pptx"* ]]; then
            pip install python-pptx
        else
            pip install -r requirements.txt
        fi
        cd ..
        
        log "Restarting backend after fixing dependencies..."
        kill_servers
        start_backend
        
    elif [[ "$error_msg" == *"Address already in use"* ]]; then
        warning "Port conflict detected, killing conflicting processes..."
        fuser -k 8000/tcp
        sleep 2
        start_backend
        
    elif [[ "$error_msg" == *"MongoDB"* ]] || [[ "$error_msg" == *"connection"* ]]; then
        warning "Database connection issue detected..."
        log "Checking MongoDB status..."
        if ! pgrep mongod > /dev/null; then
            error "MongoDB not running. Please start MongoDB manually."
        fi
        
    elif [[ "$error_msg" == *"ImportError"* ]] || [[ "$error_msg" == *"SyntaxError"* ]]; then
        warning "Code error detected, checking for common issues..."
        # Could add automatic code fixes here
        log "Manual intervention may be required for code errors"
    fi
}

# Fix common frontend errors
fix_frontend_error() {
    local error_msg="$1"
    
    if [[ "$error_msg" == *"EADDRINUSE"* ]] || [[ "$error_msg" == *"port 3000"* ]]; then
        warning "Frontend port conflict detected..."
        fuser -k 3000/tcp
        sleep 2
        start_frontend
        
    elif [[ "$error_msg" == *"Module not found"* ]] || [[ "$error_msg" == *"Cannot resolve"* ]]; then
        warning "Missing Node module detected, installing..."
        cd frontend
        npm install
        cd ..
        
        log "Restarting frontend after fixing dependencies..."
        start_frontend
        
    elif [[ "$error_msg" == *"next.config.js"* ]]; then
        warning "Next.js config issue detected..."
        # Could fix config issues automatically
        log "Config issue detected, may need manual fix"
        
    elif [[ "$error_msg" == *"compilation failed"* ]] || [[ "$error_msg" == *"TypeScript error"* ]]; then
        warning "Compilation error detected..."
        log "Code compilation issue, may need manual intervention"
    fi
}

# Monitor logs for errors
monitor_logs() {
    log "Starting log monitoring..."
    
    # Monitor backend logs
    tail -f $BACKEND_LOG 2>/dev/null | while read line; do
        if [[ "$line" == *"ERROR"* ]] || [[ "$line" == *"Exception"* ]] || [[ "$line" == *"Traceback"* ]]; then
            error "Backend: $line"
            fix_backend_error "$line"
        elif [[ "$line" == *"WARNING"* ]]; then
            warning "Backend: $line"
        fi
    done &
    
    # Monitor frontend logs
    tail -f $FRONTEND_LOG 2>/dev/null | while read line; do
        if [[ "$line" == *"Error"* ]] || [[ "$line" == *"Failed"* ]] || [[ "$line" == *"error"* ]]; then
            error "Frontend: $line"
            fix_frontend_error "$line"
        elif [[ "$line" == *"warn"* ]] || [[ "$line" == *"Warning"* ]]; then
            warning "Frontend: $line"
        fi
    done &
}

# Check server health
check_health() {
    local backend_ok=false
    local frontend_ok=false
    
    if curl -s http://localhost:8000/health > /dev/null; then
        backend_ok=true
    fi
    
    if curl -s http://localhost:3000 > /dev/null; then
        frontend_ok=true
    fi
    
    if $backend_ok && $frontend_ok; then
        success "Both servers are healthy"
    else
        if ! $backend_ok; then
            error "Backend server is down, restarting..."
            start_backend
        fi
        if ! $frontend_ok; then
            error "Frontend server is down, restarting..."
            start_frontend
        fi
    fi
}

# Main execution
main() {
    log "🚀 Starting Server Management Agent"
    
    # Create logs directory
    mkdir -p logs
    
    # Kill existing servers
    kill_servers
    
    # Start servers
    if start_backend && start_frontend; then
        success "✅ Both servers started successfully"
        log "🌐 Frontend: http://localhost:3000"
        log "📊 Backend: http://localhost:8000"
        log "📋 API Docs: http://localhost:8000/docs"
        
        # Start monitoring
        monitor_logs
        
        # Health check loop
        while true; do
            sleep 30
            check_health
        done
    else
        error "❌ Failed to start servers"
        exit 1
    fi
}

# Handle Ctrl+C
trap 'log "Shutting down..."; kill_servers; exit 0' INT

# Run main function
main

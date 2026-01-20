# Server Monitoring System

This directory contains an enhanced server monitoring system that automatically detects and fixes common server issues for both backend and frontend servers.

## 🚀 Quick Start

### Option 1: Enhanced Auto-Monitoring Agent (Recommended)
```bash
# Start the enhanced monitoring agent
./run_enhanced_agent.sh
```

This agent will:
- ✅ Start both servers automatically
- 🔍 Monitor logs in real-time
- 🛠️ Auto-fix common errors (missing dependencies, port conflicts, etc.)
- 📊 Perform health checks every 15 seconds
- 📝 Log all activities to `logs/agent.log`
- 🔄 Auto-restart servers when they crash

### Option 2: Interactive Dashboard
```bash
# Start the interactive dashboard
python3 server_dashboard.py
```

Features:
- 📊 Real-time server status display
- ⚠️ Recent error monitoring
- 🔧 Quick restart commands
- 📋 Log viewing
- 🌐 Direct links to servers

### Option 3: Command Line Interface
```bash
# Check server status
python3 server_commands.py status

# View logs
python3 server_commands.py logs backend
python3 server_commands.py logs frontend

# Restart servers
python3 server_commands.py restart backend
python3 server_commands.py restart frontend
python3 server_commands.py restart both

# Live monitoring
python3 server_commands.py monitor
```

## 🔧 What Gets Fixed Automatically

### Backend Issues
- ❌ **Missing Python modules** → Installs via pip
- ❌ **Port 8000 conflicts** → Kills conflicting processes
- ❌ **MongoDB connection issues** → Starts MongoDB service
- ❌ **Permission errors** → Fixes file permissions
- ❌ **Virtual environment issues** → Recreates venv

### Frontend Issues
- ❌ **Port 3000 conflicts** → Kills conflicting processes
- ❌ **Missing Node modules** → Runs npm install
- ❌ **Compilation errors** → Clears Next.js cache
- ❌ **Network/API errors** → Checks backend connectivity

### Common Issues
- ❌ **Server crashes** → Auto-restart with health checks
- ❌ **Dependency conflicts** → Reinstalls dependencies
- ❌ **Process zombies** → Proper process cleanup

## 📁 File Structure

```
├── enhanced_server_agent.py    # Main monitoring agent
├── run_enhanced_agent.sh       # Agent launcher script
├── server_dashboard.py         # Interactive dashboard
├── server_commands.py          # Command line interface
├── logs/                       # Log files directory
│   ├── agent.log              # Agent activity log
│   ├── backend.log            # Backend server log
│   ├── frontend.log           # Frontend server log
│   └── agent_output.log       # Agent console output
└── SERVER_MONITORING.md        # This file
```

## 🔍 Monitoring Features

### Real-time Log Analysis
- Scans backend and frontend logs continuously
- Detects error patterns and keywords
- Triggers appropriate fixes automatically
- Maintains error history for debugging

### Health Monitoring
- HTTP health checks every 15 seconds
- Process monitoring (PID tracking)
- Port availability checks
- Automatic restart on failure

### Error Classification
- **Critical**: Server crashes, startup failures
- **Error**: Runtime errors, exceptions
- **Warning**: Non-fatal issues, deprecations
- **Info**: Normal operations, status updates

## 🛠️ Manual Troubleshooting

### If Servers Won't Start
```bash
# Check what's using the ports
lsof -i :3000
lsof -i :8000

# Kill processes manually
sudo kill -9 <PID>

# Check MongoDB status
sudo systemctl status mongod
sudo systemctl start mongod

# Check Python virtual environment
cd backend
source venv/bin/activate
pip list
```

### If Auto-fixes Aren't Working
```bash
# Check agent logs
tail -f logs/agent.log

# Manual dependency installation
cd backend && source venv/bin/activate && pip install -r requirements.txt
cd frontend && npm install

# Clear caches
rm -rf frontend/.next
rm -rf frontend/node_modules/.cache
```

### Common Error Solutions

#### "ModuleNotFoundError: No module named 'X'"
```bash
cd backend
source venv/bin/activate
pip install X
```

#### "EADDRINUSE: address already in use"
```bash
# Kill process on port
lsof -ti:3000 | xargs kill -9
lsof -ti:8000 | xargs kill -9
```

#### "MongoDB connection refused"
```bash
sudo systemctl start mongod
sudo systemctl enable mongod
```

#### "Permission denied"
```bash
chmod -R 755 .
chown -R $USER:$USER .
```

## 📊 Dashboard Commands

When using the interactive dashboard (`python3 server_dashboard.py`):

- `r` - Restart both servers
- `rb` - Restart backend only  
- `rf` - Restart frontend only
- `l` - Show recent logs
- `s` - Show detailed status
- `q` - Quit dashboard

## 🔄 Process Management

### Starting Servers Manually
```bash
# Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend  
cd frontend
npm run dev
```

### Stopping Servers
```bash
# Kill by process name
pkill -f "uvicorn"
pkill -f "npm run dev"

# Kill by port
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

## 📝 Log Files

- **`logs/agent.log`**: Detailed agent activities and decisions
- **`logs/backend.log`**: Backend server output and errors
- **`logs/frontend.log`**: Frontend server output and errors
- **`logs/agent_output.log`**: Agent console output

## 🚨 Emergency Procedures

### Complete Reset
```bash
# Stop everything
pkill -f "uvicorn"
pkill -f "npm run dev"
pkill -f "python3 enhanced_server_agent.py"

# Clean up
rm -rf logs/
rm -rf backend/venv/
rm -rf frontend/node_modules/
rm -rf frontend/.next/

# Restart from scratch
./run_enhanced_agent.sh
```

### If Agent Gets Stuck
```bash
# Find and kill agent process
ps aux | grep enhanced_server_agent
kill -9 <PID>

# Restart agent
./run_enhanced_agent.sh
```

## 🎯 Best Practices

1. **Always use the enhanced agent** for development
2. **Check logs regularly** to understand what's happening
3. **Let auto-fixes run** before manual intervention
4. **Use the dashboard** for quick status checks
5. **Keep dependencies updated** to prevent issues

## 🔧 Customization

### Adding New Error Patterns
Edit `enhanced_server_agent.py` and add patterns to:
- `analyze_backend_error()` for backend issues
- `analyze_frontend_error()` for frontend issues

### Adjusting Monitoring Intervals
- Health checks: Change `time.sleep(15)` in `health_monitor()`
- Status reports: Change `time.sleep(60)` in `status_reporter()`
- Log monitoring: Change `time.sleep(0.5)` in monitor functions

### Custom Fix Actions
Add new fix methods and call them from the analyze functions:
```python
def fix_custom_error(self, error_line):
    # Your custom fix logic here
    return True  # Return True if fix was applied
```

## 📞 Support

If you encounter issues not covered by the auto-fixes:

1. Check `logs/agent.log` for detailed information
2. Use `python3 server_commands.py status` for current state
3. Try manual troubleshooting steps above
4. Reset everything as last resort

The monitoring system is designed to handle 90% of common development issues automatically, letting you focus on coding instead of server management!

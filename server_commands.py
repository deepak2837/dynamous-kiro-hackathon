#!/usr/bin/env python3
"""
Server Command Interface
Allows you to send commands to the running server agent
"""

import sys
import time
import requests
import subprocess
from pathlib import Path

def check_server_status():
    """Check the status of both servers"""
    backend_ok = False
    frontend_ok = False
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=3)
        backend_ok = response.status_code == 200
    except:
        pass
    
    try:
        response = requests.get("http://localhost:3000", timeout=3)
        frontend_ok = response.status_code in [200, 404]
    except:
        pass
    
    return backend_ok, frontend_ok

def show_logs(server_type, lines=20):
    """Show recent logs for a server"""
    log_file = f"logs/{server_type}.log"
    
    if Path(log_file).exists():
        try:
            result = subprocess.run(
                ["tail", "-n", str(lines), log_file], 
                capture_output=True, text=True
            )
            print(f"\n📋 Recent {server_type} logs:")
            print("=" * 50)
            print(result.stdout)
            print("=" * 50)
        except Exception as e:
            print(f"❌ Failed to read {server_type} logs: {e}")
    else:
        print(f"⚠️ No {server_type} log file found")

def restart_server(server_type):
    """Restart a specific server"""
    print(f"🔄 Restarting {server_type} server...")
    
    if server_type == "backend":
        # Kill backend processes
        subprocess.run("pkill -f 'uvicorn'", shell=True, capture_output=True)
        subprocess.run("lsof -ti:8000 | xargs kill -9", shell=True, capture_output=True)
        time.sleep(2)
        
        # Start backend
        subprocess.Popen([
            "bash", "-c", 
            "cd backend && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1"
        ])
        
    elif server_type == "frontend":
        # Kill frontend processes
        subprocess.run("pkill -f 'npm run dev'", shell=True, capture_output=True)
        subprocess.run("lsof -ti:3000 | xargs kill -9", shell=True, capture_output=True)
        time.sleep(2)
        
        # Start frontend
        subprocess.Popen([
            "bash", "-c", 
            "cd frontend && npm run dev > ../logs/frontend.log 2>&1"
        ])
    
    print(f"✅ {server_type} restart initiated")

def main():
    if len(sys.argv) < 2:
        print("🔧 Server Command Interface")
        print("=" * 40)
        print("Usage: python3 server_commands.py <command>")
        print("\nAvailable commands:")
        print("  status          - Check server status")
        print("  logs backend    - Show backend logs")
        print("  logs frontend   - Show frontend logs")
        print("  restart backend - Restart backend server")
        print("  restart frontend- Restart frontend server")
        print("  restart both    - Restart both servers")
        print("  monitor         - Show live monitoring")
        return
    
    command = sys.argv[1].lower()
    
    if command == "status":
        backend_ok, frontend_ok = check_server_status()
        backend_status = "🟢 UP" if backend_ok else "🔴 DOWN"
        frontend_status = "🟢 UP" if frontend_ok else "🔴 DOWN"
        
        print(f"\n📊 SERVER STATUS")
        print("=" * 30)
        print(f"Backend (8000):  {backend_status}")
        print(f"Frontend (3000): {frontend_status}")
        print("=" * 30)
        
        if backend_ok:
            print("🌐 Backend: http://localhost:8000")
            print("📋 API Docs: http://localhost:8000/docs")
        if frontend_ok:
            print("🌐 Frontend: http://localhost:3000")
    
    elif command == "logs":
        if len(sys.argv) > 2:
            server_type = sys.argv[2].lower()
            if server_type in ["backend", "frontend"]:
                show_logs(server_type)
            else:
                print("❌ Invalid server type. Use 'backend' or 'frontend'")
        else:
            print("❌ Please specify server type: logs backend|frontend")
    
    elif command == "restart":
        if len(sys.argv) > 2:
            server_type = sys.argv[2].lower()
            if server_type == "both":
                restart_server("backend")
                time.sleep(2)
                restart_server("frontend")
            elif server_type in ["backend", "frontend"]:
                restart_server(server_type)
            else:
                print("❌ Invalid server type. Use 'backend', 'frontend', or 'both'")
        else:
            print("❌ Please specify server type: restart backend|frontend|both")
    
    elif command == "monitor":
        print("📊 Live Server Monitoring")
        print("Press Ctrl+C to stop")
        print("=" * 40)
        
        try:
            while True:
                backend_ok, frontend_ok = check_server_status()
                backend_status = "🟢 UP" if backend_ok else "🔴 DOWN"
                frontend_status = "🟢 UP" if frontend_ok else "🔴 DOWN"
                
                timestamp = time.strftime("%H:%M:%S")
                print(f"[{timestamp}] Backend: {backend_status} | Frontend: {frontend_status}")
                
                time.sleep(5)
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped")
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'python3 server_commands.py' to see available commands")

if __name__ == "__main__":
    main()

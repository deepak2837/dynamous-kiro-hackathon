#!/usr/bin/env python3
"""
Real-time Server Dashboard
Shows live status, logs, and allows quick actions
"""

import os
import sys
import time
import requests
import subprocess
import threading
from datetime import datetime
from pathlib import Path

class ServerDashboard:
    def __init__(self):
        self.running = True
        self.backend_status = False
        self.frontend_status = False
        self.last_backend_error = None
        self.last_frontend_error = None
        
    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def check_servers(self):
        """Check server status"""
        # Backend
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            self.backend_status = response.status_code == 200
        except:
            self.backend_status = False
        
        # Frontend
        try:
            response = requests.get("http://localhost:3000", timeout=2)
            self.frontend_status = response.status_code in [200, 404]
        except:
            self.frontend_status = False
    
    def get_recent_errors(self):
        """Get recent errors from logs"""
        # Backend errors
        backend_log = Path("logs/backend.log")
        if backend_log.exists():
            try:
                result = subprocess.run(
                    ["tail", "-n", "5", str(backend_log)], 
                    capture_output=True, text=True
                )
                lines = result.stdout.strip().split('\n')
                for line in reversed(lines):
                    if any(keyword in line.lower() for keyword in ["error", "exception", "failed"]):
                        self.last_backend_error = line[:80] + "..." if len(line) > 80 else line
                        break
            except:
                pass
        
        # Frontend errors
        frontend_log = Path("logs/frontend.log")
        if frontend_log.exists():
            try:
                result = subprocess.run(
                    ["tail", "-n", "5", str(frontend_log)], 
                    capture_output=True, text=True
                )
                lines = result.stdout.strip().split('\n')
                for line in reversed(lines):
                    if any(keyword in line.lower() for keyword in ["error", "failed", "compilation"]):
                        self.last_frontend_error = line[:80] + "..." if len(line) > 80 else line
                        break
            except:
                pass
    
    def display_dashboard(self):
        """Display the main dashboard"""
        self.clear_screen()
        
        # Header
        print("🚀 STUDY BUDDY SERVER DASHBOARD")
        print("=" * 60)
        print(f"⏰ Last Updated: {datetime.now().strftime('%H:%M:%S')}")
        print()
        
        # Server Status
        backend_icon = "🟢" if self.backend_status else "🔴"
        frontend_icon = "🟢" if self.frontend_status else "🔴"
        
        print("📊 SERVER STATUS")
        print("-" * 30)
        print(f"{backend_icon} Backend (Port 8000):  {'RUNNING' if self.backend_status else 'STOPPED'}")
        print(f"{frontend_icon} Frontend (Port 3000): {'RUNNING' if self.frontend_status else 'STOPPED'}")
        print()
        
        # URLs
        if self.backend_status or self.frontend_status:
            print("🌐 QUICK ACCESS")
            print("-" * 30)
            if self.backend_status:
                print("📊 Backend API: http://localhost:8000")
                print("📋 API Docs:    http://localhost:8000/docs")
            if self.frontend_status:
                print("🌐 Frontend:    http://localhost:3000")
            print()
        
        # Recent Errors
        if self.last_backend_error or self.last_frontend_error:
            print("⚠️  RECENT ERRORS")
            print("-" * 30)
            if self.last_backend_error:
                print(f"Backend: {self.last_backend_error}")
            if self.last_frontend_error:
                print(f"Frontend: {self.last_frontend_error}")
            print()
        
        # Commands
        print("🔧 QUICK COMMANDS")
        print("-" * 30)
        print("r  - Restart both servers")
        print("rb - Restart backend only")
        print("rf - Restart frontend only")
        print("l  - Show recent logs")
        print("s  - Show detailed status")
        print("q  - Quit dashboard")
        print()
        print("Enter command: ", end="", flush=True)
    
    def restart_backend(self):
        """Restart backend server"""
        print("🔄 Restarting backend...")
        subprocess.run("pkill -f 'uvicorn'", shell=True, capture_output=True)
        subprocess.run("lsof -ti:8000 | xargs kill -9", shell=True, capture_output=True)
        time.sleep(2)
        
        subprocess.Popen([
            "bash", "-c", 
            "cd backend && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1"
        ])
        print("✅ Backend restart initiated")
        time.sleep(2)
    
    def restart_frontend(self):
        """Restart frontend server"""
        print("🔄 Restarting frontend...")
        subprocess.run("pkill -f 'npm run dev'", shell=True, capture_output=True)
        subprocess.run("lsof -ti:3000 | xargs kill -9", shell=True, capture_output=True)
        time.sleep(2)
        
        subprocess.Popen([
            "bash", "-c", 
            "cd frontend && npm run dev > ../logs/frontend.log 2>&1"
        ])
        print("✅ Frontend restart initiated")
        time.sleep(2)
    
    def show_logs(self):
        """Show recent logs"""
        self.clear_screen()
        print("📋 RECENT LOGS")
        print("=" * 60)
        
        # Backend logs
        print("\n🔧 BACKEND LOGS (last 10 lines):")
        print("-" * 40)
        backend_log = Path("logs/backend.log")
        if backend_log.exists():
            result = subprocess.run(
                ["tail", "-n", "10", str(backend_log)], 
                capture_output=True, text=True
            )
            print(result.stdout)
        else:
            print("No backend logs found")
        
        # Frontend logs
        print("\n🌐 FRONTEND LOGS (last 10 lines):")
        print("-" * 40)
        frontend_log = Path("logs/frontend.log")
        if frontend_log.exists():
            result = subprocess.run(
                ["tail", "-n", "10", str(frontend_log)], 
                capture_output=True, text=True
            )
            print(result.stdout)
        else:
            print("No frontend logs found")
        
        print("\nPress Enter to return to dashboard...")
        input()
    
    def show_detailed_status(self):
        """Show detailed server status"""
        self.clear_screen()
        print("📊 DETAILED SERVER STATUS")
        print("=" * 60)
        
        # Check processes
        print("\n🔍 PROCESS CHECK:")
        print("-" * 30)
        
        # Backend process
        result = subprocess.run(
            ["pgrep", "-f", "uvicorn"], 
            capture_output=True, text=True
        )
        if result.stdout.strip():
            print(f"✅ Backend process running (PID: {result.stdout.strip()})")
        else:
            print("❌ Backend process not found")
        
        # Frontend process
        result = subprocess.run(
            ["pgrep", "-f", "npm run dev"], 
            capture_output=True, text=True
        )
        if result.stdout.strip():
            print(f"✅ Frontend process running (PID: {result.stdout.strip()})")
        else:
            print("❌ Frontend process not found")
        
        # Port check
        print("\n🌐 PORT CHECK:")
        print("-" * 30)
        
        for port in [8000, 3000]:
            result = subprocess.run(
                ["lsof", "-i", f":{port}"], 
                capture_output=True, text=True
            )
            if result.stdout.strip():
                print(f"✅ Port {port} is in use")
            else:
                print(f"❌ Port {port} is free")
        
        # Health check
        print("\n🏥 HEALTH CHECK:")
        print("-" * 30)
        
        try:
            response = requests.get("http://localhost:8000/health", timeout=3)
            print(f"✅ Backend health: {response.status_code}")
        except Exception as e:
            print(f"❌ Backend health: {str(e)[:50]}")
        
        try:
            response = requests.get("http://localhost:3000", timeout=3)
            print(f"✅ Frontend health: {response.status_code}")
        except Exception as e:
            print(f"❌ Frontend health: {str(e)[:50]}")
        
        print("\nPress Enter to return to dashboard...")
        input()
    
    def status_updater(self):
        """Update status in background"""
        while self.running:
            self.check_servers()
            self.get_recent_errors()
            time.sleep(3)
    
    def run(self):
        """Run the dashboard"""
        print("🚀 Starting Server Dashboard...")
        
        # Start background status updater
        status_thread = threading.Thread(target=self.status_updater, daemon=True)
        status_thread.start()
        
        try:
            while self.running:
                self.display_dashboard()
                
                # Get user input with timeout
                try:
                    import select
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        command = input().strip().lower()
                        
                        if command == 'q':
                            self.running = False
                            break
                        elif command == 'r':
                            self.restart_backend()
                            self.restart_frontend()
                        elif command == 'rb':
                            self.restart_backend()
                        elif command == 'rf':
                            self.restart_frontend()
                        elif command == 'l':
                            self.show_logs()
                        elif command == 's':
                            self.show_detailed_status()
                        elif command == '':
                            continue
                        else:
                            print(f"Unknown command: {command}")
                            time.sleep(1)
                except:
                    time.sleep(1)
                
        except KeyboardInterrupt:
            pass
        
        print("\n👋 Dashboard stopped")

if __name__ == "__main__":
    dashboard = ServerDashboard()
    dashboard.run()

#!/usr/bin/env python3
"""
Enhanced Non-Blocking Server Management Agent
Monitors logs, auto-fixes errors, and provides interactive commands
"""

import os
import sys
import time
import subprocess
import signal
import requests
import threading
import re
import json
from datetime import datetime
from pathlib import Path
from collections import deque

class EnhancedServerAgent:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.backend_log = Path("logs/backend.log")
        self.frontend_log = Path("logs/frontend.log")
        self.running = True
        
        # Create logs directory
        Path("logs").mkdir(exist_ok=True)
        
        # Error tracking
        self.backend_errors = deque(maxlen=50)
        self.frontend_errors = deque(maxlen=50)
        self.last_backend_restart = None
        self.last_frontend_restart = None
        
        # Health status
        self.backend_healthy = False
        self.frontend_healthy = False
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {
            "INFO": "\033[0;34m",
            "SUCCESS": "\033[0;32m", 
            "WARNING": "\033[1;33m",
            "ERROR": "\033[0;31m",
            "CRITICAL": "\033[1;31m",
            "FIX": "\033[0;36m"
        }
        color = colors.get(level, "\033[0m")
        print(f"{color}[{timestamp}] {level}:\033[0m {message}")
        
        # Also write to agent log
        with open("logs/agent.log", "a") as f:
            f.write(f"[{timestamp}] {level}: {message}\n")
    
    def kill_existing_servers(self):
        """Kill any existing server processes"""
        self.log("Cleaning up existing servers...")
        
        # Kill by port
        for port in [3000, 8000]:
            try:
                result = subprocess.run(f"lsof -ti:{port}", shell=True, capture_output=True, text=True)
                if result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        subprocess.run(f"kill -9 {pid}", shell=True, capture_output=True)
                        self.log(f"Killed process {pid} on port {port}")
            except:
                pass
        
        # Kill by process name
        try:
            subprocess.run("pkill -f 'npm run dev'", shell=True, capture_output=True)
            subprocess.run("pkill -f 'uvicorn'", shell=True, capture_output=True)
        except:
            pass
        
        time.sleep(2)
    
    def start_backend(self):
        """Start the backend server"""
        self.log("Starting backend server...")
        
        try:
            # Check if virtual environment exists
            venv_path = Path("backend/venv")
            if not venv_path.exists():
                self.log("Creating Python virtual environment...")
                subprocess.run(["python3", "-m", "venv", "backend/venv"], check=True)
                
                # Install requirements
                self.log("Installing Python dependencies...")
                subprocess.run([
                    "bash", "-c", 
                    "cd backend && source venv/bin/activate && pip install -r requirements.txt"
                ], check=True)
            
            # Start server with proper logging
            cmd = [
                "bash", "-c", 
                "cd backend && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level info"
            ]
            
            with open(self.backend_log, "w") as log_file:
                self.backend_process = subprocess.Popen(
                    cmd, 
                    stdout=log_file, 
                    stderr=subprocess.STDOUT,
                    preexec_fn=os.setsid  # Create new process group
                )
            
            self.last_backend_restart = datetime.now()
            
            # Wait and check if server started
            for i in range(10):  # Wait up to 10 seconds
                time.sleep(1)
                if self.check_backend_health():
                    self.log("Backend server started successfully", "SUCCESS")
                    self.backend_healthy = True
                    return True
                    
            self.log("Backend server failed to start properly", "ERROR")
            return False
                
        except Exception as e:
            self.log(f"Failed to start backend: {e}", "ERROR")
            return False
    
    def start_frontend(self):
        """Start the frontend server"""
        self.log("Starting frontend server...")
        
        try:
            # Check if node_modules exists
            if not Path("frontend/node_modules").exists():
                self.log("Installing Node dependencies...")
                subprocess.run(["npm", "install"], cwd="frontend", check=True)
            
            # Start server with proper logging
            cmd = ["bash", "-c", "cd frontend && npm run dev -- --port 3000"]
            
            with open(self.frontend_log, "w") as log_file:
                self.frontend_process = subprocess.Popen(
                    cmd, 
                    stdout=log_file, 
                    stderr=subprocess.STDOUT,
                    preexec_fn=os.setsid  # Create new process group
                )
            
            self.last_frontend_restart = datetime.now()
            
            # Wait and check if server started
            for i in range(15):  # Wait up to 15 seconds for Next.js
                time.sleep(1)
                if self.check_frontend_health():
                    self.log("Frontend server started successfully", "SUCCESS")
                    self.frontend_healthy = True
                    return True
                    
            self.log("Frontend server failed to start properly", "ERROR")
            return False
                
        except Exception as e:
            self.log(f"Failed to start frontend: {e}", "ERROR")
            return False
    
    def check_backend_health(self):
        """Check if backend server is healthy"""
        try:
            response = requests.get("http://localhost:8000/health", timeout=3)
            return response.status_code == 200
        except:
            return False
    
    def check_frontend_health(self):
        """Check if frontend server is healthy"""
        try:
            response = requests.get("http://localhost:3000", timeout=3)
            return response.status_code in [200, 404]  # 404 is OK for Next.js
        except:
            return False
    
    def analyze_backend_error(self, error_line):
        """Analyze and fix backend errors"""
        error_line = error_line.lower()
        
        # Module/Import errors
        if "modulenotfounderror" in error_line or "importerror" in error_line:
            module_match = re.search(r"no module named '([^']+)'", error_line)
            if module_match:
                module = module_match.group(1)
                self.log(f"Missing Python module: {module}", "FIX")
                return self.fix_python_dependency(module)
        
        # Port conflicts
        elif "address already in use" in error_line or "port 8000" in error_line:
            self.log("Backend port conflict detected", "FIX")
            return self.fix_port_conflict(8000)
        
        # Database connection issues
        elif any(db_error in error_line for db_error in ["mongodb", "connection refused", "database"]):
            self.log("Database connection issue detected", "FIX")
            return self.fix_database_connection()
        
        # Permission errors
        elif "permission denied" in error_line:
            self.log("Permission error detected", "FIX")
            return self.fix_permissions()
        
        # Syntax errors
        elif "syntaxerror" in error_line:
            self.log("Syntax error in backend code", "ERROR")
            self.log("Please check your Python code for syntax errors")
            return False
        
        return False
    
    def analyze_frontend_error(self, error_line):
        """Analyze and fix frontend errors"""
        error_line = error_line.lower()
        
        # Port conflicts
        if "eaddrinuse" in error_line or "port 3000" in error_line:
            self.log("Frontend port conflict detected", "FIX")
            return self.fix_port_conflict(3000)
        
        # Module not found
        elif "module not found" in error_line or "cannot resolve" in error_line:
            self.log("Missing Node module detected", "FIX")
            return self.fix_node_dependencies()
        
        # Compilation errors
        elif "compilation failed" in error_line or "failed to compile" in error_line:
            self.log("Frontend compilation error", "ERROR")
            return self.fix_compilation_error()
        
        # Network errors
        elif "network error" in error_line or "fetch failed" in error_line:
            self.log("Network/API error detected", "FIX")
            return self.check_api_connectivity()
        
        return False
    
    def fix_python_dependency(self, module):
        """Fix missing Python dependencies"""
        try:
            self.log(f"Installing Python module: {module}")
            result = subprocess.run([
                "bash", "-c", 
                f"cd backend && source venv/bin/activate && pip install {module}"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self.log(f"Successfully installed {module}", "SUCCESS")
                return True
            else:
                self.log(f"Failed to install {module}: {result.stderr}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Error installing {module}: {e}", "ERROR")
            return False
    
    def fix_node_dependencies(self):
        """Fix missing Node dependencies"""
        try:
            self.log("Reinstalling Node dependencies...")
            result = subprocess.run(
                ["npm", "install"], 
                cwd="frontend", 
                capture_output=True, 
                text=True, 
                timeout=120
            )
            
            if result.returncode == 0:
                self.log("Node dependencies fixed", "SUCCESS")
                return True
            else:
                self.log(f"Failed to fix Node dependencies: {result.stderr}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Error fixing Node dependencies: {e}", "ERROR")
            return False
    
    def fix_port_conflict(self, port):
        """Fix port conflicts"""
        try:
            self.log(f"Killing processes on port {port}")
            subprocess.run(f"lsof -ti:{port} | xargs kill -9", shell=True, capture_output=True)
            time.sleep(2)
            return True
        except:
            return False
    
    def fix_database_connection(self):
        """Fix database connection issues"""
        try:
            # Check if MongoDB is running
            result = subprocess.run(
                ["systemctl", "is-active", "mongod"], 
                capture_output=True, 
                text=True
            )
            
            if "active" not in result.stdout:
                self.log("Starting MongoDB service...")
                subprocess.run(["sudo", "systemctl", "start", "mongod"], check=True)
                time.sleep(3)
                return True
            else:
                self.log("MongoDB is running, checking connection...")
                return True
        except:
            self.log("Could not start MongoDB. Please start it manually: sudo systemctl start mongod", "ERROR")
            return False
    
    def fix_permissions(self):
        """Fix permission issues"""
        try:
            self.log("Fixing file permissions...")
            subprocess.run(["chmod", "-R", "755", "."], check=True)
            return True
        except:
            return False
    
    def fix_compilation_error(self):
        """Fix frontend compilation errors"""
        try:
            self.log("Clearing Next.js cache...")
            subprocess.run(["rm", "-rf", "frontend/.next"], check=True)
            subprocess.run(["rm", "-rf", "frontend/node_modules/.cache"], check=True)
            return True
        except:
            return False
    
    def check_api_connectivity(self):
        """Check API connectivity"""
        if self.check_backend_health():
            self.log("Backend API is accessible", "SUCCESS")
            return True
        else:
            self.log("Backend API is not accessible", "ERROR")
            return False
    
    def restart_backend(self):
        """Restart backend server"""
        if self.last_backend_restart and (datetime.now() - self.last_backend_restart).seconds < 30:
            self.log("Backend restarted recently, waiting...", "WARNING")
            return
        
        self.log("Restarting backend server...")
        self.backend_healthy = False
        
        if self.backend_process:
            try:
                os.killpg(os.getpgid(self.backend_process.pid), signal.SIGTERM)
                self.backend_process.wait(timeout=5)
            except:
                try:
                    os.killpg(os.getpgid(self.backend_process.pid), signal.SIGKILL)
                except:
                    pass
        
        time.sleep(2)
        self.start_backend()
    
    def restart_frontend(self):
        """Restart frontend server"""
        if self.last_frontend_restart and (datetime.now() - self.last_frontend_restart).seconds < 30:
            self.log("Frontend restarted recently, waiting...", "WARNING")
            return
        
        self.log("Restarting frontend server...")
        self.frontend_healthy = False
        
        if self.frontend_process:
            try:
                os.killpg(os.getpgid(self.frontend_process.pid), signal.SIGTERM)
                self.frontend_process.wait(timeout=5)
            except:
                try:
                    os.killpg(os.getpgid(self.frontend_process.pid), signal.SIGKILL)
                except:
                    pass
        
        time.sleep(2)
        self.start_frontend()
    
    def monitor_backend_logs(self):
        """Monitor backend logs for errors"""
        self.log("Starting backend log monitoring...")
        
        while self.running:
            try:
                if self.backend_log.exists():
                    with open(self.backend_log, "r") as f:
                        f.seek(0, 2)  # Go to end
                        
                        while self.running:
                            line = f.readline()
                            if line:
                                line = line.strip()
                                
                                # Check for errors
                                if any(keyword in line.lower() for keyword in [
                                    "error", "exception", "traceback", "failed", 
                                    "critical", "fatal", "modulenotfounderror"
                                ]):
                                    self.log(f"Backend Error: {line[:100]}...", "ERROR")
                                    self.backend_errors.append(line)
                                    
                                    # Try to fix the error
                                    if self.analyze_backend_error(line):
                                        self.restart_backend()
                                
                                # Check for warnings
                                elif "warning" in line.lower():
                                    self.log(f"Backend Warning: {line[:100]}...", "WARNING")
                                
                                # Check for successful startup
                                elif "uvicorn running on" in line.lower():
                                    self.log("Backend server is ready", "SUCCESS")
                                    self.backend_healthy = True
                            else:
                                time.sleep(0.5)
                else:
                    time.sleep(1)
                    
            except Exception as e:
                self.log(f"Error monitoring backend logs: {e}", "ERROR")
                time.sleep(5)
    
    def monitor_frontend_logs(self):
        """Monitor frontend logs for errors"""
        self.log("Starting frontend log monitoring...")
        
        while self.running:
            try:
                if self.frontend_log.exists():
                    with open(self.frontend_log, "r") as f:
                        f.seek(0, 2)  # Go to end
                        
                        while self.running:
                            line = f.readline()
                            if line:
                                line = line.strip()
                                
                                # Check for errors
                                if any(keyword in line.lower() for keyword in [
                                    "error", "failed", "compilation failed", 
                                    "module not found", "cannot resolve", "eaddrinuse"
                                ]):
                                    self.log(f"Frontend Error: {line[:100]}...", "ERROR")
                                    self.frontend_errors.append(line)
                                    
                                    # Try to fix the error
                                    if self.analyze_frontend_error(line):
                                        self.restart_frontend()
                                
                                # Check for warnings
                                elif any(keyword in line.lower() for keyword in ["warn", "warning"]):
                                    self.log(f"Frontend Warning: {line[:100]}...", "WARNING")
                                
                                # Check for successful startup
                                elif any(keyword in line.lower() for keyword in [
                                    "ready", "compiled successfully", "local:"
                                ]):
                                    if "localhost:3000" in line.lower():
                                        self.log("Frontend server is ready", "SUCCESS")
                                        self.frontend_healthy = True
                            else:
                                time.sleep(0.5)
                else:
                    time.sleep(1)
                    
            except Exception as e:
                self.log(f"Error monitoring frontend logs: {e}", "ERROR")
                time.sleep(5)
    
    def health_monitor(self):
        """Monitor server health and restart if needed"""
        self.log("Starting health monitoring...")
        
        while self.running:
            time.sleep(15)  # Check every 15 seconds
            
            # Check backend health
            backend_ok = self.check_backend_health()
            if backend_ok != self.backend_healthy:
                if backend_ok:
                    self.log("Backend server recovered", "SUCCESS")
                else:
                    self.log("Backend server became unhealthy", "ERROR")
                self.backend_healthy = backend_ok
            
            # Check frontend health
            frontend_ok = self.check_frontend_health()
            if frontend_ok != self.frontend_healthy:
                if frontend_ok:
                    self.log("Frontend server recovered", "SUCCESS")
                else:
                    self.log("Frontend server became unhealthy", "ERROR")
                self.frontend_healthy = frontend_ok
            
            # Restart unhealthy servers
            if not backend_ok and self.backend_process:
                self.log("Backend health check failed, restarting...", "CRITICAL")
                self.restart_backend()
            
            if not frontend_ok and self.frontend_process:
                self.log("Frontend health check failed, restarting...", "CRITICAL")
                self.restart_frontend()
    
    def status_reporter(self):
        """Report status periodically"""
        while self.running:
            time.sleep(60)  # Report every minute
            
            backend_status = "🟢 UP" if self.backend_healthy else "🔴 DOWN"
            frontend_status = "🟢 UP" if self.frontend_healthy else "🔴 DOWN"
            
            self.log(f"Status Report - Backend: {backend_status}, Frontend: {frontend_status}", "INFO")
            
            # Report recent errors
            if self.backend_errors:
                self.log(f"Recent backend errors: {len(self.backend_errors)}", "WARNING")
            if self.frontend_errors:
                self.log(f"Recent frontend errors: {len(self.frontend_errors)}", "WARNING")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.log("Shutting down server agent...")
        self.running = False
        
        if self.backend_process:
            try:
                os.killpg(os.getpgid(self.backend_process.pid), signal.SIGTERM)
            except:
                pass
        
        if self.frontend_process:
            try:
                os.killpg(os.getpgid(self.frontend_process.pid), signal.SIGTERM)
            except:
                pass
        
        sys.exit(0)
    
    def run(self):
        """Main execution function"""
        self.log("🚀 Starting Enhanced Server Management Agent", "SUCCESS")
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Kill existing servers
        self.kill_existing_servers()
        
        # Start servers
        backend_started = self.start_backend()
        frontend_started = self.start_frontend()
        
        if backend_started or frontend_started:
            if backend_started and frontend_started:
                self.log("✅ Both servers started successfully", "SUCCESS")
            elif backend_started:
                self.log("⚠️ Backend started, frontend failed", "WARNING")
            else:
                self.log("⚠️ Frontend started, backend failed", "WARNING")
            
            self.log("🌐 Frontend: http://localhost:3000", "INFO")
            self.log("📊 Backend: http://localhost:8000", "INFO")
            self.log("📋 API Docs: http://localhost:8000/docs", "INFO")
            
            # Start monitoring threads
            threads = [
                threading.Thread(target=self.monitor_backend_logs, daemon=True),
                threading.Thread(target=self.monitor_frontend_logs, daemon=True),
                threading.Thread(target=self.health_monitor, daemon=True),
                threading.Thread(target=self.status_reporter, daemon=True)
            ]
            
            for thread in threads:
                thread.start()
            
            self.log("🔍 Monitoring active - logs, health checks, and auto-fixes enabled", "SUCCESS")
            self.log("📝 Check logs/agent.log for detailed monitoring history", "INFO")
            
            # Keep main thread alive and responsive
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.signal_handler(None, None)
        else:
            self.log("❌ Failed to start any servers", "CRITICAL")
            sys.exit(1)

if __name__ == "__main__":
    agent = EnhancedServerAgent()
    agent.run()

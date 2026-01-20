#!/usr/bin/env python3
"""
Intelligent Server Management Agent
Automatically runs both servers and fixes common errors
"""

import os
import sys
import time
import subprocess
import signal
import requests
import threading
import re
from datetime import datetime
from pathlib import Path

class ServerAgent:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.backend_log = Path("logs/backend.log")
        self.frontend_log = Path("logs/frontend.log")
        self.running = True
        
        # Create logs directory
        Path("logs").mkdir(exist_ok=True)
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {
            "INFO": "\033[0;34m",
            "SUCCESS": "\033[0;32m", 
            "WARNING": "\033[1;33m",
            "ERROR": "\033[0;31m"
        }
        color = colors.get(level, "\033[0m")
        print(f"{color}[{timestamp}] {level}:\033[0m {message}")
    
    def kill_existing_servers(self):
        """Kill any existing server processes"""
        self.log("Killing existing servers...")
        
        # Kill by port
        for port in [3000, 8000]:
            try:
                subprocess.run(f"fuser -k {port}/tcp", shell=True, capture_output=True)
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
            # Change to backend directory and start server
            cmd = [
                "bash", "-c", 
                "cd backend && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
            ]
            
            with open(self.backend_log, "w") as log_file:
                self.backend_process = subprocess.Popen(
                    cmd, stdout=log_file, stderr=subprocess.STDOUT
                )
            
            # Wait and check if server started
            time.sleep(3)
            if self.check_backend_health():
                self.log("Backend server started successfully", "SUCCESS")
                return True
            else:
                self.log("Backend server failed to start", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Failed to start backend: {e}", "ERROR")
            return False
    
    def start_frontend(self):
        """Start the frontend server"""
        self.log("Starting frontend server...")
        
        try:
            cmd = ["bash", "-c", "cd frontend && npm run dev"]
            
            with open(self.frontend_log, "w") as log_file:
                self.frontend_process = subprocess.Popen(
                    cmd, stdout=log_file, stderr=subprocess.STDOUT
                )
            
            # Wait and check if server started
            time.sleep(5)
            if self.check_frontend_health():
                self.log("Frontend server started successfully", "SUCCESS")
                return True
            else:
                self.log("Frontend server failed to start", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Failed to start frontend: {e}", "ERROR")
            return False
    
    def check_backend_health(self):
        """Check if backend server is healthy"""
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def check_frontend_health(self):
        """Check if frontend server is healthy"""
        try:
            response = requests.get("http://localhost:3000", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def fix_backend_error(self, error_line):
        """Automatically fix common backend errors"""
        if "ModuleNotFoundError" in error_line or "ImportError" in error_line:
            self.log("Fixing missing Python dependencies...", "WARNING")
            
            # Extract module name
            module_match = re.search(r"No module named '([^']+)'", error_line)
            if module_match:
                module = module_match.group(1)
                self.log(f"Installing missing module: {module}")
                
                try:
                    subprocess.run([
                        "bash", "-c", 
                        f"cd backend && source venv/bin/activate && pip install {module}"
                    ], check=True)
                    
                    self.log("Dependencies fixed, restarting backend...")
                    self.restart_backend()
                    
                except subprocess.CalledProcessError:
                    self.log(f"Failed to install {module}", "ERROR")
        
        elif "Address already in use" in error_line:
            self.log("Fixing port conflict...", "WARNING")
            subprocess.run("fuser -k 8000/tcp", shell=True, capture_output=True)
            time.sleep(2)
            self.restart_backend()
        
        elif "MongoDB" in error_line or "connection" in error_line.lower():
            self.log("Database connection issue detected", "WARNING")
            # Could add MongoDB restart logic here
            
    def fix_frontend_error(self, error_line):
        """Automatically fix common frontend errors"""
        if "EADDRINUSE" in error_line or "port 3000" in error_line:
            self.log("Fixing frontend port conflict...", "WARNING")
            subprocess.run("fuser -k 3000/tcp", shell=True, capture_output=True)
            time.sleep(2)
            self.restart_frontend()
            
        elif "Module not found" in error_line or "Cannot resolve" in error_line:
            self.log("Fixing missing Node dependencies...", "WARNING")
            try:
                subprocess.run(["npm", "install"], cwd="frontend", check=True)
                self.log("Dependencies fixed, restarting frontend...")
                self.restart_frontend()
            except subprocess.CalledProcessError:
                self.log("Failed to install Node dependencies", "ERROR")
    
    def restart_backend(self):
        """Restart backend server"""
        if self.backend_process:
            self.backend_process.terminate()
            self.backend_process.wait()
        time.sleep(1)
        self.start_backend()
    
    def restart_frontend(self):
        """Restart frontend server"""
        if self.frontend_process:
            self.frontend_process.terminate()
            self.frontend_process.wait()
        time.sleep(1)
        self.start_frontend()
    
    def monitor_backend_logs(self):
        """Monitor backend logs for errors"""
        try:
            with open(self.backend_log, "r") as f:
                f.seek(0, 2)  # Go to end of file
                
                while self.running:
                    line = f.readline()
                    if line:
                        line = line.strip()
                        if any(keyword in line.lower() for keyword in ["error", "exception", "traceback", "failed"]):
                            self.log(f"Backend Error: {line}", "ERROR")
                            self.fix_backend_error(line)
                        elif "warning" in line.lower():
                            self.log(f"Backend Warning: {line}", "WARNING")
                    else:
                        time.sleep(0.1)
        except FileNotFoundError:
            time.sleep(1)
            if self.running:
                self.monitor_backend_logs()
    
    def monitor_frontend_logs(self):
        """Monitor frontend logs for errors"""
        try:
            with open(self.frontend_log, "r") as f:
                f.seek(0, 2)  # Go to end of file
                
                while self.running:
                    line = f.readline()
                    if line:
                        line = line.strip()
                        if any(keyword in line.lower() for keyword in ["error", "failed", "compilation failed"]):
                            self.log(f"Frontend Error: {line}", "ERROR")
                            self.fix_frontend_error(line)
                        elif any(keyword in line.lower() for keyword in ["warn", "warning"]):
                            self.log(f"Frontend Warning: {line}", "WARNING")
                    else:
                        time.sleep(0.1)
        except FileNotFoundError:
            time.sleep(1)
            if self.running:
                self.monitor_frontend_logs()
    
    def health_check_loop(self):
        """Periodically check server health"""
        while self.running:
            time.sleep(30)
            
            backend_ok = self.check_backend_health()
            frontend_ok = self.check_frontend_health()
            
            if backend_ok and frontend_ok:
                self.log("Both servers are healthy", "SUCCESS")
            else:
                if not backend_ok:
                    self.log("Backend server is down, restarting...", "ERROR")
                    self.restart_backend()
                if not frontend_ok:
                    self.log("Frontend server is down, restarting...", "ERROR")
                    self.restart_frontend()
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.log("Shutting down server agent...")
        self.running = False
        
        if self.backend_process:
            self.backend_process.terminate()
        if self.frontend_process:
            self.frontend_process.terminate()
        
        sys.exit(0)
    
    def run(self):
        """Main execution function"""
        self.log("🚀 Starting Intelligent Server Management Agent")
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Kill existing servers
        self.kill_existing_servers()
        
        # Start servers
        backend_started = self.start_backend()
        frontend_started = self.start_frontend()
        
        if backend_started and frontend_started:
            self.log("✅ Both servers started successfully", "SUCCESS")
            self.log("🌐 Frontend: http://localhost:3000")
            self.log("📊 Backend: http://localhost:8000")
            self.log("📋 API Docs: http://localhost:8000/docs")
            self.log("🔍 Monitoring logs for errors...")
            
            # Start monitoring threads
            backend_monitor = threading.Thread(target=self.monitor_backend_logs, daemon=True)
            frontend_monitor = threading.Thread(target=self.monitor_frontend_logs, daemon=True)
            health_checker = threading.Thread(target=self.health_check_loop, daemon=True)
            
            backend_monitor.start()
            frontend_monitor.start()
            health_checker.start()
            
            # Keep main thread alive
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.signal_handler(None, None)
        else:
            self.log("❌ Failed to start servers", "ERROR")
            sys.exit(1)

if __name__ == "__main__":
    agent = ServerAgent()
    agent.run()

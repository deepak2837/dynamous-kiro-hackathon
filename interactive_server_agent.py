#!/usr/bin/env python3
"""
Enhanced Interactive Server Management Agent
Monitors logs, auto-fixes errors, and accepts manual issue reports
"""

import os
import sys
import time
import subprocess
import signal
import requests
import threading
import re
import queue
import select
from datetime import datetime
from pathlib import Path

class InteractiveServerAgent:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.backend_log = Path("logs/backend.log")
        self.frontend_log = Path("logs/frontend.log")
        self.running = True
        self.input_queue = queue.Queue()
        
        # Create logs directory
        Path("logs").mkdir(exist_ok=True)
        
        # Status tracking
        self.last_backend_check = None
        self.last_frontend_check = None
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {
            "INFO": "\033[0;34m",
            "SUCCESS": "\033[0;32m", 
            "WARNING": "\033[1;33m",
            "ERROR": "\033[0;31m",
            "INPUT": "\033[0;35m"
        }
        color = colors.get(level, "\033[0m")
        print(f"{color}[{timestamp}] {level}:\033[0m {message}")
    
    def print_status(self):
        """Print current server status"""
        backend_status = "🟢 UP" if self.check_backend_health() else "🔴 DOWN"
        frontend_status = "🟢 UP" if self.check_frontend_health() else "🔴 DOWN"
        
        print(f"\n{'='*50}")
        print(f"📊 SERVER STATUS")
        print(f"{'='*50}")
        print(f"Backend (8000):  {backend_status}")
        print(f"Frontend (3000): {frontend_status}")
        print(f"{'='*50}")
        print(f"💡 Type your issue and press Enter to report problems")
        print(f"💡 Type 'status' to see current server status")
        print(f"💡 Type 'restart backend' or 'restart frontend' to restart")
        print(f"💡 Type 'logs backend' or 'logs frontend' to see recent logs")
        print(f"💡 Type 'quit' to stop the agent")
        print(f"{'='*50}\n")
    
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
            # Ensure virtual environment exists
            if not Path("backend/venv").exists():
                self.log("Creating Python virtual environment...")
                subprocess.run(["python", "-m", "venv", "backend/venv"], check=True)
                subprocess.run([
                    "bash", "-c", 
                    "cd backend && source venv/bin/activate && pip install -r requirements.txt"
                ], check=True)
            
            # Start server
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
            # Ensure node_modules exists
            if not Path("frontend/node_modules").exists():
                self.log("Installing Node dependencies...")
                subprocess.run(["npm", "install"], cwd="frontend", check=True)
            
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
            self.last_backend_check = datetime.now()
            return response.status_code == 200
        except:
            return False
    
    def check_frontend_health(self):
        """Check if frontend server is healthy"""
        try:
            response = requests.get("http://localhost:3000", timeout=5)
            self.last_frontend_check = datetime.now()
            return response.status_code == 200
        except:
            return False
    
    def show_recent_logs(self, server_type, lines=20):
        """Show recent logs for a server"""
        log_file = self.backend_log if server_type == "backend" else self.frontend_log
        
        if log_file.exists():
            try:
                result = subprocess.run(
                    ["tail", "-n", str(lines), str(log_file)], 
                    capture_output=True, text=True
                )
                self.log(f"Recent {server_type} logs:")
                print(result.stdout)
            except Exception as e:
                self.log(f"Failed to read {server_type} logs: {e}", "ERROR")
        else:
            self.log(f"No {server_type} log file found", "WARNING")
    
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
            self.log("Please ensure MongoDB is running: sudo systemctl start mongod")
            
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
        self.log("Restarting backend server...")
        if self.backend_process:
            self.backend_process.terminate()
            self.backend_process.wait()
        time.sleep(1)
        self.start_backend()
    
    def restart_frontend(self):
        """Restart frontend server"""
        self.log("Restarting frontend server...")
        if self.frontend_process:
            self.frontend_process.terminate()
            self.frontend_process.wait()
        time.sleep(1)
        self.start_frontend()
    
    def handle_user_input(self, user_input):
        """Handle manual issue reports and commands from user"""
        user_input = user_input.strip().lower()
        
        if user_input == "quit" or user_input == "exit":
            self.log("Shutting down by user request...")
            self.running = False
            return
        
        elif user_input == "status":
            self.print_status()
            return
        
        elif user_input == "restart backend":
            self.restart_backend()
            return
        
        elif user_input == "restart frontend":
            self.restart_frontend()
            return
        
        elif user_input == "logs backend":
            self.show_recent_logs("backend")
            return
        
        elif user_input == "logs frontend":
            self.show_recent_logs("frontend")
            return
        
        # Handle issue reports
        self.log(f"Processing user-reported issue: {user_input}", "INPUT")
        
        # Analyze the issue and provide fixes
        if any(keyword in user_input for keyword in ["frontend", "3000", "next", "react"]):
            self.log("Investigating frontend issue...")
            
            if not self.check_frontend_health():
                self.log("Frontend is down, restarting...", "WARNING")
                self.restart_frontend()
            else:
                self.log("Frontend appears healthy, checking logs...")
                self.show_recent_logs("frontend", 10)
                
                if any(keyword in user_input for keyword in ["error", "crash", "broken", "not working"]):
                    self.log("Attempting frontend restart to resolve issue...")
                    self.restart_frontend()
        
        elif any(keyword in user_input for keyword in ["backend", "8000", "api", "server"]):
            self.log("Investigating backend issue...")
            
            if not self.check_backend_health():
                self.log("Backend is down, restarting...", "WARNING")
                self.restart_backend()
            else:
                self.log("Backend appears healthy, checking logs...")
                self.show_recent_logs("backend", 10)
                
                if any(keyword in user_input for keyword in ["error", "crash", "broken", "not working"]):
                    self.log("Attempting backend restart to resolve issue...")
                    self.restart_backend()
        
        elif any(keyword in user_input for keyword in ["both", "all", "everything"]):
            self.log("Restarting both servers...")
            self.restart_backend()
            time.sleep(2)
            self.restart_frontend()
        
        elif any(keyword in user_input for keyword in ["dependency", "module", "install"]):
            self.log("Checking and fixing dependencies...")
            try:
                subprocess.run(["npm", "install"], cwd="frontend", check=True)
                subprocess.run([
                    "bash", "-c", 
                    "cd backend && source venv/bin/activate && pip install -r requirements.txt"
                ], check=True)
                self.log("Dependencies updated, restarting servers...")
                self.restart_backend()
                time.sleep(2)
                self.restart_frontend()
            except Exception as e:
                self.log(f"Failed to update dependencies: {e}", "ERROR")
        
        else:
            self.log("Issue not automatically recognized. Checking server health...")
            backend_ok = self.check_backend_health()
            frontend_ok = self.check_frontend_health()
            
            if not backend_ok or not frontend_ok:
                self.log("Found unhealthy servers, attempting restart...")
                if not backend_ok:
                    self.restart_backend()
                if not frontend_ok:
                    self.restart_frontend()
            else:
                self.log("Both servers appear healthy. Please provide more specific details about the issue.")
                self.log("Try: 'logs backend', 'logs frontend', or describe the specific error you're seeing")
    
    def input_listener(self):
        """Listen for user input in a separate thread"""
        while self.running:
            try:
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    user_input = input().strip()
                    if user_input:
                        self.input_queue.put(user_input)
            except:
                break
    
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
    
    def input_processor(self):
        """Process user input from queue"""
        while self.running:
            try:
                user_input = self.input_queue.get(timeout=1)
                self.handle_user_input(user_input)
            except queue.Empty:
                continue
    
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
        self.log("🚀 Starting Interactive Server Management Agent")
        
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
            
            # Print initial status
            self.print_status()
            
            # Start monitoring threads
            backend_monitor = threading.Thread(target=self.monitor_backend_logs, daemon=True)
            frontend_monitor = threading.Thread(target=self.monitor_frontend_logs, daemon=True)
            health_checker = threading.Thread(target=self.health_check_loop, daemon=True)
            input_listener = threading.Thread(target=self.input_listener, daemon=True)
            input_processor = threading.Thread(target=self.input_processor, daemon=True)
            
            backend_monitor.start()
            frontend_monitor.start()
            health_checker.start()
            input_listener.start()
            input_processor.start()
            
            self.log("🔍 Monitoring logs and waiting for your input...")
            
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
    agent = InteractiveServerAgent()
    agent.run()

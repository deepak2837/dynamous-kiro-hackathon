#!/usr/bin/env python3
"""
API-based test for topic input flow with log monitoring
"""

import requests
import time
import logging
import subprocess
import threading
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_test.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class TopicInputAPITest:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.token = None
        self.session_id = None
        self.backend_logs = []
        
    def monitor_backend_logs(self):
        """Monitor backend logs in real-time"""
        try:
            process = subprocess.Popen(
                ['tail', '-f', '/home/unknown/Documents/hackathon application/dynamous-kiro-hackathon/backend/backend.log'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            for line in iter(process.stdout.readline, ''):
                if line.strip():
                    self.backend_logs.append(line.strip())
                    if any(keyword in line.lower() for keyword in ['error', 'failed', 'exception']):
                        logger.error(f"BACKEND ERROR: {line.strip()}")
                    elif any(keyword in line.lower() for keyword in ['generated', 'completed', 'success']):
                        logger.info(f"BACKEND SUCCESS: {line.strip()}")
                        
        except Exception as e:
            logger.error(f"Error monitoring backend logs: {e}")
    
    def login(self):
        """Login with provided credentials"""
        logger.info("🔐 Starting login process...")
        
        login_data = {
            "mobile_number": "7045024042",
            "password": "Alan#walker672"
        }
        
        try:
            response = requests.post(f"{self.base_url}/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                logger.info("✅ Login successful")
                return True
            else:
                logger.error(f"❌ Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Login error: {e}")
            return False
    
    def process_topic(self):
        """Process topic input"""
        logger.info("📝 Processing topic input...")
        
        if not self.token:
            logger.error("❌ No authentication token")
            return False
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        topic_data = {
            "topic": "Cardiovascular System - Heart anatomy, blood circulation, cardiac cycle, ECG interpretation, heart diseases, hypertension, cardiac medications"
        }
        
        try:
            # Try the text input endpoint
            response = requests.post(
                f"{self.base_url}/api/v1/text-input", 
                json=topic_data, 
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.session_id = data.get("session_id")
                logger.info(f"✅ Topic processing started - Session: {self.session_id}")
                return True
            else:
                logger.error(f"❌ Topic processing failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Topic processing error: {e}")
            return False
    
    def monitor_processing(self):
        """Monitor processing status"""
        logger.info("⏳ Monitoring processing...")
        
        if not self.session_id:
            logger.error("❌ No session ID")
            return False
        
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        
        start_time = time.time()
        max_wait_time = 300  # 5 minutes
        
        while time.time() - start_time < max_wait_time:
            try:
                response = requests.get(
                    f"{self.base_url}/api/v1/sessions/{self.session_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status", "unknown")
                    
                    logger.info(f"📊 Status: {status}")
                    
                    if status == "completed":
                        logger.info("✅ Processing completed")
                        return True
                    elif status == "failed":
                        logger.error("❌ Processing failed")
                        return False
                
                time.sleep(5)
                
            except Exception as e:
                logger.warning(f"Error checking status: {e}")
                time.sleep(5)
        
        logger.warning("⏱️ Processing timeout")
        return False
    
    def verify_outputs(self):
        """Verify all 5 outputs are generated"""
        logger.info("🔍 Verifying outputs...")
        
        if not self.session_id:
            logger.error("❌ No session ID")
            return False
        
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        
        endpoints = [
            ("Questions", f"/api/v1/questions/{self.session_id}"),
            ("Mock Tests", f"/api/v1/mock-tests/{self.session_id}"),
            ("Mnemonics", f"/api/v1/mnemonics/{self.session_id}"),
            ("Cheat Sheets", f"/api/v1/cheat-sheets/{self.session_id}"),
            ("Notes", f"/api/v1/notes/{self.session_id}")
        ]
        
        results = {}
        
        for name, endpoint in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check if data exists
                    if isinstance(data, dict):
                        if name == "Questions" and data.get("questions"):
                            count = len(data["questions"])
                            results[name] = count
                            logger.info(f"✅ {name}: {count} items")
                        elif name == "Mock Tests" and data.get("mock_tests"):
                            count = len(data["mock_tests"])
                            results[name] = count
                            logger.info(f"✅ {name}: {count} items")
                        elif name == "Mnemonics" and data.get("mnemonics"):
                            count = len(data["mnemonics"])
                            results[name] = count
                            logger.info(f"✅ {name}: {count} items")
                        elif name == "Cheat Sheets" and data.get("cheat_sheets"):
                            count = len(data["cheat_sheets"])
                            results[name] = count
                            logger.info(f"✅ {name}: {count} items")
                        elif name == "Notes" and data.get("notes"):
                            results[name] = 1
                            logger.info(f"✅ {name}: Available")
                        else:
                            results[name] = 0
                            logger.warning(f"⚠️ {name}: No data found")
                    else:
                        results[name] = 0
                        logger.warning(f"⚠️ {name}: Invalid response format")
                else:
                    results[name] = 0
                    logger.error(f"❌ {name}: HTTP {response.status_code}")
                    
            except Exception as e:
                results[name] = 0
                logger.error(f"❌ {name}: Error - {e}")
        
        success_count = sum(1 for count in results.values() if count > 0)
        logger.info(f"📊 Generated {success_count}/5 outputs: {results}")
        
        return success_count == 5
    
    def run_test(self):
        """Run the complete test"""
        logger.info("🧪 Starting Topic Input API Test")
        
        try:
            # Start backend log monitoring in background
            log_thread = threading.Thread(target=self.monitor_backend_logs, daemon=True)
            log_thread.start()
            
            # Run test steps
            if not self.login():
                return False
            
            time.sleep(2)
            
            if not self.process_topic():
                return False
            
            time.sleep(5)
            
            if not self.monitor_processing():
                return False
            
            time.sleep(2)
            
            success = self.verify_outputs()
            
            if success:
                logger.info("✅ Test completed successfully - All outputs generated")
            else:
                logger.error("❌ Test failed - Some outputs missing")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Test failed: {e}")
            return False
        
        finally:
            self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        logger.info("\n" + "="*50)
        logger.info("📋 TEST SUMMARY")
        logger.info("="*50)
        
        logger.info(f"Backend log entries: {len(self.backend_logs)}")
        
        # Show recent backend logs
        if self.backend_logs:
            logger.info("\n🔧 Recent Backend Logs:")
            for log in self.backend_logs[-15:]:
                logger.info(f"   {log}")
        
        logger.info("="*50)

if __name__ == "__main__":
    test = TopicInputAPITest()
    success = test.run_test()
    
    if success:
        logger.info("🎉 ALL TESTS PASSED")
    else:
        logger.error("💥 TESTS FAILED")

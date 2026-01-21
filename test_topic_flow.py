#!/usr/bin/env python3
"""
Test topic input flow - verify all 5 outputs are generated
"""

import requests
import time
import logging
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TopicFlowTest:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.token = None
        self.session_id = None
        
    def login(self):
        """Login and get token"""
        logger.info("🔐 Logging in...")
        
        response = requests.post(f"{self.base_url}/login", json={
            "mobile_number": "7045024042",
            "password": "Alan#walker672"
        })
        
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            logger.info("✅ Login successful")
            return True
        else:
            logger.error(f"❌ Login failed: {response.text}")
            return False
    
    def submit_topic(self):
        """Submit topic for processing"""
        logger.info("📝 Submitting topic...")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Get user ID from token (simplified)
        user_response = requests.get(f"{self.base_url}/api/v1/auth/me", headers=headers)
        if user_response.status_code != 200:
            logger.error("❌ Could not get user info")
            return False
        
        user_id = user_response.json()["id"]
        
        # Submit topic
        topic_data = {
            "topic": "Cardiovascular System - Heart anatomy, blood circulation, cardiac cycle, ECG interpretation, heart diseases, hypertension, cardiac medications, arrhythmias, heart failure",
            "user_id": user_id
        }
        
        response = requests.post(
            f"{self.base_url}/api/v1/text-input/", 
            data=topic_data,  # Use form data
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            self.session_id = data["session_id"]
            logger.info(f"✅ Topic submitted - Session: {self.session_id}")
            return True
        else:
            logger.error(f"❌ Topic submission failed: {response.status_code} - {response.text}")
            return False
    
    def wait_for_completion(self):
        """Wait for processing to complete"""
        logger.info("⏳ Waiting for processing...")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        for i in range(60):  # Wait up to 5 minutes
            try:
                response = requests.get(f"{self.base_url}/api/v1/sessions/{self.session_id}", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status", "unknown")
                    
                    logger.info(f"📊 Status: {status} ({i*5}s)")
                    
                    if status == "completed":
                        logger.info("✅ Processing completed!")
                        return True
                    elif status == "failed":
                        logger.error("❌ Processing failed!")
                        return False
                
                time.sleep(5)
                
            except Exception as e:
                logger.warning(f"Error checking status: {e}")
                time.sleep(5)
        
        logger.warning("⏱️ Timeout waiting for completion")
        return False
    
    def verify_all_outputs(self):
        """Verify all 5 outputs are generated"""
        logger.info("🔍 Verifying all outputs...")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        outputs = {
            "Questions": f"/api/v1/questions/{self.session_id}",
            "Mock Tests": f"/api/v1/mock-tests/{self.session_id}", 
            "Mnemonics": f"/api/v1/mnemonics/{self.session_id}",
            "Cheat Sheets": f"/api/v1/cheat-sheets/{self.session_id}",
            "Notes": f"/api/v1/notes/{self.session_id}"
        }
        
        results = {}
        
        for name, endpoint in outputs.items():
            try:
                response = requests.get(f"{self.base_url}{endpoint}", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Count items
                    if name == "Questions" and "questions" in data:
                        count = len(data["questions"])
                        results[name] = count
                        logger.info(f"✅ {name}: {count} items")
                        
                        # Show sample question
                        if count > 0:
                            sample = data["questions"][0]
                            logger.info(f"   📄 Sample: {sample.get('question_text', '')[:100]}...")
                            
                    elif name == "Mock Tests" and "mock_tests" in data:
                        count = len(data["mock_tests"])
                        results[name] = count
                        logger.info(f"✅ {name}: {count} items")
                        
                    elif name == "Mnemonics" and "mnemonics" in data:
                        count = len(data["mnemonics"])
                        results[name] = count
                        logger.info(f"✅ {name}: {count} items")
                        
                        # Show sample mnemonic
                        if count > 0:
                            sample = data["mnemonics"][0]
                            logger.info(f"   🧠 Sample: {sample.get('mnemonic_text', '')[:100]}...")
                            
                    elif name == "Cheat Sheets" and "cheat_sheets" in data:
                        count = len(data["cheat_sheets"])
                        results[name] = count
                        logger.info(f"✅ {name}: {count} items")
                        
                    elif name == "Notes" and "notes" in data:
                        results[name] = 1 if data["notes"] else 0
                        logger.info(f"✅ {name}: Available")
                        
                    else:
                        results[name] = 0
                        logger.warning(f"⚠️ {name}: No data found")
                        
                else:
                    results[name] = 0
                    logger.error(f"❌ {name}: HTTP {response.status_code}")
                    
            except Exception as e:
                results[name] = 0
                logger.error(f"❌ {name}: Error - {e}")
        
        # Summary
        success_count = sum(1 for count in results.values() if count > 0)
        logger.info(f"\n📊 RESULTS: {success_count}/5 outputs generated")
        
        for name, count in results.items():
            status = "✅" if count > 0 else "❌"
            logger.info(f"   {status} {name}: {count}")
        
        return success_count == 5
    
    def run_test(self):
        """Run complete test"""
        logger.info("🧪 Starting Topic Input Flow Test")
        logger.info("="*50)
        
        try:
            if not self.login():
                return False
            
            if not self.submit_topic():
                return False
            
            if not self.wait_for_completion():
                return False
            
            success = self.verify_all_outputs()
            
            logger.info("="*50)
            if success:
                logger.info("🎉 TEST PASSED - All 5 outputs generated!")
            else:
                logger.error("💥 TEST FAILED - Some outputs missing")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Test failed: {e}")
            return False

if __name__ == "__main__":
    test = TopicFlowTest()
    test.run_test()

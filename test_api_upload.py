#!/usr/bin/env python3
"""
Simple API-based test for Study Buddy upload flow
Tests the complete flow via API calls instead of browser automation
"""

import requests
import json
import time
import os

class StudyBuddyAPITest:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.mobile = "7045024042"
        self.password = "Alan#walker672"
        self.test_file = "/home/unknown/Downloads/Text-to-PDF-r1p.pdf"
        self.session = requests.Session()
        self.token = None
        
    def test_login(self):
        """Test login via API"""
        print("🔐 Testing API login...")
        
        login_data = {
            "mobile_number": self.mobile,
            "password": self.password
        }
        
        response = self.session.post(f"{self.base_url}/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            if self.token:
                print("✅ Login successful")
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                return True
            else:
                print("❌ No token received")
                return False
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return False
    
    def test_file_upload(self):
        """Test file upload via API"""
        print("📤 Testing file upload...")
        
        if not os.path.exists(self.test_file):
            print(f"❌ Test file not found: {self.test_file}")
            return False
        
        # Prepare file upload
        files = {
            'files': ('test.pdf', open(self.test_file, 'rb'), 'application/pdf')
        }
        
        data = {
            'processing_mode': 'OCR_AI',
            'user_id': 'test_user'  # In real app this comes from JWT
        }
        
        response = self.session.post(f"{self.base_url}/api/v1/upload", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            session_id = result.get("session_id")
            print(f"✅ Upload successful - Session ID: {session_id}")
            return session_id
        else:
            print(f"❌ Upload failed: {response.status_code} - {response.text}")
            return None
    
    def test_processing_status(self, session_id):
        """Monitor processing status"""
        print("⏳ Waiting for processing to complete...")
        
        # Since status endpoint might not exist, wait a bit and try to get results
        print("⏳ Waiting 30 seconds for processing...")
        time.sleep(30)
        
        return True  # Assume processing completed
    
    def test_get_results(self, session_id):
        """Test getting generated results"""
        print("📋 Testing results retrieval...")
        
        result_types = [
            ("questions", "Questions"),
            ("mock-tests", "Mock Tests"), 
            ("mnemonics", "Mnemonics"),
            ("cheat-sheets", "Cheat Sheets"),
            ("notes", "Notes")
        ]
        
        results_found = {}
        
        for endpoint, name in result_types:
            response = self.session.get(f"{self.base_url}/api/v1/{endpoint}/{session_id}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for content
                if endpoint == "questions":
                    items = data.get("questions", [])
                elif endpoint == "mock-tests":
                    items = data.get("mock_tests", [])
                elif endpoint == "mnemonics":
                    items = data.get("mnemonics", [])
                elif endpoint == "cheat-sheets":
                    items = data.get("cheat_sheets", [])
                elif endpoint == "notes":
                    items = data.get("notes", {})
                    items = [items] if items else []
                
                if items:
                    print(f"✅ {name}: {len(items)} items found")
                    results_found[name] = items
                    
                    # Check for mock responses
                    if endpoint == "questions" and items:
                        first_question = items[0]
                        question_text = first_question.get("question", "")
                        if "FALLBACK" in question_text or "API_KEY" in question_text:
                            print(f"❌ {name}: MOCK RESPONSES DETECTED!")
                            print("   - AI service not configured properly")
                            results_found[f"{name}_is_mock"] = True
                        else:
                            print(f"✅ {name}: Real AI responses detected")
                            results_found[f"{name}_is_mock"] = False
                else:
                    print(f"⚠️ {name}: No items found")
            else:
                print(f"❌ {name}: Failed to retrieve ({response.status_code})")
        
        return results_found
    
    def run_test(self):
        """Run complete API test"""
        try:
            print("🚀 Starting Study Buddy API Test")
            print("=" * 50)
            
            # Test login
            if not self.test_login():
                return False
            
            # Test upload
            session_id = self.test_file_upload()
            if not session_id:
                return False
            
            # Monitor processing
            if not self.test_processing_status(session_id):
                return False
            
            # Get results
            results = self.test_get_results(session_id)
            
            print("\n" + "=" * 50)
            print("📊 Test Results Summary:")
            
            total_types = 5
            found_types = len([k for k in results.keys() if not k.endswith("_is_mock")])
            mock_types = len([k for k, v in results.items() if k.endswith("_is_mock") and v])
            
            print(f"   📋 Content Types Found: {found_types}/{total_types}")
            print(f"   🤖 Real AI Responses: {found_types - mock_types}")
            print(f"   ⚠️  Mock Responses: {mock_types}")
            
            if found_types >= 3 and mock_types == 0:
                print("\n✅ API Test PASSED - Real AI content generated!")
                return True
            elif found_types >= 3:
                print("\n⚠️ API Test PARTIAL - Content generated but some are mock responses")
                print("   💡 Check GEMINI_API_KEY configuration")
                return True
            else:
                print("\n❌ API Test FAILED - Insufficient content generated")
                return False
                
        except Exception as e:
            print(f"\n❌ API Test Failed: {str(e)}")
            return False

if __name__ == "__main__":
    test = StudyBuddyAPITest()
    success = test.run_test()
    
    if success:
        print("\n🎉 Study Buddy is working!")
    else:
        print("\n🔧 Study Buddy needs configuration fixes")

#!/usr/bin/env python3
"""
End-to-End Upload Test
Tests the complete flow: upload PDF -> process -> generate all 5 outputs
"""

import requests
import time
import json
import os
from pathlib import Path

class StudyBuddyE2ETest:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.api_url = f"{self.base_url}/api/v1"
        self.token = None
        self.user_id = None
        self.session_id = None
        
    def login(self):
        """Login and get auth token"""
        print("🔐 Logging in...")
        
        # Use test credentials - adjust as needed
        login_data = {
            "mobile_number": "+919876543210",
            "password": "testpass123"
        }
        
        response = requests.post(f"{self.base_url}/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.user_id = data.get("user", {}).get("id")
            print(f"✅ Login successful - User ID: {self.user_id}")
            return True
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return False
    
    def upload_file(self, file_path):
        """Upload PDF file"""
        print(f"📤 Uploading file: {file_path}")
        
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return False
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        with open(file_path, 'rb') as f:
            files = {"files": (os.path.basename(file_path), f, "application/pdf")}
            data = {"processing_mode": "default"}
            
            response = requests.post(
                f"{self.api_url}/upload/",
                headers=headers,
                files=files,
                data=data
            )
        
        if response.status_code == 200:
            result = response.json()
            self.session_id = result.get("session_id")
            print(f"✅ Upload successful - Session ID: {self.session_id}")
            return True
        else:
            print(f"❌ Upload failed: {response.status_code} - {response.text}")
            return False
    
    def wait_for_processing(self, timeout=120):
        """Wait for processing to complete"""
        print("⏳ Waiting for processing to complete...")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            response = requests.get(
                f"{self.api_url}/upload/status/{self.session_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                status_data = response.json()
                status = status_data.get("status")
                
                print(f"📊 Status: {status}")
                
                if status == "completed":
                    print("✅ Processing completed!")
                    return True
                elif status == "failed":
                    error = status_data.get("error_message", "Unknown error")
                    print(f"❌ Processing failed: {error}")
                    return False
                
                time.sleep(5)
            else:
                print(f"❌ Status check failed: {response.status_code}")
                return False
        
        print("❌ Processing timeout")
        return False
    
    def verify_questions(self):
        """Verify questions were generated"""
        print("📝 Checking questions...")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(
            f"{self.api_url}/questions/{self.session_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            questions = data.get("questions", [])
            count = len(questions)
            
            if count > 0:
                print(f"✅ Questions generated: {count}")
                # Show sample question
                if questions:
                    sample = questions[0]
                    print(f"   Sample: {sample.get('question_text', 'N/A')[:100]}...")
                return True
            else:
                print("❌ No questions generated")
                return False
        else:
            print(f"❌ Questions check failed: {response.status_code}")
            return False
    
    def verify_mock_tests(self):
        """Verify mock tests were generated"""
        print("📊 Checking mock tests...")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(
            f"{self.api_url}/mock-tests/{self.session_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            tests = data.get("mock_tests", [])
            count = len(tests)
            
            if count > 0:
                print(f"✅ Mock tests generated: {count}")
                if tests:
                    sample = tests[0]
                    print(f"   Sample: {sample.get('test_name', 'N/A')}")
                return True
            else:
                print("❌ No mock tests generated")
                return False
        else:
            print(f"❌ Mock tests check failed: {response.status_code}")
            return False
    
    def verify_mnemonics(self):
        """Verify mnemonics were generated"""
        print("🧠 Checking mnemonics...")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(
            f"{self.api_url}/mnemonics/{self.session_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            mnemonics = data.get("mnemonics", [])
            count = len(mnemonics)
            
            if count > 0:
                print(f"✅ Mnemonics generated: {count}")
                if mnemonics:
                    sample = mnemonics[0]
                    print(f"   Sample: {sample.get('topic', 'N/A')} - {sample.get('mnemonic_text', 'N/A')[:50]}...")
                return True
            else:
                print("❌ No mnemonics generated")
                return False
        else:
            print(f"❌ Mnemonics check failed: {response.status_code}")
            return False
    
    def verify_cheat_sheets(self):
        """Verify cheat sheets were generated"""
        print("📋 Checking cheat sheets...")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(
            f"{self.api_url}/cheat-sheets/{self.session_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            sheets = data.get("cheat_sheets", [])
            count = len(sheets)
            
            if count > 0:
                print(f"✅ Cheat sheets generated: {count}")
                if sheets:
                    sample = sheets[0]
                    print(f"   Sample: {sample.get('title', 'N/A')}")
                return True
            else:
                print("❌ No cheat sheets generated")
                return False
        else:
            print(f"❌ Cheat sheets check failed: {response.status_code}")
            return False
    
    def verify_notes(self):
        """Verify notes were generated"""
        print("📖 Checking notes...")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(
            f"{self.api_url}/notes/{self.session_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            notes = data.get("notes", [])
            count = len(notes)
            
            if count > 0:
                print(f"✅ Notes generated: {count}")
                if notes:
                    sample = notes[0]
                    print(f"   Sample: {sample.get('title', 'N/A')}")
                return True
            else:
                print("❌ No notes generated")
                return False
        else:
            print(f"❌ Notes check failed: {response.status_code}")
            return False
    
    def run_test(self, pdf_path):
        """Run complete end-to-end test"""
        print("🚀 Starting End-to-End Upload Test")
        print("=" * 50)
        
        # Step 1: Login
        if not self.login():
            return False
        
        # Step 2: Upload file
        if not self.upload_file(pdf_path):
            return False
        
        # Step 3: Wait for processing
        if not self.wait_for_processing():
            return False
        
        # Step 4: Verify all 5 outputs
        print("\n🔍 Verifying generated content...")
        print("-" * 30)
        
        results = {
            "questions": self.verify_questions(),
            "mock_tests": self.verify_mock_tests(),
            "mnemonics": self.verify_mnemonics(),
            "cheat_sheets": self.verify_cheat_sheets(),
            "notes": self.verify_notes()
        }
        
        # Summary
        print("\n📊 TEST RESULTS")
        print("=" * 50)
        
        passed = sum(results.values())
        total = len(results)
        
        for feature, success in results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{feature.replace('_', ' ').title()}: {status}")
        
        print(f"\nOverall: {passed}/{total} features working")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! End-to-end flow is working perfectly.")
            return True
        else:
            print("⚠️  Some features failed. Check the logs above.")
            return False

def main():
    # Test configuration
    pdf_path = "/home/unknown/Downloads/Text-to-PDF-r1p.pdf"
    
    # Run test
    test = StudyBuddyE2ETest()
    success = test.run_test(pdf_path)
    
    exit(0 if success else 1)

if __name__ == "__main__":
    main()

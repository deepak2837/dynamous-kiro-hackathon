#!/usr/bin/env python3
"""
End-to-End Upload Test

Tests the complete upload flow with an existing authenticated user:
1. Login with test credentials
2. Upload a PDF file
3. Monitor processing status
4. Verify all 5 output types are generated (questions, mock tests, mnemonics, cheat sheets, notes)

Prerequisites:
- Backend server running on localhost:8000
- Test user already registered with credentials:
  - Mobile: 7045024042
  - Password: Alan#walker672
- Test PDF file at: /home/unknown/Downloads/Text-to-PDF-r1p.pdf
"""

import requests
import time
import os
import json



def login_test_user():
    """Login with test user"""
    print("🔐 Logging in test user...")
    
    login_data = {
        "mobile_number": "7045024042",
        "password": "Alan#walker672"
    }
    
    try:
        response = requests.post("http://localhost:8000/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user_id = data.get("user", {}).get("id")
            print(f"✅ Login successful - Token: {token[:20]}...")
            return token, user_id
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ Login request failed: {e}")
        return None, None

def test_authenticated_upload():
    """Test upload with authentication using existing user credentials"""
    pdf_path = "/home/unknown/Downloads/Text-to-PDF-r1p.pdf"
    
    print("🚀 Authenticated Upload Test")
    print("=" * 40)
    
    # Check file
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return False
    
    # Login user (assumes user already exists in database)
    token, user_id = login_test_user()
    
    if not token:
        return False
    
    # Upload file
    print(f"\n📤 Uploading {os.path.basename(pdf_path)}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        with open(pdf_path, 'rb') as f:
            files = {"files": (os.path.basename(pdf_path), f, "application/pdf")}
            data = {"processing_mode": "default"}
            
            response = requests.post(
                "http://localhost:8000/api/v1/upload/",
                headers=headers,
                files=files,
                data=data,
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            session_id = result.get("session_id")
            print(f"✅ Upload successful!")
            print(f"   Session ID: {session_id}")
            print(f"   Files uploaded: {result.get('files_uploaded', 0)}")
            
            # Wait for processing
            print("\n⏳ Waiting for processing...")
            return wait_and_verify(session_id, token)
            
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Upload request failed: {e}")
        return False

def wait_and_verify(session_id, token):
    """Wait for processing and verify results"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Wait for processing
    for i in range(24):  # Wait up to 2 minutes
        try:
            response = requests.get(
                f"http://localhost:8000/api/v1/upload/status/{session_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                status_data = response.json()
                status = status_data.get("status")
                print(f"   Status: {status}")
                
                if status == "completed":
                    print("✅ Processing completed!")
                    break
                elif status == "failed":
                    print(f"❌ Processing failed: {status_data.get('error_message')}")
                    return False
                    
                time.sleep(5)
            else:
                print(f"❌ Status check failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Status check error: {e}")
            return False
    else:
        print("❌ Processing timeout")
        return False
    
    # Verify all 5 outputs
    print("\n🔍 Verifying generated content...")
    
    endpoints = {
        "Questions": f"/api/v1/questions/{session_id}",
        "Mock Tests": f"/api/v1/mock-tests/{session_id}",
        "Mnemonics": f"/api/v1/mnemonics/{session_id}",
        "Cheat Sheets": f"/api/v1/cheat-sheets/{session_id}",
        "Notes": f"/api/v1/notes/{session_id}"
    }
    
    results = {}
    
    for name, endpoint in endpoints.items():
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", headers=headers)
            if response.status_code == 200:
                data = response.json()
                
                # Count items based on response structure
                if name == "Questions":
                    count = len(data.get("questions", []))
                elif name == "Mock Tests":
                    count = len(data.get("mock_tests", []))
                else:
                    # For mnemonics, cheat_sheets, notes
                    key = name.lower().replace(" ", "_")
                    count = len(data.get(key, []))
                
                results[name] = count > 0
                status = "✅" if count > 0 else "❌"
                print(f"   {name}: {status} ({count} items)")
            else:
                results[name] = False
                print(f"   {name}: ❌ (HTTP {response.status_code})")
                
        except Exception as e:
            results[name] = False
            print(f"   {name}: ❌ (Error: {e})")
    
    # Summary
    passed = sum(results.values())
    total = len(results)
    
    print(f"\n📊 RESULTS: {passed}/{total} features working")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! End-to-end flow is working perfectly.")
        return True
    else:
        print("⚠️ Some features failed.")
        return False

if __name__ == "__main__":
    success = test_authenticated_upload()
    exit(0 if success else 1)

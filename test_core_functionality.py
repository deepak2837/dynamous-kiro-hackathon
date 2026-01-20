#!/usr/bin/env python3
"""
Core Functionality Test for StudyBuddy

Tests the essential functionality:
1. User authentication
2. File upload
3. Processing completion
4. All 5 outputs generation

This test uses API calls instead of browser automation for reliability.
"""

import requests
import time
import json

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_CREDENTIALS = {
    "mobile_number": "7045024042",
    "password": "Alan#walker672"
}
TEST_FILE_PATH = "/home/unknown/Downloads/Text-to-PDF-r1p.pdf"

def log(message):
    """Print timestamped log message"""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_authentication():
    """Test user authentication"""
    log("🔐 Testing authentication...")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/auth/login",
            json=TEST_CREDENTIALS,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user = data.get("user")
            
            if token and user:
                log(f"✅ Authentication successful - User: {user.get('name')}")
                return token
            else:
                log("❌ Authentication failed - Invalid response format")
                return None
        else:
            log(f"❌ Authentication failed - Status: {response.status_code}")
            return None
            
    except Exception as e:
        log(f"❌ Authentication error: {e}")
        return None

def test_file_upload(token):
    """Test file upload and processing initiation"""
    log("📤 Testing file upload...")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        with open(TEST_FILE_PATH, 'rb') as file:
            files = {"files": file}
            data = {"processing_mode": "default"}
            
            response = requests.post(
                f"{API_BASE_URL}/api/v1/upload/",
                headers=headers,
                files=files,
                data=data,
                timeout=30
            )
        
        if response.status_code == 200:
            data = response.json()
            session_id = data.get("session_id")
            
            if session_id:
                log(f"✅ File upload successful - Session ID: {session_id}")
                return session_id
            else:
                log("❌ File upload failed - No session ID returned")
                return None
        else:
            log(f"❌ File upload failed - Status: {response.status_code}")
            log(f"Response: {response.text}")
            return None
            
    except Exception as e:
        log(f"❌ File upload error: {e}")
        return None

def test_processing_completion(token, session_id, max_wait=120):
    """Test processing completion"""
    log("⏳ Testing processing completion...")
    
    headers = {"Authorization": f"Bearer {token}"}
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(
                f"{API_BASE_URL}/api/v1/upload/status/{session_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                
                if status == "completed":
                    log("✅ Processing completed successfully")
                    return True
                elif status == "failed":
                    log("❌ Processing failed")
                    log(f"Error: {data.get('error_message', 'Unknown error')}")
                    return False
                else:
                    log(f"Status: {status}")
                    time.sleep(5)
            else:
                log(f"❌ Status check failed - Status: {response.status_code}")
                return False
                
        except Exception as e:
            log(f"Error checking status: {e}")
            time.sleep(5)
    
    log("⏰ Processing timeout")
    return False

def test_outputs_generation(token, session_id):
    """Test that all 5 outputs are generated"""
    log("🔍 Testing outputs generation...")
    
    headers = {"Authorization": f"Bearer {token}"}
    outputs = {
        "Questions": f"{API_BASE_URL}/api/v1/questions/{session_id}",
        "Mock Tests": f"{API_BASE_URL}/api/v1/mock-tests/{session_id}",
        "Mnemonics": f"{API_BASE_URL}/api/v1/mnemonics/{session_id}",
        "Cheat Sheets": f"{API_BASE_URL}/api/v1/cheat-sheets/{session_id}",
        "Notes": f"{API_BASE_URL}/api/v1/notes/{session_id}"
    }
    
    results = {}
    
    for output_name, url in outputs.items():
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if data contains actual content
                if output_name == "Questions":
                    count = len(data.get("questions", []))
                elif output_name == "Mock Tests":
                    count = len(data.get("mock_tests", []))
                elif output_name == "Mnemonics":
                    count = len(data.get("mnemonics", []))
                elif output_name == "Cheat Sheets":
                    count = len(data.get("cheat_sheets", []))
                elif output_name == "Notes":
                    count = len(data.get("notes", []))
                
                if count > 0:
                    log(f"✅ {output_name}: {count} items generated")
                    results[output_name] = True
                else:
                    log(f"❌ {output_name}: No items generated")
                    results[output_name] = False
            else:
                log(f"❌ {output_name}: API error - Status {response.status_code}")
                results[output_name] = False
                
        except Exception as e:
            log(f"❌ {output_name}: Error - {e}")
            results[output_name] = False
    
    return results

def main():
    """Run complete core functionality test"""
    log("=" * 60)
    log("🚀 Starting StudyBuddy Core Functionality Test")
    log("=" * 60)
    
    # Test 1: Authentication
    token = test_authentication()
    if not token:
        log("❌ Test failed at authentication step")
        return False
    
    # Test 2: File Upload
    session_id = test_file_upload(token)
    if not session_id:
        log("❌ Test failed at file upload step")
        return False
    
    # Test 3: Processing Completion
    processing_success = test_processing_completion(token, session_id)
    if not processing_success:
        log("❌ Test failed at processing step")
        return False
    
    # Test 4: Outputs Generation
    outputs = test_outputs_generation(token, session_id)
    
    # Summary
    log("=" * 60)
    log("📊 TEST SUMMARY")
    log("=" * 60)
    log("Authentication: ✅")
    log("File Upload: ✅")
    log("Processing: ✅")
    log("Outputs:")
    
    success_count = 0
    for output_name, success in outputs.items():
        status_icon = "✅" if success else "❌"
        log(f"  {status_icon} {output_name}")
        if success:
            success_count += 1
    
    log(f"\nOutputs Generated: {success_count}/5")
    
    if success_count == 5:
        log("🎉 ALL TESTS PASSED - StudyBuddy core functionality is working!")
        return True
    else:
        log("⚠️ Some outputs failed to generate")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

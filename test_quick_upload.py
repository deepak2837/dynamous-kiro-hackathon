#!/usr/bin/env python3
"""
Quick Upload Test (No Auth Required)
Tests upload functionality directly with the backend
"""

import requests
import time
import os

def test_upload_direct():
    """Test upload without authentication (for debugging)"""
    
    pdf_path = "/home/unknown/Downloads/Text-to-PDF-r1p.pdf"
    
    print("🧪 Quick Upload Test")
    print("=" * 30)
    
    # Check if file exists
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return False
    
    print(f"📁 File found: {os.path.basename(pdf_path)} ({os.path.getsize(pdf_path)} bytes)")
    
    # Test 1: Check backend health
    print("\n1️⃣ Testing backend health...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is healthy")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False
    
    # Test 2: Test upload endpoint (expect auth error)
    print("\n2️⃣ Testing upload endpoint...")
    try:
        with open(pdf_path, 'rb') as f:
            files = {"files": (os.path.basename(pdf_path), f, "application/pdf")}
            data = {"processing_mode": "default"}
            
            response = requests.post(
                "http://localhost:8000/api/v1/upload/",
                files=files,
                data=data,
                timeout=10
            )
        
        if response.status_code == 401:
            print("✅ Upload endpoint working (authentication required)")
            return True
        elif response.status_code == 200:
            print("✅ Upload successful (no auth required)")
            return True
        else:
            print(f"❌ Upload failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Upload request failed: {e}")
        return False

if __name__ == "__main__":
    success = test_upload_direct()
    print(f"\n{'🎉 Test completed successfully!' if success else '❌ Test failed!'}")
    exit(0 if success else 1)

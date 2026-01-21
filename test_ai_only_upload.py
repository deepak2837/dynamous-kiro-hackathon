#!/usr/bin/env python3
"""
Test AI_ONLY mode upload via API
"""
import requests
import os

def test_ai_only_upload():
    """Test uploading a file with AI_ONLY mode"""
    
    # API endpoint
    url = "http://localhost:8000/api/v1/upload"
    
    # Test file
    test_file = "test_sample.pdf"
    if not os.path.exists(test_file):
        print(f"❌ Test file {test_file} not found")
        return False
    
    # Prepare the request
    files = {
        'files': ('test_sample.pdf', open(test_file, 'rb'), 'application/pdf')
    }
    
    data = {
        'processing_mode': 'ai_only',  # This should trigger our new service
        'user_id': '696e936b3d2d1e1da742da0d'  # Test user ID
    }
    
    print(f"🚀 TESTING AI_ONLY UPLOAD")
    print(f"📁 File: {test_file}")
    print(f"🤖 Mode: ai_only")
    print(f"👤 User: {data['user_id']}")
    
    try:
        # Make the request
        response = requests.post(url, files=files, data=data)
        
        print(f"\n📡 UPLOAD RESPONSE:")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            session_id = response.json().get('session_id')
            print(f"   Session ID: {session_id}")
            
            # Check processing status
            status_url = f"http://localhost:8000/api/v1/upload/status/{session_id}"
            status_response = requests.get(status_url)
            
            print(f"\n📊 PROCESSING STATUS:")
            print(f"   Status: {status_response.status_code}")
            print(f"   Response: {status_response.json()}")
            
            return True
        else:
            print(f"❌ Upload failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    finally:
        files['files'][1].close()

if __name__ == "__main__":
    test_ai_only_upload()

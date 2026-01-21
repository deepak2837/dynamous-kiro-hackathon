#!/usr/bin/env python3
"""
Test AI_ONLY mode via upload endpoint (simulating frontend)
"""
import requests
import os

def test_ai_only_via_api():
    """Test uploading with AI_ONLY mode via API"""
    
    # API endpoint
    url = "http://localhost:8000/api/v1/upload"
    
    # Test file
    test_file = "test_sample.pdf"
    if not os.path.exists(test_file):
        print(f"❌ Test file {test_file} not found")
        return False
    
    # Prepare the request (simulating frontend)
    files = {
        'files': ('test_sample.pdf', open(test_file, 'rb'), 'application/pdf')
    }
    
    data = {
        'processing_mode': 'ai_only',  # This should trigger our new comprehensive service
        'user_id': '696e936b3d2d1e1da742da0d'  # Test user ID
    }
    
    print(f"🧪 TESTING AI_ONLY MODE VIA UPLOAD API")
    print(f"📁 File: {test_file}")
    print(f"🤖 Mode: ai_only (should trigger comprehensive processing)")
    print(f"👤 User: {data['user_id']}")
    
    try:
        # Make the request
        response = requests.post(url, files=files, data=data)
        
        print(f"\n📡 UPLOAD RESPONSE:")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Response: {result}")
            session_id = result.get('session_id')
            print(f"   Session ID: {session_id}")
            
            # Wait a bit for processing
            import time
            print(f"\n⏳ Waiting for processing to complete...")
            time.sleep(45)  # Wait for AI processing
            
            # Check results by querying questions
            questions_url = f"http://localhost:8000/api/v1/questions/{session_id}"
            questions_response = requests.get(questions_url)
            
            if questions_response.status_code == 200:
                questions_data = questions_response.json()
                question_count = len(questions_data.get('questions', []))
                
                print(f"\n📊 RESULTS:")
                print(f"   Questions generated: {question_count}")
                
                if question_count >= 10:
                    print(f"   ✅ SUCCESS: AI_ONLY mode working! Generated {question_count} questions")
                    print(f"   🎉 This indicates comprehensive processing was used")
                    return True
                else:
                    print(f"   ❌ FAILURE: Only {question_count} questions generated")
                    print(f"   🔍 This suggests fallback/old processing was used")
                    return False
            else:
                print(f"   ❌ Failed to get questions: {questions_response.status_code}")
                return False
                
        else:
            print(f"   ❌ Upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    finally:
        files['files'][1].close()

if __name__ == "__main__":
    success = test_ai_only_via_api()
    if success:
        print(f"\n🎉 AI_ONLY MODE TEST PASSED!")
    else:
        print(f"\n❌ AI_ONLY MODE TEST FAILED!")

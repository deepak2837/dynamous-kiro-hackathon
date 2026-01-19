#!/usr/bin/env python3
"""
Gemini API Connection Test Script
Tests both Google AI Studio and Google Cloud Vertex AI connections
"""

import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_google_ai_studio():
    """Test Google AI Studio connection (free tier)"""
    print("🧪 Testing Google AI Studio Connection...")
    
    try:
        import google.generativeai as genai
        
        # Configure API key
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ GEMINI_API_KEY not found in environment variables")
            return False
            
        genai.configure(api_key=api_key)
        
        # Test model listing
        print("📋 Available models:")
        models = genai.list_models()
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                print(f"  ✓ {model.name}")
        
        # Test content generation
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content("Hello! This is a test. Please respond with 'AI Studio connection successful!'")
        
        print(f"🤖 Response: {response.text}")
        print("✅ Google AI Studio connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ Google AI Studio connection failed: {e}")
        return False

def test_google_cloud_vertex():
    """Test Google Cloud Vertex AI connection"""
    print("\n🧪 Testing Google Cloud Vertex AI Connection...")
    
    try:
        import vertexai
        from vertexai.generative_models import GenerativeModel
        
        # Configure credentials
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
        location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        
        if not project_id:
            print("❌ GOOGLE_CLOUD_PROJECT_ID not found in environment variables")
            return False
            
        if not credentials_path or not os.path.exists(credentials_path):
            print(f"❌ Service account credentials not found at: {credentials_path}")
            return False
            
        # Set credentials environment variable
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        
        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)
        
        # Test content generation
        model = GenerativeModel('gemini-2.5-flash')
        response = model.generate_content("Hello! This is a test. Please respond with 'Vertex AI connection successful!'")
        
        print(f"🤖 Response: {response.text}")
        print("✅ Google Cloud Vertex AI connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ Google Cloud Vertex AI connection failed: {e}")
        return False

def test_medical_content_generation():
    """Test medical content generation capabilities"""
    print("\n🧪 Testing Medical Content Generation...")
    
    try:
        import google.generativeai as genai
        
        # Use AI Studio for medical content (less restrictive)
        api_key = os.getenv('GEMINI_API_KEY')
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Test medical question generation
        prompt = """
        Generate a medical MCQ about the cardiovascular system suitable for NEET preparation.
        Include 4 options and explain the correct answer.
        """
        
        response = model.generate_content(prompt)
        print("📚 Medical Content Generation Test:")
        print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
        print("✅ Medical content generation successful!")
        return True
        
    except Exception as e:
        print(f"❌ Medical content generation failed: {e}")
        return False

def test_prompt_loading():
    """Test loading system prompts"""
    print("\n🧪 Testing System Prompt Loading...")
    
    try:
        prompts_dir = "./prompts"
        if not os.path.exists(prompts_dir):
            print(f"❌ Prompts directory not found: {prompts_dir}")
            return False
            
        prompt_files = [f for f in os.listdir(prompts_dir) if f.endswith('.txt')]
        
        if not prompt_files:
            print("❌ No prompt files found in prompts directory")
            return False
            
        print(f"📁 Found {len(prompt_files)} prompt files:")
        for prompt_file in prompt_files:
            file_path = os.path.join(prompts_dir, prompt_file)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"  ✓ {prompt_file} ({len(content)} characters)")
        
        print("✅ System prompt loading successful!")
        return True
        
    except Exception as e:
        print(f"❌ System prompt loading failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 StudyBuddy Gemini API Connection Test")
    print("=" * 50)
    
    # Check required packages
    required_packages = ['google-generativeai', 'google-cloud-aiplatform', 'python-dotenv']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'google-generativeai':
                import google.generativeai
            elif package == 'google-cloud-aiplatform':
                import vertexai
            elif package == 'python-dotenv':
                import dotenv
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False
    
    # Run tests
    tests = [
        test_google_ai_studio,
        test_google_cloud_vertex,
        test_medical_content_generation,
        test_prompt_loading
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"✅ Passed: {sum(results)}/{len(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}/{len(results)}")
    
    if all(results):
        print("\n🎉 All tests passed! Gemini integration is ready.")
        return True
    else:
        print("\n⚠️  Some tests failed. Check configuration and credentials.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

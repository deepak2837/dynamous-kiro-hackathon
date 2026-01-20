#!/usr/bin/env python3
"""
Test script to verify AI service configuration
Run this to check if your GEMINI_API_KEY is working
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Load environment variables
load_dotenv('backend/.env')

async def test_ai_service():
    """Test the AI service configuration"""
    try:
        from backend.app.services.ai_service import AIService
        from backend.app.config import settings
        
        print("🔍 Testing AI Service Configuration...")
        print(f"📁 Environment file: backend/.env")
        
        # Check API key
        api_key = settings.google_ai_api_key
        if not api_key:
            print("❌ GEMINI_API_KEY not found in environment")
            return False
        elif api_key == "your_api_key_here" or api_key == "your_actual_gemini_api_key_here":
            print("❌ GEMINI_API_KEY is still set to placeholder value")
            print("   Please replace with your actual Gemini API key")
            return False
        else:
            print(f"✅ GEMINI_API_KEY found: {api_key[:10]}...{api_key[-4:]}")
        
        # Test AI service
        print("\n🤖 Testing AI service...")
        ai_service = AIService()
        
        # Test with simple medical text
        test_text = """
        The heart is a muscular organ that pumps blood throughout the body. 
        It has four chambers: two atria and two ventricles. 
        The right side pumps blood to the lungs, while the left side pumps blood to the rest of the body.
        """
        
        print("📝 Generating test questions...")
        questions = await ai_service.generate_new_questions(test_text, 2)
        
        if questions and len(questions) > 0:
            print(f"✅ Successfully generated {len(questions)} questions!")
            print("\n📋 Sample question:")
            q = questions[0]
            print(f"   Q: {q.get('question', 'N/A')}")
            print(f"   A: {q.get('options', ['N/A'])[0]}")
            
            # Check if it's a fallback question
            if "FALLBACK" in q.get('question', ''):
                print("⚠️  This is a fallback question - AI service failed")
                return False
            else:
                print("✅ Real AI-generated question detected!")
                return True
        else:
            print("❌ No questions generated")
            return False
            
    except Exception as e:
        print(f"❌ Error testing AI service: {str(e)}")
        return False

async def main():
    """Main test function"""
    print("🚀 Study Buddy AI Service Test")
    print("=" * 40)
    
    success = await test_ai_service()
    
    print("\n" + "=" * 40)
    if success:
        print("✅ AI Service is working correctly!")
        print("   Your uploaded files should now generate real AI content.")
    else:
        print("❌ AI Service configuration failed!")
        print("\n🔧 To fix this:")
        print("1. Get a Gemini API key from: https://makersuite.google.com/app/apikey")
        print("2. Edit backend/.env file")
        print("3. Replace GEMINI_API_KEY=your_actual_gemini_api_key_here")
        print("4. Restart the backend server")
        print("5. Run this test again")

if __name__ == "__main__":
    asyncio.run(main())

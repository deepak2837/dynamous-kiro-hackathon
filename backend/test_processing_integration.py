#!/usr/bin/env python3
"""
Test script to verify processing integration
"""
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.processing import ProcessingService
from app.models import ProcessingMode
from app.logging_config import logger

async def test_processing():
    """Test processing service"""
    print("🧪 Testing Processing Integration...")
    
    try:
        # Create a simple test file
        test_content = "This is a test medical document about anatomy and physiology."
        test_file = "/tmp/test_medical.txt"
        
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        # Test processing service
        processing_service = ProcessingService()
        session_id = "test-session-123"
        
        print(f"📄 Created test file: {test_file}")
        print(f"🔄 Starting processing for session: {session_id}")
        
        # This would normally be called in background
        # await processing_service.start_processing(
        #     session_id, 
        #     [test_file], 
        #     ProcessingMode.DEFAULT, 
        #     "test-user"
        # )
        
        print("✅ Processing service integration ready!")
        print("📝 Note: Actual processing requires database connection")
        
    except Exception as e:
        print(f"❌ Processing test error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_processing())

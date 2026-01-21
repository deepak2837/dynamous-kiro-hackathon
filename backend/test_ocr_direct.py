#!/usr/bin/env python3
"""
Simple test script to verify OCR logging is working
Run this to test OCR functionality directly
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Configure logging to write to backend.log (same as production)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backend.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Set specific loggers
logging.getLogger("app.services.file_processor").setLevel(logging.INFO)

async def test_ocr_logging():
    """Test OCR logging functionality"""
    
    print("🧪 Testing OCR Logging Functionality")
    print("=" * 50)
    
    try:
        from app.services.file_processor import FileProcessor
        
        # Initialize file processor
        file_processor = FileProcessor()
        
        # Test with a non-existent file to see error logging
        test_file = "/tmp/test_ocr_file.pdf"
        
        print(f"🔍 Testing OCR logging with file: {test_file}")
        print("📝 Expected: OCR pipeline logs should appear in backend.log")
        print("-" * 40)
        
        # Test OCR extraction (will fail but should show logs)
        result = await file_processor.extract_text_ocr(test_file, session_id="test-session-123")
        
        print(f"✅ OCR test completed")
        print(f"📊 Result length: {len(result)} characters")
        
        # Test with batched OCR
        print("\n🔍 Testing batched OCR logging...")
        batches = await file_processor.extract_text_ocr_batched(test_file, "test-session-456")
        
        print(f"✅ Batched OCR test completed")
        print(f"📊 Batches created: {len(batches)}")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 OCR Logging Test Complete")
    print("📋 Check 'backend.log' file for detailed OCR logs")
    print("🔍 Look for logs with emojis like 🔄, 📊, 🔧, 👁️, etc.")

if __name__ == "__main__":
    asyncio.run(test_ocr_logging())

#!/usr/bin/env python3
"""
Test script to verify OCR logging functionality
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.file_processor import FileProcessor

# Configure logging to see all the detailed logs
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('ocr_test.log')
    ]
)

async def test_ocr_logging():
    """Test OCR logging with different file types"""
    
    print("🧪 Starting OCR Logging Test")
    print("=" * 50)
    
    # Initialize file processor
    file_processor = FileProcessor()
    
    # Test files (you can replace these with actual test files)
    test_files = [
        # Add paths to your test files here
        # "/path/to/test.pdf",
        # "/path/to/test.jpg", 
        # "/path/to/test.pptx"
    ]
    
    # If no test files provided, create a simple test
    if not test_files:
        print("⚠️ No test files provided. Testing with non-existent file to see error logging...")
        test_files = ["/tmp/non_existent_test.pdf"]
    
    for test_file in test_files:
        print(f"\n🔍 Testing OCR logging for: {test_file}")
        print("-" * 40)
        
        try:
            # Test OCR extraction with logging
            result = await file_processor.extract_text_ocr(test_file, session_id="test-session-123")
            
            print(f"✅ OCR completed. Result length: {len(result)} characters")
            if result:
                print(f"📝 First 100 chars: {result[:100]}...")
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 OCR Logging Test Complete")
    print("📋 Check 'ocr_test.log' file for detailed logs")

if __name__ == "__main__":
    asyncio.run(test_ocr_logging())

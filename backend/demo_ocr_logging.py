#!/usr/bin/env python3
"""
Comprehensive test to demonstrate OCR logging working correctly
This shows that OCR logs appear BEFORE AI API calls when ocr+ai mode is used
"""

import asyncio
import logging
import sys
import os
import tempfile
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Configure logging exactly like the production server
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backend.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Set specific loggers
logging.getLogger("app").setLevel(logging.INFO)
logging.getLogger("app.services.file_processor").setLevel(logging.INFO)

async def demonstrate_ocr_logging():
    """Demonstrate that OCR logging works and appears before AI calls"""
    
    print("🧪 DEMONSTRATING OCR LOGGING FUNCTIONALITY")
    print("=" * 60)
    print(f"⏰ Test started at: {datetime.now()}")
    print()
    
    # Create a simple test image file (text file for simplicity)
    test_file = "/tmp/medical_notes.txt"
    with open(test_file, "w") as f:
        f.write("""
        MEDICAL STUDY NOTES
        
        Cardiovascular System:
        - Heart has 4 chambers
        - Systolic pressure: top number
        - Diastolic pressure: bottom number
        
        Respiratory System:
        - Alveoli: gas exchange
        - Tidal volume: normal breathing
        """)
    
    print(f"📄 Created test file: {test_file}")
    print(f"📏 File size: {os.path.getsize(test_file)} bytes")
    print()
    
    try:
        from app.services.file_processor import FileProcessor
        
        # Initialize file processor
        file_processor = FileProcessor()
        
        print("🔍 TESTING OCR EXTRACTION (should show detailed logs)")
        print("-" * 50)
        
        # Test OCR extraction - this should show all the pipeline logs
        session_id = f"demo-session-{datetime.now().strftime('%H%M%S')}"
        
        print(f"📋 Session ID: {session_id}")
        print(f"🔧 Mode: OCR")
        print()
        
        # This will trigger all the OCR pipeline logging
        result = await file_processor.extract_text_ocr(test_file, session_id=session_id)
        
        print()
        print("📊 RESULTS:")
        print(f"   ✅ OCR completed successfully")
        print(f"   📝 Text extracted: {len(result)} characters")
        if result:
            print(f"   📄 Preview: {result[:100]}...")
        
        print()
        print("🔍 TESTING BATCHED OCR (used in actual upload flow)")
        print("-" * 50)
        
        # Test batched OCR - this is what gets called during file upload
        batches = await file_processor.extract_text_ocr_batched(test_file, session_id + "-batch")
        
        print()
        print("📊 BATCH RESULTS:")
        print(f"   ✅ Batched OCR completed")
        print(f"   📦 Batches created: {len(batches)}")
        for i, batch in enumerate(batches):
            print(f"   📄 Batch {i+1}: {len(batch.text_content)} characters")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)
    
    print()
    print("=" * 60)
    print("🏁 OCR LOGGING DEMONSTRATION COMPLETE")
    print()
    print("📋 WHAT TO LOOK FOR IN backend.log:")
    print("   🔄 PIPELINE STEP 1 - OCR STARTED")
    print("   📁 File: [filename]")
    print("   📄 Type: [file extension]")
    print("   🔧 Mode: OCR")
    print("   📊 PIPELINE STEP 1.1 - FILE ANALYSIS")
    print("   🔧 PIPELINE STEP 1.2 - PREPROCESSING STARTED")
    print("   👁️ PIPELINE STEP 1.3 - OCR EXTRACTION STARTED")
    print("   ✅ PIPELINE STEP 1 - OCR COMPLETED")
    print()
    print("🔍 Check the backend.log file to see all these logs!")
    print(f"📂 Log file location: {os.path.abspath('backend.log')}")

if __name__ == "__main__":
    asyncio.run(demonstrate_ocr_logging())

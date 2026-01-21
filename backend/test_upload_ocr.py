#!/usr/bin/env python3
"""
Test script to simulate file upload with OCR+AI mode
This will help verify that OCR logs appear when uploading files
"""

import asyncio
import logging
import sys
import os
import tempfile
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Configure logging to write to backend.log
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
logging.getLogger("app.services.processing").setLevel(logging.INFO)

async def test_upload_with_ocr():
    """Test upload flow with OCR+AI mode"""
    
    print("🧪 Testing Upload Flow with OCR+AI Mode")
    print("=" * 50)
    
    try:
        from app.api.upload_basic import process_files_background
        
        # Create a test session
        session_id = "test-session-ocr-ai"
        
        # Create test file data (simulating uploaded files)
        files_data = [
            {
                "filename": "test_document.pdf",
                "path": "/tmp/test_document.pdf",
                "s3_key": None,
                "size": 1024
            }
        ]
        
        # Create a dummy PDF file for testing
        test_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000074 00000 n \n0000000120 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n179\n%%EOF"
        
        with open("/tmp/test_document.pdf", "wb") as f:
            f.write(test_content)
        
        # Simulate session storage
        from app.api.upload_basic import session_storage
        session_storage[session_id] = {
            "session_id": session_id,
            "user_id": "test-user-123",
            "processing_mode": "ocr+ai",  # This should trigger OCR logging
            "status": "pending"
        }
        
        print(f"🔍 Testing background processing with OCR+AI mode")
        print(f"📁 Session ID: {session_id}")
        print(f"📄 Test file: test_document.pdf")
        print("-" * 40)
        
        # Run the background processing
        await process_files_background(session_id, files_data)
        
        print(f"✅ Background processing completed")
        
        # Clean up
        if os.path.exists("/tmp/test_document.pdf"):
            os.remove("/tmp/test_document.pdf")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("🏁 Upload OCR Test Complete")
    print("📋 Check 'backend.log' file for OCR pipeline logs")
    print("🔍 Look for logs starting with 🔄 PIPELINE STEP 1 - OCR STARTED")

if __name__ == "__main__":
    asyncio.run(test_upload_with_ocr())

#!/usr/bin/env python3
"""
Test OCR extraction with the actual PDF file
"""

import asyncio
import logging
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backend.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

async def test_pdf_ocr():
    """Test OCR with the actual PDF file"""
    
    pdf_file = "/home/unknown/Downloads/Text-to-PDF-r1p.pdf"
    
    print(f"🧪 Testing OCR with PDF: {pdf_file}")
    
    if not os.path.exists(pdf_file):
        print(f"❌ PDF file not found: {pdf_file}")
        return
    
    print(f"📄 File size: {os.path.getsize(pdf_file)} bytes")
    
    try:
        from app.services.file_processor import FileProcessor
        
        file_processor = FileProcessor()
        
        print("🔍 Testing OCR extraction...")
        result = await file_processor.extract_text_ocr(pdf_file, session_id="test-pdf-session")
        
        print(f"✅ OCR completed")
        print(f"📝 Text length: {len(result)} characters")
        if result:
            print(f"📄 Preview: {result[:200]}...")
        else:
            print("⚠️ No text extracted!")
            
        print("\n🔍 Testing batched OCR...")
        batches = await file_processor.extract_text_ocr_batched(pdf_file, "test-pdf-batch")
        
        print(f"📦 Batches: {len(batches)}")
        for i, batch in enumerate(batches):
            print(f"   Batch {i+1}: {len(batch.text_content)} chars")
            if batch.text_content:
                print(f"   Preview: {batch.text_content[:100]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_pdf_ocr())

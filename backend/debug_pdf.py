#!/usr/bin/env python3
"""
Debug the specific PDF file processing
"""

import asyncio
import logging
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug_pdf.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

async def debug_pdf_processing():
    """Debug the specific PDF processing issue"""
    
    pdf_file = "/home/unknown/Downloads/Text-to-PDF-r1p.pdf"
    
    print(f"🔍 Debugging PDF: {pdf_file}")
    
    if not os.path.exists(pdf_file):
        print(f"❌ PDF file not found: {pdf_file}")
        return
    
    try:
        from app.services.file_processor import FileProcessor
        
        file_processor = FileProcessor()
        
        # Test batch creation
        print("\n1. Testing batch creation...")
        batches = file_processor.create_batches(pdf_file, "debug-session")
        print(f"   Created {len(batches)} batches:")
        for i, batch in enumerate(batches):
            print(f"   Batch {i+1}: Pages {batch.page_range[0]}-{batch.page_range[1]}")
        
        # Test direct PDF text extraction
        print("\n2. Testing direct PDF text extraction...")
        direct_text = await file_processor._extract_pdf_text(pdf_file)
        print(f"   Direct extraction: {len(direct_text)} characters")
        if direct_text:
            print(f"   Preview: {direct_text[:100]}...")
        
        # Test OCR batched extraction
        print("\n3. Testing OCR batched extraction...")
        ocr_batches = await file_processor.extract_text_ocr_batched(pdf_file, "debug-ocr-session")
        print(f"   OCR batches: {len(ocr_batches)}")
        for i, batch in enumerate(ocr_batches):
            print(f"   Batch {i+1}: {len(batch.text_content)} characters")
            if batch.text_content:
                print(f"   Preview: {batch.text_content[:100]}...")
        
        # Test small PDF processing
        print("\n4. Testing small PDF processing...")
        small_pdf_text = await file_processor._process_small_pdf(pdf_file)
        print(f"   Small PDF processing: {len(small_pdf_text)} characters")
        if small_pdf_text:
            print(f"   Preview: {small_pdf_text[:100]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_pdf_processing())

#!/usr/bin/env python3
"""
Test File Upload AI Processing Service
Tests the new separate file upload processing service
"""
import asyncio
import sys
import os
import uuid
from datetime import datetime

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Change to backend directory for imports
original_cwd = os.getcwd()
os.chdir(backend_path)

from app.database import get_database, connect_to_mongo
from app.services.file_upload_processing_service import FileUploadProcessingService
from app.models import ProcessingMode

async def test_file_upload_processing():
    """Test the new file upload processing service"""
    print("🧪 TESTING FILE UPLOAD AI PROCESSING SERVICE")
    print("=" * 60)
    
    # Connect to database first
    await connect_to_mongo()
    print("✅ Connected to database")
    
    # Create test session
    session_id = str(uuid.uuid4())
    user_id = "test_user_123"
    
    print(f"📋 Test Session ID: {session_id}")
    print(f"👤 Test User ID: {user_id}")
    
    # Create test session in database
    db = get_database()
    
    # Use existing test PDF
    test_file = os.path.join(original_cwd, "test_sample.pdf")
    if not os.path.exists(test_file):
        print(f"❌ Test file {test_file} not found")
        return False
    
    session_data = {
        "session_id": session_id,
        "user_id": user_id,
        "session_name": "Test File Upload Session",
        "created_at": datetime.utcnow(),
        "file_paths": [test_file],
        "s3_keys": [],
        "processing_mode": "ai_only",
        "processing_status": "pending",
        "progress": 0
    }
    
    await db.study_sessions.insert_one(session_data)
    print(f"✅ Created test session in database")
    
    try:
        # Test the new file upload processing service
        print(f"\n🚀 TESTING FILE UPLOAD PROCESSING SERVICE")
        processor = FileUploadProcessingService()
        
        await processor.process_uploaded_files(session_id, user_id)
        
        print(f"\n✅ FILE UPLOAD PROCESSING COMPLETED")
        
        # Verify results
        print(f"\n🔍 VERIFYING RESULTS:")
        
        questions = await db.questions.find({"session_id": session_id}).to_list(None)
        print(f"   📝 Questions: {len(questions)}")
        
        mock_tests = await db.mock_tests.find({"session_id": session_id}).to_list(None)
        print(f"   📊 Mock Tests: {len(mock_tests)}")
        
        mnemonics = await db.mnemonics.find({"session_id": session_id}).to_list(None)
        print(f"   🧠 Mnemonics: {len(mnemonics)}")
        
        cheat_sheets = await db.cheat_sheets.find({"session_id": session_id}).to_list(None)
        print(f"   📋 Cheat Sheets: {len(cheat_sheets)}")
        
        notes = await db.notes.find({"session_id": session_id}).to_list(None)
        print(f"   📖 Notes: {len(notes)}")
        
        # Show sample question
        if questions:
            sample_q = questions[0]
            print(f"\n📝 SAMPLE QUESTION:")
            print(f"   Question: {sample_q['question_text'][:100]}...")
            print(f"   Options: {len(sample_q.get('options', []))}")
            print(f"   Difficulty: {sample_q.get('difficulty', 'N/A')}")
        
        # Show sample mnemonic
        if mnemonics:
            sample_m = mnemonics[0]
            print(f"\n🧠 SAMPLE MNEMONIC:")
            print(f"   Topic: {sample_m.get('topic', 'N/A')}")
            print(f"   Mnemonic: {sample_m.get('mnemonic_text', 'N/A')[:100]}...")
        
        print(f"\n🎉 FILE UPLOAD AI PROCESSING TEST SUCCESSFUL!")
        return True
        
    except Exception as e:
        print(f"❌ FILE UPLOAD PROCESSING FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        print(f"\n🧹 CLEANING UP TEST DATA")
        await db.study_sessions.delete_one({"session_id": session_id})
        await db.questions.delete_many({"session_id": session_id})
        await db.mock_tests.delete_many({"session_id": session_id})
        await db.mnemonics.delete_many({"session_id": session_id})
        await db.cheat_sheets.delete_many({"session_id": session_id})
        await db.notes.delete_many({"session_id": session_id})
        print(f"✅ Cleanup completed")

if __name__ == "__main__":
    asyncio.run(test_file_upload_processing())

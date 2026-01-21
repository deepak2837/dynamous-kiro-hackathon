#!/usr/bin/env python3
"""
Test AI_ONLY mode processing directly
"""
import asyncio
import sys
import os
import uuid
from datetime import datetime

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)
os.chdir(backend_path)

from app.database import get_database, connect_to_mongo
from app.services.processing import ProcessingService
from app.models import ProcessingMode

async def test_ai_only_processing():
    """Test AI_ONLY mode processing directly"""
    print("🧪 TESTING AI_ONLY MODE PROCESSING DIRECTLY")
    print("=" * 60)
    
    # Connect to database
    await connect_to_mongo()
    print("✅ Connected to database")
    
    # Create test session
    session_id = str(uuid.uuid4())
    user_id = "test_user_ai_only"
    
    print(f"📋 Test Session ID: {session_id}")
    print(f"👤 Test User ID: {user_id}")
    
    # Use existing test PDF
    test_file = os.path.join(os.path.dirname(backend_path), "test_sample.pdf")
    if not os.path.exists(test_file):
        print(f"❌ Test file {test_file} not found")
        return False
    
    # Create test session in database
    db = get_database()
    session_data = {
        "session_id": session_id,
        "user_id": user_id,
        "session_name": "AI_ONLY Test Session",
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
        # Test the processing service with AI_ONLY mode
        print(f"\n🚀 TESTING PROCESSING SERVICE WITH AI_ONLY MODE")
        processing_service = ProcessingService()
        
        # This should trigger the new file upload processing service
        await processing_service.start_processing(
            session_id=session_id,
            files=[test_file],
            mode=ProcessingMode.AI_ONLY,  # This should trigger our new service
            user_id=user_id
        )
        
        print(f"\n✅ PROCESSING COMPLETED")
        
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
        
        # Check if we got comprehensive results (like topic feature)
        if len(questions) >= 10 and len(mnemonics) >= 3 and len(cheat_sheets) >= 1 and len(notes) >= 1:
            print(f"\n🎉 AI_ONLY MODE WORKING CORRECTLY!")
            print(f"   Generated comprehensive study materials like topic feature")
            return True
        else:
            print(f"\n⚠️ AI_ONLY MODE NOT WORKING AS EXPECTED")
            print(f"   Should generate 10+ questions, 3+ mnemonics, 1+ cheat sheet, 1+ notes")
            return False
        
    except Exception as e:
        print(f"❌ PROCESSING FAILED: {str(e)}")
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
    asyncio.run(test_ai_only_processing())

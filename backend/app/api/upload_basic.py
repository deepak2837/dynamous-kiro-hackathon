from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Depends
from fastapi.security import HTTPBearer
from typing import List
import uuid
import os
import tempfile
from datetime import datetime
from app.services.s3_service import s3_service
from app.api.auth_simple import get_current_user
from app.auth_models_simple import UserResponse
import asyncio
import json
import pymongo

router = APIRouter()
security = HTTPBearer()

# In-memory storage for session status
session_storage = {}

def get_db():
    """Get database connection"""
    client = pymongo.MongoClient("mongodb://localhost:27017")
    return client["studybuddy"]

@router.get("/file-limits")
async def get_file_limits():
    """Get file size limits"""
    return {
        "pdf": {"max_size_mb": 50, "description": "PDF documents up to 50MB"},
        "image": {"max_size_mb": 10, "description": "Images up to 10MB"},
        "slide": {"max_size_mb": 100, "description": "Presentation files up to 100MB"}
    }

async def process_files_background(session_id: str, files_data: List[dict]):
    """Background task to process uploaded files"""
    try:
        # Update status to processing
        session_storage[session_id]["status"] = "processing"
        
        # Update database status
        try:
            db = get_db()
            db.study_sessions.update_one(
                {"session_id": session_id},
                {"$set": {"status": "processing"}}
            )
        except Exception as e:
            print(f"Error updating session status: {e}")
        
        # Simulate processing time
        await asyncio.sleep(2)
        
        # Extract text from files (simplified)
        all_text = ""
        for file_data in files_data:
            # In real implementation, extract text from file
            all_text += f"Content from {file_data['filename']}: Sample medical content about anatomy, physiology, and pathology.\n"
        
        # Generate outputs
        questions = generate_questions(all_text)
        mock_tests = generate_mock_tests(questions)
        mnemonics = generate_mnemonics(all_text)
        cheat_sheets = generate_cheat_sheets(all_text)
        notes = generate_notes(all_text, questions, mnemonics)
        
        # Store results in memory
        session_storage[session_id].update({
            "status": "completed",
            "questions": questions,
            "mock_tests": mock_tests,
            "mnemonics": mnemonics,
            "cheat_sheets": cheat_sheets,
            "notes": notes,
            "completed_at": datetime.utcnow().isoformat()
        })
        
        # Store results in database
        try:
            db = get_db()
            
            # Update session status
            db.study_sessions.update_one(
                {"session_id": session_id},
                {"$set": {
                    "status": "completed",
                    "outputs_generated": {
                        "questions": True,
                        "mock_tests": True,
                        "mnemonics": True,
                        "cheat_sheets": True,
                        "notes": True
                    }
                }}
            )
            
            # Store individual content items
            for question in questions:
                question["session_id"] = session_id
                db.questions.insert_one(question)
            
            for test in mock_tests:
                test["session_id"] = session_id
                db.mock_tests.insert_one(test)
            
            for mnemonic in mnemonics:
                mnemonic["session_id"] = session_id
                db.mnemonics.insert_one(mnemonic)
            
            for sheet in cheat_sheets:
                sheet["session_id"] = session_id
                db.cheat_sheets.insert_one(sheet)
            
            for note in notes:
                note["session_id"] = session_id
                db.notes.insert_one(note)
                
        except Exception as e:
            print(f"Error storing results in database: {e}")
        
    except Exception as e:
        session_storage[session_id]["status"] = "failed"
        session_storage[session_id]["error"] = str(e)
        
        # Update database status
        try:
            db = get_db()
            db.study_sessions.update_one(
                {"session_id": session_id},
                {"$set": {"status": "failed"}}
            )
        except Exception as e:
            print(f"Error updating failed status: {e}")

def generate_questions(text: str) -> List[dict]:
    """Generate sample questions"""
    return [
        {
            "question_id": str(uuid.uuid4()),
            "question_text": "What is the primary function of the heart?",
            "options": [
                {"option_id": "a", "text": "Pump blood", "is_correct": True},
                {"option_id": "b", "text": "Filter toxins", "is_correct": False},
                {"option_id": "c", "text": "Produce hormones", "is_correct": False},
                {"option_id": "d", "text": "Store nutrients", "is_correct": False}
            ],
            "explanation": "The heart's primary function is to pump blood throughout the body.",
            "difficulty": "Easy",
            "medical_subject": "Anatomy"
        },
        {
            "question_id": str(uuid.uuid4()),
            "question_text": "Which chamber of the heart receives oxygenated blood?",
            "options": [
                {"option_id": "a", "text": "Right atrium", "is_correct": False},
                {"option_id": "b", "text": "Left atrium", "is_correct": True},
                {"option_id": "c", "text": "Right ventricle", "is_correct": False},
                {"option_id": "d", "text": "Left ventricle", "is_correct": False}
            ],
            "explanation": "The left atrium receives oxygenated blood from the lungs.",
            "difficulty": "Medium",
            "medical_subject": "Anatomy"
        }
    ]

def generate_mock_tests(questions: List[dict]) -> List[dict]:
    """Generate mock tests from questions"""
    return [
        {
            "test_id": str(uuid.uuid4()),
            "test_name": "Cardiovascular System Mock Test",
            "questions": [q["question_id"] for q in questions],
            "duration_minutes": 30,
            "total_marks": len(questions) * 2
        }
    ]

def generate_mnemonics(text: str) -> List[dict]:
    """Generate sample mnemonics"""
    return [
        {
            "mnemonic_id": str(uuid.uuid4()),
            "topic": "Heart Chambers",
            "mnemonic_text": "Try Pulling My Arm - Tricuspid, Pulmonary, Mitral, Aortic (heart valves)",
            "explanation": "Helps remember the four heart valves in order",
            "key_terms": ["Tricuspid", "Pulmonary", "Mitral", "Aortic"],
            "is_india_specific": False
        },
        {
            "mnemonic_id": str(uuid.uuid4()),
            "topic": "Cranial Nerves",
            "mnemonic_text": "Oh Oh Oh To Touch And Feel Very Good Velvet, Ah Heaven - for 12 cranial nerves",
            "explanation": "Mnemonic for remembering all 12 cranial nerves",
            "key_terms": ["Olfactory", "Optic", "Oculomotor"],
            "is_india_specific": True
        }
    ]

def generate_cheat_sheets(text: str) -> List[dict]:
    """Generate sample cheat sheets"""
    return [
        {
            "sheet_id": str(uuid.uuid4()),
            "title": "Cardiovascular System Quick Reference",
            "key_points": [
                "Heart has 4 chambers: 2 atria, 2 ventricles",
                "Right side pumps deoxygenated blood to lungs",
                "Left side pumps oxygenated blood to body",
                "Normal heart rate: 60-100 bpm"
            ],
            "high_yield_facts": [
                "Cardiac output = Heart rate × Stroke volume",
                "Frank-Starling mechanism regulates stroke volume",
                "Coronary arteries supply blood to heart muscle"
            ]
        }
    ]

def generate_notes(text: str, questions: List[dict], mnemonics: List[dict]) -> List[dict]:
    """Generate compiled notes"""
    return [
        {
            "note_id": str(uuid.uuid4()),
            "title": "Study Session Summary",
            "content": "Comprehensive notes covering cardiovascular system",
            "important_questions": [q["question_id"] for q in questions[:3]],
            "summary_points": [
                "Heart anatomy and physiology covered",
                "Key concepts: cardiac cycle, blood flow",
                "Important mnemonics for memorization"
            ],
            "related_mnemonics": [m["mnemonic_id"] for m in mnemonics]
        }
    ]

@router.post("/")
async def upload_files(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    processing_mode: str = Form("default"),
    current_user: UserResponse = Depends(get_current_user)
):
    """Upload files and start processing - requires authentication"""
    try:
        user_id = current_user.id
        session_id = str(uuid.uuid4())
        uploaded_files = []
        
        # Initialize session storage (both in-memory and database)
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "processing_mode": processing_mode,
            "files_uploaded": []
        }
        
        session_storage[session_id] = session_data
        
        # Store in database
        try:
            db = get_db()
            db.study_sessions.insert_one({
                "session_id": session_id,
                "user_id": user_id,
                "session_name": f"Session {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
                "status": "pending",
                "created_at": datetime.utcnow(),
                "processing_mode": processing_mode,
                "files_uploaded": [],
                "outputs_generated": {
                    "questions": False,
                    "mock_tests": False,
                    "mnemonics": False,
                    "cheat_sheets": False,
                    "notes": False
                }
            })
        except Exception as e:
            print(f"Error storing session in database: {e}")
        
        for file in files:
            # Validate file
            if file.size > 50 * 1024 * 1024:  # 50MB limit
                raise HTTPException(status_code=413, detail=f"File {file.filename} too large")
            
            # Create temp file
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            # Upload to S3 or keep local
            file_url, s3_key = await s3_service.upload_file(
                temp_file_path, 
                session_id, 
                file.filename
            )
            
            uploaded_files.append({
                "filename": file.filename,
                "url": file_url,
                "s3_key": s3_key
            })
        
        # Start background processing
        background_tasks.add_task(process_files_background, session_id, uploaded_files)
        
        return {
            "session_id": session_id,
            "message": "Files uploaded successfully. Processing started.",
            "files_uploaded": len(uploaded_files)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{session_id}")
async def get_processing_status(
    session_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get processing status - requires authentication"""
    if session_id not in session_storage:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = session_storage[session_id]
    
    # Check if session belongs to current user
    if session["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied to this session")
    
    return {
        "session_id": session_id,
        "status": session["status"],
        "message": f"Session is {session['status']}",
        "error_message": session.get("error")
    }

@router.get("/check-upload-allowed/{user_id}")
async def check_upload_allowed(
    user_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Check if user can upload files - requires authentication"""
    # Verify user can only check their own upload status
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        "upload_allowed": True,
        "message": "Upload allowed",
        "remaining_seconds": 0
    }

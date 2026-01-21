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
from app.services.ai_service import AIService
import asyncio
import json
import pymongo
import logging

router = APIRouter()
security = HTTPBearer()

# In-memory storage for session status
session_storage = {}

logger = logging.getLogger(__name__)

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
        
        # Initialize AI Service
        ai_service = AIService()
        
        # Extract text from files (simplified for now - in production would use FileProcessor)
        all_text = ""
        for file_data in files_data:
            # Get file path or content
            file_path = file_data.get('path', '')
            filename = file_data.get('filename', '')
            
            # For now, use the filename to generate placeholder text
            # In production, this would use FileProcessor to extract actual text
            all_text += f"Content from {filename}: Medical educational material for study.\n"
        
        # Use real AI service to generate content
        user_id = session_storage[session_id].get("user_id", "unknown")
        try:
            # Generate questions using AI
            questions_data = await ai_service.generate_questions(all_text, doc_type="STUDY_NOTES", num_questions=15)
            questions = []
            for i, q in enumerate(questions_data):
                options_list = q.get("options", ["Option A", "Option B", "Option C", "Option D"])
                # Ensure options is a list of strings
                if options_list and isinstance(options_list[0], dict):
                    options_list = [o.get("text", f"Option {i}") for i, o in enumerate(options_list)]
                
                question = {
                    "question_id": str(uuid.uuid4()),
                    "session_id": session_id,
                    "user_id": user_id,
                    "question_text": q.get("question", f"Question {i+1}"),
                    "options": options_list[:4] if len(options_list) >= 4 else options_list + ["Option"] * (4 - len(options_list)),
                    "correct_answer": q.get("correct_answer", 0),
                    "explanation": q.get("explanation", ""),
                    "difficulty": q.get("difficulty", "medium").lower(),
                    "topic": q.get("topic", "General")
                }
                questions.append(question)
            
            # Generate mnemonics using AI
            mnemonics_data = await ai_service.generate_mnemonics(all_text, num_mnemonics=5)
            mnemonics = []
            for m in mnemonics_data:
                mnemonic = {
                    "mnemonic_id": str(uuid.uuid4()),
                    "mnemonic_text": m.get("mnemonic", ""),
                    "meaning": m.get("explanation", ""),
                    "topic": m.get("topic", "")
                }
                mnemonics.append(mnemonic)
            
            # Generate cheat sheets using AI
            cheat_sheets_data = await ai_service.generate_cheat_sheets(all_text, num_sheets=2)
            cheat_sheets = []
            for cs in cheat_sheets_data:
                sheet = {
                    "sheet_id": str(uuid.uuid4()),
                    "topic": cs.get("title", "Study Sheet"),
                    "key_points": cs.get("key_points", []),
                    "quick_facts": cs.get("high_yield_facts", [])
                }
                cheat_sheets.append(sheet)
            
        except Exception as ai_error:
            print(f"AI service error: {ai_error}, using fallback questions")
            # Fallback to mock data if AI fails
            questions = generate_questions(all_text)
            mnemonics = generate_mnemonics(all_text)
            cheat_sheets = generate_cheat_sheets(all_text)
        
        # Generate mock tests from questions (no AI needed)
        mock_tests = generate_mock_tests(questions)
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

@router.post("")
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

async def extract_text_from_file(file_path: str, file_type: str) -> str:
    """Extract text from uploaded file."""
    logger.info(f"=== EXTRACTING TEXT FROM FILE ===")
    logger.info(f"File path: {file_path}")
    logger.info(f"File type: {file_type}")
    
    text_content = ""
    
    try:
        if file_type == "application/pdf":
            # PDF extraction logic
            # ...existing code...
            pass
        elif file_type.startswith("image/"):
            # OCR for images
            # ...existing code...
            pass
        else:
            # Text file
            with open(file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
        
        # Log the extracted text
        logger.info(f"=== OCR/EXTRACTED TEXT START ===")
        logger.info(f"Text length: {len(text_content)} characters")
        logger.info(f"Text preview (first 1000 chars): {text_content[:1000]}")
        logger.info(f"=== OCR/EXTRACTED TEXT END ===")
        
        return text_content
        
    except Exception as e:
        logger.error(f"Error extracting text: {e}")
        return ""

async def process_upload(file, session_id: str, user_id: str, num_questions: int = 15):
    """Process uploaded file and generate questions."""
    # ...existing code for file saving...
    
    # Extract text
    text_content = await extract_text_from_file(file_path, file_type)
    
    logger.info(f"=== CONTENT BEING SENT TO AI ===")
    logger.info(f"Session ID: {session_id}")
    logger.info(f"Content length: {len(text_content)} characters")
    logger.info(f"Content preview: {text_content[:500] if text_content else 'EMPTY'}")
    logger.info(f"=== END CONTENT PREVIEW ===")
    
    if not text_content or len(text_content.strip()) < 50:
        logger.warning(f"Insufficient text content extracted: {len(text_content)} chars")
    
    # Generate questions
    questions = await ai_service.generate_questions(
        content=text_content,
        doc_type="STUDY_NOTES",
        num_questions=num_questions
    )
    
    logger.info(f"=== AI GENERATION RESULT ===")
    logger.info(f"Questions generated: {len(questions) if questions else 0}")
    logger.info(f"=== END AI RESULT ===")
    
    # ...existing code for saving questions...

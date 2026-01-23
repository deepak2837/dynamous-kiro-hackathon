from typing import List, Optional
from fastapi import APIRouter, Request, HTTPException
import logging

from app.database import get_database

logger = logging.getLogger(__name__)

router = APIRouter()

async def get_questions_by_session(session_id: str, skip: int = 0, limit: int = 50) -> List[dict]:
    """Get questions for a session from the database."""
    db = get_database()
    
    # First try to get from questions collection
    cursor = db.questions.find({"session_id": session_id}).skip(skip).limit(limit)
    questions = await cursor.to_list(length=limit)
    
    # If no questions found, try to get from sessions/uploads collection
    if not questions:
        # Check sessions collection
        session = await db.sessions.find_one({"session_id": session_id})
        if session and session.get("questions"):
            questions = session.get("questions", [])[skip:skip+limit]
        
        # Check uploads collection
        if not questions:
            upload = await db.uploads.find_one({"session_id": session_id})
            if upload and upload.get("questions"):
                questions = upload.get("questions", [])[skip:skip+limit]
        
        # Check upload_status collection
        if not questions:
            status = await db.upload_status.find_one({"session_id": session_id})
            if status and status.get("questions"):
                questions = status.get("questions", [])[skip:skip+limit]
    
    return questions

@router.get("/{session_id}", response_model=List[dict])
async def get_session_questions(
    request: Request,
    session_id: str,
    skip: int = 0,
    limit: int = 50
):
    """Get questions for a session"""
    questions = await get_questions_by_session(session_id, skip, limit)
    
    if not questions:
        logger.warning(f"No questions found for session {session_id}")
        return []
    
    # Transform database format to API format
    transformed_questions = []
    for q in questions:
        try:
            # Handle options - can be list of strings, list of dicts, or dict
            raw_options = q.get("options", [])
            correct = q.get("correct_answer", 0)
            options_dict = {}
            
            if isinstance(raw_options, list):
                # If it's a list of strings (most common for file upload)
                if len(raw_options) > 0 and isinstance(raw_options[0], str):
                    for i, opt_text in enumerate(raw_options):
                        opt_id = chr(65 + i)  # A, B, C, D
                        options_dict[opt_id] = opt_text
                    # Correct answer is an index, convert to letter
                    if isinstance(correct, int):
                        correct = chr(65 + correct)
                # If it's a list of dicts
                else:
                    for opt in raw_options:
                        if isinstance(opt, dict):
                            opt_id = opt.get("option_id", "").upper()
                            options_dict[opt_id] = opt.get("text", "")
                            if opt.get("is_correct"):
                                correct = opt_id
            elif isinstance(raw_options, dict):
                # Already a dict
                options_dict = raw_options
            
            # Normalize difficulty to lowercase
            difficulty = q.get("difficulty", "medium")
            if isinstance(difficulty, str):
                difficulty = difficulty.lower()
            
            # Build the question dict - use question_text OR question
            question_text = q.get("question_text") or q.get("question", "")
            
            question_data = {
                "id": str(q.get("_id", q.get("question_id", q.get("id", "")))),
                "session_id": q.get("session_id", session_id),
                "user_id": q.get("user_id", "anonymous"),
                "question_text": question_text,  # Frontend uses question_text
                "question": question_text,  # Also provide as question for compatibility
                "options": options_dict,
                "correct_answer": correct,
                "explanation": q.get("explanation", ""),
                "difficulty": difficulty,
                "topic": q.get("topic", "General"),
                "question_type": q.get("question_type", "multiple_choice"),
                "created_at": q.get("created_at"),
            }
            transformed_questions.append(question_data)
        except Exception as e:
            logger.error(f"Error transforming question: {e}")
            continue
    
    return transformed_questions

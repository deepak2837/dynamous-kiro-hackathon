from fastapi import APIRouter, HTTPException, Depends
from app.api.upload_basic import session_storage
from app.api.auth_simple import get_current_user
from app.auth_models_simple import UserResponse
import pymongo

router = APIRouter()

def get_db():
    """Get database connection"""
    client = pymongo.MongoClient("mongodb://localhost:27017")
    return client["studybuddy"]

@router.get("/{session_id}")
async def get_session_questions(
    session_id: str,
    skip: int = 0,
    limit: int = 50,
    difficulty: str = None,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get questions for a session - requires authentication"""
    
    # First check in-memory storage
    if session_id in session_storage:
        session = session_storage[session_id]
        if session["user_id"] == current_user.id:
            questions = session.get("questions", [])
            if questions:
                return {
                    "questions": questions,
                    "total_count": len(questions)
                }
    
    # Check database
    try:
        db = get_db()
        
        # Verify session belongs to user
        session = db.study_sessions.find_one({
            "session_id": session_id,
            "user_id": current_user.id
        })
        
        if not session:
            return {"questions": [], "total_count": 0}
        
        # Get questions from database
        questions = list(db.questions.find(
            {"session_id": session_id},
            {"_id": 0}  # Exclude MongoDB _id field
        ))
        
        # Clean up any remaining ObjectId fields
        for question in questions:
            # Convert any ObjectId fields to strings
            for key, value in question.items():
                if hasattr(value, '__class__') and 'ObjectId' in str(type(value)):
                    question[key] = str(value)
        
        return {
            "questions": questions,
            "total_count": len(questions)
        }
        
    except Exception as e:
        print(f"Database error: {e}")
        return {"questions": [], "total_count": 0}

@router.get("/question/{question_id}")
async def get_question(question_id: str):
    """Get a specific question"""
    # Search through all sessions for the question
    for session in session_storage.values():
        questions = session.get("questions", [])
        for question in questions:
            if question["question_id"] == question_id:
                return question
    
    raise HTTPException(status_code=404, detail="Question not found")

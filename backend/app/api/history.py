from fastapi import APIRouter, Depends, HTTPException
from typing import List
import pymongo
from bson import ObjectId
from app.auth_models_simple import UserResponse
from app.api.auth_simple import get_current_user
from app.utils.error_logger import error_logger

router = APIRouter(prefix="/api/v1/history", tags=["History"])

def get_db():
    client = pymongo.MongoClient("mongodb://localhost:27017")
    return client["studybuddy"]

@router.get("/sessions")
async def get_user_sessions(
    current_user: UserResponse = Depends(get_current_user)
):
    """Get user's session history"""
    try:
        db = get_db()
        sessions = list(db.study_sessions.find(
            {"user_id": current_user.id}
        ).sort("created_at", -1).limit(20))
        
        # Convert ObjectId to string and add content counts
        for session in sessions:
            session["_id"] = str(session["_id"])
            
            # Get content counts
            session_id = session.get("session_id")
            if session_id:
                session["content_counts"] = {
                    "questions": db.questions.count_documents({"session_id": session_id}),
                    "mock_tests": db.mock_tests.count_documents({"session_id": session_id}),
                    "mnemonics": db.mnemonics.count_documents({"session_id": session_id}),
                    "cheat_sheets": db.cheat_sheets.count_documents({"session_id": session_id}),
                    "notes": db.notes.count_documents({"session_id": session_id})
                }
            
        return {"sessions": sessions}
    except Exception as e:
        error_logger.log_error(e, "get_user_sessions", current_user.id)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}")
async def get_session_details(
    session_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get detailed session information"""
    try:
        db = get_db()
        session = db.study_sessions.find_one({
            "session_id": session_id,
            "user_id": current_user.id
        })
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
            
        session["_id"] = str(session["_id"])
        
        # Get generated content counts
        counts = {
            "questions": db.questions.count_documents({"session_id": session_id}),
            "mock_tests": db.mock_tests.count_documents({"session_id": session_id}),
            "mnemonics": db.mnemonics.count_documents({"session_id": session_id}),
            "cheat_sheets": db.cheat_sheets.count_documents({"session_id": session_id}),
            "notes": db.notes.count_documents({"session_id": session_id})
        }
        
        session["content_counts"] = counts
        return session
    except Exception as e:
        error_logger.log_error(e, "get_session_details", current_user.id, {"session_id": session_id})
        raise HTTPException(status_code=500, detail=str(e))

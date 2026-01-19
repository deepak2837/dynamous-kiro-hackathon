from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from app.models import SessionListResponse, StudySession
from app.database import get_database

router = APIRouter()

@router.get("/", response_model=SessionListResponse)
async def get_user_sessions(
    user_id: str = Query(...),  # In real app, this would come from JWT token
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db=Depends(get_database)
):
    """Get all sessions for a user"""
    
    # Get sessions with pagination
    cursor = db.study_sessions.find({"user_id": user_id}).sort("created_at", -1)
    sessions = await cursor.skip(skip).limit(limit).to_list(length=limit)
    
    # Get total count
    total_count = await db.study_sessions.count_documents({"user_id": user_id})
    
    # Convert to Pydantic models
    session_models = [StudySession(**session) for session in sessions]
    
    return SessionListResponse(
        sessions=session_models,
        total_count=total_count
    )

@router.get("/{session_id}")
async def get_session(
    session_id: str,
    db=Depends(get_database)
):
    """Get specific session details"""
    
    session = await db.study_sessions.find_one({"session_id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return StudySession(**session)

@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    db=Depends(get_database)
):
    """Delete a session and all associated data"""
    
    # Check if session exists
    session = await db.study_sessions.find_one({"session_id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Delete all associated data
    await db.study_sessions.delete_one({"session_id": session_id})
    await db.questions.delete_many({"session_id": session_id})
    await db.mock_tests.delete_many({"session_id": session_id})
    await db.mnemonics.delete_many({"session_id": session_id})
    await db.cheat_sheets.delete_many({"session_id": session_id})
    await db.notes.delete_many({"session_id": session_id})
    
    # TODO: Delete uploaded files
    
    return {"message": "Session deleted successfully"}

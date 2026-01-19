from fastapi import APIRouter, HTTPException, Depends, Query
from app.models import Note
from app.database import get_database

router = APIRouter()

@router.get("/{session_id}")
async def get_session_notes(
    session_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=20),
    db=Depends(get_database)
):
    """Get notes for a specific session"""
    
    # Get notes with pagination
    cursor = db.notes.find({"session_id": session_id}).sort("created_at", -1)
    notes = await cursor.skip(skip).limit(limit).to_list(length=limit)
    
    # Get total count
    total_count = await db.notes.count_documents({"session_id": session_id})
    
    # Convert to Pydantic models
    note_models = [Note(**note) for note in notes]
    
    return {
        "notes": note_models,
        "total_count": total_count
    }

@router.get("/note/{note_id}")
async def get_note(
    note_id: str,
    db=Depends(get_database)
):
    """Get specific note details"""
    
    note = await db.notes.find_one({"note_id": note_id})
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return Note(**note)

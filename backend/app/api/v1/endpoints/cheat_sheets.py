from fastapi import APIRouter, HTTPException, Depends, Query
from app.models import CheatSheet
from app.database import get_database

router = APIRouter()

@router.get("/{session_id}")
async def get_session_cheat_sheets(
    session_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=20),
    db=Depends(get_database)
):
    """Get cheat sheets for a specific session"""
    
    # Get cheat sheets with pagination
    cursor = db.cheat_sheets.find({"session_id": session_id}).sort("created_at", -1)
    cheat_sheets = await cursor.skip(skip).limit(limit).to_list(length=limit)
    
    # Get total count
    total_count = await db.cheat_sheets.count_documents({"session_id": session_id})
    
    # Convert to Pydantic models
    sheet_models = [CheatSheet(**sheet) for sheet in cheat_sheets]
    
    return {
        "cheat_sheets": sheet_models,
        "total_count": total_count
    }

@router.get("/sheet/{sheet_id}")
async def get_cheat_sheet(
    sheet_id: str,
    db=Depends(get_database)
):
    """Get specific cheat sheet details"""
    
    sheet = await db.cheat_sheets.find_one({"sheet_id": sheet_id})
    if not sheet:
        raise HTTPException(status_code=404, detail="Cheat sheet not found")
    
    return CheatSheet(**sheet)

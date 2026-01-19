from fastapi import APIRouter, HTTPException, Depends, Query
from app.models import Mnemonic
from app.database import get_database

router = APIRouter()

@router.get("/{session_id}")
async def get_session_mnemonics(
    session_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    db=Depends(get_database)
):
    """Get mnemonics for a specific session"""
    
    # Get mnemonics with pagination
    cursor = db.mnemonics.find({"session_id": session_id}).sort("created_at", -1)
    mnemonics = await cursor.skip(skip).limit(limit).to_list(length=limit)
    
    # Get total count
    total_count = await db.mnemonics.count_documents({"session_id": session_id})
    
    # Convert to Pydantic models
    mnemonic_models = [Mnemonic(**mnemonic) for mnemonic in mnemonics]
    
    return {
        "mnemonics": mnemonic_models,
        "total_count": total_count
    }

@router.get("/mnemonic/{mnemonic_id}")
async def get_mnemonic(
    mnemonic_id: str,
    db=Depends(get_database)
):
    """Get specific mnemonic details"""
    
    mnemonic = await db.mnemonics.find_one({"mnemonic_id": mnemonic_id})
    if not mnemonic:
        raise HTTPException(status_code=404, detail="Mnemonic not found")
    
    return Mnemonic(**mnemonic)

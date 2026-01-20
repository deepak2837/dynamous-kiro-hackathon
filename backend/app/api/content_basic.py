from fastapi import APIRouter, Depends
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
async def get_session_content(
    session_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get content for a session - used for mnemonics, cheat sheets, and notes"""
    
    # First check in-memory storage
    if session_id in session_storage:
        session = session_storage[session_id]
        if session["user_id"] == current_user.id:
            mnemonics = session.get("mnemonics", [])
            cheat_sheets = session.get("cheat_sheets", [])
            notes = session.get("notes", [])
            
            if mnemonics or cheat_sheets or notes:
                return {
                    "mnemonics": mnemonics,
                    "cheat_sheets": cheat_sheets,
                    "notes": notes,
                    "total_count": len(mnemonics + cheat_sheets + notes)
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
            return {"mnemonics": [], "cheat_sheets": [], "notes": [], "total_count": 0}
        
        # Get content from database
        mnemonics = list(db.mnemonics.find(
            {"session_id": session_id},
            {"_id": 0}
        ))
        
        cheat_sheets = list(db.cheat_sheets.find(
            {"session_id": session_id},
            {"_id": 0}
        ))
        
        notes = list(db.notes.find(
            {"session_id": session_id},
            {"_id": 0}
        ))
        
        return {
            "mnemonics": mnemonics,
            "cheat_sheets": cheat_sheets,
            "notes": notes,
            "total_count": len(mnemonics + cheat_sheets + notes)
        }
        
    except Exception as e:
        print(f"Database error: {e}")
        return {"mnemonics": [], "cheat_sheets": [], "notes": [], "total_count": 0}

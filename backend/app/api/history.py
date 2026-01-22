from fastapi import APIRouter, Depends, HTTPException, Header
from typing import List, Optional
from bson import ObjectId
from app.utils.error_logger import error_logger
import jwt

router = APIRouter(prefix="/api/v1/history", tags=["History"])

def get_db():
    from motor.motor_asyncio import AsyncIOMotorClient
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    return client["studybuddy"]

def get_user_id_from_token(authorization: Optional[str] = Header(None)) -> dict:
    """Extract user_id and mobile_number from JWT token"""
    if not authorization or not authorization.startswith("Bearer "):
        return {}
    
    token = authorization.replace("Bearer ", "")
    try:
        # Decode JWT token
        from app.config import settings
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return {
            "user_id": payload.get("user_id", ""),
            "mobile_number": payload.get("mobile_number", ""),
            "sub": payload.get("sub", "")
        }
    except jwt.ExpiredSignatureError:
        import logging
        logging.getLogger(__name__).warning("JWT token expired")
        return {}
    except jwt.InvalidTokenError as e:
        import logging
        logging.getLogger(__name__).warning(f"Invalid JWT token: {e}")
        return {}

@router.get("/sessions")
async def get_user_sessions(authorization: Optional[str] = Header(None)):
    """Get user's session history"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Get user info from JWT token
        user_info = get_user_id_from_token(authorization)
        logger.info(f"User info from JWT: {user_info}")
        
        db = get_db()
        
        # Build query to match any of the user identifiers
        user_id = user_info.get("user_id", "")
        mobile = user_info.get("mobile_number", "")
        
        # Create list of possible user_ids to search
        possible_ids = []
        if user_id:
            possible_ids.append(user_id)
        if mobile:
            possible_ids.append(mobile)
            # Also try without country code prefix
            if mobile.startswith("+91"):
                possible_ids.append(mobile[3:])  # Remove +91
            if mobile.startswith("+"):
                possible_ids.append(mobile[1:])  # Remove just +
        
        logger.info(f"Searching for user_ids: {possible_ids}")
        
        if possible_ids:
            sessions = await db.study_sessions.find(
                {"user_id": {"$in": possible_ids}}
            ).sort("created_at", -1).limit(20).to_list(length=20)
        else:
            # Fallback: get recent sessions
            logger.warning("No user identifiers found, returning recent sessions")
            sessions = await db.study_sessions.find().sort("created_at", -1).limit(20).to_list(length=20)
        
        logger.info(f"Found {len(sessions)} sessions")
        
        # Convert ObjectId to string and add content counts
        for session in sessions:
            session["_id"] = str(session["_id"])
            
            # Get content counts
            session_id = session.get("session_id")
            if session_id:
                session["content_counts"] = {
                    "questions": await db.questions.count_documents({"session_id": session_id}),
                    "mock_tests": await db.mock_tests.count_documents({"session_id": session_id}),
                    "mnemonics": await db.mnemonics.count_documents({"session_id": session_id}),
                    "cheat_sheets": await db.cheat_sheets.count_documents({"session_id": session_id}),
                    "notes": await db.notes.count_documents({"session_id": session_id})
                }
            
        return {"sessions": sessions}
    except Exception as e:
        error_logger.log_error(e, "get_user_sessions", None)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}")
async def get_session_details(
    session_id: str,
    user_id: str = "7045024042"
):
    """Get detailed session information"""
    try:
        db = get_db()
        session = db.study_sessions.find_one({
            "session_id": session_id,
            "user_id": user_id
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

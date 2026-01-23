from typing import List, Optional
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel
import logging
import uuid
from datetime import datetime

from app.database import get_database
from app.models import Flashcard

logger = logging.getLogger(__name__)

router = APIRouter()

class FlashcardReview(BaseModel):
    quality: int  # 0-5 rating for spaced repetition
    time_spent: int  # seconds spent reviewing
    
class FlashcardListResponse(BaseModel):
    flashcards: List[Flashcard]
    total_count: int

async def get_flashcards_by_session(session_id: str, skip: int = 0, limit: int = 50) -> List[dict]:
    """Get flashcards for a session from the database."""
    db = get_database()
    
    # Query only the flashcards collection with proper indexing
    cursor = db.flashcards.find({"session_id": session_id}).skip(skip).limit(limit)
    flashcards = await cursor.to_list(length=limit)
    
    return flashcards

async def ensure_flashcard_indexes():
    """Ensure proper database indexes for flashcard queries."""
    db = get_database()
    try:
        # Create compound index for efficient queries
        await db.flashcards.create_index([("session_id", 1), ("user_id", 1)])
        await db.flashcards.create_index([("session_id", 1), ("spaced_repetition_data.next_review_date", 1)])
        logger.info("Flashcard database indexes created successfully")
    except Exception as e:
        logger.warning(f"Failed to create flashcard indexes: {e}")

# Index creation will be handled by the first request or startup event

@router.get("/flashcards/{session_id}")
async def get_session_flashcards(session_id: str, request: Request, skip: int = 0, limit: int = 50):
    """Get flashcards for a specific session"""
    try:
        logger.info(f"Getting flashcards for session: {session_id}")
        
        flashcards = await get_flashcards_by_session(session_id, skip, limit)
        
        if not flashcards:
            logger.warning(f"No flashcards found for session: {session_id}")
            return {
                "flashcards": [],
                "total_count": 0,
                "message": "No flashcards found for this session"
            }
        
        # Convert to proper format if needed
        formatted_flashcards = []
        for flashcard in flashcards:
            if isinstance(flashcard, dict):
                # Ensure all required fields are present
                formatted_card = {
                    "flashcard_id": flashcard.get("flashcard_id", str(uuid.uuid4())),
                    "session_id": flashcard.get("session_id", session_id),
                    "user_id": flashcard.get("user_id", ""),
                    "front_text": flashcard.get("front_text", flashcard.get("front", "")),
                    "back_text": flashcard.get("back_text", flashcard.get("back", "")),
                    "category": flashcard.get("category", "clinical"),
                    "difficulty": flashcard.get("difficulty", "medium"),
                    "medical_topic": flashcard.get("medical_topic"),
                    "pronunciation": flashcard.get("pronunciation"),
                    "spaced_repetition_data": flashcard.get("spaced_repetition_data", {
                        "ease_factor": 2.5,
                        "interval": 1,
                        "repetitions": 0,
                        "next_review_date": datetime.utcnow().isoformat(),
                        "last_reviewed": None
                    }),
                    "created_at": flashcard.get("created_at", datetime.utcnow().isoformat())
                }
                formatted_flashcards.append(formatted_card)
        
        logger.info(f"Found {len(formatted_flashcards)} flashcards for session: {session_id}")
        
        return {
            "flashcards": formatted_flashcards,
            "total_count": len(formatted_flashcards)
        }
        
    except Exception as e:
        logger.error(f"Error getting flashcards for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get flashcards: {str(e)}")

@router.post("/flashcards/{flashcard_id}/review")
async def review_flashcard(flashcard_id: str, review_data: FlashcardReview, request: Request):
    """Update spaced repetition data after reviewing a flashcard"""
    try:
        logger.info(f"Reviewing flashcard: {flashcard_id} with quality: {review_data.quality}")
        
        db = get_database()
        
        # Find the flashcard
        flashcard = await db.flashcards.find_one({"flashcard_id": flashcard_id})
        if not flashcard:
            raise HTTPException(status_code=404, detail="Flashcard not found")
        
        # Calculate new spaced repetition values
        current_sr = flashcard.get("spaced_repetition_data", {
            "ease_factor": 2.5,
            "interval": 1,
            "repetitions": 0
        })
        
        # Simple spaced repetition algorithm (SM-2 based)
        quality = max(0, min(5, review_data.quality))  # Clamp to 0-5
        
        if quality >= 3:  # Correct answer
            if current_sr["repetitions"] == 0:
                interval = 1
            elif current_sr["repetitions"] == 1:
                interval = 6
            else:
                interval = round(current_sr["interval"] * current_sr["ease_factor"])
            
            repetitions = current_sr["repetitions"] + 1
            ease_factor = current_sr["ease_factor"] + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        else:  # Incorrect answer
            repetitions = 0
            interval = 1
            ease_factor = current_sr["ease_factor"]
        
        # Ensure ease factor doesn't go below 1.3
        ease_factor = max(1.3, ease_factor)
        
        # Calculate next review date
        next_review_date = datetime.utcnow()
        next_review_date = next_review_date.replace(day=next_review_date.day + interval)
        
        # Update spaced repetition data
        new_sr_data = {
            "ease_factor": ease_factor,
            "interval": interval,
            "repetitions": repetitions,
            "next_review_date": next_review_date.isoformat(),
            "last_reviewed": datetime.utcnow().isoformat()
        }
        
        # Update in database
        await db.flashcards.update_one(
            {"flashcard_id": flashcard_id},
            {"$set": {"spaced_repetition_data": new_sr_data}}
        )
        
        logger.info(f"Updated flashcard {flashcard_id} - next review in {interval} days")
        
        return {
            "message": "Flashcard review recorded successfully",
            "next_review_date": next_review_date.isoformat(),
            "interval_days": interval
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reviewing flashcard {flashcard_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to review flashcard: {str(e)}")

@router.get("/flashcards/{session_id}/study")
async def get_study_flashcards(session_id: str, request: Request, limit: int = 10):
    """Get flashcards due for review (spaced repetition study mode)"""
    try:
        logger.info(f"Getting study flashcards for session: {session_id}")
        
        db = get_database()
        current_time = datetime.utcnow()
        
        # Find flashcards due for review
        cursor = db.flashcards.find({
            "session_id": session_id,
            "$or": [
                {"spaced_repetition_data.next_review_date": {"$lte": current_time.isoformat()}},
                {"spaced_repetition_data.next_review_date": {"$exists": False}},
                {"spaced_repetition_data": {"$exists": False}}
            ]
        }).limit(limit)
        
        flashcards = await cursor.to_list(length=limit)
        
        if not flashcards:
            logger.info(f"No flashcards due for review in session: {session_id}")
            return {
                "flashcards": [],
                "total_count": 0,
                "message": "No flashcards due for review at this time"
            }
        
        # Format flashcards for study mode
        study_flashcards = []
        for flashcard in flashcards:
            study_card = {
                "flashcard_id": flashcard.get("flashcard_id"),
                "front_text": flashcard.get("front_text"),
                "back_text": flashcard.get("back_text"),
                "category": flashcard.get("category"),
                "difficulty": flashcard.get("difficulty"),
                "medical_topic": flashcard.get("medical_topic"),
                "pronunciation": flashcard.get("pronunciation"),
                "repetitions": flashcard.get("spaced_repetition_data", {}).get("repetitions", 0)
            }
            study_flashcards.append(study_card)
        
        logger.info(f"Found {len(study_flashcards)} flashcards due for review")
        
        return {
            "flashcards": study_flashcards,
            "total_count": len(study_flashcards)
        }
        
    except Exception as e:
        logger.error(f"Error getting study flashcards for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get study flashcards: {str(e)}")

from fastapi import APIRouter, HTTPException, Depends, Query
from app.models import QuestionListResponse, Question
from app.database import get_database

router = APIRouter()

@router.get("/{session_id}", response_model=QuestionListResponse)
async def get_session_questions(
    session_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    difficulty: str = Query(None),
    db=Depends(get_database)
):
    """Get questions for a specific session"""
    
    # Build query
    query = {"session_id": session_id}
    if difficulty:
        query["difficulty"] = difficulty
    
    # Get questions with pagination
    cursor = db.questions.find(query).sort("created_at", -1)
    questions = await cursor.skip(skip).limit(limit).to_list(length=limit)
    
    # Get total count
    total_count = await db.questions.count_documents(query)
    
    # Convert to Pydantic models
    question_models = [Question(**question) for question in questions]
    
    return QuestionListResponse(
        questions=question_models,
        total_count=total_count
    )

@router.get("/question/{question_id}")
async def get_question(
    question_id: str,
    db=Depends(get_database)
):
    """Get specific question details"""
    
    question = await db.questions.find_one({"question_id": question_id})
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    return Question(**question)

from fastapi import APIRouter, HTTPException, Depends, Query
from app.models import MockTestListResponse, MockTest
from app.database import get_database

router = APIRouter()

@router.get("/{session_id}", response_model=MockTestListResponse)
async def get_session_mock_tests(
    session_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    db=Depends(get_database)
):
    """Get mock tests for a specific session"""
    
    # Get mock tests with pagination
    cursor = db.mock_tests.find({"session_id": session_id}).sort("created_at", -1)
    mock_tests = await cursor.skip(skip).limit(limit).to_list(length=limit)
    
    # Get total count
    total_count = await db.mock_tests.count_documents({"session_id": session_id})
    
    # Convert to Pydantic models
    test_models = [MockTest(**test) for test in mock_tests]
    
    return MockTestListResponse(
        mock_tests=test_models,
        total_count=total_count
    )

@router.get("/test/{test_id}")
async def get_mock_test(
    test_id: str,
    db=Depends(get_database)
):
    """Get specific mock test details with questions"""
    
    test = await db.mock_tests.find_one({"test_id": test_id})
    if not test:
        raise HTTPException(status_code=404, detail="Mock test not found")
    
    # Get associated questions
    questions = await db.questions.find(
        {"question_id": {"$in": test["questions"]}}
    ).to_list(length=None)
    
    test_model = MockTest(**test)
    
    return {
        "test": test_model,
        "questions": questions
    }

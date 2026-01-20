from fastapi import APIRouter, HTTPException, Depends
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
async def get_session_mock_tests(
    session_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get mock tests for a session"""
    
    # First check in-memory storage
    if session_id in session_storage:
        session = session_storage[session_id]
        if session["user_id"] == current_user.id:
            mock_tests = session.get("mock_tests", [])
            if mock_tests:
                return {
                    "mock_tests": mock_tests,
                    "total_count": len(mock_tests)
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
            return {"mock_tests": [], "total_count": 0}
        
        # Get mock tests from database
        mock_tests = list(db.mock_tests.find(
            {"session_id": session_id},
            {"_id": 0}  # Exclude MongoDB _id field
        ))
        
        return {
            "mock_tests": mock_tests,
            "total_count": len(mock_tests)
        }
        
    except Exception as e:
        print(f"Database error: {e}")
        return {"mock_tests": [], "total_count": 0}

@router.get("/test/{test_id}")
async def get_mock_test(test_id: str):
    """Get a specific mock test"""
    # Search through all sessions for the test
    for session in session_storage.values():
        mock_tests = session.get("mock_tests", [])
        for test in mock_tests:
            if test["test_id"] == test_id:
                # Get questions for this test
                questions = []
                session_questions = session.get("questions", [])
                for q_id in test["questions"]:
                    for question in session_questions:
                        if question["question_id"] == q_id:
                            questions.append(question)
                            break
                
                return {
                    "test": test,
                    "questions": questions
                }
    
    raise HTTPException(status_code=404, detail="Mock test not found")

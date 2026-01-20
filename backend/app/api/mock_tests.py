from fastapi import APIRouter, Depends
from app.api.auth_simple import get_current_user
from app.auth_models_simple import UserResponse

router = APIRouter()

@router.get("/{session_id}")
async def get_mock_tests(
    session_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Mock tests endpoint"""
    return {
        "mock_tests": [
            {
                "test_id": "mock-t1",
                "test_name": "Cardiovascular System Mock Test",
                "questions": ["mock-q1", "mock-q2"],
                "duration_minutes": 30,
                "total_marks": 4,
                "total_questions": 2
            }
        ],
        "total_count": 1
    }

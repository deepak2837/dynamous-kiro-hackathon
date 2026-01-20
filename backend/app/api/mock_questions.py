from fastapi import APIRouter, Depends
from app.api.auth_simple import get_current_user
from app.auth_models_simple import UserResponse

router = APIRouter()

@router.get("/{session_id}")
async def get_mock_questions(
    session_id: str,
    skip: int = 0,
    limit: int = 50,
    current_user: UserResponse = Depends(get_current_user)
):
    """Mock questions endpoint for testing frontend"""
    return {
        "questions": [
            {
                "question_id": "mock-q1",
                "question_text": "What is the primary function of the cardiovascular system?",
                "options": [
                    {"option_id": "a", "text": "Transport oxygen and nutrients", "is_correct": True},
                    {"option_id": "b", "text": "Filter waste products", "is_correct": False},
                    {"option_id": "c", "text": "Produce hormones", "is_correct": False},
                    {"option_id": "d", "text": "Store energy", "is_correct": False}
                ],
                "explanation": "The cardiovascular system's main function is to transport oxygen, nutrients, and waste products throughout the body.",
                "difficulty": "Easy",
                "medical_subject": "Physiology"
            },
            {
                "question_id": "mock-q2", 
                "question_text": "Which valve prevents backflow from the left ventricle to the left atrium?",
                "options": [
                    {"option_id": "a", "text": "Tricuspid valve", "is_correct": False},
                    {"option_id": "b", "text": "Mitral valve", "is_correct": True},
                    {"option_id": "c", "text": "Aortic valve", "is_correct": False},
                    {"option_id": "d", "text": "Pulmonary valve", "is_correct": False}
                ],
                "explanation": "The mitral (bicuspid) valve prevents backflow from the left ventricle to the left atrium.",
                "difficulty": "Medium",
                "medical_subject": "Anatomy"
            }
        ],
        "total_count": 2
    }

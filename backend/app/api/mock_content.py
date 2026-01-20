from fastapi import APIRouter, Depends
from app.api.auth_simple import get_current_user
from app.auth_models_simple import UserResponse

router = APIRouter()

@router.get("/{session_id}")
async def get_mock_content(
    session_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Mock content endpoint for mnemonics, cheat sheets, and notes"""
    return {
        "mnemonics": [
            {
                "mnemonic_id": "mock-m1",
                "topic": "Heart Chambers",
                "mnemonic_text": "Try Pulling My Arm - Tricuspid, Pulmonary, Mitral, Aortic",
                "explanation": "Helps remember the four heart valves in order",
                "key_terms": ["Tricuspid", "Pulmonary", "Mitral", "Aortic"],
                "is_india_specific": False
            }
        ],
        "cheat_sheets": [
            {
                "sheet_id": "mock-cs1",
                "title": "Cardiovascular System Quick Reference",
                "key_points": [
                    "Heart has 4 chambers: 2 atria, 2 ventricles",
                    "Right side pumps deoxygenated blood to lungs",
                    "Left side pumps oxygenated blood to body"
                ],
                "high_yield_facts": [
                    "Normal heart rate: 60-100 bpm",
                    "Cardiac output = Heart rate × Stroke volume"
                ],
                "quick_references": {
                    "Systole": "Contraction phase",
                    "Diastole": "Relaxation phase"
                }
            }
        ],
        "notes": [
            {
                "note_id": "mock-n1",
                "title": "Study Session Summary",
                "content": "Comprehensive notes covering cardiovascular system basics",
                "summary_points": [
                    "Heart anatomy and physiology covered",
                    "Key concepts: cardiac cycle, blood flow"
                ]
            }
        ],
        "total_count": 3
    }

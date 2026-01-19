from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional

from app.services.gemini_service import get_gemini_service

router = APIRouter()

class TestConnectionRequest(BaseModel):
    message: Optional[str] = "Test connection"

class ContentAnalysisRequest(BaseModel):
    content: str
    content_type: str = "text"

class QuestionGenerationRequest(BaseModel):
    content: str
    num_questions: int = 5
    difficulty: str = "mixed"

class MnemonicRequest(BaseModel):
    concept: str
    context: Optional[str] = ""

@router.post("/test-connection")
async def test_gemini_connection(request: TestConnectionRequest):
    """Test Gemini API connection"""
    try:
        gemini = get_gemini_service()
        result = await gemini.test_connection()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Connection test failed: {str(e)}")

@router.post("/analyze-content")
async def analyze_content(request: ContentAnalysisRequest):
    """Analyze content using Gemini AI"""
    try:
        gemini = get_gemini_service()
        result = await gemini.analyze_content(request.content, request.content_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content analysis failed: {str(e)}")

@router.post("/generate-questions")
async def generate_questions(request: QuestionGenerationRequest):
    """Generate MCQs from content"""
    try:
        gemini = get_gemini_service()
        questions = await gemini.generate_questions(
            request.content, 
            request.num_questions, 
            request.difficulty
        )
        return {
            "success": True,
            "questions": questions,
            "total_generated": len(questions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Question generation failed: {str(e)}")

@router.post("/generate-mnemonic")
async def generate_mnemonic(request: MnemonicRequest):
    """Generate mnemonic for a concept"""
    try:
        gemini = get_gemini_service()
        result = await gemini.generate_mnemonics(request.concept, request.context)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mnemonic generation failed: {str(e)}")

@router.post("/create-cheat-sheet")
async def create_cheat_sheet(request: ContentAnalysisRequest):
    """Create a cheat sheet from content"""
    try:
        gemini = get_gemini_service()
        result = await gemini.create_cheat_sheet(request.content, "Medical Topic")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cheat sheet creation failed: {str(e)}")

@router.post("/generate-notes")
async def generate_notes(request: ContentAnalysisRequest):
    """Generate structured notes from content"""
    try:
        gemini = get_gemini_service()
        result = await gemini.generate_notes(request.content, "structured")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Notes generation failed: {str(e)}")

@router.post("/create-mock-test")
async def create_mock_test(request: QuestionGenerationRequest):
    """Create a complete mock test"""
    try:
        gemini = get_gemini_service()
        result = await gemini.create_mock_test(
            request.content, 
            request.num_questions, 
            30  # 30 minutes default
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mock test creation failed: {str(e)}")

@router.get("/health")
async def gemini_health_check():
    """Health check for Gemini service"""
    try:
        gemini = get_gemini_service()
        result = await gemini.test_connection()
        return {
            "service": "Gemini AI",
            "status": "healthy" if result.get("success") else "unhealthy",
            "details": result
        }
    except Exception as e:
        return {
            "service": "Gemini AI",
            "status": "unhealthy",
            "error": str(e)
        }

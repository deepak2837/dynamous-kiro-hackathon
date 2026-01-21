from fastapi import APIRouter
from app.api.v1.endpoints import auth, gemini, sessions, questions, mock_tests, mnemonics, cheat_sheets, notes, text_input

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(gemini.router, prefix="/gemini", tags=["ai-services"])
# Note: upload routes are handled by upload_basic in main.py
api_router.include_router(text_input.router, prefix="/text-input", tags=["text-input"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(questions.router, prefix="/questions", tags=["questions"])
api_router.include_router(mock_tests.router, prefix="/mock-tests", tags=["mock-tests"])
api_router.include_router(mnemonics.router, prefix="/mnemonics", tags=["mnemonics"])
api_router.include_router(cheat_sheets.router, prefix="/cheat-sheets", tags=["cheat-sheets"])
api_router.include_router(notes.router, prefix="/notes", tags=["notes"])


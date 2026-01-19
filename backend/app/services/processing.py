import asyncio
import uuid
import logging
from typing import List
from datetime import datetime

from app.models import ProcessingMode, SessionStatus, Question, MockTest, Mnemonic, CheatSheet, Note, DifficultyLevel
from app.database import get_database
from app.services.ai_service import AIService
from app.services.file_processor import FileProcessor

logger = logging.getLogger(__name__)

class ProcessingService:
    def __init__(self):
        self.ai_service = AIService()
        self.file_processor = FileProcessor()
    
    async def start_processing(self, session_id: str, files: List[str], mode: ProcessingMode, user_id: str):
        """Start async processing of uploaded files"""
        try:
            # Update session status to processing
            db = get_database()
            await db.study_sessions.update_one(
                {"session_id": session_id},
                {"$set": {"status": SessionStatus.PROCESSING}}
            )
            
            # Process files and extract text
            extracted_text = await self._extract_text_from_files(files, mode)
            
            if not extracted_text.strip():
                raise Exception("No text could be extracted from the uploaded files")
            
            # Generate all content types
            await self._generate_questions(session_id, user_id, extracted_text)
            await self._generate_mock_tests(session_id, user_id)
            await self._generate_mnemonics(session_id, user_id, extracted_text)
            await self._generate_cheat_sheets(session_id, user_id, extracted_text)
            await self._generate_notes(session_id, user_id, extracted_text)
            
            # Update session status to completed
            await db.study_sessions.update_one(
                {"session_id": session_id},
                {
                    "$set": {
                        "status": SessionStatus.COMPLETED,
                        "completed_at": datetime.utcnow()
                    }
                }
            )
            
            logger.info(f"Processing completed for session {session_id}")
            
        except Exception as e:
            logger.error(f"Processing failed for session {session_id}: {str(e)}")
            
            # Update session status to failed
            db = get_database()
            await db.study_sessions.update_one(
                {"session_id": session_id},
                {
                    "$set": {
                        "status": SessionStatus.FAILED,
                        "error_message": str(e)
                    }
                }
            )
    
    async def _extract_text_from_files(self, files: List[str], mode: ProcessingMode) -> str:
        """Extract text from uploaded files based on processing mode"""
        all_text = []
        
        for file_path in files:
            try:
                if mode == ProcessingMode.DEFAULT:
                    text = await self.file_processor.extract_text_default(file_path)
                elif mode == ProcessingMode.OCR:
                    text = await self.file_processor.extract_text_ocr(file_path)
                else:  # AI_BASED
                    text = await self.file_processor.extract_text_ai(file_path)
                
                if text:
                    all_text.append(text)
                    
            except Exception as e:
                logger.warning(f"Failed to process file {file_path}: {str(e)}")
                continue
        
        return "\n\n".join(all_text)
    
    async def _generate_questions(self, session_id: str, user_id: str, text: str):
        """Generate questions from extracted text"""
        try:
            questions_data = await self.ai_service.generate_questions(text)
            db = get_database()
            
            for q_data in questions_data:
                question = Question(
                    question_id=str(uuid.uuid4()),
                    session_id=session_id,
                    user_id=user_id,
                    question_text=q_data["question"],
                    options=q_data["options"],
                    correct_answer=q_data["correct_answer"],
                    explanation=q_data["explanation"],
                    difficulty=DifficultyLevel(q_data["difficulty"]),
                    topic=q_data.get("topic")
                )
                
                await db.questions.insert_one(question.dict())
            
            logger.info(f"Generated {len(questions_data)} questions for session {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to generate questions for session {session_id}: {str(e)}")
    
    async def _generate_mock_tests(self, session_id: str, user_id: str):
        """Generate mock tests from existing questions"""
        try:
            db = get_database()
            
            # Get all questions for this session
            questions = await db.questions.find({"session_id": session_id}).to_list(length=None)
            
            if len(questions) < 5:
                logger.warning(f"Not enough questions to create mock test for session {session_id}")
                return
            
            # Create mock tests with different difficulty levels
            test_configs = [
                {"name": "Quick Practice Test", "count": min(10, len(questions)), "duration": 15},
                {"name": "Comprehensive Mock Test", "count": min(25, len(questions)), "duration": 45},
                {"name": "Master Challenge Test", "count": min(50, len(questions)), "duration": 90}
            ]
            
            for config in test_configs:
                if len(questions) >= config["count"]:
                    selected_questions = questions[:config["count"]]
                    
                    mock_test = MockTest(
                        test_id=str(uuid.uuid4()),
                        session_id=session_id,
                        user_id=user_id,
                        test_name=config["name"],
                        questions=[q["question_id"] for q in selected_questions],
                        duration_minutes=config["duration"],
                        total_questions=len(selected_questions)
                    )
                    
                    await db.mock_tests.insert_one(mock_test.dict())
            
            logger.info(f"Generated mock tests for session {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to generate mock tests for session {session_id}: {str(e)}")
    
    async def _generate_mnemonics(self, session_id: str, user_id: str, text: str):
        """Generate mnemonics from extracted text"""
        try:
            mnemonics_data = await self.ai_service.generate_mnemonics(text)
            db = get_database()
            
            for m_data in mnemonics_data:
                mnemonic = Mnemonic(
                    mnemonic_id=str(uuid.uuid4()),
                    session_id=session_id,
                    user_id=user_id,
                    topic=m_data["topic"],
                    mnemonic_text=m_data["mnemonic"],
                    explanation=m_data["explanation"],
                    key_terms=m_data.get("key_terms", [])
                )
                
                await db.mnemonics.insert_one(mnemonic.dict())
            
            logger.info(f"Generated {len(mnemonics_data)} mnemonics for session {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to generate mnemonics for session {session_id}: {str(e)}")
    
    async def _generate_cheat_sheets(self, session_id: str, user_id: str, text: str):
        """Generate cheat sheets from extracted text"""
        try:
            sheets_data = await self.ai_service.generate_cheat_sheets(text)
            db = get_database()
            
            for s_data in sheets_data:
                cheat_sheet = CheatSheet(
                    sheet_id=str(uuid.uuid4()),
                    session_id=session_id,
                    user_id=user_id,
                    title=s_data["title"],
                    key_points=s_data["key_points"],
                    high_yield_facts=s_data["high_yield_facts"],
                    quick_references=s_data.get("quick_references", {})
                )
                
                await db.cheat_sheets.insert_one(cheat_sheet.dict())
            
            logger.info(f"Generated {len(sheets_data)} cheat sheets for session {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to generate cheat sheets for session {session_id}: {str(e)}")
    
    async def _generate_notes(self, session_id: str, user_id: str, text: str):
        """Generate compiled notes from extracted text"""
        try:
            notes_data = await self.ai_service.generate_notes(text)
            db = get_database()
            
            # Get related questions and mnemonics
            questions = await db.questions.find({"session_id": session_id}).to_list(length=None)
            mnemonics = await db.mnemonics.find({"session_id": session_id}).to_list(length=None)
            
            for n_data in notes_data:
                note = Note(
                    note_id=str(uuid.uuid4()),
                    session_id=session_id,
                    user_id=user_id,
                    title=n_data["title"],
                    content=n_data["content"],
                    important_questions=[q["question_id"] for q in questions[:5]],  # Top 5 questions
                    summary_points=n_data["summary_points"],
                    related_mnemonics=[m["mnemonic_id"] for m in mnemonics[:3]]  # Top 3 mnemonics
                )
                
                await db.notes.insert_one(note.dict())
            
            logger.info(f"Generated {len(notes_data)} notes for session {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to generate notes for session {session_id}: {str(e)}")

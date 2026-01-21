"""
File Upload Processing Service - Separate from topic processing
Handles AI_ONLY mode for uploaded files (like text-input but for files)
"""
import asyncio
import uuid
import logging
import os
from typing import List, Dict, Any
from datetime import datetime

from app.models import ProcessingStep, Question, MockTest, Mnemonic, CheatSheet, Note, DifficultyLevel
from app.database import get_database
from app.services.file_upload_ai_service import FileUploadAIService
from app.services.file_processor import FileProcessor
from app.services.mock_test_generator import MockTestGenerator
from app.services.s3_service import s3_service
from app.services.progress_tracker import ProgressTracker
from app.utils.error_handler import ErrorHandler

logger = logging.getLogger(__name__)

class FileUploadProcessingService:
    """Processing service specifically for uploaded files (AI_ONLY mode)"""
    
    def __init__(self):
        self.ai_service = FileUploadAIService()
        self.file_processor = FileProcessor()
        self.mock_test_generator = MockTestGenerator()
    
    async def process_uploaded_files(self, session_id: str, user_id: str):
        """Process uploaded files exactly like topic feature - direct AI generation of all 5 outputs"""
        try:
            logger.info(f"🚀 STARTING FILE UPLOAD AI PROCESSING (LIKE TOPIC FEATURE)")
            logger.info(f"📋 Session ID: {session_id}")
            logger.info(f"👤 User ID: {user_id}")
            
            # Initialize progress tracking
            await ProgressTracker.update_progress(
                session_id, 
                ProcessingStep.AI_PROCESSING, 
                0, 
                "Extracting content from uploaded files..."
            )
            
            # Get session data
            db = get_database()
            session_data = await db.study_sessions.find_one({"session_id": session_id})
            if not session_data:
                raise Exception("Session not found")
            
            session_name = session_data.get("session_name", "Study Session")
            files = session_data.get("files", [])  # Use 'files' field from StudySession model
            s3_keys = session_data.get("s3_keys", [])
            
            logger.info(f"📁 FILES TO PROCESS: {len(files)} files")
            for i, file_path in enumerate(files):
                logger.info(f"   File {i+1}: {file_path}")
            
            # Extract text from all uploaded files
            await ProgressTracker.update_progress(
                session_id, 
                ProcessingStep.AI_PROCESSING, 
                10, 
                "Reading content from your files..."
            )
            
            all_text_content = []
            file_names = []
            
            logger.info(f"🔍 STARTING TEXT EXTRACTION FROM {len(files)} FILES")
            
            for i, file_path in enumerate(files):
                try:
                    logger.info(f"📄 PROCESSING FILE {i+1}/{len(files)}: {file_path}")
                    
                    # Get S3 key if available
                    s3_key = s3_keys[i] if i < len(s3_keys) else None
                    
                    # Download from S3 if needed
                    if s3_key and s3_service.is_s3_enabled():
                        temp_filename = os.path.basename(file_path)
                        temp_path = os.path.join("/tmp", f"processing_{temp_filename}")
                        logger.info(f"⬇️ Downloading from S3 to: {temp_path}")
                        local_file_path = await s3_service.download_file_for_processing(s3_key, temp_path)
                    else:
                        local_file_path = file_path
                    
                    # Extract text directly using AI mode
                    logger.info(f"🔍 EXTRACTING TEXT FROM: {os.path.basename(local_file_path)}")
                    text_content = await self.file_processor.extract_text_ai(local_file_path)
                    
                    if text_content:
                        logger.info(f"✅ EXTRACTED {len(text_content)} CHARACTERS FROM: {os.path.basename(local_file_path)}")
                        logger.info(f"📝 CONTENT PREVIEW (first 200 chars): {text_content[:200]}...")
                        all_text_content.append(text_content)
                        file_names.append(os.path.basename(local_file_path))
                    else:
                        logger.warning(f"⚠️ NO TEXT EXTRACTED FROM: {os.path.basename(local_file_path)}")
                    
                    # Clean up temp file
                    if s3_key and s3_service.is_s3_enabled() and os.path.exists(local_file_path):
                        os.remove(local_file_path)
                        
                except Exception as e:
                    logger.error(f"❌ FAILED TO EXTRACT TEXT FROM FILE {file_path}: {str(e)}")
                    continue
            
            if not all_text_content:
                logger.error(f"❌ NO TEXT CONTENT EXTRACTED FROM ANY FILES")
                raise Exception("No text content could be extracted from uploaded files")
            
            # Combine all text content
            combined_content = "\n\n".join(all_text_content)
            logger.info(f"📊 COMBINED CONTENT STATS:")
            logger.info(f"   - Files processed: {len(file_names)}")
            logger.info(f"   - Total characters: {len(combined_content)}")
            logger.info(f"   - File names: {file_names}")
            
            # Generate all content using AI (exactly like topic feature)
            await ProgressTracker.update_progress(
                session_id, 
                ProcessingStep.AI_PROCESSING, 
                20, 
                "Generating comprehensive study materials from your files..."
            )
            
            logger.info(f"🤖 CALLING FILE UPLOAD AI SERVICE TO GENERATE ALL CONTENT")
            content = await self.ai_service.generate_content_from_uploaded_files(combined_content, file_names)
            logger.info(f"📥 AI SERVICE RESPONSE: {list(content.keys())}")
            
            # Store questions (same as topic feature)
            await ProgressTracker.update_progress(
                session_id, 
                ProcessingStep.GENERATING_QUESTIONS, 
                35, 
                "Processing and storing questions..."
            )
            
            questions_data = content.get("questions", [])
            logger.info(f"💾 STORING {len(questions_data)} QUESTIONS")
            stored_questions = []
            for q_data in questions_data:
                question = Question(
                    question_id=str(uuid.uuid4()),
                    session_id=session_id,
                    user_id=user_id,
                    question_text=q_data.get("question", ""),
                    options=q_data.get("options", []),
                    correct_answer=q_data.get("correct_answer", 0),
                    explanation=q_data.get("explanation", ""),
                    difficulty=DifficultyLevel(q_data.get("difficulty", "medium")),
                    topic=f"From {file_names[0]}" if file_names else "Uploaded Files"
                )
                await db.questions.insert_one(question.dict())
                stored_questions.append(question)
            
            logger.info(f"✅ STORED {len(stored_questions)} QUESTIONS FROM FILES")
            
            # Create mock test from questions (same as topic feature)
            await ProgressTracker.update_progress(
                session_id, 
                ProcessingStep.GENERATING_MOCK_TESTS, 
                55, 
                "Creating mock test from generated questions..."
            )
            
            if len(stored_questions) >= 5:
                mock_test = await self.mock_test_generator.create_mock_test_from_questions(
                    session_id, user_id, stored_questions, session_name
                )
                if mock_test:
                    await db.mock_tests.insert_one(mock_test.dict())
                    logger.info(f"✅ CREATED MOCK TEST WITH {mock_test.total_questions} QUESTIONS")
            
            # Store mnemonics (same as topic feature)
            await ProgressTracker.update_progress(
                session_id, 
                ProcessingStep.GENERATING_MNEMONICS, 
                70, 
                "Processing and storing mnemonics..."
            )
            
            mnemonics_data = content.get("mnemonics", [])
            logger.info(f"💾 STORING {len(mnemonics_data)} MNEMONICS")
            for m_data in mnemonics_data:
                mnemonic = Mnemonic(
                    mnemonic_id=str(uuid.uuid4()),
                    session_id=session_id,
                    user_id=user_id,
                    topic=m_data.get("topic", "From Files"),
                    mnemonic_text=m_data.get("mnemonic", ""),
                    explanation=m_data.get("explanation", ""),
                    key_terms=m_data.get("key_terms", [])
                )
                await db.mnemonics.insert_one(mnemonic.dict())
            
            logger.info(f"✅ STORED {len(mnemonics_data)} MNEMONICS FROM FILES")
            
            # Store cheat sheet (same as topic feature)
            await ProgressTracker.update_progress(
                session_id, 
                ProcessingStep.GENERATING_CHEAT_SHEETS, 
                85, 
                "Processing and storing cheat sheet..."
            )
            
            cheat_sheet_data = content.get("cheat_sheet", {})
            if cheat_sheet_data:
                cheat_sheet = CheatSheet(
                    sheet_id=str(uuid.uuid4()),
                    session_id=session_id,
                    user_id=user_id,
                    title=cheat_sheet_data.get("title", f"Cheat Sheet: {session_name}"),
                    key_points=cheat_sheet_data.get("key_points", []),
                    high_yield_facts=cheat_sheet_data.get("high_yield_facts", []),
                    quick_references=cheat_sheet_data.get("quick_references", {})
                )
                await db.cheat_sheets.insert_one(cheat_sheet.dict())
                logger.info(f"✅ STORED CHEAT SHEET FROM FILES")
            
            # Store notes (same as topic feature)
            await ProgressTracker.update_progress(
                session_id, 
                ProcessingStep.GENERATING_NOTES, 
                95, 
                "Compiling notes..."
            )
            
            notes_data = content.get("notes", {})
            note = Note(
                note_id=str(uuid.uuid4()),
                session_id=session_id,
                user_id=user_id,
                title=notes_data.get("title", f"Study Notes: {session_name}"),
                content=notes_data.get("content", f"Comprehensive notes from uploaded files"),
                important_questions=[q.question_id for q in stored_questions[:5]],
                summary_points=notes_data.get("summary_points", []),
                related_mnemonics=[]
            )
            await db.notes.insert_one(note.dict())
            logger.info(f"✅ STORED NOTES FROM FILES")
            
            # Mark as completed (same as topic feature)
            await ProgressTracker.update_progress(
                session_id, 
                ProcessingStep.COMPLETED, 
                100, 
                "All study materials ready!"
            )
            
            logger.info(f"🎉 FILE UPLOAD AI PROCESSING COMPLETED FOR SESSION {session_id}")
            logger.info(f"📊 FINAL SUMMARY:")
            logger.info(f"   - Questions: {len(stored_questions)}")
            logger.info(f"   - Mock Tests: 1")
            logger.info(f"   - Mnemonics: {len(mnemonics_data)}")
            logger.info(f"   - Cheat Sheets: 1")
            logger.info(f"   - Notes: 1")
            
        except Exception as e:
            logger.error(f"❌ FILE UPLOAD AI PROCESSING FAILED FOR SESSION {session_id}: {str(e)}")
            
            error_info = await ErrorHandler.handle_processing_error(
                e, 
                {"session_id": session_id, "step": "file_upload_ai_processing"}
            )
            
            await ProgressTracker.update_progress(
                session_id, 
                ProcessingStep.FAILED, 
                0, 
                error_info["user_message"]
            )

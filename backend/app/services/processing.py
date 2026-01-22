import asyncio
import uuid
import logging
import os
from typing import List, Dict, Any
from datetime import datetime

from app.models import ProcessingMode, SessionStatus, Question, MockTest, Mnemonic, CheatSheet, Note, DifficultyLevel, ProcessingStep, DocumentType
from app.database import get_database
from motor.motor_asyncio import AsyncIOMotorClient
from app.services.ai_service import AIService
from app.services.file_processor import FileProcessor
from app.services.content_aggregator import ContentAggregator
from app.services.mock_test_generator import MockTestGenerator
from app.services.s3_service import s3_service
from app.services.progress_tracker import ProgressTracker
from app.utils.error_handler import ErrorHandler, RecoveryAction
from app.logging_config import logger

class ProcessingService:
    def __init__(self):
        self.ai_service = AIService()
        self.file_processor = FileProcessor()
        self.content_aggregator = ContentAggregator()
        self.mock_test_generator = MockTestGenerator()
    
    async def start_processing(self, session_id: str, files: List[str], mode: ProcessingMode, user_id: str):
        """Start processing files by sending actual file content to AI model"""
        logger.info(f"🚀 Starting processing for session {session_id} with {len(files)} files")
        try:
            # Send file directly to AI model with prompts
            await self._process_file_content_with_prompts(session_id, files[0], user_id)
            logger.info(f"✅ Processing completed for session {session_id}")
            
        except Exception as e:
            logger.error(f"❌ Processing failed for session {session_id}: {str(e)}")
            # Update session status to failed
            db = get_database()
            await db.study_sessions.update_one(
                {"session_id": session_id},
                {"$set": {"status": "failed", "error_message": str(e)}}
            )
    
    async def _read_file_content(self, file_path: str) -> str:
        """Read content from uploaded file"""
        try:
            # For PDF files, extract text (simple approach)
            if file_path.lower().endswith('.pdf'):
                # For now, return placeholder - in real implementation would extract PDF text
                return f"Medical study content from PDF file: {os.path.basename(file_path)}"
            else:
                # For other files, read as text
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return f"Medical content from file: {os.path.basename(file_path)}"
    
    async def _process_file_content_with_prompts(self, session_id: str, file_path: str, user_id: str):
        """Process file by sending it directly to AI model with prompts.
        
        This method uploads the file directly to Gemini API and uses specialized
        prompts for generating questions, mnemonics, cheat sheets, and notes.
        All content is generated based on the actual file content.
        """
        try:
            import os
            
            # Load prompts from files
            prompts_dir = os.path.join(os.path.dirname(__file__), "prompts")
            
            # Read prompts
            with open(os.path.join(prompts_dir, "file_upload_question_generation.txt"), 'r') as f:
                question_prompt = f.read()
            with open(os.path.join(prompts_dir, "file_upload_content_analysis.txt"), 'r') as f:
                content_prompt = f.read()
            with open(os.path.join(prompts_dir, "file_upload_mnemonic_generation.txt"), 'r') as f:
                mnemonic_prompt = f.read()
            
            db = get_database()
            
            # Update progress: Starting file analysis
            await ProgressTracker.update_progress(
                session_id, 
                ProcessingStep.AI_PROCESSING, 
                10, 
                "Analyzing uploaded file with AI..."
            )
            
            logger.info(f"📄 Processing file: {file_path}")
            
            # Generate questions by sending file to AI
            await ProgressTracker.update_progress(
                session_id, 
                ProcessingStep.GENERATING_QUESTIONS, 
                20, 
                "Generating questions from file content..."
            )
            
            questions_response = await self.ai_service.analyze_file_with_prompt(
                file_path, 
                f"{question_prompt}\n\nAnalyze the uploaded file and generate questions based on its content."
            )
            questions_data = self.ai_service.extract_json_from_response(questions_response)
            if isinstance(questions_data, dict):
                questions_data = questions_data.get("questions", [])
            questions_data = questions_data or []
            
            logger.info(f"📝 Generated {len(questions_data)} questions")
            
            # Save questions and track for mock test
            stored_questions = []
            for q_data in questions_data:
                question = {
                    "question_id": str(uuid.uuid4()),
                    "session_id": session_id,
                    "user_id": user_id,
                    "question_text": q_data.get("question", ""),
                    "options": q_data.get("options", []),
                    "correct_answer": q_data.get("correct_answer", 0),
                    "explanation": q_data.get("explanation", ""),
                    "difficulty": q_data.get("difficulty", "medium"),
                    "topic": q_data.get("topic", "File Upload Content")
                }
                await db.questions.insert_one(question)
                stored_questions.append(question)
            
            # Generate mock test from questions
            await ProgressTracker.update_progress(
                session_id, 
                ProcessingStep.GENERATING_MOCK_TESTS, 
                40, 
                "Creating mock test from generated questions..."
            )
            
            if len(stored_questions) >= 5:
                session_data = await db.study_sessions.find_one({"session_id": session_id})
                session_name = session_data.get("session_name", "Study Session") if session_data else "Study Session"
                
                total_questions = len(stored_questions)
                duration = max(15, min(90, int(total_questions * 1.5)))
                
                mock_test = {
                    "test_id": str(uuid.uuid4()),
                    "session_id": session_id,
                    "user_id": user_id,
                    "test_name": f"Mock Test - {session_name}",
                    "questions": [q["question_id"] for q in stored_questions],
                    "duration_minutes": duration,
                    "total_questions": total_questions
                }
                await db.mock_tests.insert_one(mock_test)
                logger.info(f"📋 Created mock test with {total_questions} questions")
            
            # Generate mnemonics by sending file to AI
            await ProgressTracker.update_progress(
                session_id, 
                ProcessingStep.GENERATING_MNEMONICS, 
                55, 
                "Creating mnemonics from file content..."
            )
            
            mnemonics_response = await self.ai_service.analyze_file_with_prompt(
                file_path, 
                f"{mnemonic_prompt}\n\nAnalyze the uploaded file and create mnemonics based on its content."
            )
            mnemonics_data = self.ai_service.extract_json_from_response(mnemonics_response)
            if isinstance(mnemonics_data, dict):
                mnemonics_data = mnemonics_data.get("mnemonics", [])
            mnemonics_data = mnemonics_data or []
            
            logger.info(f"🧠 Generated {len(mnemonics_data)} mnemonics")
            
            # Save mnemonics
            for m_data in mnemonics_data:
                mnemonic = {
                    "mnemonic_id": str(uuid.uuid4()),
                    "session_id": session_id,
                    "user_id": user_id,
                    "topic": m_data.get("topic", "File Content"),
                    "mnemonic_text": m_data.get("mnemonic", ""),
                    "explanation": m_data.get("explanation", ""),
                    "key_terms": m_data.get("key_terms", [])
                }
                await db.mnemonics.insert_one(mnemonic)
            
            # Generate cheat sheet and notes by sending file to AI
            await ProgressTracker.update_progress(
                session_id, 
                ProcessingStep.GENERATING_CHEAT_SHEETS, 
                70, 
                "Creating cheat sheet and notes from file content..."
            )
            
            content_response = await self.ai_service.analyze_file_with_prompt(
                file_path, 
                f"{content_prompt}\n\nAnalyze the uploaded file and create cheat sheet and notes based on its content."
            )
            content_data = self.ai_service.extract_json_from_response(content_response) or {}
            
            # Save cheat sheet
            cheat_sheet_data = content_data.get("cheat_sheet", content_data)
            if cheat_sheet_data and (cheat_sheet_data.get("title") or cheat_sheet_data.get("key_points")):
                cheat_sheet = {
                    "sheet_id": str(uuid.uuid4()),
                    "session_id": session_id,
                    "user_id": user_id,
                    "title": cheat_sheet_data.get("title", "File Content Cheat Sheet"),
                    "key_points": cheat_sheet_data.get("key_points", []),
                    "high_yield_facts": cheat_sheet_data.get("high_yield_facts", []),
                    "quick_references": cheat_sheet_data.get("quick_references", {})
                }
                await db.cheat_sheets.insert_one(cheat_sheet)
                logger.info(f"📑 Created cheat sheet")
            
            # Save notes
            await ProgressTracker.update_progress(
                session_id, 
                ProcessingStep.GENERATING_NOTES, 
                85, 
                "Compiling study notes..."
            )
            
            notes_data = content_data.get("notes", {})
            note = {
                "note_id": str(uuid.uuid4()),
                "session_id": session_id,
                "user_id": user_id,
                "title": notes_data.get("title", "Study Notes from File"),
                "content": notes_data.get("content", "Study notes compiled from uploaded file content."),
                "important_questions": [q["question_id"] for q in stored_questions[:5]],
                "summary_points": notes_data.get("summary_points", []),
                "related_mnemonics": []
            }
            await db.notes.insert_one(note)
            logger.info(f"📝 Created study notes")
            
            # Mark as completed
            await ProgressTracker.update_progress(
                session_id, 
                ProcessingStep.COMPLETED, 
                100, 
                "All study materials ready!"
            )
            
            # Update session status to completed
            await db.study_sessions.update_one(
                {"session_id": session_id},
                {"$set": {"status": "completed", "overall_progress": 100}}
            )
            
            logger.info(f"✅ File processing completed for session {session_id}")
            
        except Exception as e:
            logger.error(f"❌ File processing failed for session {session_id}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
            # Update session status to failed
            db = get_database()
            await db.study_sessions.update_one(
                {"session_id": session_id},
                {"$set": {"status": "failed", "error_message": str(e)}}
            )
            
            await ProgressTracker.update_progress(
                session_id, 
                ProcessingStep.FAILED, 
                0, 
                f"Processing failed: {str(e)[:100]}"
            )

    
    async def _extract_text_from_files(self, files: List[str]) -> str:
        """Extract text from files - simplified version"""
        try:
            # For now, just return placeholder text
            # The AI will generate content based on the topic
            return "Medical study content from uploaded files"
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            return "Medical content from uploaded files"
            
            # Process files with batching
            await ProgressTracker.update_progress(
                session_id, 
                ProcessingStep.AI_PROCESSING, 
                0, 
                "Extracting text from files..."
            )
            
            # Extract text with batching
            all_batches = []
            doc_type = DocumentType.STUDY_NOTES  # Default
            
            for i, file_path in enumerate(files):
                try:
                    # Get S3 key if available
                    s3_key = s3_keys[i] if i < len(s3_keys) else None
                    
                    # Download from S3 if needed
                    if s3_key and s3_service.is_s3_enabled():
                        temp_filename = os.path.basename(file_path)
                        temp_path = os.path.join("/tmp", f"processing_{temp_filename}")
                        local_file_path = await s3_service.download_file_for_processing(s3_key, temp_path)
                    else:
                        local_file_path = file_path
                    
                    # Extract text with batching
                    logger.info(f"🔍 Extracting text from file {i+1}/{len(files)}: {os.path.basename(local_file_path)}")
                    
                    # AI_ONLY mode
                    logger.info(f"🔍 Using AI-only mode for text extraction")
                    batches = await self.file_processor.extract_text_ai_batched(local_file_path, session_id)
                    
                    logger.info(f"📊 Extracted {len(batches)} batches from {os.path.basename(local_file_path)}")
                    for j, batch in enumerate(batches):
                        logger.info(f"   Batch {j+1}: {len(batch.text_content)} characters")
                    
                    all_batches.extend(batches)
                    
                    # Detect document type from first batch
                    if i == 0 and batches and batches[0].text_content:
                        doc_type = await self.ai_service.detect_document_type(batches[0].text_content)
                        logger.info(f"Detected document type: {doc_type}")
                    
                    # Clean up temp file
                    if s3_key and s3_service.is_s3_enabled() and os.path.exists(local_file_path):
                        os.remove(local_file_path)
                        
                except Exception as e:
                    logger.error(f"Failed to process file {file_path}: {str(e)}")
                    # Try OCR fallback if AI failed
                    if mode == ProcessingMode.AI_ONLY:
                        error_info = await ErrorHandler.handle_ocr_error(e, {"file": file_path})
                        if error_info["recovery_action"] == RecoveryAction.FALLBACK_AI:
                            logger.info("Attempting OCR fallback...")
                            try:
                                batches = await self.file_processor.extract_text_ocr_batched(local_file_path, session_id)
                                all_batches.extend(batches)
                            except Exception as fallback_error:
                                logger.error(f"Fallback also failed: {fallback_error}")
                    continue
            
            if not all_batches:
                raise Exception("No text could be extracted from the uploaded files")
            
            logger.info(f"📊 TEXT EXTRACTION COMPLETE - Created {len(all_batches)} batches for processing")
            total_chars = sum(len(batch.text_content) for batch in all_batches)
            logger.info(f"📝 Total text extracted: {total_chars} characters")
            
            # Now start AI processing AFTER text extraction is complete
            logger.info(f"🤖 STARTING AI PROCESSING - Processing {len(all_batches)} batches with AI")
            
            # Process each batch and generate content
            await ProgressTracker.update_progress(
                session_id, 
                ProcessingStep.GENERATING_QUESTIONS, 
                0, 
                f"Processing batch 1 of {len(all_batches)}..."
            )
            
            batch_contents = []
            for i, batch in enumerate(all_batches, 1):
                try:
                    # Generate content from batch
                    batch_content = await self.ai_service.generate_content_from_batch(
                        batch.text_content, 
                        doc_type
                    )
                    batch_contents.append(batch_content)
                    
                    # Update progress
                    progress = int((i / len(all_batches)) * 100)
                    await ProgressTracker.update_progress(
                        session_id,
                        ProcessingStep.GENERATING_QUESTIONS,
                        progress,
                        f"Processing batch {i} of {len(all_batches)}...",
                        pages_processed=i * 3  # Approximate pages
                    )
                    
                except Exception as e:
                    logger.error(f"Failed to process batch {i}: {str(e)}")
                    error_info = await ErrorHandler.handle_ai_error(e, {"batch": i})
                    logger.warning(f"Batch {i} error: {error_info['user_message']}")
                    continue
            
            if not batch_contents:
                raise Exception("Failed to generate content from any batch")
            
            # Aggregate results
            await ProgressTracker.update_progress(
                session_id, 
                ProcessingStep.GENERATING_QUESTIONS, 
                100, 
                "Aggregating questions..."
            )
            
            all_questions = await self.content_aggregator.aggregate_questions(
                batch_contents, session_id, user_id
            )
            
            # Store questions
            for question in all_questions:
                await db.questions.insert_one(question.dict())
            
            logger.info(f"Stored {len(all_questions)} questions")
            
            # Create mock test from questions (NO AI CALL)
            await ProgressTracker.update_progress(
                session_id, 
                ProcessingStep.GENERATING_MOCK_TESTS, 
                0, 
                "Creating mock test..."
            )
            
            mock_test = await self.mock_test_generator.create_mock_test_from_questions(
                session_id, user_id, all_questions, session_name
            )
            
            if mock_test:
                await db.mock_tests.insert_one(mock_test.dict())
                logger.info(f"Created mock test with {mock_test.total_questions} questions")
            
            # Aggregate mnemonics
            await ProgressTracker.update_progress(
                session_id, 
                ProcessingStep.GENERATING_MNEMONICS, 
                0, 
                "Aggregating mnemonics..."
            )
            
            all_mnemonics = await self.content_aggregator.aggregate_mnemonics(
                batch_contents, session_id, user_id
            )
            
            for mnemonic in all_mnemonics:
                await db.mnemonics.insert_one(mnemonic.dict())
            
            logger.info(f"Stored {len(all_mnemonics)} mnemonics")
            
            # Aggregate cheat sheets
            await ProgressTracker.update_progress(
                session_id, 
                ProcessingStep.GENERATING_CHEAT_SHEETS, 
                0, 
                "Creating cheat sheets..."
            )
            
            all_cheat_sheets = await self.content_aggregator.aggregate_cheat_sheets(
                batch_contents, session_id, user_id
            )
            
            for sheet in all_cheat_sheets:
                await db.cheat_sheets.insert_one(sheet.dict())
            
            logger.info(f"Stored {len(all_cheat_sheets)} cheat sheets")
            
            # Compile notes
            await ProgressTracker.update_progress(
                session_id, 
                ProcessingStep.GENERATING_NOTES, 
                0, 
                "Compiling study notes..."
            )
            
            note = await self.content_aggregator.compile_notes(
                all_questions, all_mnemonics, all_cheat_sheets,
                session_id, user_id
            )
            
            await db.notes.insert_one(note.dict())
            logger.info("Compiled and stored notes")
            
            # Finalize processing
            await ProgressTracker.update_progress(
                session_id, 
                ProcessingStep.FINALIZING, 
                50, 
                "Finalizing study materials..."
            )
            
            # Mark as completed
            await ProgressTracker.update_progress(
                session_id, 
                ProcessingStep.COMPLETED, 
                100, 
                "All study materials ready!"
            )
            
            logger.info(f"Processing completed for session {session_id}")
            
        except Exception as e:
            logger.error(f"Processing failed for session {session_id}: {str(e)}")
            
            # Handle error and update progress
            error_info = await ErrorHandler.handle_processing_error(
                e, 
                {"session_id": session_id, "step": "processing"}
            )
            
            await ProgressTracker.update_progress(
                session_id, 
                ProcessingStep.FAILED, 
                0, 
                error_info["user_message"]
            )
    
    async def process_text_input(self, session_id: str, topic: str, user_id: str):
        """Process text-only topic input to generate study materials without files"""
        try:
            logger.info(f"Starting text-input processing for topic: {topic}")
            
            # Initialize progress tracking
            await ProgressTracker.update_progress(
                session_id, 
                ProcessingStep.AI_PROCESSING, 
                0, 
                f"Generating content for topic: {topic[:50]}..."
            )
            
            # Get session data
            db = get_database()
            session_data = await db.study_sessions.find_one({"session_id": session_id})
            if not session_data:
                raise Exception("Session not found")
            
            session_name = session_data.get("session_name", f"Topic: {topic}")
            
            # Generate content about the topic using AI
            await ProgressTracker.update_progress(
                session_id, 
                ProcessingStep.AI_PROCESSING, 
                10, 
                "Analyzing topic and preparing content generation..."
            )
            
            # Generate all content from topic
            logger.info(f"Calling AI service to generate content for topic: {topic}")
            content = await self.ai_service.generate_content_from_topic(topic)
            logger.info(f"AI service returned content with keys: {list(content.keys())}")
            
            # Store questions
            await ProgressTracker.update_progress(
                session_id, 
                ProcessingStep.GENERATING_QUESTIONS, 
                25, 
                "Processing and storing questions..."
            )
            
            # Store questions
            questions_data = content.get("questions", [])
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
                    topic=topic
                )
                await db.questions.insert_one(question.dict())
                stored_questions.append(question)
            
            logger.info(f"Stored {len(stored_questions)} questions for topic: {topic}")
            
            # Create mock test from questions (NO AI CALL)
            await ProgressTracker.update_progress(
                session_id, 
                ProcessingStep.GENERATING_MOCK_TESTS, 
                45, 
                "Creating mock test from generated questions..."
            )
            
            if len(stored_questions) >= 5:
                mock_test = await self.mock_test_generator.create_mock_test_from_questions(
                    session_id, user_id, stored_questions, session_name
                )
                if mock_test:
                    await db.mock_tests.insert_one(mock_test.dict())
                    logger.info(f"Created mock test with {mock_test.total_questions} questions")
            
            # Store mnemonics
            await ProgressTracker.update_progress(
                session_id, 
                ProcessingStep.GENERATING_MNEMONICS, 
                65, 
                "Processing and storing mnemonics..."
            )
            
            mnemonics_data = content.get("mnemonics", [])
            for m_data in mnemonics_data:
                mnemonic = Mnemonic(
                    mnemonic_id=str(uuid.uuid4()),
                    session_id=session_id,
                    user_id=user_id,
                    topic=m_data.get("topic", topic),
                    mnemonic_text=m_data.get("mnemonic", ""),
                    explanation=m_data.get("explanation", ""),
                    key_terms=m_data.get("key_terms", [])
                )
                await db.mnemonics.insert_one(mnemonic.dict())
            
            logger.info(f"Stored {len(mnemonics_data)} mnemonics for topic: {topic}")
            
            # Store cheat sheet
            await ProgressTracker.update_progress(
                session_id, 
                ProcessingStep.GENERATING_CHEAT_SHEETS, 
                80, 
                "Processing and storing cheat sheet..."
            )
            
            cheat_sheet_data = content.get("cheat_sheet", {})
            if cheat_sheet_data:
                cheat_sheet = CheatSheet(
                    sheet_id=str(uuid.uuid4()),
                    session_id=session_id,
                    user_id=user_id,
                    title=cheat_sheet_data.get("title", f"Cheat Sheet: {topic}"),
                    key_points=cheat_sheet_data.get("key_points", []),
                    high_yield_facts=cheat_sheet_data.get("high_yield_facts", []),
                    quick_references=cheat_sheet_data.get("quick_references", {})
                )
                await db.cheat_sheets.insert_one(cheat_sheet.dict())
                logger.info(f"Stored cheat sheet for topic: {topic}")
            
            # Store notes
            await ProgressTracker.update_progress(
                session_id, 
                ProcessingStep.GENERATING_NOTES, 
                90, 
                "Compiling notes..."
            )
            
            notes_data = content.get("notes", {})
            note = Note(
                note_id=str(uuid.uuid4()),
                session_id=session_id,
                user_id=user_id,
                title=notes_data.get("title", f"Study Notes: {topic}"),
                content=notes_data.get("content", f"Comprehensive notes on {topic}"),
                important_questions=[q.question_id for q in stored_questions[:5]],
                summary_points=notes_data.get("summary_points", []),
                related_mnemonics=[]
            )
            await db.notes.insert_one(note.dict())
            logger.info(f"Stored notes for topic: {topic}")
            
            # Mark as completed
            await ProgressTracker.update_progress(
                session_id, 
                ProcessingStep.COMPLETED, 
                100, 
                "All study materials ready!"
            )
            
            logger.info(f"Text-input processing completed for session {session_id}")
            
        except Exception as e:
            logger.error(f"Text-input processing failed for session {session_id}: {str(e)}")
            
            error_info = await ErrorHandler.handle_processing_error(
                e, 
                {"session_id": session_id, "step": "text_input_processing"}
            )
            
            await ProgressTracker.update_progress(
                session_id, 
                ProcessingStep.FAILED, 
                0, 
                error_info["user_message"]
            )
    
    async def _count_total_pages(self, files: List[str], s3_keys: List[str] = None) -> int:
        """Count total pages in all uploaded files"""
        total_pages = 0
        try:
            for i, file_path in enumerate(files):
                try:
                    if s3_keys and i < len(s3_keys):
                        # Download from S3 first
                        local_path = f"/tmp/{s3_keys[i].split('/')[-1]}"
                        await s3_service.download_file_for_processing(s3_keys[i], local_path)
                        file_path = local_path
                    
                    # Count pages based on file type
                    if file_path.lower().endswith('.pdf'):
                        import PyPDF2
                        with open(file_path, 'rb') as file:
                            pdf_reader = PyPDF2.PdfReader(file)
                            total_pages += len(pdf_reader.pages)
                    else:
                        # For images and other files, count as 1 page each
                        total_pages += 1
                        
                except Exception as e:
                    logger.warning(f"Could not count pages for {file_path}: {str(e)}")
                    total_pages += 1  # Default to 1 page
                    
            return max(1, total_pages)  # Minimum 1 page
            
        except Exception as e:
            logger.error(f"Error counting pages: {str(e)}")
            return len(files)  # Fallback to file count
    
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
        """Generate one mock test from existing questions based on PDF content"""
        try:
            db = get_database()
            
            # Get all questions for this session
            questions = await db.questions.find({"session_id": session_id}).to_list(length=None)
            
            if len(questions) < 5:
                logger.warning(f"Not enough questions to create mock test for session {session_id}")
                return
            
            # Create one comprehensive mock test based on all generated questions
            total_questions = len(questions)
            
            # Determine test duration based on number of questions (1.5 minutes per question)
            duration = max(15, min(90, int(total_questions * 1.5)))
            
            # Generate test name based on content
            session_data = await db.study_sessions.find_one({"session_id": session_id})
            session_name = session_data.get("session_name", "Study Session") if session_data else "Study Session"
            
            mock_test = MockTest(
                test_id=str(uuid.uuid4()),
                session_id=session_id,
                user_id=user_id,
                test_name=f"Mock Test - {session_name}",
                questions=[q["question_id"] for q in questions],
                duration_minutes=duration,
                total_questions=total_questions
            )
            
            await db.mock_tests.insert_one(mock_test.dict())
            
            logger.info(f"Generated 1 mock test with {total_questions} questions for session {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to generate mock test for session {session_id}: {str(e)}")
    
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
    
    async def _store_questions(self, session_id: str, user_id: str, questions_data: List[Dict[str, Any]]):
        """Store generated questions in database"""
        try:
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
            logger.info(f"Stored {len(questions_data)} questions for session {session_id}")
        except Exception as e:
            logger.error(f"Failed to store questions: {str(e)}")
    
    async def _store_mock_test(self, session_id: str, user_id: str, mock_test_data: Dict[str, Any]):
        """Store generated mock test in database"""
        try:
            if not mock_test_data:
                return
            
            db = get_database()
            mock_test = MockTest(
                test_id=str(uuid.uuid4()),
                session_id=session_id,
                user_id=user_id,
                test_name=mock_test_data["name"],
                questions=mock_test_data["questions"],
                duration_minutes=mock_test_data["duration_minutes"],
                total_questions=mock_test_data["total_questions"]
            )
            await db.mock_tests.insert_one(mock_test.dict())
            logger.info(f"Stored mock test for session {session_id}")
        except Exception as e:
            logger.error(f"Failed to store mock test: {str(e)}")
    
    async def _store_mnemonics(self, session_id: str, user_id: str, mnemonics_data: List[Dict[str, Any]]):
        """Store generated mnemonics in database"""
        try:
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
            logger.info(f"Stored {len(mnemonics_data)} mnemonics for session {session_id}")
        except Exception as e:
            logger.error(f"Failed to store mnemonics: {str(e)}")
    
    async def _store_cheat_sheet(self, session_id: str, user_id: str, cheat_sheet_data: Dict[str, Any]):
        """Store generated cheat sheet in database"""
        try:
            if not cheat_sheet_data:
                return
            
            db = get_database()
            cheat_sheet = CheatSheet(
                sheet_id=str(uuid.uuid4()),
                session_id=session_id,
                user_id=user_id,
                title=cheat_sheet_data["title"],
                key_points=cheat_sheet_data["key_points"],
                high_yield_facts=cheat_sheet_data["high_yield_facts"],
                quick_references=cheat_sheet_data.get("quick_references", {})
            )
            await db.cheat_sheets.insert_one(cheat_sheet.dict())
            logger.info(f"Stored cheat sheet for session {session_id}")
        except Exception as e:
            logger.error(f"Failed to store cheat sheet: {str(e)}")
    
    async def _store_notes(self, session_id: str, user_id: str, notes_data: Dict[str, Any]):
        """Store generated notes in database"""
        try:
            if not notes_data:
                return
            
            db = get_database()
            note = Note(
                note_id=str(uuid.uuid4()),
                session_id=session_id,
                user_id=user_id,
                title=notes_data["title"],
                content=notes_data["content"],
                important_questions=[],
                summary_points=notes_data.get("summary_points", []),
                related_mnemonics=[]
            )
            await db.notes.insert_one(note.dict())
            logger.info(f"Stored notes for session {session_id}")
        except Exception as e:
            logger.error(f"Failed to store notes: {str(e)}")

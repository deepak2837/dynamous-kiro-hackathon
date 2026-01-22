import logging
import json
import re
import base64
import uuid
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from app.config import settings
from app.models import DocumentType

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        """Initialize AI service with Gemini API"""
        self.api_key = settings.google_ai_api_key
        if self.api_key and self.api_key != "your_api_key_here":
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            logger.info("AIService initialized with Gemini API")
        else:
            self.model = None
            logger.warning("AIService initialized without valid API key")
    
    def _log_ai_request(self, operation: str, prompt: str, additional_info: Dict[str, Any] = None):
        """Log AI request details"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "prompt_length": len(prompt),
            "prompt_preview": prompt[:500] + "..." if len(prompt) > 500 else prompt,
        }
        if additional_info:
            log_entry.update(additional_info)
        
        logger.info(f"=== AI REQUEST: {operation} ===")
        logger.info(f"Timestamp: {log_entry['timestamp']}")
        logger.info(f"Prompt Length: {log_entry['prompt_length']} characters")
        logger.info(f"Prompt Preview:\n{log_entry['prompt_preview']}")
        if additional_info:
            logger.info(f"Additional Info: {json.dumps(additional_info, indent=2)}")
        logger.info(f"=== END AI REQUEST ===")
        
        return log_entry
    
    def _log_ai_response(self, operation: str, response_text: str, success: bool, additional_info: Dict[str, Any] = None):
        """Log AI response details"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "success": success,
            "response_length": len(response_text) if response_text else 0,
            "response_preview": (response_text[:1000] + "..." if len(response_text) > 1000 else response_text) if response_text else "No response",
        }
        if additional_info:
            log_entry.update(additional_info)
        
        logger.info(f"=== AI RESPONSE: {operation} ===")
        logger.info(f"Timestamp: {log_entry['timestamp']}")
        logger.info(f"Success: {log_entry['success']}")
        logger.info(f"Response Length: {log_entry['response_length']} characters")
        logger.info(f"Response Preview:\n{log_entry['response_preview']}")
        if additional_info:
            logger.info(f"Additional Info: {json.dumps(additional_info, indent=2)}")
        logger.info(f"=== END AI RESPONSE ===")
        
        return log_entry

    async def detect_document_type(self, text: str) -> DocumentType:
        """Detect the type of document based on its content"""
        operation = "DETECT_DOCUMENT_TYPE"
        
        prompt = f"""Analyze this text and determine if it:
1. Contains existing MCQ questions (CONTAINS_QUESTIONS)
2. Is study notes/educational content (STUDY_NOTES)
3. Has both questions and study content (MIXED)

Text sample: {text[:2000]}

Respond with only one of: CONTAINS_QUESTIONS, STUDY_NOTES, or MIXED"""

        self._log_ai_request(operation, prompt, {"text_sample_length": min(len(text), 2000)})
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip().upper()
            
            self._log_ai_response(operation, response_text, True, {"detected_type": response_text})
            
            if "CONTAINS_QUESTIONS" in response_text:
                return DocumentType.CONTAINS_QUESTIONS
            elif "MIXED" in response_text:
                return DocumentType.MIXED
            else:
                return DocumentType.STUDY_NOTES
        except Exception as e:
            self._log_ai_response(operation, str(e), False, {"error": str(e)})
            logger.error(f"Failed to detect document type: {str(e)}")
            return DocumentType.STUDY_NOTES

    async def extract_existing_questions(self, text: str) -> List[Dict[str, Any]]:
        """Extract questions that already exist in the document"""
        operation = "EXTRACT_EXISTING_QUESTIONS"
        
        prompt = f"""Extract all multiple choice questions (MCQs) from the following text.
For each question found, extract:
- The question text
- All options (A, B, C, D or 1, 2, 3, 4)
- The correct answer (as index 0-3)
- The explanation (if provided)
- Difficulty level (easy/medium/hard - estimate if not provided)
- Topic/subject (estimate from context)

IMPORTANT: Preserve the EXACT original wording of questions, options, and explanations.
Do not rephrase or modify the content.

Text:
{text[:5000]}

Return as JSON array:
[
    {{
        "question": "Original question text?",
        "options": ["Original option A", "Original option B", "Original option C", "Original option D"],
        "correct_answer": 0,
        "explanation": "Original explanation text",
        "difficulty": "medium",
        "topic": "Subject name"
    }}
]

If no questions are found, return an empty array: []
"""
        
        self._log_ai_request(operation, prompt, {"text_length": len(text)})
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            self._log_ai_response(operation, response_text, True)
            
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                questions_data = json.loads(json_match.group())
                logger.info(f"Extracted {len(questions_data)} existing questions from document")
                return questions_data
            else:
                logger.warning("No questions found in document")
                return []
                
        except Exception as e:
            self._log_ai_response(operation, str(e), False, {"error": str(e)})
            logger.error(f"Failed to extract existing questions: {str(e)}")
            return []

    async def generate_new_questions(self, text: str, num_questions: int = 15) -> List[Dict[str, Any]]:
        """Generate new MCQs from study notes content"""
        operation = "GENERATE_NEW_QUESTIONS"
        
        # Check if API key is configured
        if not settings.google_ai_api_key or settings.google_ai_api_key == "your_api_key_here":
            logger.error("GEMINI_API_KEY not configured properly in .env file")
            raise Exception("AI service not configured - please set GEMINI_API_KEY in .env file")
        
        prompt = f"""Based on the following study material, generate {num_questions} high-quality multiple choice questions (MCQs) that are DIRECTLY BASED ON THE PROVIDED CONTENT.

IMPORTANT: Generate questions ONLY from the content below. Do NOT add external knowledge.

Content to analyze:
{text[:4000]}

Generate questions that test:
- Key concepts mentioned in the text
- Specific facts and definitions from the content
- Relationships and processes described
- Important details and terminology used

For each question, provide:
1. Question text (directly based on the content)
2. Four options (A, B, C, D) with plausible distractors
3. Correct answer (0-3 index)
4. Detailed explanation referencing the source content
5. Difficulty level (easy/medium/hard)
6. Topic from the content

Format as JSON array:
[
    {{
        "question": "Question text here?",
        "options": ["Option A", "Option B", "Option C", "Option D"],
        "correct_answer": 0,
        "explanation": "Detailed explanation based on the provided content",
        "difficulty": "medium",
        "topic": "Topic from content"
    }}
]

CRITICAL: Questions must be directly derived from the provided text content. Do not generate generic questions."""

        self._log_ai_request(operation, prompt, {
            "num_questions": num_questions,
            "text_length": len(text)
        })

        try:
            logger.info(f"Calling Gemini API to generate {num_questions} questions...")
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            self._log_ai_response(operation, response_text, True, {
                "num_questions_requested": num_questions
            })
            
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                questions_data = json.loads(json_match.group())
                logger.info(f"Successfully generated {len(questions_data)} new questions from study notes")
                return questions_data[:num_questions]
            else:
                logger.warning("Could not extract JSON from AI response")
                return self._generate_fallback_questions(text, num_questions)
                
        except Exception as e:
            self._log_ai_response(operation, str(e), False, {"error": str(e)})
            logger.error(f"Failed to generate new questions: {str(e)}")
            if "API_KEY" in str(e).upper():
                logger.error("API Key issue detected - check GEMINI_API_KEY in .env file")
            return self._generate_fallback_questions(text, num_questions)

    async def generate_content_from_batch(self, batch_text: str, document_type: "DocumentType") -> Dict[str, Any]:
        """Generate all content types from a single batch"""
        operation = "GENERATE_CONTENT_FROM_BATCH"
        
        self._log_ai_request(operation, f"Batch processing for document type: {document_type}", {
            "document_type": str(document_type),
            "batch_text_length": len(batch_text)
        })
        
        try:
            from app.models import BatchContent
            
            # Generate questions (5 per batch to keep processing fast)
            if document_type == DocumentType.CONTAINS_QUESTIONS:
                questions = await self.extract_existing_questions(batch_text)
            else:
                questions = await self.generate_new_questions(batch_text, num_questions=5)
            
            # Generate mnemonics (3 per batch)
            mnemonics = await self.generate_mnemonics(batch_text, num_mnemonics=3)
            
            # Extract key points for cheat sheets
            cheat_sheet_points = await self._extract_key_points(batch_text)
            
            # Extract key concepts
            key_concepts = await self._extract_key_concepts(batch_text)
            
            batch_content = BatchContent(
                batch_id=str(uuid.uuid4()),
                questions=questions,
                mnemonics=mnemonics,
                cheat_sheet_points=cheat_sheet_points,
                key_concepts=key_concepts
            )
            
            self._log_ai_response(operation, "Batch content generated successfully", True, {
                "questions_count": len(questions),
                "mnemonics_count": len(mnemonics),
                "cheat_sheet_points_count": len(cheat_sheet_points),
                "key_concepts_count": len(key_concepts)
            })
            
            logger.info(f"Generated content from batch: {len(questions)} questions, {len(mnemonics)} mnemonics")
            return batch_content
            
        except Exception as e:
            self._log_ai_response(operation, str(e), False, {"error": str(e)})
            logger.error(f"Failed to generate content from batch: {str(e)}")
            return BatchContent(
                batch_id=str(uuid.uuid4()),
                questions=[],
                mnemonics=[],
                cheat_sheet_points=[],
                key_concepts=[]
            )

    async def _extract_key_points(self, text: str) -> List[str]:
        """Extract key points for cheat sheets from text"""
        operation = "EXTRACT_KEY_POINTS"
        
        prompt = f"""Extract 5-7 key points from this medical text that would be useful for a cheat sheet.
Focus on:
- Important definitions
- Critical facts
- Clinical pearls
- High-yield information

Text: {text[:2000]}

Return as a simple list, one point per line."""

        self._log_ai_request(operation, prompt, {"text_length": min(len(text), 2000)})
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            self._log_ai_response(operation, response_text, True)
            
            points = [line.strip() for line in response_text.split('\n') if line.strip() and not line.strip().startswith('#')]
            return points[:7]
            
        except Exception as e:
            self._log_ai_response(operation, str(e), False, {"error": str(e)})
            logger.error(f"Failed to extract key points: {str(e)}")
            return []

    async def _extract_key_concepts(self, text: str) -> List[str]:
        """Extract key concepts from text"""
        operation = "EXTRACT_KEY_CONCEPTS"
        
        prompt = f"""Extract 5-10 key medical concepts or terms from this text that students should focus on.

Text: {text[:2000]}

Return as a simple list, one concept per line."""

        self._log_ai_request(operation, prompt, {"text_length": min(len(text), 2000)})
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            self._log_ai_response(operation, response_text, True)
            
            concepts = [line.strip() for line in response_text.split('\n') if line.strip() and not line.strip().startswith('#')]
            return concepts[:10]
            
        except Exception as e:
            self._log_ai_response(operation, str(e), False, {"error": str(e)})
            logger.error(f"Failed to extract key concepts: {str(e)}")
            return []

    async def analyze_images(self, image_paths: List[str]) -> str:
        """Analyze images directly with AI"""
        operation = "ANALYZE_IMAGES"
        
        self._log_ai_request(operation, f"Analyzing {len(image_paths)} images", {
            "image_count": len(image_paths),
            "image_paths": image_paths[:5]  # Log first 5 paths
        })
        
        try:
            all_text = []
            for image_path in image_paths:
                with open(image_path, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode('utf-8')
                
                prompt = "Extract all text from this image. If it contains medical content, preserve medical terminology accurately."
                
                response = self.model.generate_content([
                    prompt,
                    {"mime_type": "image/jpeg", "data": image_data}
                ])
                
                if response.text:
                    all_text.append(response.text)
            
            combined_text = "\n\n".join(all_text)
            
            self._log_ai_response(operation, combined_text, True, {
                "images_processed": len(image_paths),
                "total_text_length": len(combined_text)
            })
            
            return combined_text
            
        except Exception as e:
            self._log_ai_response(operation, str(e), False, {"error": str(e)})
            logger.error(f"Failed to analyze images: {str(e)}")
            return ""
    # Cache for uploaded files to avoid re-uploading
    _file_cache: Dict[str, Any] = {}

    async def analyze_file_with_prompt(self, file_path: str, prompt: str) -> str:
        """
        Analyze a file (PDF, image, etc.) by uploading it directly to Gemini API.
        
        This is the key method for file-based content generation. It sends the actual
        file to Gemini rather than extracting text first, allowing the AI to analyze
        the complete document including layout, diagrams, and context.
        
        Uses caching to avoid re-uploading the same file for multiple prompts.
        
        Args:
            file_path: Path to the file to analyze
            prompt: The instruction prompt for generating content
            
        Returns:
            The AI-generated response text
        """
        operation = "ANALYZE_FILE_WITH_PROMPT"
        
        self._log_ai_request(operation, prompt[:500], {
            "file_path": file_path,
            "prompt_length": len(prompt)
        })
        
        try:
            import os
            import mimetypes
            
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Determine MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type is None:
                # Default based on extension
                ext = os.path.splitext(file_path)[1].lower()
                mime_types_map = {
                    '.pdf': 'application/pdf',
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.png': 'image/png',
                    '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                    '.ppt': 'application/vnd.ms-powerpoint'
                }
                mime_type = mime_types_map.get(ext, 'application/octet-stream')
            
            file_size = os.path.getsize(file_path)
            logger.info(f"Analyzing file: {file_path}, MIME: {mime_type}, Size: {file_size} bytes")
            
            # Check if we already have this file uploaded (for reuse across multiple prompts)
            cache_key = f"{file_path}:{os.path.getmtime(file_path)}"
            
            # For large files (> 20MB), use the File API with caching
            # For smaller files, always use inline data (more reliable)
            if file_size > 20 * 1024 * 1024:  # 20MB threshold
                if cache_key in self._file_cache:
                    logger.info(f"Using cached file upload: {self._file_cache[cache_key].name}")
                    uploaded_file = self._file_cache[cache_key]
                else:
                    logger.info(f"Using File API for large file upload")
                    try:
                        # Upload file to Gemini File API
                        uploaded_file = genai.upload_file(file_path, mime_type=mime_type)
                        logger.info(f"File uploaded successfully: {uploaded_file.name}")
                        # Cache the uploaded file
                        self._file_cache[cache_key] = uploaded_file
                    except Exception as upload_error:
                        logger.warning(f"File API upload failed, falling back to inline: {upload_error}")
                        # Fall back to inline for this file
                        with open(file_path, 'rb') as f:
                            file_data = f.read()
                        file_content = {
                            "mime_type": mime_type,
                            "data": base64.b64encode(file_data).decode('utf-8')
                        }
                        response = self.model.generate_content([prompt, file_content])
                        if response and response.text:
                            return response.text
                        return ""
                
                # Generate content with uploaded file
                response = self.model.generate_content([prompt, uploaded_file])
            else:
                # For smaller files, use inline data (more reliable, no caching needed)
                logger.info(f"Using inline data for file analysis")
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                
                file_content = {
                    "mime_type": mime_type,
                    "data": base64.b64encode(file_data).decode('utf-8')
                }
                
                response = self.model.generate_content([prompt, file_content])
            
            if response and response.text:
                response_text = response.text
                self._log_ai_response(operation, response_text, True, {
                    "file_path": file_path,
                    "response_length": len(response_text)
                })
                return response_text
            else:
                logger.warning(f"Empty response from AI for file: {file_path}")
                return ""
                
        except Exception as e:
            self._log_ai_response(operation, str(e), False, {"error": str(e), "file_path": file_path})
            logger.error(f"❌ File analysis failed: {str(e)}")
            raise

    def cleanup_file_cache(self):
        """Clean up all cached uploaded files."""
        for cache_key, uploaded_file in self._file_cache.items():
            try:
                genai.delete_file(uploaded_file.name)
                logger.info(f"Cleaned up cached file: {uploaded_file.name}")
            except Exception as e:
                logger.warning(f"Failed to cleanup cached file: {e}")
        self._file_cache.clear()

    async def generate_content_from_text(self, text: str) -> Dict[str, Any]:
        """Generate all content types from extracted text"""
        operation = "GENERATE_CONTENT_FROM_TEXT"
        
        self._log_ai_request(operation, f"Generating all content types from text", {
            "text_length": len(text)
        })
        
        try:
            # Generate questions
            questions = await self.generate_questions(text)
            
            # Generate mock test
            mock_test = await self.generate_mock_test_from_questions(questions)
            
            # Generate mnemonics
            mnemonics = await self.generate_mnemonics(text)
            
            # Generate cheat sheet
            cheat_sheet = await self.generate_cheat_sheets(text)
            
            # Generate notes
            notes = await self.generate_notes(text)
            
            result = {
                "questions": questions,
                "mock_test": mock_test,
                "mnemonics": mnemonics,
                "cheat_sheet": cheat_sheet,
                "notes": notes
            }
            
            self._log_ai_response(operation, "All content generated successfully", True, {
                "questions_count": len(questions),
                "mnemonics_count": len(mnemonics),
                "cheat_sheets_count": len(cheat_sheet) if isinstance(cheat_sheet, list) else 1,
                "notes_count": len(notes) if isinstance(notes, list) else 1
            })
            
            return result
            
        except Exception as e:
            self._log_ai_response(operation, str(e), False, {"error": str(e)})
            logger.error(f"Failed to generate content from text: {str(e)}")
            return {}

    async def generate_content_from_topic(self, topic: str) -> Dict[str, Any]:
        """Generate all content types from a topic name (no file upload)."""
        operation = "GENERATE_CONTENT_FROM_TOPIC"
        
        prompt = f"""You are a medical education expert. Generate comprehensive study materials for MBBS students about the topic: "{topic}"

Generate the following content in JSON format:

{{
    "questions": [
        {{
            "question": "MCQ question text?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": 0,
            "explanation": "Detailed explanation",
            "difficulty": "easy|medium|hard"
        }}
    ],
    "mnemonics": [
        {{
            "topic": "Sub-topic name",
            "mnemonic": "The mnemonic text",
            "explanation": "What it helps remember",
            "key_terms": ["term1", "term2"]
        }}
    ],
    "cheat_sheet": {{
        "title": "Cheat Sheet: {topic}",
        "key_points": ["Key point 1", "Key point 2"],
        "high_yield_facts": ["High-yield fact 1", "High-yield fact 2"],
        "quick_references": {{"Term": "Definition"}}
    }},
    "notes": {{
        "title": "Study Notes: {topic}",
        "content": "Comprehensive content about the topic...",
        "summary_points": ["Summary point 1", "Summary point 2"]
    }}
}}

Requirements:
1. Generate 10-15 high-quality MCQs covering different aspects of {topic}
2. Generate 5-7 memorable mnemonics (use India-specific references when possible)
3. Create a comprehensive cheat sheet with 8-10 key points
4. Write detailed study notes covering all important aspects

Make all content medically accurate and relevant for MBBS exams in India."""

        self._log_ai_request(operation, prompt, {"topic": topic})

        try:
            logger.info(f"Generating content from topic: {topic}")
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            self._log_ai_response(operation, response_text, True, {"topic": topic})
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                content = json.loads(json_match.group())
                logger.info(f"Generated content from topic: {len(content.get('questions', []))} questions")
                return content
            else:
                logger.warning(f"Could not extract JSON from topic response for: {topic}")
                return self._generate_fallback_topic_content(topic)
                
        except Exception as e:
            self._log_ai_response(operation, str(e), False, {"error": str(e), "topic": topic})
            logger.error(f"Failed to generate content from topic: {str(e)}")
            return self._generate_fallback_topic_content(topic)

    def _generate_fallback_topic_content(self, topic: str) -> Dict[str, Any]:
        """Generate fallback content when AI fails for topic input"""
        logger.warning(f"Using fallback content for topic: {topic}")
        return {
            "questions": [
                {
                    "question": f"⚠️ What are the key aspects of {topic}? (AI service issue)",
                    "options": ["Check API key", "Restart service", "Try again later", "Contact support"],
                    "correct_answer": 0,
                    "explanation": "AI service encountered an error. Please check your configuration.",
                    "difficulty": "medium"
                }
            ],
            "mnemonics": [
                {
                    "topic": topic,
                    "mnemonic": "AI service unavailable",
                    "explanation": "Please check GEMINI_API_KEY configuration",
                    "key_terms": ["API", "configuration"]
                }
            ],
            "cheat_sheet": {
                "title": f"Cheat Sheet: {topic}",
                "key_points": ["AI service unavailable - check configuration"],
                "high_yield_facts": ["Please verify GEMINI_API_KEY in .env file"],
                "quick_references": {"Status": "Error - AI unavailable"}
            },
            "notes": {
                "title": f"Study Notes: {topic}",
                "content": "AI service encountered an error. Please check your GEMINI_API_KEY configuration in the .env file.",
                "summary_points": ["Check API configuration", "Restart backend service"]
            }
        }

    async def generate_mock_test_from_questions(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a single mock test from questions"""
        operation = "GENERATE_MOCK_TEST"
        
        self._log_ai_request(operation, f"Creating mock test from {len(questions)} questions", {
            "questions_count": len(questions)
        })
        
        try:
            if not questions or len(questions) < 5:
                self._log_ai_response(operation, "Insufficient questions for mock test", False, {
                    "questions_count": len(questions) if questions else 0
                })
                return {}
            
            # Create mock test structure
            total_questions = len(questions)
            duration = max(15, min(90, int(total_questions * 1.5)))
            
            mock_test = {
                "name": f"Comprehensive Mock Test ({total_questions} Questions)",
                "questions": [q["question_id"] if "question_id" in q else str(i) for i, q in enumerate(questions)],
                "duration_minutes": duration,
                "total_questions": total_questions,
                "description": f"Mock test based on uploaded PDF content with {total_questions} questions"
            }
            
            self._log_ai_response(operation, "Mock test created successfully", True, {
                "test_name": mock_test["name"],
                "duration_minutes": duration,
                "total_questions": total_questions
            })
            
            return mock_test
            
        except Exception as e:
            self._log_ai_response(operation, str(e), False, {"error": str(e)})
            logger.error(f"Failed to generate mock test: {str(e)}")
            return {}

    async def generate_questions(self, text: str, num_questions: int = 15) -> List[Dict[str, Any]]:
        """Generate or extract questions based on document type"""
        operation = "GENERATE_QUESTIONS_MAIN"
        
        self._log_ai_request(operation, f"Main question generation method called", {
            "text_length": len(text),
            "num_questions": num_questions
        })
        
        try:
            # First, detect document type
            doc_type = await self.detect_document_type(text)
            
            # Route based on document type
            if doc_type == DocumentType.CONTAINS_QUESTIONS:
                logger.info("Document contains questions - extracting existing questions")
                questions = await self.extract_existing_questions(text)
                
                if questions:
                    self._log_ai_response(operation, f"Extracted {len(questions)} existing questions", True, {
                        "doc_type": str(doc_type),
                        "questions_count": len(questions)
                    })
                    return questions
                else:
                    logger.warning("Question extraction failed, falling back to generation")
                    return await self.generate_new_questions(text, num_questions)
            
            elif doc_type == DocumentType.MIXED:
                logger.info("Document has mixed content - extracting and generating questions")
                existing_questions = await self.extract_existing_questions(text)
                
                if len(existing_questions) >= num_questions:
                    self._log_ai_response(operation, f"Extracted {len(existing_questions)} questions from mixed content", True, {
                        "doc_type": str(doc_type),
                        "questions_count": len(existing_questions)
                    })
                    return existing_questions[:num_questions]
                else:
                    additional_needed = num_questions - len(existing_questions)
                    new_questions = await self.generate_new_questions(text, additional_needed)
                    combined = existing_questions + new_questions
                    self._log_ai_response(operation, f"Combined {len(combined)} questions", True, {
                        "doc_type": str(doc_type),
                        "existing_count": len(existing_questions),
                        "generated_count": len(new_questions)
                    })
                    return combined
            
            else:  # STUDY_NOTES
                logger.info("Document is study notes - generating new questions")
                questions = await self.generate_new_questions(text, num_questions)
                self._log_ai_response(operation, f"Generated {len(questions)} questions from study notes", True, {
                    "doc_type": str(doc_type),
                    "questions_count": len(questions)
                })
                return questions
                
        except Exception as e:
            self._log_ai_response(operation, str(e), False, {"error": str(e)})
            logger.error(f"Failed to generate questions: {str(e)}")
            return self._generate_fallback_questions(text, num_questions)

    async def generate_mnemonics(self, text: str, num_mnemonics: int = 10) -> List[Dict[str, Any]]:
        """Generate mnemonics from text"""
        operation = "GENERATE_MNEMONICS"
        
        prompt = f"""
Based on the following medical study material, create {num_mnemonics} memorable mnemonics suitable for Indian medical students.

Text: {text[:3000]}

For each mnemonic, provide:
1. Topic/concept it helps remember
2. The mnemonic text
3. Explanation of what it represents
4. Key terms highlighted

Make mnemonics:
- India-specific when possible (use Indian names, places, cultural references)
- Easy to remember
- Medically accurate
- Relevant to MBBS curriculum

Format as JSON array:
[
    {{
        "topic": "Topic name",
        "mnemonic": "Mnemonic text here",
        "explanation": "What this mnemonic helps remember",
        "key_terms": ["term1", "term2", "term3"]
    }}
]
"""

        self._log_ai_request(operation, prompt, {
            "num_mnemonics": num_mnemonics,
            "text_length": len(text)
        })
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            self._log_ai_response(operation, response_text, True, {
                "num_mnemonics_requested": num_mnemonics
            })
            
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                mnemonics_data = json.loads(json_match.group())
                logger.info(f"Successfully generated {len(mnemonics_data)} mnemonics")
                return mnemonics_data[:num_mnemonics]
            else:
                logger.warning("Could not extract JSON from mnemonics response")
                return self._generate_fallback_mnemonics(text, num_mnemonics)
                
        except Exception as e:
            self._log_ai_response(operation, str(e), False, {"error": str(e)})
            logger.error(f"Failed to generate mnemonics: {str(e)}")
            return self._generate_fallback_mnemonics(text, num_mnemonics)

    async def generate_cheat_sheets(self, text: str, num_sheets: int = 5) -> List[Dict[str, Any]]:
        """Generate cheat sheets from text"""
        operation = "GENERATE_CHEAT_SHEETS"
        
        prompt = f"""
Based on the following medical study material, create {num_sheets} concise cheat sheets for quick revision.

Text: {text[:3000]}

For each cheat sheet, provide:
1. Title/topic
2. Key points (5-10 bullet points)
3. High-yield facts for exams
4. Quick reference mappings (term: definition)

Focus on:
- Most important concepts
- Exam-relevant facts
- Easy-to-scan format
- Memory aids

Format as JSON array:
[
    {{
        "title": "Cheat Sheet Title",
        "key_points": ["Point 1", "Point 2", "Point 3"],
        "high_yield_facts": ["Fact 1", "Fact 2", "Fact 3"],
        "quick_references": {{"Term": "Definition", "Term2": "Definition2"}}
    }}
]
"""

        self._log_ai_request(operation, prompt, {
            "num_sheets": num_sheets,
            "text_length": len(text)
        })
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            self._log_ai_response(operation, response_text, True, {
                "num_sheets_requested": num_sheets
            })
            
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                sheets_data = json.loads(json_match.group())
                logger.info(f"Successfully generated {len(sheets_data)} cheat sheets")
                return sheets_data[:num_sheets]
            else:
                logger.warning("Could not extract JSON from cheat sheets response")
                return self._generate_fallback_cheat_sheets(text, num_sheets)
                
        except Exception as e:
            self._log_ai_response(operation, str(e), False, {"error": str(e)})
            logger.error(f"Failed to generate cheat sheets: {str(e)}")
            return self._generate_fallback_cheat_sheets(text, num_sheets)

    async def generate_notes(self, text: str, num_notes: int = 3) -> List[Dict[str, Any]]:
        """Generate compiled notes from text"""
        operation = "GENERATE_NOTES"
        
        prompt = f"""
Based on the following medical study material, create {num_notes} comprehensive study notes.

Text: {text[:4000]}

For each note, provide:
1. Title
2. Detailed content (well-structured)
3. Summary points (key takeaways)

Make notes:
- Well-organized and structured
- Include important details
- Highlight key concepts
- Suitable for exam preparation

Format as JSON array:
[
    {{
        "title": "Note Title",
        "content": "Detailed note content with proper structure...",
        "summary_points": ["Summary point 1", "Summary point 2"]
    }}
]
"""

        self._log_ai_request(operation, prompt, {
            "num_notes": num_notes,
            "text_length": len(text)
        })
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            self._log_ai_response(operation, response_text, True, {
                "num_notes_requested": num_notes
            })
            
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                notes_data = json.loads(json_match.group())
                logger.info(f"Successfully generated {len(notes_data)} notes")
                return notes_data[:num_notes]
            else:
                logger.warning("Could not extract JSON from notes response")
                return self._generate_fallback_notes(text, num_notes)
                
        except Exception as e:
            self._log_ai_response(operation, str(e), False, {"error": str(e)})
            logger.error(f"Failed to generate notes: {str(e)}")
            return self._generate_fallback_notes(text, num_notes)

    def _generate_fallback_questions(self, text: str, num_questions: int) -> List[Dict[str, Any]]:
        """Generate fallback questions when AI fails"""
        logger.warning("Using fallback questions - AI service failed")
        
        questions = []
        for i in range(min(num_questions, 5)):
            questions.append({
                "question": f"⚠️ FALLBACK: What is the main concept discussed in section {i+1}? (AI service failed - check GEMINI_API_KEY)",
                "options": [
                    "AI service not configured properly", 
                    "Check GEMINI_API_KEY in .env file", 
                    "Restart backend after fixing API key", 
                    "Contact support if issue persists"
                ],
                "correct_answer": 0,
                "explanation": "This is a fallback question generated when AI processing failed. Please check your GEMINI_API_KEY configuration in the .env file.",
                "difficulty": "medium",
                "topic": "Configuration Error"
            })
        
        return questions

    def _generate_fallback_mnemonics(self, text: str, num_mnemonics: int) -> List[Dict[str, Any]]:
        """Generate fallback mnemonics when AI fails"""
        mnemonics = []
        
        for i in range(min(num_mnemonics, 3)):
            mnemonics.append({
                "topic": f"Topic {i+1}",
                "mnemonic": f"Remember: Key concept {i+1}",
                "explanation": "This is a fallback mnemonic generated when AI processing failed.",
                "key_terms": ["term1", "term2"]
            })
        
        return mnemonics

    def _generate_fallback_cheat_sheets(self, text: str, num_sheets: int) -> List[Dict[str, Any]]:
        """Generate fallback cheat sheets when AI fails"""
        sheets = []
        
        for i in range(min(num_sheets, 2)):
            sheets.append({
                "title": f"Study Sheet {i+1}",
                "key_points": ["Key point 1", "Key point 2", "Key point 3"],
                "high_yield_facts": ["Important fact 1", "Important fact 2"],
                "quick_references": {"Term": "Definition"}
            })
        
        return sheets

    def _generate_fallback_notes(self, text: str, num_notes: int) -> List[Dict[str, Any]]:
        """Generate fallback notes when AI fails"""
        notes = []
        
        for i in range(min(num_notes, 2)):
            notes.append({
                "title": f"Study Note {i+1}",
                "content": f"This is a fallback note generated from the uploaded content. The original text contained important medical information that could not be processed by AI at this time.",
                "summary_points": ["Summary point 1", "Summary point 2"]
            })
        
        return notes

    def extract_json_from_response(self, response_text: str) -> Optional[Dict | List]:
        """Extract JSON from AI response with multiple fallback methods."""
        operation = "EXTRACT_JSON"
        
        logger.info(f"=== RAW AI RESPONSE START ===")
        logger.info(response_text)
        logger.info(f"=== RAW AI RESPONSE END ===")
        
        if not response_text or not response_text.strip():
            logger.error("Empty response from AI")
            return None
        
        # Method 1: Direct JSON parse
        try:
            result = json.loads(response_text.strip())
            logger.info("JSON extracted using Method 1: Direct parse")
            return result
        except json.JSONDecodeError as e:
            logger.debug(f"Method 1 failed: {e}")
        
        # Method 2: Find JSON in markdown code blocks
        json_match = re.search(r'```(?:json)?\s*\n?([\s\S]*?)\n?```', response_text)
        if json_match:
            try:
                result = json.loads(json_match.group(1).strip())
                logger.info("JSON extracted using Method 2: Markdown code block")
                return result
            except json.JSONDecodeError as e:
                logger.debug(f"Method 2 failed: {e}")
        
        # Method 3: Find JSON array
        array_match = re.search(r'(\[[\s\S]*\])', response_text)
        if array_match:
            try:
                result = json.loads(array_match.group(1))
                logger.info("JSON extracted using Method 3: Array pattern")
                return result
            except json.JSONDecodeError as e:
                logger.debug(f"Method 3 failed: {e}")
        
        # Method 4: Find JSON object
        object_match = re.search(r'(\{[\s\S]*\})', response_text)
        if object_match:
            try:
                result = json.loads(object_match.group(1))
                logger.info("JSON extracted using Method 4: Object pattern")
                return result
            except json.JSONDecodeError as e:
                logger.debug(f"Method 4 failed: {e}")
        
        # Method 5: Clean and parse
        cleaned = response_text.strip()
        cleaned = re.sub(r'^```\w*\n?', '', cleaned)
        cleaned = re.sub(r'\n?```$', '', cleaned)
        cleaned = re.sub(r',\s*([}\]])', r'\1', cleaned)
        cleaned = re.sub(r"'([^']*)':", r'"\1":', cleaned)
        
        try:
            result = json.loads(cleaned)
            logger.info("JSON extracted using Method 5: Cleaned text")
            return result
        except json.JSONDecodeError as e:
            logger.debug(f"Method 5 failed: {e}")
        
        # Method 6: Extract questions array specifically
        questions_match = re.search(r'"questions"\s*:\s*(\[[\s\S]*?\])', response_text)
        if questions_match:
            try:
                questions = json.loads(questions_match.group(1))
                logger.info("JSON extracted using Method 6: Questions array extraction")
                return {"questions": questions}
            except json.JSONDecodeError as e:
                logger.debug(f"Method 6 failed: {e}")
        
        logger.error(f"All JSON extraction methods failed for response: {response_text[:500]}...")
        return None

    async def call_gemini_with_retry(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """Call Gemini API with retry logic."""
        operation = "GEMINI_API_CALL_WITH_RETRY"
        
        self._log_ai_request(operation, prompt, {"max_retries": max_retries})
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Gemini API call attempt {attempt + 1}/{max_retries}")
                response = self.model.generate_content(prompt)
                
                if response and response.text:
                    self._log_ai_response(operation, response.text, True, {
                        "attempt": attempt + 1,
                        "max_retries": max_retries
                    })
                    return response.text
                    
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    self._log_ai_response(operation, str(e), False, {
                        "attempt": attempt + 1,
                        "error": str(e)
                    })
                    raise
        
        return None

    async def generate_questions_for_study_notes(self, content: str, num_questions: int = 15) -> List[Dict]:
        """Generate questions specifically for study notes."""
        operation = "GENERATE_QUESTIONS_STUDY_NOTES"
        logger.info(f"Generating {num_questions} questions for STUDY_NOTES")
        
        prompt = self._build_study_notes_prompt(content, num_questions)
        
        self._log_ai_request(operation, prompt, {
            "num_questions": num_questions,
            "content_length": len(content)
        })
        
        response_text = await self.call_gemini_with_retry(prompt)
        if not response_text:
            logger.error("Failed to get response for study notes questions")
            return self._get_fallback_questions("study notes")
        
        self._log_ai_response(operation, response_text, True, {
            "num_questions_requested": num_questions
        })
        
        json_data = self.extract_json_from_response(response_text)
        if not json_data:
            logger.warning("JSON extraction failed, retrying with stricter prompt...")
            strict_prompt = prompt + "\n\nCRITICAL: Return ONLY the JSON array, no other text. Start with [ and end with ]"
            response_text = await self.call_gemini_with_retry(strict_prompt)
            if response_text:
                json_data = self.extract_json_from_response(response_text)
        
        if json_data:
            questions = json_data if isinstance(json_data, list) else json_data.get("questions", [])
            if questions:
                logger.info(f"Successfully generated {len(questions)} questions for study notes")
                return questions
        
        logger.warning("Using fallback questions for study notes")
        return self._get_fallback_questions("study notes")

    async def generate_questions_for_cheat_sheet(self, content: str, num_questions: int = 15) -> List[Dict]:
        """Generate questions specifically for cheat sheets."""
        operation = "GENERATE_QUESTIONS_CHEAT_SHEET"
        logger.info(f"Generating {num_questions} questions for CHEAT_SHEET")
        
        prompt = self._build_cheat_sheet_prompt(content, num_questions)
        
        self._log_ai_request(operation, prompt, {
            "num_questions": num_questions,
            "content_length": len(content)
        })
        
        response_text = await self.call_gemini_with_retry(prompt)
        if not response_text:
            logger.error("Failed to get response for cheat sheet questions")
            return self._get_fallback_questions("cheat sheet")
        
        self._log_ai_response(operation, response_text, True, {
            "num_questions_requested": num_questions
        })
        
        json_data = self.extract_json_from_response(response_text)
        if not json_data:
            logger.warning("JSON extraction failed, retrying with stricter prompt...")
            strict_prompt = prompt + "\n\nCRITICAL: Return ONLY the JSON array, no other text. Start with [ and end with ]"
            response_text = await self.call_gemini_with_retry(strict_prompt)
            if response_text:
                json_data = self.extract_json_from_response(response_text)
        
        if json_data:
            questions = json_data if isinstance(json_data, list) else json_data.get("questions", [])
            if questions:
                logger.info(f"Successfully generated {len(questions)} questions for cheat sheet")
                return questions
        
        logger.warning("Using fallback questions for cheat sheet")
        return self._get_fallback_questions("cheat sheet")

    async def generate_questions_for_mnemonic(self, content: str, num_questions: int = 15) -> List[Dict]:
        """Generate questions specifically for mnemonics."""
        operation = "GENERATE_QUESTIONS_MNEMONIC"
        logger.info(f"Generating {num_questions} questions for MNEMONIC")
        
        prompt = self._build_mnemonic_prompt(content, num_questions)
        
        self._log_ai_request(operation, prompt, {
            "num_questions": num_questions,
            "content_length": len(content)
        })
        
        response_text = await self.call_gemini_with_retry(prompt)
        if not response_text:
            logger.error("Failed to get response for mnemonic questions")
            return self._get_fallback_questions("mnemonic")
        
        self._log_ai_response(operation, response_text, True, {
            "num_questions_requested": num_questions
        })
        
        json_data = self.extract_json_from_response(response_text)
        if not json_data:
            logger.warning("JSON extraction failed, retrying with stricter prompt...")
            strict_prompt = prompt + "\n\nCRITICAL: Return ONLY the JSON array, no other text. Start with [ and end with ]"
            response_text = await self.call_gemini_with_retry(strict_prompt)
            if response_text:
                json_data = self.extract_json_from_response(response_text)
        
        if json_data:
            questions = json_data if isinstance(json_data, list) else json_data.get("questions", [])
            if questions:
                logger.info(f"Successfully generated {len(questions)} questions for mnemonic")
                return questions
        
        logger.warning("Using fallback questions for mnemonic")
        return self._get_fallback_questions("mnemonic")

    def _build_study_notes_prompt(self, content: str, num_questions: int) -> str:
        """Build prompt for study notes question generation."""
        prompt = f"""You are a question generator for study materials. Generate exactly {num_questions} multiple choice questions based on the following study notes.

CONTENT:
{content[:8000]}

OUTPUT REQUIREMENTS - STRICTLY FOLLOW:
1. Return ONLY a valid JSON array, nothing else
2. No markdown, no explanations, no additional text
3. Start your response with [ and end with ]
4. Each question must have exactly this structure:

[
  {{
    "question": "Clear question text here?",
    "difficulty": "easy|medium|hard",
    "topic": "Topic name",
    "options": {{
      "A": "First option",
      "B": "Second option", 
      "C": "Third option",
      "D": "Fourth option"
    }},
    "correct_answer": "A|B|C|D",
    "explanation": "Brief explanation why this answer is correct"
  }}
]

Generate {num_questions} questions now. ONLY return the JSON array:"""

        # Log the full prompt
        logger.info(f"=== FULL PROMPT BEING SENT TO GEMINI ===")
        logger.info(f"Prompt length: {len(prompt)} characters")
        logger.info(f"Content in prompt (first 2000 chars): {content[:2000]}")
        logger.info(f"=== END PROMPT PREVIEW ===")
        
        return prompt

    def _build_cheat_sheet_prompt(self, content: str, num_questions: int) -> str:
        """Build prompt for cheat sheet question generation."""
        return f"""You are a question generator for quick reference cheat sheets. Generate exactly {num_questions} multiple choice questions focusing on key facts and quick recall.

CONTENT:
{content[:8000]}

OUTPUT REQUIREMENTS - STRICTLY FOLLOW:
1. Return ONLY a valid JSON array, nothing else
2. No markdown, no explanations, no additional text
3. Start your response with [ and end with ]
4. Focus on factual recall and quick definitions

[
  {{
    "question": "Question about key fact or definition?",
    "difficulty": "easy|medium|hard",
    "topic": "Topic name",
    "options": {{
      "A": "First option",
      "B": "Second option",
      "C": "Third option", 
      "D": "Fourth option"
    }},
    "correct_answer": "A|B|C|D",
    "explanation": "Brief explanation"
  }}
]

Generate {num_questions} questions now. ONLY return the JSON array:"""

    def _build_mnemonic_prompt(self, content: str, num_questions: int) -> str:
        """Build prompt for mnemonic question generation."""
        return f"""You are a question generator for mnemonic devices and memory aids. Generate exactly {num_questions} multiple choice questions that test understanding of mnemonics and what they represent.

CONTENT:
{content[:8000]}

OUTPUT REQUIREMENTS - STRICTLY FOLLOW:
1. Return ONLY a valid JSON array, nothing else
2. No markdown, no explanations, no additional text
3. Start your response with [ and end with ]
4. Test both the mnemonic itself and what each letter/part represents

[
  {{
    "question": "Question about mnemonic or its meaning?",
    "difficulty": "easy|medium|hard",
    "topic": "Topic name",
    "options": {{
      "A": "First option",
      "B": "Second option",
      "C": "Third option",
      "D": "Fourth option"
    }},
    "correct_answer": "A|B|C|D",
    "explanation": "Brief explanation connecting to the mnemonic"
  }}
]

Generate {num_questions} questions now. ONLY return the JSON array:"""

    def _get_fallback_questions(self, doc_type: str) -> List[Dict]:
        """Return fallback questions when AI fails."""
        return [
            {
                "question": f"⚠️ FALLBACK: What is the main concept discussed in section 1? (AI service failed for {doc_type} - check GEMINI_API_KEY)",
                "difficulty": "medium",
                "topic": "Configuration Error",
                "options": {
                    "A": "Option A - Please retry upload",
                    "B": "Option B - Check API key",
                    "C": "Option C - Review logs",
                    "D": "Option D - Contact support"
                },
                "correct_answer": "B",
                "explanation": f"This is a fallback question generated when AI processing failed for {doc_type}. Please check your GEMINI_API_KEY configuration in the .env file."
            }
        ]

    async def generate_questions(self, content: str, doc_type: str = "STUDY_NOTES", num_questions: int = 15) -> List[Dict]:
        """Main method to generate questions based on document type."""
        operation = "GENERATE_QUESTIONS_BY_DOC_TYPE"
        logger.info(f"Generating questions for document type: {doc_type}")
        
        self._log_ai_request(operation, f"Generating questions for doc_type: {doc_type}", {
            "doc_type": doc_type,
            "num_questions": num_questions,
            "content_length": len(content)
        })
        
        doc_type_upper = doc_type.upper() if doc_type else "STUDY_NOTES"
        
        if doc_type_upper == "MNEMONIC" or (doc_type and "mnemonic" in doc_type.lower()):
            result = await self.generate_questions_for_mnemonic(content, num_questions)
        elif doc_type_upper == "CHEAT_SHEET" or (doc_type and "cheat" in doc_type.lower()):
            result = await self.generate_questions_for_cheat_sheet(content, num_questions)
        else:  # STUDY_NOTES or default
            result = await self.generate_questions_for_study_notes(content, num_questions)
        
        self._log_ai_response(operation, f"Generated {len(result)} questions", True, {
            "doc_type": doc_type,
            "questions_count": len(result)
        })
        
        return result

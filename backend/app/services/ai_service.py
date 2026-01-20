import logging
import json
import re
import base64
import uuid
from typing import List, Dict, Any
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from app.config import settings
from app.models import DocumentType

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        # Configure Google GenAI
        genai.configure(api_key=settings.google_ai_api_key)
        
        # Safety settings for medical content - allow all content for adult educational purposes
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        }
        
        # Log safety settings configuration for audit purposes
        logger.info("Gemini AI Service initialized with safety settings:")
        logger.info(f"  - DANGEROUS_CONTENT: BLOCK_NONE (medical content allowed)")
        logger.info(f"  - HATE_SPEECH: BLOCK_NONE (medical terminology allowed)")
        logger.info(f"  - HARASSMENT: BLOCK_NONE (clinical descriptions allowed)")
        logger.info(f"  - SEXUALLY_EXPLICIT: BLOCK_NONE (anatomical content allowed)")
        
        # Initialize models with safety settings
        self.model = genai.GenerativeModel('gemini-pro', safety_settings=self.safety_settings)
        self.vision_model = genai.GenerativeModel('gemini-pro-vision', safety_settings=self.safety_settings)
    
    async def detect_document_type(self, text: str) -> DocumentType:
        """
        Analyze text to determine if it contains questions or study notes
        Returns: CONTAINS_QUESTIONS, STUDY_NOTES, or MIXED
        """
        try:
            # Quick heuristic check first
            question_indicators = [
                r'\b\d+\.\s*[A-Z]',  # Numbered questions
                r'\b[A-D]\)',  # Multiple choice options
                r'\bcorrect answer',
                r'\bexplanation:',
                r'\bwhich of the following',
                r'\bwhat is',
                r'\bselect the',
                r'\bchoose the'
            ]
            
            question_count = sum(1 for pattern in question_indicators if re.search(pattern, text[:2000], re.IGNORECASE))
            
            # If strong indicators of questions, return quickly
            if question_count >= 3:
                logger.info("Document type detected: CONTAINS_QUESTIONS (heuristic)")
                return DocumentType.CONTAINS_QUESTIONS
            
            # Use AI for more nuanced detection
            prompt = f"""Analyze the following text and determine if it:
1. Contains practice questions/MCQs with options and answers (CONTAINS_QUESTIONS)
2. Contains study notes, explanations, or educational content without questions (STUDY_NOTES)
3. Contains both questions and study notes (MIXED)

Text sample (first 1500 characters):
{text[:1500]}

Respond with ONLY one word: CONTAINS_QUESTIONS, STUDY_NOTES, or MIXED"""
            
            response = self.model.generate_content(prompt)
            result_text = response.text.strip().upper()
            
            if "CONTAINS_QUESTIONS" in result_text:
                logger.info("Document type detected: CONTAINS_QUESTIONS (AI)")
                return DocumentType.CONTAINS_QUESTIONS
            elif "MIXED" in result_text:
                logger.info("Document type detected: MIXED (AI)")
                return DocumentType.MIXED
            else:
                logger.info("Document type detected: STUDY_NOTES (AI)")
                return DocumentType.STUDY_NOTES
                
        except Exception as e:
            logger.error(f"Failed to detect document type: {str(e)}")
            # Default to STUDY_NOTES on error (safer to generate questions)
            return DocumentType.STUDY_NOTES
    
    async def extract_existing_questions(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract questions that already exist in the document
        Preserves original format, options, and explanations
        Returns list of Question dicts
        """
        try:
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
            
            response = self.model.generate_content(prompt)
            
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
            if json_match:
                questions_data = json.loads(json_match.group())
                logger.info(f"Extracted {len(questions_data)} existing questions from document")
                return questions_data
            else:
                logger.warning("No questions found in document")
                return []
                
        except Exception as e:
            logger.error(f"Failed to extract existing questions: {str(e)}")
            return []
    
    async def generate_new_questions(self, text: str, num_questions: int = 15) -> List[Dict[str, Any]]:
        """
        Generate new MCQs from study notes content
        Creates clinically relevant questions for MBBS students
        Returns list of Question dicts
        """
        try:
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
            logger.info(f"Calling Gemini API to generate {num_questions} questions...")
            logger.info(f"Text content preview: {text[:200]}...")
            response = self.model.generate_content(prompt)
            logger.info("Received response from Gemini API")
            
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
            if json_match:
                questions_data = json.loads(json_match.group())
                logger.info(f"Successfully generated {len(questions_data)} new questions from study notes")
                return questions_data[:num_questions]  # Ensure we don't exceed requested number
            else:
                logger.warning("Could not extract JSON from AI response")
                logger.debug(f"AI Response: {response.text[:500]}...")
                return self._generate_fallback_questions(text, num_questions)
                
        except Exception as e:
            logger.error(f"Failed to generate new questions: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            if "API_KEY" in str(e).upper():
                logger.error("API Key issue detected - check GEMINI_API_KEY in .env file")
            return self._generate_fallback_questions(text, num_questions)
    
    async def generate_content_from_batch(self, batch_text: str, document_type: "DocumentType") -> Dict[str, Any]:
        """
        Generate all content types from a single batch
        Returns BatchContent with questions, mnemonics, and cheat sheet points
        """
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
            
            logger.info(f"Generated content from batch: {len(questions)} questions, {len(mnemonics)} mnemonics")
            return batch_content
            
        except Exception as e:
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
        try:
            prompt = f"""Extract 5-7 key points from this medical text that would be useful for a cheat sheet.
Focus on:
- Important definitions
- Critical facts
- Clinical pearls
- High-yield information

Text: {text[:2000]}

Return as a simple list, one point per line."""
            
            response = self.model.generate_content(prompt)
            points = [line.strip() for line in response.text.split('\n') if line.strip() and not line.strip().startswith('#')]
            return points[:7]  # Limit to 7 points
            
        except Exception as e:
            logger.error(f"Failed to extract key points: {str(e)}")
            return []
    
    async def _extract_key_concepts(self, text: str) -> List[str]:
        """Extract key concepts from text"""
        try:
            prompt = f"""Identify 3-5 key medical concepts or terms from this text.
Return only the concept names, one per line.

Text: {text[:1500]}"""
            
            response = self.model.generate_content(prompt)
            concepts = [line.strip() for line in response.text.split('\n') if line.strip()]
            return concepts[:5]  # Limit to 5 concepts
            
        except Exception as e:
            logger.error(f"Failed to extract key concepts: {str(e)}")
            return []
    
    async def analyze_images(self, image_paths: List[str]) -> str:
        """Analyze images directly with AI"""
        try:
            # Load images
            images = []
            for path in image_paths:
                with open(path, 'rb') as f:
                    images.append(f.read())
            
            prompt = """
            Analyze these medical document images and extract all text content.
            Focus on:
            - Medical terminology and concepts
            - Key facts and definitions
            - Clinical information
            - Anatomical details
            - Diagnostic criteria
            - Treatment information
            
            Provide a comprehensive text extraction that maintains the structure and context.
            """
            
            # Use vision model for image analysis
            response = self.vision_model.generate_content([prompt] + images)
            return response.text
            
        except Exception as e:
            logger.error(f"Failed to analyze images with AI: {str(e)}")
            return ""
    
    async def generate_content_from_text(self, text: str) -> Dict[str, Any]:
        """Generate all content types from extracted text"""
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
            
            return {
                "questions": questions,
                "mock_test": mock_test,
                "mnemonics": mnemonics,
                "cheat_sheet": cheat_sheet,
                "notes": notes
            }
            
        except Exception as e:
            logger.error(f"Failed to generate content from text: {str(e)}")
            return {}
    
    async def generate_mock_test_from_questions(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a single mock test from questions"""
        try:
            if not questions or len(questions) < 5:
                return {}
            
            # Create mock test structure
            total_questions = len(questions)
            duration = max(15, min(90, int(total_questions * 1.5)))  # 1.5 minutes per question
            
            mock_test = {
                "name": f"Comprehensive Mock Test ({total_questions} Questions)",
                "questions": [q["question_id"] if "question_id" in q else str(i) for i, q in enumerate(questions)],
                "duration_minutes": duration,
                "total_questions": total_questions,
                "description": f"Mock test based on uploaded PDF content with {total_questions} questions"
            }
            
            return mock_test
            
        except Exception as e:
            logger.error(f"Failed to generate mock test: {str(e)}")
            return {}
    
    async def generate_questions(self, text: str, num_questions: int = 15) -> List[Dict[str, Any]]:
        """
        Generate or extract questions based on document type
        Routes to extract_existing_questions() or generate_new_questions()
        """
        try:
            # First, detect document type
            doc_type = await self.detect_document_type(text)
            
            # Route based on document type
            if doc_type == DocumentType.CONTAINS_QUESTIONS:
                # Extract existing questions
                logger.info("Document contains questions - extracting existing questions")
                questions = await self.extract_existing_questions(text)
                
                # If we got questions, return them
                if questions:
                    return questions
                else:
                    # Fallback to generation if extraction failed
                    logger.warning("Question extraction failed, falling back to generation")
                    return await self.generate_new_questions(text, num_questions)
            
            elif doc_type == DocumentType.MIXED:
                # Extract existing questions and generate additional ones if needed
                logger.info("Document has mixed content - extracting and generating questions")
                existing_questions = await self.extract_existing_questions(text)
                
                if len(existing_questions) >= num_questions:
                    return existing_questions[:num_questions]
                else:
                    # Generate additional questions to reach target
                    additional_needed = num_questions - len(existing_questions)
                    new_questions = await self.generate_new_questions(text, additional_needed)
                    return existing_questions + new_questions
            
            else:  # STUDY_NOTES
                # Generate new questions from study notes
                logger.info("Document is study notes - generating new questions")
                return await self.generate_new_questions(text, num_questions)
                
        except Exception as e:
            logger.error(f"Failed to generate questions: {str(e)}")
            return self._generate_fallback_questions(text, num_questions)
    
    async def generate_mnemonics(self, text: str, num_mnemonics: int = 10) -> List[Dict[str, Any]]:
        """Generate mnemonics from text"""
        try:
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
            
            response = self.model.generate_content(prompt)
            
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
            if json_match:
                mnemonics_data = json.loads(json_match.group())
                return mnemonics_data[:num_mnemonics]
            else:
                return self._generate_fallback_mnemonics(text, num_mnemonics)
                
        except Exception as e:
            logger.error(f"Failed to generate mnemonics: {str(e)}")
            return self._generate_fallback_mnemonics(text, num_mnemonics)
    
    async def generate_cheat_sheets(self, text: str, num_sheets: int = 5) -> List[Dict[str, Any]]:
        """Generate cheat sheets from text"""
        try:
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
            
            response = self.model.generate_content(prompt)
            
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
            if json_match:
                sheets_data = json.loads(json_match.group())
                return sheets_data[:num_sheets]
            else:
                return self._generate_fallback_cheat_sheets(text, num_sheets)
                
        except Exception as e:
            logger.error(f"Failed to generate cheat sheets: {str(e)}")
            return self._generate_fallback_cheat_sheets(text, num_sheets)
    
    async def generate_notes(self, text: str, num_notes: int = 3) -> List[Dict[str, Any]]:
        """Generate compiled notes from text"""
        try:
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
            
            response = self.model.generate_content(prompt)
            
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
            if json_match:
                notes_data = json.loads(json_match.group())
                return notes_data[:num_notes]
            else:
                return self._generate_fallback_notes(text, num_notes)
                
        except Exception as e:
            logger.error(f"Failed to generate notes: {str(e)}")
            return self._generate_fallback_notes(text, num_notes)
    
    def _generate_fallback_questions(self, text: str, num_questions: int) -> List[Dict[str, Any]]:
        """Generate fallback questions when AI fails"""
        logger.warning("Using fallback questions - AI service failed")
        
        # Simple fallback - create basic questions from text
        questions = []
        words = text.split()
        
        for i in range(min(num_questions, 5)):  # Limit fallback questions
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

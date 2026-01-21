"""
File Upload AI Service - Separate from topic-based processing
Handles AI_ONLY mode for uploaded files
"""
import os
import json
import re
import logging
from typing import Dict, Any, List
import google.generativeai as genai
from datetime import datetime

from app.config import settings

logger = logging.getLogger(__name__)

class FileUploadAIService:
    """AI service specifically for processing uploaded files (AI_ONLY mode)"""
    
    def __init__(self):
        """Initialize the file upload AI service"""
        try:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            logger.info("FileUploadAIService initialized with Gemini API")
        except Exception as e:
            logger.error(f"Failed to initialize FileUploadAIService: {e}")
            raise
    
    def _load_prompts(self):
        """Load prompts from files"""
        try:
            prompts_dir = os.path.join(os.path.dirname(__file__), "prompts")
            
            with open(os.path.join(prompts_dir, "file_upload_question_generation.txt"), 'r') as f:
                question_prompt = f.read()
            with open(os.path.join(prompts_dir, "file_upload_mnemonic_generation.txt"), 'r') as f:
                mnemonic_prompt = f.read()
            with open(os.path.join(prompts_dir, "file_upload_content_analysis.txt"), 'r') as f:
                content_prompt = f.read()
                
            logger.info("📋 LOADED FILE UPLOAD PROMPTS FROM FILES")
            return question_prompt, mnemonic_prompt, content_prompt
        except Exception as e:
            logger.warning(f"⚠️ Could not load file upload prompts: {e}")
            return None, None, None
    
    async def generate_content_from_uploaded_files(self, text_content: str, file_names: List[str] = None) -> Dict[str, Any]:
        """Generate all content types from uploaded files (like topic feature but for files)"""
        operation = "GENERATE_CONTENT_FROM_UPLOADED_FILES"
        
        file_info = f" from uploaded files: {', '.join(file_names)}" if file_names else " from uploaded files"
        
        logger.info(f"🤖 GENERATE_CONTENT_FROM_UPLOADED_FILES - STARTING")
        logger.info(f"📁 File names: {file_names}")
        logger.info(f"📝 Content length: {len(text_content)} characters")
        logger.info(f"📄 Content preview (first 300 chars): {text_content[:300]}...")
        
        # Load file upload specific prompts
        question_prompt, mnemonic_prompt, content_prompt = self._load_prompts()
        
        # Create comprehensive prompt for uploaded files
        prompt = f"""You are a medical education expert. Analyze the following study material content{file_info} and generate comprehensive study materials for MBBS students preparing for NEET, AIIMS, JIPMER, and other medical entrance exams.

UPLOADED FILE CONTENT TO ANALYZE:
{text_content[:8000]}...

Based on the uploaded file content above, generate the following study materials in JSON format:

{{
    "questions": [
        {{
            "question": "MCQ question based on uploaded file content",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": 0,
            "explanation": "Detailed explanation referencing the uploaded material",
            "difficulty": "easy|medium|hard"
        }}
    ],
    "mnemonics": [
        {{
            "topic": "Medical concept from uploaded files",
            "mnemonic": "Indian-specific mnemonic using cultural references",
            "explanation": "How this helps remember the uploaded content",
            "key_terms": ["term1 from files", "term2 from files"]
        }}
    ],
    "cheat_sheet": {{
        "title": "Cheat Sheet: [Main Topic from Uploaded Files]",
        "key_points": ["Key point 1 from uploaded material", "Key point 2 from files"],
        "high_yield_facts": ["High-yield fact 1 from uploaded content", "High-yield fact 2"],
        "quick_references": {{"Term from content": "Definition from uploaded material"}}
    }},
    "notes": {{
        "title": "Study Notes: [Main Topic from Uploaded Files]",
        "content": "Comprehensive summary of the uploaded material with key concepts and clinical correlations from the files...",
        "summary_points": ["Summary point 1 from uploaded content", "Summary point 2"]
    }}
}}

CRITICAL REQUIREMENTS FOR UPLOADED FILES:

FOR QUESTIONS (Generate 10-15):
- Base ALL questions on content actually present in the uploaded files
- Create clear question stems from the uploaded material
- Use 4 options with plausible distractors based on the file content
- Include detailed explanations referencing the uploaded material
- Classify difficulty: Easy (40%), Medium (45%), Hard (15%)
- Focus on application of concepts from the uploaded files
- Do NOT add external information not in the uploaded content

FOR MNEMONICS (Generate 5-7):
- Extract key concepts and terms from the uploaded files only
- Use Indian cultural references: names (Raj, Priya, Amit), cities (Mumbai, Delhi), foods (Dal, Rice), festivals (Diwali, Holi)
- Create memorable memory aids for information in the uploaded content
- Base all mnemonics on concepts actually present in the uploaded files

FOR CHEAT SHEET:
- Extract 8-10 key points directly from the uploaded material
- Include high-yield facts found in the uploaded content
- Create quick references from definitions in the uploaded files
- Organize based on the structure of the uploaded material

FOR NOTES:
- Summarize the uploaded material comprehensively
- Include main topics and subtopics from the uploaded files
- Add clinical correlations mentioned in the uploaded content
- Structure for exam preparation based on the uploaded material

ABSOLUTE REQUIREMENT: All generated content must be directly based on and relevant to the uploaded file material. Do not add external medical knowledge not present in the uploaded files. Focus only on information actually contained in the provided file content."""

        logger.info(f"📤 SENDING COMPREHENSIVE PROMPT TO AI MODEL:")
        logger.info(f"   - Prompt length: {len(prompt)} characters")
        logger.info(f"   - Content being analyzed: {len(text_content)} characters from files: {file_names}")

        try:
            logger.info(f"🔄 Generating comprehensive content from uploaded files: {file_names}")
            logger.info(f"📡 Calling Gemini API with uploaded file content...")
            
            # Add timeout to prevent hanging
            import asyncio
            import concurrent.futures
            
            def generate_with_timeout():
                return self.model.generate_content(prompt)
            
            # Run with timeout
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(generate_with_timeout)
                try:
                    response = future.result(timeout=45.0)  # 45 second timeout
                    response_text = response.text
                except concurrent.futures.TimeoutError:
                    logger.error(f"❌ GEMINI API TIMEOUT after 45 seconds")
                    raise Exception("AI processing timeout - please try again with a smaller file")
            
            logger.info(f"📥 RECEIVED AI RESPONSE:")
            logger.info(f"   - Response length: {len(response_text)} characters")
            logger.info(f"   - Response preview (first 500 chars): {response_text[:500]}...")
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                content = json.loads(json_match.group())
                logger.info(f"✅ SUCCESSFULLY PARSED JSON RESPONSE FROM UPLOADED FILES")
                logger.info(f"📊 Generated content from uploaded files:")
                logger.info(f"   - Questions: {len(content.get('questions', []))}")
                logger.info(f"   - Mnemonics: {len(content.get('mnemonics', []))}")
                logger.info(f"   - Cheat sheet: {'✅' if content.get('cheat_sheet') else '❌'}")
                logger.info(f"   - Notes: {'✅' if content.get('notes') else '❌'}")
                return content
            else:
                logger.warning(f"⚠️ Could not extract JSON from uploaded files response")
                logger.warning(f"Raw response: {response_text}")
                return self._generate_fallback_content()
                
        except Exception as e:
            logger.error(f"❌ Failed to generate content from uploaded files: {str(e)}")
            return self._generate_fallback_content()
    
    def _generate_fallback_content(self) -> Dict[str, Any]:
        """Generate fallback content when AI fails for uploaded files"""
        logger.warning("Using fallback content for uploaded file processing")
        return {
            "questions": [
                {
                    "question": "⚠️ What should you do when file processing fails? (AI service issue)",
                    "options": ["Check API key", "Verify file format", "Try again later", "Contact support"],
                    "correct_answer": 0,
                    "explanation": "AI service encountered an error while processing your uploaded files. Please check your configuration.",
                    "difficulty": "medium"
                }
            ],
            "mnemonics": [
                {
                    "topic": "File Processing Error",
                    "mnemonic": "AI service unavailable",
                    "explanation": "Please check GEMINI_API_KEY configuration",
                    "key_terms": ["API", "configuration", "files"]
                }
            ],
            "cheat_sheet": {
                "title": "Cheat Sheet: File Processing Error",
                "key_points": ["AI service unavailable - check configuration", "Verify uploaded file formats"],
                "high_yield_facts": ["Please verify GEMINI_API_KEY in .env file", "Supported formats: PDF, images"],
                "quick_references": {"Status": "Error - AI unavailable", "Action": "Check configuration"}
            },
            "notes": {
                "title": "Study Notes: File Processing Error",
                "content": "AI service encountered an error while processing your uploaded files. Please check your GEMINI_API_KEY configuration in the .env file and ensure your files are in supported formats.",
                "summary_points": ["Check API configuration", "Verify file formats", "Restart backend service"]
            }
        }

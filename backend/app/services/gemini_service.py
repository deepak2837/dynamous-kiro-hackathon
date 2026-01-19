"""
Gemini AI Service for StudyBuddy
Handles content generation, analysis, and AI-powered features
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from app.config import settings

logger = logging.getLogger(__name__)

class GeminiService:
    """Service for interacting with Google Gemini AI"""
    
    def __init__(self):
        """Initialize Gemini service with API key and configuration"""
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Safety settings for medical content
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        }
        
        # Initialize models
        self.model = genai.GenerativeModel(
            'gemini-2.5-flash',
            safety_settings=self.safety_settings
        )
        
        # Load system prompts
        self.prompts = self._load_prompts()
        
        logger.info("Gemini service initialized successfully")
    
    def _load_prompts(self) -> Dict[str, str]:
        """Load system prompts from files"""
        prompts = {}
        prompts_dir = Path("prompts")
        
        if not prompts_dir.exists():
            logger.warning("Prompts directory not found")
            return prompts
        
        for prompt_file in prompts_dir.glob("*.txt"):
            try:
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    prompt_name = prompt_file.stem
                    prompts[prompt_name] = f.read().strip()
                    logger.debug(f"Loaded prompt: {prompt_name}")
            except Exception as e:
                logger.error(f"Error loading prompt {prompt_file}: {e}")
        
        return prompts
    
    async def analyze_content(self, content: str, content_type: str = "text") -> Dict[str, Any]:
        """Analyze uploaded content and extract key information"""
        try:
            prompt = self.prompts.get('content_analysis', '')
            if not prompt:
                prompt = "Analyze this content and extract key educational information suitable for medical students."
            
            full_prompt = f"{prompt}\n\nContent to analyze:\n{content}"
            
            response = self.model.generate_content(full_prompt)
            
            return {
                "success": True,
                "analysis": response.text,
                "content_type": content_type
            }
            
        except Exception as e:
            logger.error(f"Content analysis failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_questions(self, content: str, num_questions: int = 5, difficulty: str = "mixed") -> List[Dict[str, Any]]:
        """Generate MCQs from content"""
        try:
            prompt = self.prompts.get('question_generation', '')
            if not prompt:
                prompt = "Generate medical MCQs from the given content."
            
            full_prompt = f"""{prompt}

Content: {content}

Generate {num_questions} questions with difficulty level: {difficulty}

Return the response as a JSON array of questions, each with:
- question_text
- options (array of 4 options)
- correct_answer (index 0-3)
- explanation
- difficulty
- topic
- subtopic
"""
            
            response = self.model.generate_content(full_prompt)
            
            # Try to parse JSON response
            try:
                questions = json.loads(response.text)
                if isinstance(questions, list):
                    return questions
                else:
                    # If not a list, wrap in array
                    return [questions]
            except json.JSONDecodeError:
                # If JSON parsing fails, return structured response
                return [{
                    "question_text": "Generated question (parsing error)",
                    "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
                    "correct_answer": 0,
                    "explanation": response.text,
                    "difficulty": difficulty,
                    "topic": "General",
                    "subtopic": "Content Analysis"
                }]
            
        except Exception as e:
            logger.error(f"Question generation failed: {e}")
            return []
    
    async def generate_mnemonics(self, concept: str, context: str = "") -> Dict[str, Any]:
        """Generate memory aids and mnemonics"""
        try:
            prompt = self.prompts.get('mnemonic_generation', '')
            if not prompt:
                prompt = "Create memorable mnemonics for medical concepts with Indian cultural context."
            
            full_prompt = f"""{prompt}

Concept: {concept}
Context: {context}

Generate a mnemonic that helps Indian medical students remember this concept.
Return as JSON with: concept, mnemonic_type, mnemonic_text, explanation, cultural_context, difficulty, subject
"""
            
            response = self.model.generate_content(full_prompt)
            
            try:
                mnemonic = json.loads(response.text)
                return {
                    "success": True,
                    "mnemonic": mnemonic
                }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "mnemonic": {
                        "concept": concept,
                        "mnemonic_type": "text",
                        "mnemonic_text": response.text,
                        "explanation": "Generated mnemonic",
                        "cultural_context": "Indian medical education",
                        "difficulty": "medium",
                        "subject": "Medical"
                    }
                }
            
        except Exception as e:
            logger.error(f"Mnemonic generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_cheat_sheet(self, content: str, topic: str) -> Dict[str, Any]:
        """Create concise cheat sheets from content"""
        try:
            prompt = f"""Create a comprehensive cheat sheet for medical students on the topic: {topic}

Content: {content}

Format the cheat sheet with:
1. Key Points (bullet points)
2. Important Definitions
3. Clinical Correlations
4. Memory Aids
5. High-Yield Facts

Make it concise but comprehensive for exam preparation."""
            
            response = self.model.generate_content(prompt)
            
            return {
                "success": True,
                "cheat_sheet": response.text,
                "topic": topic
            }
            
        except Exception as e:
            logger.error(f"Cheat sheet creation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_notes(self, content: str, style: str = "structured") -> Dict[str, Any]:
        """Generate structured notes from content"""
        try:
            prompt = f"""Convert the following content into well-structured study notes for medical students.

Style: {style}
Content: {content}

Create notes with:
- Clear headings and subheadings
- Key concepts highlighted
- Clinical relevance noted
- Easy to review format
- Suitable for medical exam preparation
"""
            
            response = self.model.generate_content(prompt)
            
            return {
                "success": True,
                "notes": response.text,
                "style": style
            }
            
        except Exception as e:
            logger.error(f"Notes generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_mock_test(self, content: str, num_questions: int = 10, time_limit: int = 30) -> Dict[str, Any]:
        """Create a complete mock test"""
        try:
            questions = await self.generate_questions(content, num_questions, "mixed")
            
            if not questions:
                return {
                    "success": False,
                    "error": "Failed to generate questions for mock test"
                }
            
            mock_test = {
                "test_name": f"Mock Test - {num_questions} Questions",
                "time_limit_minutes": time_limit,
                "total_questions": len(questions),
                "questions": questions,
                "instructions": [
                    "Read each question carefully",
                    "Select the best answer from the given options",
                    "Manage your time effectively",
                    "Review your answers before submitting"
                ]
            }
            
            return {
                "success": True,
                "mock_test": mock_test
            }
            
        except Exception as e:
            logger.error(f"Mock test creation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test Gemini API connection"""
        try:
            response = self.model.generate_content("Hello! Please respond with 'Gemini connection successful!'")
            return {
                "success": True,
                "message": response.text,
                "model": "gemini-2.5-flash"
            }
        except Exception as e:
            logger.error(f"Gemini connection test failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Global instance
gemini_service = None

def get_gemini_service() -> GeminiService:
    """Get or create Gemini service instance"""
    global gemini_service
    if gemini_service is None:
        gemini_service = GeminiService()
    return gemini_service

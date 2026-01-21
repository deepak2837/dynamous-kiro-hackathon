"""
Gemini AI Service for StudyBuddy
Handles content generation, analysis, and AI-powered features
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from app.config import settings

logger = logging.getLogger(__name__)

# Global instance
_gemini_service = None

def get_gemini_service():
    """Get or create GeminiService instance"""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service

class GeminiService:
    """Service for interacting with Google Gemini AI"""
    
    def __init__(self):
        """Initialize Gemini service with API key and configuration"""
        self.api_key = settings.google_ai_api_key
        self.prompts = self._load_prompts()
        
        if self.api_key and self.api_key != "your_api_key_here":
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.is_configured = True
            logger.info("GeminiService initialized successfully")
        else:
            self.model = None
            self.is_configured = False
            logger.warning("GeminiService not configured - missing API key")
    
    def _load_prompts(self) -> Dict[str, str]:
        """Load system prompts from files"""
        return {
            'question_generation': 'Generate medical MCQs from content',
            'mnemonic_generation': 'Create memorable mnemonics for medical concepts',
            'cheat_sheet_generation': 'Create concise cheat sheets for medical topics',
            'notes_generation': 'Generate structured study notes'
        }
    
    def _log_ai_request(self, operation: str, prompt: str, additional_info: Dict[str, Any] = None):
        """Log AI request details"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": "GeminiService",
            "operation": operation,
            "prompt_length": len(prompt),
            "prompt_preview": prompt[:500] + "..." if len(prompt) > 500 else prompt,
        }
        if additional_info:
            log_entry.update(additional_info)
        
        logger.info(f"=== GEMINI REQUEST: {operation} ===")
        logger.info(f"Timestamp: {log_entry['timestamp']}")
        logger.info(f"Prompt Length: {log_entry['prompt_length']} characters")
        logger.info(f"Prompt Preview:\n{log_entry['prompt_preview']}")
        if additional_info:
            logger.info(f"Additional Info: {json.dumps(additional_info, indent=2)}")
        logger.info(f"=== END GEMINI REQUEST ===")
        
        return log_entry
    
    def _log_ai_response(self, operation: str, response_text: str, success: bool, additional_info: Dict[str, Any] = None):
        """Log AI response details"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": "GeminiService",
            "operation": operation,
            "success": success,
            "response_length": len(response_text) if response_text else 0,
            "response_preview": (response_text[:1000] + "..." if len(response_text) > 1000 else response_text) if response_text else "No response",
        }
        if additional_info:
            log_entry.update(additional_info)
        
        logger.info(f"=== GEMINI RESPONSE: {operation} ===")
        logger.info(f"Timestamp: {log_entry['timestamp']}")
        logger.info(f"Success: {log_entry['success']}")
        logger.info(f"Response Length: {log_entry['response_length']} characters")
        logger.info(f"Response Preview:\n{log_entry['response_preview']}")
        if additional_info:
            logger.info(f"Additional Info: {json.dumps(additional_info, indent=2)}")
        logger.info(f"=== END GEMINI RESPONSE ===")
        
        return log_entry

    async def analyze_content(self, content: str, content_type: str = "text") -> Dict[str, Any]:
        """Analyze uploaded content and extract key information"""
        operation = "ANALYZE_CONTENT"
        
        prompt = f"""Analyze the following {content_type} content and provide:
1. Main topics covered
2. Key concepts
3. Difficulty level
4. Suggested study approach

Content: {content[:3000]}"""

        self._log_ai_request(operation, prompt, {"content_type": content_type, "content_length": len(content)})

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            self._log_ai_response(operation, response_text, True, {"content_type": content_type})
            
            return {
                "success": True,
                "analysis": response_text,
                "content_type": content_type
            }
        except Exception as e:
            self._log_ai_response(operation, str(e), False, {"error": str(e)})
            logger.error(f"Content analysis failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def generate_questions(self, content: str, num_questions: int = 5, difficulty: str = "mixed") -> List[Dict[str, Any]]:
        """Generate MCQs from content"""
        operation = "GENERATE_QUESTIONS"
        
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

        self._log_ai_request(operation, full_prompt, {
            "num_questions": num_questions,
            "difficulty": difficulty,
            "content_length": len(content)
        })

        try:
            response = self.model.generate_content(full_prompt)
            response_text = response.text
            
            self._log_ai_response(operation, response_text, True, {
                "num_questions_requested": num_questions,
                "difficulty": difficulty
            })
            
            # Try to parse JSON response
            try:
                questions = json.loads(response_text)
                if isinstance(questions, list):
                    return questions
                else:
                    return [questions]
            except json.JSONDecodeError:
                logger.warning("Could not parse questions as JSON, returning raw response")
                return [{
                    "question_text": response_text,
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": 0,
                    "explanation": "Raw response from AI",
                    "difficulty": difficulty,
                    "topic": "Generated",
                    "subtopic": "Auto-generated"
                }]
                
        except Exception as e:
            self._log_ai_response(operation, str(e), False, {"error": str(e)})
            logger.error(f"Question generation failed: {e}")
            return []

    async def generate_mnemonics(self, concept: str, context: str = "") -> Dict[str, Any]:
        """Generate memory aids and mnemonics"""
        operation = "GENERATE_MNEMONICS"
        
        prompt = self.prompts.get('mnemonic_generation', '')
        if not prompt:
            prompt = "Create memorable mnemonics for medical concepts with Indian cultural context."
        
        full_prompt = f"""{prompt}

Concept: {concept}
Context: {context}

Generate a mnemonic that helps Indian medical students remember this concept.
Return as JSON with: concept, mnemonic_type, mnemonic_text, explanation, cultural_context, difficulty, subject
"""

        self._log_ai_request(operation, full_prompt, {
            "concept": concept,
            "context": context
        })

        try:
            response = self.model.generate_content(full_prompt)
            response_text = response.text
            
            self._log_ai_response(operation, response_text, True, {"concept": concept})
            
            try:
                mnemonic = json.loads(response_text)
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
                        "mnemonic_text": response_text,
                        "explanation": "Generated mnemonic",
                        "cultural_context": "Indian medical education",
                        "difficulty": "medium",
                        "subject": "Medical"
                    }
                }
            
        except Exception as e:
            self._log_ai_response(operation, str(e), False, {"error": str(e)})
            logger.error(f"Mnemonic generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def create_cheat_sheet(self, content: str, topic: str) -> Dict[str, Any]:
        """Create concise cheat sheets from content"""
        operation = "CREATE_CHEAT_SHEET"
        
        full_prompt = f"""Create a comprehensive cheat sheet for medical students on the topic: {topic}

Content: {content}

Format the cheat sheet with:
1. Key Points (bullet points)
2. Important Definitions
3. Clinical Correlations
4. Memory Aids
5. High-Yield Facts

Make it concise but comprehensive for exam preparation."""

        self._log_ai_request(operation, full_prompt, {
            "topic": topic,
            "content_length": len(content)
        })

        try:
            response = self.model.generate_content(full_prompt)
            response_text = response.text
            
            self._log_ai_response(operation, response_text, True, {"topic": topic})
            
            return {
                "success": True,
                "cheat_sheet": response_text,
                "topic": topic
            }
            
        except Exception as e:
            self._log_ai_response(operation, str(e), False, {"error": str(e)})
            logger.error(f"Cheat sheet creation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def generate_notes(self, content: str, style: str = "structured") -> Dict[str, Any]:
        """Generate structured notes from content"""
        operation = "GENERATE_NOTES"
        
        full_prompt = f"""Convert the following content into well-structured study notes for medical students.

Style: {style}
Content: {content}

Create notes with:
- Clear headings and subheadings
- Key concepts highlighted
- Clinical relevance noted
- Easy to review format
- Suitable for medical exam preparation
"""

        self._log_ai_request(operation, full_prompt, {
            "style": style,
            "content_length": len(content)
        })

        try:
            response = self.model.generate_content(full_prompt)
            response_text = response.text
            
            self._log_ai_response(operation, response_text, True, {"style": style})
            
            return {
                "success": True,
                "notes": response_text,
                "style": style
            }
            
        except Exception as e:
            self._log_ai_response(operation, str(e), False, {"error": str(e)})
            logger.error(f"Notes generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def create_mock_test(self, content: str, num_questions: int = 10, time_limit: int = 30) -> Dict[str, Any]:
        """Create a complete mock test"""
        operation = "CREATE_MOCK_TEST"
        
        self._log_ai_request(operation, f"Creating mock test with {num_questions} questions", {
            "num_questions": num_questions,
            "time_limit": time_limit,
            "content_length": len(content)
        })
        
        try:
            questions = await self.generate_questions(content, num_questions, "mixed")
            
            if not questions:
                self._log_ai_response(operation, "Failed to generate questions", False)
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
            
            self._log_ai_response(operation, "Mock test created successfully", True, {
                "test_name": mock_test["test_name"],
                "total_questions": len(questions),
                "time_limit": time_limit
            })
            
            return {
                "success": True,
                "mock_test": mock_test
            }
            
        except Exception as e:
            self._log_ai_response(operation, str(e), False, {"error": str(e)})
            logger.error(f"Mock test creation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def test_connection(self) -> Dict[str, Any]:
        """Test Gemini API connection"""
        operation = "TEST_CONNECTION"
        
        if not self.is_configured:
            self._log_ai_response(operation, "Service not configured", False)
            return {
                "success": False,
                "error": "Gemini service not configured - missing API key"
            }
        
        test_prompt = "Say 'Hello, StudyBuddy!' to confirm the connection is working."
        
        self._log_ai_request(operation, test_prompt)
        
        try:
            response = self.model.generate_content(test_prompt)
            response_text = response.text
            
            self._log_ai_response(operation, response_text, True)
            
            return {
                "success": True,
                "message": "Gemini API connection successful",
                "response": response_text
            }
        except Exception as e:
            self._log_ai_response(operation, str(e), False, {"error": str(e)})
            return {
                "success": False,
                "error": str(e)
            }

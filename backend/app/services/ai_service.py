import logging
import json
import re
from typing import List, Dict, Any
import google.generativeai as genai
from app.config import settings

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        # Configure Google GenAI
        genai.configure(api_key=settings.google_ai_api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def generate_questions(self, text: str, num_questions: int = 20) -> List[Dict[str, Any]]:
        """Generate MCQ questions from text"""
        try:
            prompt = f"""
            Based on the following medical study material, generate {num_questions} multiple choice questions (MCQs) suitable for MBBS students.

            Text: {text[:4000]}  # Limit text to avoid token limits

            For each question, provide:
            1. Question text
            2. Four options (A, B, C, D)
            3. Correct answer (0-3 index)
            4. Detailed explanation
            5. Difficulty level (easy/medium/hard)
            6. Medical topic/subject

            Format as JSON array:
            [
                {{
                    "question": "Question text here?",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": 0,
                    "explanation": "Detailed explanation here",
                    "difficulty": "medium",
                    "topic": "Anatomy"
                }}
            ]

            Focus on:
            - High-yield medical facts
            - Clinical correlations
            - Exam-relevant content
            - Clear, unambiguous questions
            - Plausible distractors
            """
            
            response = self.model.generate_content(prompt)
            
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
            if json_match:
                questions_data = json.loads(json_match.group())
                return questions_data[:num_questions]  # Ensure we don't exceed requested number
            else:
                logger.warning("Could not extract JSON from AI response")
                return self._generate_fallback_questions(text, num_questions)
                
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
        # Simple fallback - create basic questions from text
        questions = []
        words = text.split()
        
        for i in range(min(num_questions, 5)):  # Limit fallback questions
            questions.append({
                "question": f"What is the main concept discussed in section {i+1}?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": 0,
                "explanation": "This is a fallback question generated when AI processing failed.",
                "difficulty": "medium",
                "topic": "General"
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

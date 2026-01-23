"""
Export service for generating PDF downloads of study materials.
"""
import os
import tempfile
from typing import List, Optional
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

from app.models import Question, Note, CheatSheet, Mnemonic
from app.database import get_database


class ExportService:
    def __init__(self):
        self.db = get_database()
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom styles for medical content."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=HexColor('#ec4899'),  # Pink color
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=HexColor('#be185d'),  # Darker pink
            spaceAfter=20,
            spaceBefore=20
        ))
        
        # Medical content style
        self.styles.add(ParagraphStyle(
            name='MedicalContent',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=14,
            spaceAfter=12,
            alignment=TA_JUSTIFY
        ))
        
        # Highlight style for important content
        self.styles.add(ParagraphStyle(
            name='Highlight',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=HexColor('#be185d'),
            fontName='Helvetica-Bold',
            spaceAfter=10
        ))

    async def generate_questions_pdf(self, session_id: str) -> str:
        """Generate PDF for questions."""
        try:
            # Fetch questions from database
            questions_cursor = self.db.questions.find({"session_id": session_id})
            questions = await questions_cursor.to_list(length=None)
            
            if not questions:
                raise ValueError("No questions found for this session")
            
            print(f"Found {len(questions)} questions for session {session_id}")
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_file.close()
            
            # Create PDF
            doc = SimpleDocTemplate(temp_file.name, pagesize=A4)
            story = []
            
            # Title
            story.append(Paragraph("Medical Questions Bank", self.styles['CustomTitle']))
            story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", self.styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Questions
            for i, question in enumerate(questions, 1):
                # Question number and text
                story.append(Paragraph(f"<b>Question {i}:</b> {question.get('question_text', '')}", self.styles['MedicalContent']))
                
                # Options
                options = question.get('options', [])
                correct_answer_index = question.get('correct_answer', 0)
                
                for j, option in enumerate(options):
                    option_letter = chr(65 + j)  # A, B, C, D
                    is_correct = j == correct_answer_index
                    option_style = 'Highlight' if is_correct else 'Normal'
                    story.append(Paragraph(f"{option_letter}. {option}", self.styles[option_style]))
                
                # Explanation
                if question.get('explanation'):
                    story.append(Paragraph("<b>Explanation:</b>", self.styles['Highlight']))
                    story.append(Paragraph(question['explanation'], self.styles['MedicalContent']))
                
                # Difficulty and subject
                difficulty = question.get('difficulty', 'Medium')
                subject = question.get('topic', 'General')
                story.append(Paragraph(f"<b>Difficulty:</b> {difficulty} | <b>Subject:</b> {subject}", self.styles['Normal']))
                
                story.append(Spacer(1, 20))
            
            # Build PDF
            doc.build(story)
            print(f"Successfully generated questions PDF: {temp_file.name}")
            return temp_file.name
            
        except Exception as e:
            print(f"Error generating questions PDF: {str(e)}")
            raise

    async def generate_notes_pdf(self, session_id: str) -> str:
        """Generate PDF for notes."""
        try:
            # Fetch notes from database
            notes_cursor = self.db.notes.find({"session_id": session_id})
            notes = await notes_cursor.to_list(length=None)
            
            if not notes:
                raise ValueError("No notes found for this session")
            
            print(f"Found {len(notes)} notes for session {session_id}")
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_file.close()
            
            # Create PDF
            doc = SimpleDocTemplate(temp_file.name, pagesize=A4)
            story = []
            
            # Title
            story.append(Paragraph("Study Notes", self.styles['CustomTitle']))
            story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", self.styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Notes content
            for note in notes:
                story.append(Paragraph(note.get('title', 'Untitled Note'), self.styles['CustomSubtitle']))
                
                # Main content
                content = note.get('content', '')
                # Simple markdown-like formatting to HTML conversion
                lines = content.split('\n')
                for line in lines:
                    if line.strip():
                        # Convert basic markdown formatting
                        line = line.replace('**', '<b>').replace('**', '</b>')
                        line = line.replace('*', '<i>').replace('*', '</i>')
                        story.append(Paragraph(line, self.styles['MedicalContent']))
                    else:
                        story.append(Spacer(1, 6))
                
                # Summary points
                summary_points = note.get('summary_points', [])
                if summary_points:
                    story.append(Paragraph("<b>Key Summary Points:</b>", self.styles['Highlight']))
                    for point in summary_points:
                        story.append(Paragraph(f"• {point}", self.styles['MedicalContent']))
                
                story.append(Spacer(1, 30))
            
            # Build PDF
            doc.build(story)
            print(f"Successfully generated notes PDF: {temp_file.name}")
            return temp_file.name
            
        except Exception as e:
            print(f"Error generating notes PDF: {str(e)}")
            raise

    async def generate_cheatsheet_pdf(self, session_id: str) -> str:
        """Generate PDF for cheat sheets."""
        # Fetch cheat sheets from database
        sheets_cursor = self.db.cheat_sheets.find({"session_id": session_id})
        sheets = await sheets_cursor.to_list(length=None)
        
        if not sheets:
            raise ValueError("No cheat sheets found for this session")
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_file.close()
        
        # Create PDF
        doc = SimpleDocTemplate(temp_file.name, pagesize=A4)
        story = []
        
        # Title
        story.append(Paragraph("Medical Cheat Sheets", self.styles['CustomTitle']))
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Cheat sheets content
        for sheet in sheets:
            story.append(Paragraph(sheet.get('title', 'Untitled Sheet'), self.styles['CustomSubtitle']))
            
            # Key points
            key_points = sheet.get('key_points', [])
            if key_points:
                story.append(Paragraph("<b>Key Points:</b>", self.styles['Highlight']))
                for point in key_points:
                    story.append(Paragraph(f"• {point}", self.styles['MedicalContent']))
                story.append(Spacer(1, 15))
            
            # High-yield facts
            high_yield_facts = sheet.get('high_yield_facts', [])
            if high_yield_facts:
                story.append(Paragraph("<b>High-Yield Facts:</b>", self.styles['Highlight']))
                for fact in high_yield_facts:
                    story.append(Paragraph(f"⭐ {fact}", self.styles['MedicalContent']))
                story.append(Spacer(1, 15))
            
            # Quick references
            quick_refs = sheet.get('quick_references', {})
            if quick_refs:
                story.append(Paragraph("<b>Quick References:</b>", self.styles['Highlight']))
                for term, definition in quick_refs.items():
                    story.append(Paragraph(f"<b>{term}:</b> {definition}", self.styles['MedicalContent']))
            
            story.append(Spacer(1, 30))
        
        # Build PDF
        doc.build(story)
        return temp_file.name

    async def generate_mnemonics_pdf(self, session_id: str) -> str:
        """Generate PDF for mnemonics."""
        # Fetch mnemonics from database
        mnemonics_cursor = self.db.mnemonics.find({"session_id": session_id})
        mnemonics = await mnemonics_cursor.to_list(length=None)
        
        if not mnemonics:
            raise ValueError("No mnemonics found for this session")
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_file.close()
        
        # Create PDF
        doc = SimpleDocTemplate(temp_file.name, pagesize=A4)
        story = []
        
        # Title
        story.append(Paragraph("Medical Mnemonics", self.styles['CustomTitle']))
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Mnemonics content
        for mnemonic in mnemonics:
            topic = mnemonic.get('topic', 'Untitled Topic')
            story.append(Paragraph(topic, self.styles['CustomSubtitle']))
            
            # Mnemonic text (highlighted)
            mnemonic_text = mnemonic.get('mnemonic_text', '')
            story.append(Paragraph(f'"{mnemonic_text}"', self.styles['Highlight']))
            
            # Explanation
            explanation = mnemonic.get('explanation', '')
            if explanation:
                story.append(Paragraph(explanation, self.styles['MedicalContent']))
            
            # Key terms
            key_terms = mnemonic.get('key_terms', [])
            if key_terms:
                story.append(Paragraph("<b>Key Terms:</b> " + ", ".join(key_terms), self.styles['Normal']))
            
            # India-specific indicator
            if mnemonic.get('is_india_specific', False):
                story.append(Paragraph("🇮🇳 <i>India-specific content</i>", self.styles['Normal']))
            
            story.append(Spacer(1, 25))
        
        # Build PDF
        doc.build(story)
        return temp_file.name

    def cleanup_temp_file(self, file_path: str):
        """Clean up temporary PDF file."""
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error cleaning up temp file {file_path}: {e}")

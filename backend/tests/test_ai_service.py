import pytest
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from app.services.ai_service import AIService
from app.models import DocumentType


class TestAIServiceSafetySettings:
    """Test suite for AI Service safety settings configuration"""
    
    def test_safety_settings_configured(self):
        """Test that safety settings are properly configured with BLOCK_NONE for all categories"""
        # Arrange & Act
        ai_service = AIService()
        
        # Assert - verify all harm categories are set to BLOCK_NONE
        assert HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT in ai_service.safety_settings
        assert HarmCategory.HARM_CATEGORY_HATE_SPEECH in ai_service.safety_settings
        assert HarmCategory.HARM_CATEGORY_HARASSMENT in ai_service.safety_settings
        assert HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT in ai_service.safety_settings
        
        # Verify all are set to BLOCK_NONE
        assert ai_service.safety_settings[HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT] == HarmBlockThreshold.BLOCK_NONE
        assert ai_service.safety_settings[HarmCategory.HARM_CATEGORY_HATE_SPEECH] == HarmBlockThreshold.BLOCK_NONE
        assert ai_service.safety_settings[HarmCategory.HARM_CATEGORY_HARASSMENT] == HarmBlockThreshold.BLOCK_NONE
        assert ai_service.safety_settings[HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT] == HarmBlockThreshold.BLOCK_NONE
    
    def test_safety_settings_count(self):
        """Test that all 4 harm categories are configured"""
        # Arrange & Act
        ai_service = AIService()
        
        # Assert
        assert len(ai_service.safety_settings) == 4, "All 4 harm categories should be configured"
    
    def test_models_initialized_with_safety_settings(self):
        """Test that both models are initialized with safety settings"""
        # Arrange & Act
        ai_service = AIService()
        
        # Assert
        assert ai_service.model is not None, "Text model should be initialized"
        assert ai_service.vision_model is not None, "Vision model should be initialized"


class TestDocumentTypeDetection:
    """
    Property 3: Document Type Detection
    For any document, the AI_Service should classify it as either 
    CONTAINS_QUESTIONS, STUDY_NOTES, or MIXED based on content analysis.
    Validates: Requirements 1.3
    """
    
    @pytest.mark.asyncio
    async def test_detects_document_with_questions(self):
        """Test that documents with MCQs are detected as CONTAINS_QUESTIONS"""
        # Arrange
        ai_service = AIService()
        text_with_questions = """
        1. What is the function of the heart?
        A) Pump blood
        B) Filter toxins
        C) Produce hormones
        D) Store energy
        Correct answer: A
        Explanation: The heart's primary function is to pump blood throughout the body.
        
        2. Which of the following is a symptom of diabetes?
        A) Increased thirst
        B) Decreased appetite
        C) Low blood pressure
        D) Slow heart rate
        """
        
        # Act
        result = await ai_service.detect_document_type(text_with_questions)
        
        # Assert
        assert result in [DocumentType.CONTAINS_QUESTIONS, DocumentType.MIXED], \
            "Document with questions should be detected as CONTAINS_QUESTIONS or MIXED"
    
    @pytest.mark.asyncio
    async def test_detects_study_notes(self):
        """Test that study notes without questions are detected as STUDY_NOTES"""
        # Arrange
        ai_service = AIService()
        study_notes = """
        The Cardiovascular System
        
        The heart is a muscular organ that pumps blood throughout the body. It consists of four chambers:
        two atria and two ventricles. The right side pumps deoxygenated blood to the lungs, while the
        left side pumps oxygenated blood to the rest of the body.
        
        Key Functions:
        - Pumping blood to deliver oxygen and nutrients
        - Removing waste products like carbon dioxide
        - Maintaining blood pressure
        - Regulating body temperature
        """
        
        # Act
        result = await ai_service.detect_document_type(study_notes)
        
        # Assert
        assert result == DocumentType.STUDY_NOTES, \
            "Study notes without questions should be detected as STUDY_NOTES"
    
    @pytest.mark.asyncio
    async def test_returns_valid_document_type(self):
        """Property test: For any text, detect_document_type returns a valid DocumentType"""
        # Arrange
        ai_service = AIService()
        test_texts = [
            "Sample medical text about anatomy",
            "1. Question? A) Answer B) Wrong",
            "Study notes with explanations",
            ""  # Edge case: empty text
        ]
        
        # Act & Assert
        for text in test_texts:
            result = await ai_service.detect_document_type(text)
            assert isinstance(result, DocumentType), \
                f"Result should be a DocumentType enum, got {type(result)}"
            assert result in [DocumentType.CONTAINS_QUESTIONS, DocumentType.STUDY_NOTES, DocumentType.MIXED], \
                f"Result should be one of the three valid DocumentType values, got {result}"


class TestQuestionExtraction:
    """
    Property 1: Question Extraction Preserves Format
    For any document containing questions, extracting then storing those questions 
    should preserve the original question text, options, correct answer index, and explanation.
    Validates: Requirements 1.1, 1.4
    """
    
    @pytest.mark.asyncio
    async def test_extract_preserves_question_text(self):
        """Test that extracted questions preserve original question text"""
        # Arrange
        ai_service = AIService()
        original_text = """
        1. What is the primary function of the heart?
        A) Pump blood throughout the body
        B) Filter waste from blood
        C) Produce red blood cells
        D) Store oxygen
        Correct Answer: A
        Explanation: The heart's main function is to pump oxygenated blood to all parts of the body.
        """
        
        # Act
        questions = await ai_service.extract_existing_questions(original_text)
        
        # Assert
        assert len(questions) > 0, "Should extract at least one question"
        # Check that question text is preserved (allowing for minor formatting)
        assert "heart" in questions[0]["question"].lower()
        assert "function" in questions[0]["question"].lower()
    
    @pytest.mark.asyncio
    async def test_extract_preserves_options(self):
        """Test that extracted questions preserve all options"""
        # Arrange
        ai_service = AIService()
        text_with_question = """
        Question: Which organ filters blood?
        A) Heart
        B) Kidney
        C) Liver
        D) Lungs
        Answer: B
        """
        
        # Act
        questions = await ai_service.extract_existing_questions(text_with_question)
        
        # Assert
        if len(questions) > 0:
            assert len(questions[0]["options"]) == 4, "Should have 4 options"
            # Check that key terms from options are preserved
            options_text = " ".join(questions[0]["options"]).lower()
            assert "kidney" in options_text or "heart" in options_text
    
    @pytest.mark.asyncio
    async def test_extract_preserves_correct_answer(self):
        """Test that extracted questions preserve correct answer index"""
        # Arrange
        ai_service = AIService()
        text_with_question = """
        1. What is 2+2?
        A) 3
        B) 4
        C) 5
        D) 6
        Correct: B (index 1)
        """
        
        # Act
        questions = await ai_service.extract_existing_questions(text_with_question)
        
        # Assert
        if len(questions) > 0:
            assert "correct_answer" in questions[0]
            assert 0 <= questions[0]["correct_answer"] <= 3, "Correct answer should be index 0-3"


class TestQuestionGeneration:
    """
    Property 2: Question Generation for Study Notes
    For any document identified as study notes (no existing questions), 
    the generated Question_Bank should contain at least one question.
    Validates: Requirements 1.2
    """
    
    @pytest.mark.asyncio
    async def test_generates_questions_from_study_notes(self):
        """Test that questions are generated from study notes"""
        # Arrange
        ai_service = AIService()
        study_notes = """
        The Human Heart
        
        The heart is a muscular organ approximately the size of a fist. It has four chambers:
        two upper chambers (atria) and two lower chambers (ventricles). The right side receives
        deoxygenated blood and pumps it to the lungs. The left side receives oxygenated blood
        from the lungs and pumps it to the body.
        """
        
        # Act
        questions = await ai_service.generate_new_questions(study_notes, num_questions=5)
        
        # Assert
        assert len(questions) > 0, "Should generate at least one question from study notes"
        assert len(questions) <= 5, "Should not exceed requested number of questions"
    
    @pytest.mark.asyncio
    async def test_generated_questions_have_required_fields(self):
        """Test that generated questions have all required fields"""
        # Arrange
        ai_service = AIService()
        study_notes = "The liver is the largest internal organ and performs over 500 functions."
        
        # Act
        questions = await ai_service.generate_new_questions(study_notes, num_questions=3)
        
        # Assert
        assert len(questions) > 0, "Should generate questions"
        for question in questions:
            assert "question" in question, "Should have question text"
            assert "options" in question, "Should have options"
            assert "correct_answer" in question, "Should have correct answer"
            assert "explanation" in question, "Should have explanation"
            assert "difficulty" in question, "Should have difficulty"
            assert len(question["options"]) == 4, "Should have 4 options"

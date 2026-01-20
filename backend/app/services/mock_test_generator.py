import logging
from typing import List
import uuid
from app.models import Question, MockTest

logger = logging.getLogger(__name__)

class MockTestGenerator:
    """Generates mock tests from existing questions WITHOUT additional AI calls"""
    
    async def create_mock_test_from_questions(
        self,
        session_id: str,
        user_id: str,
        questions: List[Question],
        session_name: str = "Study Session"
    ) -> MockTest:
        """
        Create a comprehensive mock test from existing questions
        NO AI calls - uses only the provided questions
        
        Duration calculation: 1.5 minutes per question
        Minimum: 15 minutes, Maximum: 90 minutes
        """
        try:
            if not questions:
                logger.warning(f"No questions provided for mock test creation in session {session_id}")
                return None
            
            if len(questions) < 5:
                logger.warning(f"Insufficient questions ({len(questions)}) for mock test in session {session_id}")
                return None
            
            total_questions = len(questions)
            
            # Calculate duration: 1.5 minutes per question
            # Minimum 15 minutes, maximum 90 minutes
            duration = max(15, min(90, int(total_questions * 1.5)))
            
            # Generate descriptive test name
            test_name = f"Mock Test - {session_name}"
            
            # Create mock test
            mock_test = MockTest(
                test_id=str(uuid.uuid4()),
                session_id=session_id,
                user_id=user_id,
                test_name=test_name,
                questions=[q.question_id for q in questions],
                duration_minutes=duration,
                total_questions=total_questions
            )
            
            logger.info(
                f"Created mock test '{test_name}' with {total_questions} questions "
                f"and {duration} minutes duration for session {session_id}"
            )
            
            return mock_test
            
        except Exception as e:
            logger.error(f"Failed to create mock test: {str(e)}")
            return None
    
    async def create_multiple_mock_tests(
        self,
        session_id: str,
        user_id: str,
        questions: List[Question],
        session_name: str = "Study Session",
        tests_count: int = 1
    ) -> List[MockTest]:
        """
        Create multiple mock tests by splitting questions
        Useful for creating practice sets from large question banks
        """
        try:
            if not questions or len(questions) < 5:
                logger.warning(f"Insufficient questions for creating {tests_count} mock tests")
                return []
            
            mock_tests = []
            questions_per_test = len(questions) // tests_count
            
            if questions_per_test < 5:
                # If splitting would create tests with too few questions, create one test
                logger.info(f"Creating single test instead of {tests_count} due to question count")
                test = await self.create_mock_test_from_questions(
                    session_id, user_id, questions, session_name
                )
                if test:
                    mock_tests.append(test)
                return mock_tests
            
            # Split questions into multiple tests
            for i in range(tests_count):
                start_idx = i * questions_per_test
                end_idx = start_idx + questions_per_test if i < tests_count - 1 else len(questions)
                
                test_questions = questions[start_idx:end_idx]
                test_name = f"{session_name} - Test {i+1}"
                
                test = await self.create_mock_test_from_questions(
                    session_id, user_id, test_questions, test_name
                )
                
                if test:
                    mock_tests.append(test)
            
            logger.info(f"Created {len(mock_tests)} mock tests for session {session_id}")
            return mock_tests
            
        except Exception as e:
            logger.error(f"Failed to create multiple mock tests: {str(e)}")
            return []

import logging
from typing import List, Dict, Any
import uuid
from app.models import BatchContent, Question, Mnemonic, CheatSheet, Note, DifficultyLevel

logger = logging.getLogger(__name__)

class ContentAggregator:
    """Aggregates content from multiple batches into unified collections"""
    
    async def aggregate_questions(self, batch_contents: List[BatchContent], session_id: str, user_id: str) -> List[Question]:
        """
        Combine all questions from batches into a single question bank
        Removes duplicates if any
        """
        try:
            all_questions = []
            seen_questions = set()
            
            for batch_content in batch_contents:
                for q_data in batch_content.questions:
                    # Create unique key for deduplication
                    question_key = q_data["question"].strip().lower()
                    
                    if question_key not in seen_questions:
                        seen_questions.add(question_key)
                        
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
                        all_questions.append(question)
            
            logger.info(f"Aggregated {len(all_questions)} unique questions from {len(batch_contents)} batches")
            return all_questions
            
        except Exception as e:
            logger.error(f"Failed to aggregate questions: {str(e)}")
            return []
    
    async def aggregate_mnemonics(self, batch_contents: List[BatchContent], session_id: str, user_id: str) -> List[Mnemonic]:
        """
        Combine all mnemonics from batches
        Returns list of Mnemonic objects
        """
        try:
            all_mnemonics = []
            seen_topics = set()
            
            for batch_content in batch_contents:
                for m_data in batch_content.mnemonics:
                    # Create unique key for deduplication
                    topic_key = m_data["topic"].strip().lower()
                    
                    if topic_key not in seen_topics:
                        seen_topics.add(topic_key)
                        
                        mnemonic = Mnemonic(
                            mnemonic_id=str(uuid.uuid4()),
                            session_id=session_id,
                            user_id=user_id,
                            topic=m_data["topic"],
                            mnemonic_text=m_data["mnemonic"],
                            explanation=m_data["explanation"],
                            key_terms=m_data.get("key_terms", [])
                        )
                        all_mnemonics.append(mnemonic)
            
            logger.info(f"Aggregated {len(all_mnemonics)} unique mnemonics from {len(batch_contents)} batches")
            return all_mnemonics
            
        except Exception as e:
            logger.error(f"Failed to aggregate mnemonics: {str(e)}")
            return []
    
    async def aggregate_cheat_sheets(self, batch_contents: List[BatchContent], session_id: str, user_id: str) -> List[CheatSheet]:
        """
        Combine cheat sheet points from all batches into comprehensive sheets
        Organizes by topic/concept
        """
        try:
            # Group points by concept
            concept_groups: Dict[str, Dict[str, List[str]]] = {}
            
            for batch_content in batch_contents:
                for point in batch_content.cheat_sheet_points:
                    # Extract concept from point (first sentence or first 50 chars)
                    concept = point.split('.')[0][:50] if '.' in point else point[:50]
                    
                    if concept not in concept_groups:
                        concept_groups[concept] = {
                            "key_points": [],
                            "high_yield_facts": []
                        }
                    
                    concept_groups[concept]["key_points"].append(point)
                
                # Add key concepts as high-yield facts
                for concept in batch_content.key_concepts:
                    if concept in concept_groups:
                        concept_groups[concept]["high_yield_facts"].append(concept)
            
            # Create cheat sheets from grouped content
            cheat_sheets = []
            for i, (concept, content) in enumerate(concept_groups.items(), 1):
                cheat_sheet = CheatSheet(
                    sheet_id=str(uuid.uuid4()),
                    session_id=session_id,
                    user_id=user_id,
                    title=f"Cheat Sheet {i}: {concept}",
                    key_points=content["key_points"][:10],  # Limit to 10 points
                    high_yield_facts=content["high_yield_facts"][:5],  # Limit to 5 facts
                    quick_references={}
                )
                cheat_sheets.append(cheat_sheet)
            
            logger.info(f"Aggregated {len(cheat_sheets)} cheat sheets from {len(batch_contents)} batches")
            return cheat_sheets
            
        except Exception as e:
            logger.error(f"Failed to aggregate cheat sheets: {str(e)}")
            return []
    
    async def compile_notes(
        self, 
        questions: List[Question], 
        mnemonics: List[Mnemonic], 
        cheat_sheets: List[CheatSheet],
        session_id: str,
        user_id: str,
        summary: str = ""
    ) -> Note:
        """
        Compile comprehensive notes from all content types
        Includes important questions, cheat sheet summaries, mnemonics, and high-yield topics
        """
        try:
            # Select important questions (high difficulty or specific topics)
            important_question_ids = [
                q.question_id for q in questions 
                if q.difficulty in [DifficultyLevel.MEDIUM, DifficultyLevel.HARD]
            ][:10]  # Limit to 10 important questions
            
            # Extract summary points from cheat sheets
            summary_points = []
            for sheet in cheat_sheets:
                summary_points.extend(sheet.high_yield_facts[:3])  # Top 3 from each sheet
            
            # Get mnemonic IDs for reference
            mnemonic_ids = [m.mnemonic_id for m in mnemonics]
            
            # Compile content
            content_parts = []
            
            if summary:
                content_parts.append(f"## Overview\n{summary}\n")
            
            content_parts.append(f"## Key Concepts\n")
            for point in summary_points[:15]:  # Top 15 points
                content_parts.append(f"- {point}")
            
            content_parts.append(f"\n## Important Questions\n")
            content_parts.append(f"This note references {len(important_question_ids)} important questions for review.")
            
            content_parts.append(f"\n## Memory Aids\n")
            content_parts.append(f"This note includes {len(mnemonic_ids)} mnemonics to help with retention.")
            
            content = "\n".join(content_parts)
            
            note = Note(
                note_id=str(uuid.uuid4()),
                session_id=session_id,
                user_id=user_id,
                title="Compiled Study Notes",
                content=content,
                important_questions=important_question_ids,
                summary_points=summary_points[:15],
                related_mnemonics=mnemonic_ids
            )
            
            logger.info(f"Compiled comprehensive notes for session {session_id}")
            return note
            
        except Exception as e:
            logger.error(f"Failed to compile notes: {str(e)}")
            # Return empty note on failure
            return Note(
                note_id=str(uuid.uuid4()),
                session_id=session_id,
                user_id=user_id,
                title="Study Notes",
                content="Notes compilation failed. Please review individual outputs.",
                important_questions=[],
                summary_points=[],
                related_mnemonics=[]
            )

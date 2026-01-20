"""
Progress tracking service for Study Buddy App processing
"""
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
from app.models import ProcessingStep, ProcessingProgress, SessionStatus
from app.database import get_database
from app.services.otp_service import OTPService
from app.logging_config import logger

class ProgressTracker:
    """Tracks and updates processing progress"""
    
    # Step weights for overall progress calculation
    STEP_WEIGHTS = {
        ProcessingStep.UPLOAD_COMPLETE: 5,
        ProcessingStep.FILE_ANALYSIS: 10,
        ProcessingStep.OCR_PROCESSING: 15,
        ProcessingStep.AI_PROCESSING: 10,
        ProcessingStep.GENERATING_QUESTIONS: 20,
        ProcessingStep.GENERATING_MOCK_TESTS: 15,
        ProcessingStep.GENERATING_MNEMONICS: 10,
        ProcessingStep.GENERATING_CHEAT_SHEETS: 10,
        ProcessingStep.GENERATING_NOTES: 5,
        ProcessingStep.FINALIZING: 5,
        ProcessingStep.COMPLETED: 0
    }
    
    # Estimated time per page (seconds)
    TIME_PER_PAGE = {
        ProcessingStep.FILE_ANALYSIS: 2,
        ProcessingStep.OCR_PROCESSING: 5,
        ProcessingStep.AI_PROCESSING: 3,
        ProcessingStep.GENERATING_QUESTIONS: 8,
        ProcessingStep.GENERATING_MOCK_TESTS: 4,
        ProcessingStep.GENERATING_MNEMONICS: 3,
        ProcessingStep.GENERATING_CHEAT_SHEETS: 3,
        ProcessingStep.GENERATING_NOTES: 2
    }
    
    @staticmethod
    async def update_progress(
        session_id: str,
        step: ProcessingStep,
        step_progress: int = 0,
        message: Optional[str] = None,
        pages_processed: Optional[int] = None,
        total_pages: Optional[int] = None
    ):
        """Update processing progress for a session"""
        try:
            db = await get_database()
            
            # Calculate overall progress
            overall_progress = ProgressTracker._calculate_overall_progress(step, step_progress)
            
            # Calculate estimated time remaining
            estimated_time = ProgressTracker._calculate_estimated_time(
                step, total_pages, pages_processed
            )
            
            # Update session in database
            update_data = {
                "current_step": step.value,
                "step_progress": step_progress,
                "overall_progress": overall_progress,
                "step_message": message,
                "estimated_time_remaining": estimated_time
            }
            
            if pages_processed is not None:
                update_data["pages_processed"] = pages_processed
            if total_pages is not None:
                update_data["total_pages"] = total_pages
                
            # Update status based on step
            if step == ProcessingStep.COMPLETED:
                update_data["status"] = SessionStatus.COMPLETED.value
                update_data["completed_at"] = datetime.utcnow()
            elif step == ProcessingStep.FAILED:
                update_data["status"] = SessionStatus.FAILED.value
            elif step != ProcessingStep.UPLOAD_COMPLETE:
                update_data["status"] = SessionStatus.PROCESSING.value
            
            await db.study_sessions.update_one(
                {"session_id": session_id},
                {"$set": update_data}
            )
            
            # Send email notification if completed and enabled
            if step == ProcessingStep.COMPLETED:
                await ProgressTracker._send_completion_notification(session_id)
                
        except Exception as e:
            logger.info(f"Error updating progress: {str(e)}")
    
    @staticmethod
    def _calculate_overall_progress(step: ProcessingStep, step_progress: int) -> int:
        """Calculate overall progress percentage"""
        completed_weight = 0
        total_weight = sum(ProgressTracker.STEP_WEIGHTS.values())
        
        # Add weight of completed steps
        for s, weight in ProgressTracker.STEP_WEIGHTS.items():
            if s.value < step.value:
                completed_weight += weight
            elif s == step:
                completed_weight += (weight * step_progress / 100)
                break
        
        return min(100, int((completed_weight / total_weight) * 100))
    
    @staticmethod
    def _calculate_estimated_time(
        current_step: ProcessingStep,
        total_pages: Optional[int],
        pages_processed: Optional[int]
    ) -> Optional[int]:
        """Calculate estimated time remaining in seconds"""
        if not total_pages or total_pages == 0:
            return None
            
        remaining_time = 0
        pages_remaining = total_pages - (pages_processed or 0)
        
        # Add time for remaining steps
        step_values = [s.value for s in ProcessingStep]
        current_index = step_values.index(current_step.value)
        
        for i in range(current_index, len(step_values)):
            step = ProcessingStep(step_values[i])
            if step in ProgressTracker.TIME_PER_PAGE:
                if step == current_step:
                    # Partial time for current step
                    remaining_time += ProgressTracker.TIME_PER_PAGE[step] * pages_remaining
                else:
                    # Full time for future steps
                    remaining_time += ProgressTracker.TIME_PER_PAGE[step] * total_pages
        
        return max(10, remaining_time)  # Minimum 10 seconds
    
    @staticmethod
    async def _send_completion_notification(session_id: str):
        """Send email notification when processing is complete"""
        try:
            db = await get_database()
            session = await db.study_sessions.find_one({"session_id": session_id})
            
            if not session or not session.get("email_notification_enabled"):
                return
                
            email = session.get("notification_email")
            if not email:
                return
            
            # Send completion email
            subject = "StudyBuddy - Your Study Materials Are Ready!"
            message = f"""
            Great news! Your study materials have been successfully generated.
            
            Session ID: {session_id}
            
            Generated content includes:
            • Question Bank
            • Mock Tests  
            • Mnemonics
            • Cheat Sheets
            • Study Notes
            
            Visit StudyBuddy to access your materials: [Your App URL]
            
            Happy studying!
            - StudyBuddy Team
            """
            
            await OTPService.send_email_otp(email, "READY", message)
            logger.info(f"Completion notification sent to {email}")
            
        except Exception as e:
            logger.info(f"Error sending completion notification: {str(e)}")

    @staticmethod
    async def enable_email_notification(session_id: str, email: str):
        """Enable email notification for session completion"""
        try:
            db = await get_database()
            await db.study_sessions.update_one(
                {"session_id": session_id},
                {"$set": {
                    "email_notification_enabled": True,
                    "notification_email": email
                }}
            )
            return True
        except Exception as e:
            logger.info(f"Error enabling email notification: {str(e)}")
            return False

    @staticmethod
    async def get_progress(session_id: str) -> Optional[ProcessingProgress]:
        """Get current progress for a session"""
        try:
            db = await get_database()
            session = await db.study_sessions.find_one({"session_id": session_id})
            
            if not session:
                return None
                
            return ProcessingProgress(
                current_step=ProcessingStep(session.get("current_step", ProcessingStep.UPLOAD_COMPLETE.value)),
                step_progress=session.get("step_progress", 0),
                overall_progress=session.get("overall_progress", 0),
                estimated_time_remaining=session.get("estimated_time_remaining"),
                pages_processed=session.get("pages_processed"),
                total_pages=session.get("total_pages"),
                step_message=session.get("step_message")
            )
        except Exception as e:
            logger.info(f"Error getting progress: {str(e)}")
            return None

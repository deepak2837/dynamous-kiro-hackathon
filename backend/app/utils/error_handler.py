import logging
from typing import Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)

class RecoveryAction(str, Enum):
    """Possible recovery actions for errors"""
    RETRY = "retry"
    RETRY_LATER = "retry_later"
    FALLBACK_OCR = "fallback_ocr"
    FALLBACK_AI = "fallback_ai"
    CONTACT_SUPPORT = "contact_support"
    SKIP = "skip"

class ErrorHandler:
    """Centralized error handling with user-friendly messages and recovery strategies"""
    
    @staticmethod
    async def handle_ai_error(error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle AI service errors with appropriate user messages
        
        Returns:
            Dict with user_message, recovery_action, and technical_details
        """
        try:
            error_str = str(error).lower()
            
            # Rate limit errors
            if "rate limit" in error_str or "quota" in error_str or "429" in error_str:
                logger.warning(f"AI rate limit exceeded: {error}")
                return {
                    "user_message": "AI service rate limit exceeded. Please try again in a few minutes.",
                    "recovery_action": RecoveryAction.RETRY_LATER,
                    "technical_details": str(error),
                    "retry_after_seconds": 60
                }
            
            # Authentication errors
            elif "authentication" in error_str or "api key" in error_str or "401" in error_str or "403" in error_str:
                logger.error(f"AI authentication failed: {error}")
                return {
                    "user_message": "AI service authentication failed. Please contact support.",
                    "recovery_action": RecoveryAction.CONTACT_SUPPORT,
                    "technical_details": str(error)
                }
            
            # Content blocked by safety filters
            elif "blocked" in error_str or "safety" in error_str:
                logger.warning(f"Content blocked by safety filters: {error}")
                return {
                    "user_message": "Some content was blocked by safety filters. Processing will continue with available content.",
                    "recovery_action": RecoveryAction.SKIP,
                    "technical_details": str(error)
                }
            
            # Network/timeout errors
            elif "timeout" in error_str or "connection" in error_str or "network" in error_str:
                logger.warning(f"Network error: {error}")
                return {
                    "user_message": "Network connection issue. Retrying...",
                    "recovery_action": RecoveryAction.RETRY,
                    "technical_details": str(error),
                    "retry_after_seconds": 5
                }
            
            # Generic AI errors
            else:
                logger.error(f"AI processing error: {error}")
                return {
                    "user_message": f"AI processing encountered an error: {str(error)[:100]}",
                    "recovery_action": RecoveryAction.RETRY,
                    "technical_details": str(error)
                }
                
        except Exception as e:
            logger.error(f"Error in error handler: {e}")
            return {
                "user_message": "An unexpected error occurred during processing.",
                "recovery_action": RecoveryAction.CONTACT_SUPPORT,
                "technical_details": str(error)
            }
    
    @staticmethod
    async def handle_ocr_error(error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle OCR errors with fallback to AI_ONLY mode
        
        Returns:
            Dict with user_message, recovery_action, and fallback_mode
        """
        try:
            logger.warning(f"OCR processing failed: {error}")
            
            return {
                "user_message": "OCR processing failed. Switching to AI-based extraction...",
                "recovery_action": RecoveryAction.FALLBACK_AI,
                "technical_details": str(error),
                "fallback_mode": "AI_ONLY"
            }
            
        except Exception as e:
            logger.error(f"Error in OCR error handler: {e}")
            return {
                "user_message": "Text extraction failed. Please try with a different file.",
                "recovery_action": RecoveryAction.CONTACT_SUPPORT,
                "technical_details": str(error)
            }
    
    @staticmethod
    async def handle_processing_error(
        error: Exception, 
        context: Dict[str, Any],
        partial_results: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle general processing errors with partial result preservation
        
        Returns:
            Dict with user_message, recovery_action, and preserved_results
        """
        try:
            logger.error(f"Processing error in {context.get('step', 'unknown')}: {error}")
            
            # Determine if we have partial results to preserve
            has_partial_results = partial_results and any(partial_results.values())
            
            if has_partial_results:
                return {
                    "user_message": "Processing partially completed. Some results have been saved.",
                    "recovery_action": RecoveryAction.SKIP,
                    "technical_details": str(error),
                    "partial_results": partial_results,
                    "completed_steps": context.get("completed_steps", [])
                }
            else:
                return {
                    "user_message": f"Processing failed: {str(error)[:100]}",
                    "recovery_action": RecoveryAction.RETRY,
                    "technical_details": str(error)
                }
                
        except Exception as e:
            logger.error(f"Error in processing error handler: {e}")
            return {
                "user_message": "An unexpected error occurred.",
                "recovery_action": RecoveryAction.CONTACT_SUPPORT,
                "technical_details": str(error)
            }
    
    @staticmethod
    async def handle_file_error(error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle file-related errors (upload, read, format)
        
        Returns:
            Dict with user_message and recovery_action
        """
        try:
            error_str = str(error).lower()
            
            if "unsupported" in error_str or "format" in error_str:
                return {
                    "user_message": "Unsupported file format. Please upload PDF, JPG, PNG, or PPTX files.",
                    "recovery_action": RecoveryAction.SKIP,
                    "technical_details": str(error)
                }
            elif "size" in error_str or "too large" in error_str:
                return {
                    "user_message": "File size exceeds limit. Please upload files smaller than 50MB.",
                    "recovery_action": RecoveryAction.SKIP,
                    "technical_details": str(error)
                }
            elif "corrupt" in error_str or "damaged" in error_str:
                return {
                    "user_message": "File appears to be corrupted. Please try uploading again.",
                    "recovery_action": RecoveryAction.SKIP,
                    "technical_details": str(error)
                }
            else:
                return {
                    "user_message": f"File processing error: {str(error)[:100]}",
                    "recovery_action": RecoveryAction.SKIP,
                    "technical_details": str(error)
                }
                
        except Exception as e:
            logger.error(f"Error in file error handler: {e}")
            return {
                "user_message": "File processing failed.",
                "recovery_action": RecoveryAction.SKIP,
                "technical_details": str(error)
            }
    
    @staticmethod
    def should_retry(recovery_action: RecoveryAction, attempt: int, max_attempts: int = 3) -> bool:
        """
        Determine if an operation should be retried
        
        Args:
            recovery_action: The recovery action from error handling
            attempt: Current attempt number (1-indexed)
            max_attempts: Maximum number of retry attempts
            
        Returns:
            True if should retry, False otherwise
        """
        if attempt >= max_attempts:
            return False
        
        return recovery_action in [RecoveryAction.RETRY, RecoveryAction.RETRY_LATER]

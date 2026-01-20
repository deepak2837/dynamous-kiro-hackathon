import logging
import os
from datetime import datetime
from typing import Optional

class ErrorLogger:
    """Centralized error logging service"""
    
    def __init__(self, log_file: str = "error.log"):
        self.log_file = log_file
        self.setup_logger()
    
    def setup_logger(self):
        """Setup error logger with file handler"""
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(self.log_file) if os.path.dirname(self.log_file) else "."
        if log_dir != "." and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Configure logger
        self.logger = logging.getLogger("error_logger")
        self.logger.setLevel(logging.ERROR)
        
        # Remove existing handlers to avoid duplicates
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # File handler
        file_handler = logging.FileHandler(self.log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.ERROR)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
    
    def log_error(self, error: Exception, context: str, user_id: Optional[str] = None, additional_info: Optional[dict] = None):
        """Log error with context information"""
        error_msg = f"Context: {context}"
        if user_id:
            error_msg += f" | User: {user_id}"
        error_msg += f" | Error: {str(error)}"
        if additional_info:
            error_msg += f" | Info: {additional_info}"
        
        self.logger.error(error_msg, exc_info=True)
    
    def log_custom_error(self, message: str, context: str, user_id: Optional[str] = None):
        """Log custom error message"""
        error_msg = f"Context: {context}"
        if user_id:
            error_msg += f" | User: {user_id}"
        error_msg += f" | Message: {message}"
        
        self.logger.error(error_msg)

# Global error logger instance
error_logger = ErrorLogger("logs/error.log")

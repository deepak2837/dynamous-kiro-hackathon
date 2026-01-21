import logging
import logging.handlers
import os
from datetime import datetime

def setup_logging():
    """Setup centralized logging configuration with persistent logs"""
    
    # Avoid reconfiguring if already set up
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return logging.getLogger("app")
    
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Log file paths - all logs go to logs directory
    backend_log_file = os.path.join(log_dir, "backend.log")
    studybuddy_log_file = os.path.join(log_dir, "studybuddy.log")
    
    # Create formatters
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create handlers
    backend_handler = logging.handlers.RotatingFileHandler(
        backend_log_file,
        maxBytes=5*1024*1024,  # 5MB per file
        backupCount=10,  # Keep 10 backup files
        encoding='utf-8',
        mode='a'  # Explicitly set append mode
    )
    backend_handler.setFormatter(formatter)
    
    studybuddy_handler = logging.handlers.RotatingFileHandler(
        studybuddy_log_file,
        maxBytes=5*1024*1024,  # 5MB per file
        backupCount=20,  # Keep 20 backup files
        encoding='utf-8',
        mode='a'  # Explicitly set append mode
    )
    studybuddy_handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(backend_handler)
    root_logger.addHandler(studybuddy_handler)
    root_logger.addHandler(console_handler)
    
    # Set specific loggers to ensure OCR logs are captured
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("app").setLevel(logging.INFO)
    logging.getLogger("app.services.file_processor").setLevel(logging.INFO)  # Ensure OCR logs
    logging.getLogger("app.services.processing").setLevel(logging.INFO)
    
    # Log startup message
    app_logger = logging.getLogger("app")
    app_logger.info("=" * 50)
    app_logger.info(f"Server starting at {datetime.now()}")
    app_logger.info("=" * 50)
    
    return app_logger

# Initialize logger
logger = setup_logging()

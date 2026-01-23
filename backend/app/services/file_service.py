import os
import shutil
from typing import Optional, Tuple
import uuid
from app.config import settings

class FileService:
    """Simplified file service for local storage only"""
    
    def __init__(self):
        self.storage_mode = "LOCAL"
        self.upload_dir = settings.upload_dir
        
        # Ensure upload directory exists
        os.makedirs(self.upload_dir, exist_ok=True)
    
    def is_s3_enabled(self) -> bool:
        """Always returns False since we only support local storage"""
        return False
    
    async def upload_file(self, local_file_path: str, session_id: str, filename: str) -> Tuple[str, Optional[str]]:
        """
        Store file locally and return the local path
        Returns: (file_path, None) - s3_key is always None for local storage
        """
        try:
            # Create session directory
            session_dir = os.path.join(self.upload_dir, session_id)
            os.makedirs(session_dir, exist_ok=True)
            
            # Generate unique filename to avoid conflicts
            file_extension = os.path.splitext(filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            destination_path = os.path.join(session_dir, unique_filename)
            
            # Copy file to session directory
            shutil.copy2(local_file_path, destination_path)
            
            return destination_path, None
            
        except Exception as e:
            raise Exception(f"Failed to store file locally: {str(e)}")
    
    async def download_file_for_processing(self, s3_key: str, local_path: str) -> str:
        """
        For local storage, this is a no-op since files are already local
        Returns the s3_key as it's actually the local path
        """
        return s3_key
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete a local file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False

# Create singleton instance
file_service = FileService()

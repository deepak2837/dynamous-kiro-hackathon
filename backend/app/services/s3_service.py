import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Optional, Tuple
import uuid
from app.config import settings

class S3Service:
    def __init__(self):
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY") 
        self.aws_region = os.getenv("AWS_REGION", "ap-south-1")
        self.bucket_name = os.getenv("STUDY_BUDDY_BUCKET_NAME", "study-buddy-crud-bucket")
        self.storage_mode = os.getenv("STORAGE", "LOCAL").upper()
        
        if self.storage_mode == "S3":
            self._init_s3_client()
    
    def _init_s3_client(self):
        """Initialize S3 client with credentials"""
        if not self.aws_access_key_id or not self.aws_secret_access_key:
            raise ValueError("AWS credentials not found in environment variables")
        
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.aws_region
            )
            print(f"S3Service initialized with bucket: {self.bucket_name}, region: {self.aws_region}")
        except Exception as e:
            raise ValueError(f"Failed to initialize S3 client: {str(e)}")
    
    def is_s3_enabled(self) -> bool:
        """Check if S3 storage is enabled"""
        return self.storage_mode == "S3"
    
    async def upload_file(self, file_path: str, session_id: str, original_filename: str) -> Tuple[str, Optional[str]]:
        """
        Upload file to S3 or return local path based on storage mode
        Returns: (file_url, s3_key or None)
        """
        if not self.is_s3_enabled():
            # Return local file path
            return file_path, None
        
        try:
            # Generate unique S3 key
            file_extension = os.path.splitext(original_filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            s3_key = f"study-sessions/{session_id}/{unique_filename}"
            
            # Upload to S3
            with open(file_path, 'rb') as file_data:
                self.s3_client.upload_fileobj(
                    file_data,
                    self.bucket_name,
                    s3_key,
                    ExtraArgs={'ContentType': self._get_content_type(file_extension)}
                )
            
            # Generate S3 URL
            s3_url = f"https://{self.bucket_name}.s3.{self.aws_region}.amazonaws.com/{s3_key}"
            
            # Clean up local file after successful upload
            if os.path.exists(file_path):
                os.remove(file_path)
            
            return s3_url, s3_key
            
        except (ClientError, NoCredentialsError) as e:
            print(f"S3 upload failed: {str(e)}")
            # Fallback to local storage
            return file_path, None
        except Exception as e:
            print(f"Unexpected error during S3 upload: {str(e)}")
            return file_path, None
    
    async def delete_file(self, s3_key: str) -> bool:
        """Delete file from S3"""
        if not self.is_s3_enabled() or not s3_key:
            return True
        
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except Exception as e:
            print(f"Failed to delete S3 object {s3_key}: {str(e)}")
            return False
    
    async def download_file_for_processing(self, s3_key: str, local_path: str) -> str:
        """Download S3 file to local path for processing"""
        if not self.is_s3_enabled() or not s3_key:
            return local_path  # Return original path if not S3
        
        try:
            # Download file from S3
            self.s3_client.download_file(self.bucket_name, s3_key, local_path)
            return local_path
        except Exception as e:
            print(f"Failed to download S3 file {s3_key}: {str(e)}")
            raise Exception(f"Could not download file for processing: {str(e)}")
    
    def _get_content_type(self, file_extension: str) -> str:
        """Get content type based on file extension"""
        content_types = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        }
        return content_types.get(file_extension.lower(), 'application/octet-stream')

# Singleton instance
s3_service = S3Service()

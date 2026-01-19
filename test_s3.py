#!/usr/bin/env python3
"""
Test script to verify S3 integration
"""
import os
import sys
sys.path.append('/home/unknown/Documents/hackathon application/dynamous-kiro-hackathon/backend')

from app.services.s3_service import s3_service
from app.config import settings

def test_s3_configuration():
    """Test S3 service configuration"""
    print("=== S3 Configuration Test ===")
    print(f"Storage Mode: {s3_service.storage_mode}")
    print(f"S3 Enabled: {s3_service.is_s3_enabled()}")
    print(f"Bucket Name: {s3_service.bucket_name}")
    print(f"AWS Region: {s3_service.aws_region}")
    print(f"AWS Access Key ID: {s3_service.aws_access_key_id[:10]}..." if s3_service.aws_access_key_id else "Not set")
    print(f"AWS Secret Key: {'Set' if s3_service.aws_secret_access_key else 'Not set'}")
    
    if s3_service.is_s3_enabled():
        try:
            # Try to initialize S3 client
            s3_service._init_s3_client()
            print("✅ S3 client initialized successfully")
        except Exception as e:
            print(f"❌ S3 client initialization failed: {e}")
    else:
        print("ℹ️  S3 disabled, using local storage")

if __name__ == "__main__":
    test_s3_configuration()

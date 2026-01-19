# S3 Integration for Study Buddy App

This document explains how to configure and use S3 storage for the Study Buddy application.

## Configuration

### Environment Variables

Add the following variables to your `.env` file:

```env
# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_REGION=ap-south-1
STUDY_BUDDY_BUCKET_NAME=study-buddy-crud-bucket

# Storage Mode (LOCAL or S3)
STORAGE=LOCAL     # Change to S3 to enable S3 storage
```

### Storage Modes

- **LOCAL**: Files are stored locally in the `./uploads` directory
- **S3**: Files are uploaded to AWS S3 bucket

## How It Works

### Upload Process

1. **Local Mode**: Files are saved directly to local filesystem
2. **S3 Mode**: 
   - Files are temporarily saved locally
   - Uploaded to S3 with unique keys
   - Local temporary files are deleted
   - S3 URLs are stored in database

### Processing

1. **Local Mode**: Files are processed directly from local paths
2. **S3 Mode**:
   - Files are downloaded from S3 to temporary location
   - Processed locally
   - Temporary files are cleaned up

### Database Schema

The `StudySession` model includes:
- `files`: Original file paths (for backward compatibility)
- `file_urls`: Actual URLs (local paths or S3 URLs)
- `s3_keys`: S3 object keys (null for local files)

## Testing

Run the test script to verify configuration:

```bash
cd /home/unknown/Documents/hackathon application/dynamous-kiro-hackathon
python test_s3.py
```

## API Endpoints

### Storage Info
```
GET /api/v1/upload/storage-info
```

Returns current storage configuration:
```json
{
  "storage_mode": "LOCAL",
  "s3_enabled": false,
  "bucket_name": null,
  "region": null
}
```

## Switching Between Modes

1. **To enable S3**:
   - Set `STORAGE=S3` in `.env`
   - Configure AWS credentials
   - Restart the application

2. **To disable S3**:
   - Set `STORAGE=LOCAL` in `.env`
   - Restart the application

## Security Considerations

- AWS credentials should be kept secure
- Use IAM roles with minimal required permissions
- Consider using AWS IAM roles instead of access keys in production
- S3 bucket should have proper access policies

## Required AWS Permissions

The AWS user/role needs the following S3 permissions:
- `s3:PutObject`
- `s3:GetObject`
- `s3:DeleteObject`
- `s3:ListBucket`

## Error Handling

- If S3 upload fails, the system falls back to local storage
- Processing continues even if S3 operations fail
- Errors are logged for debugging

## Migration

When switching from LOCAL to S3:
- Existing local files remain accessible
- New uploads go to S3
- No data migration is required

When switching from S3 to LOCAL:
- Existing S3 files remain in S3
- New uploads go to local storage
- S3 files can still be accessed via their URLs

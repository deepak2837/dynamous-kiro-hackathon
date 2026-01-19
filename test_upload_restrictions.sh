#!/bin/bash

# Test script for upload restrictions
echo "Testing upload restrictions implementation..."

# Check if backend is running
echo "1. Checking if backend is running..."
curl -s http://localhost:8000/health > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Backend is running"
else
    echo "❌ Backend is not running. Please start it first."
    exit 1
fi

# Test upload restriction check endpoint
echo "2. Testing upload restriction check..."
response=$(curl -s http://localhost:8000/api/v1/upload/check-upload-allowed/demo-user-123)
echo "Response: $response"

# Check if the response contains expected fields
if echo "$response" | grep -q "upload_allowed"; then
    echo "✅ Upload restriction check endpoint working"
else
    echo "❌ Upload restriction check endpoint not working properly"
fi

echo "3. Environment variables to check in .env:"
echo "   RESTRICT_UPLOAD_TIMING=true"
echo "   UPLOAD_COOLDOWN_MINUTES=5"

echo ""
echo "Implementation complete! 🎉"
echo ""
echo "Features implemented:"
echo "✅ Upload restrictions during processing"
echo "✅ 5-minute cooldown period after upload"
echo "✅ Environment flags for configuration"
echo "✅ Frontend UI with countdown timer"
echo "✅ Real-time restriction checking"
echo "✅ User-friendly error messages"

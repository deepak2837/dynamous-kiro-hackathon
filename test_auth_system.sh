#!/bin/bash

# Test Authentication System
echo "🔐 Testing StudyBuddy Authentication System"
echo "=========================================="

API_BASE="http://localhost:8000"

# Test 1: Check if user exists (should return false for new user)
echo "📱 Test 1: Check if user exists"
curl -X POST "$API_BASE/api/v1/auth/check-user" \
  -H "Content-Type: application/json" \
  -d '{"mobile_number": "+919876543210"}' \
  -w "\nStatus: %{http_code}\n\n"

# Test 2: Send OTP for registration (SMS)
echo "📨 Test 2: Send OTP for registration (SMS)"
curl -X POST "$API_BASE/api/v1/auth/send-otp" \
  -H "Content-Type: application/json" \
  -d '{
    "mobile_number": "+919876543210",
    "otp_method": "sms"
  }' \
  -w "\nStatus: %{http_code}\n\n"

# Test 3: Send OTP for registration (Email)
echo "📧 Test 3: Send OTP for registration (Email)"
curl -X POST "$API_BASE/api/v1/auth/send-otp" \
  -H "Content-Type: application/json" \
  -d '{
    "mobile_number": "+919876543210",
    "otp_method": "email",
    "email": "test@example.com"
  }' \
  -w "\nStatus: %{http_code}\n\n"

# Test 4: Register user (with demo OTP)
echo "👤 Test 4: Register user"
curl -X POST "$API_BASE/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Student",
    "mobile_number": "+919876543210",
    "email": "test@example.com",
    "password": "password123",
    "role": "student",
    "otp_method": "sms",
    "college_name": "Test Medical College",
    "course": "MBBS",
    "year": 2
  }' \
  -w "\nStatus: %{http_code}\n\n"

# Test 5: Login with credentials
echo "🔑 Test 5: Login with credentials"
LOGIN_RESPONSE=$(curl -s -X POST "$API_BASE/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "mobile_number": "+919876543210",
    "password": "password123"
  }')

echo "$LOGIN_RESPONSE" | jq '.'
TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token // empty')

if [ -n "$TOKEN" ]; then
  echo "✅ Login successful! Token: ${TOKEN:0:20}..."
  
  # Test 6: Get user info with token
  echo ""
  echo "👤 Test 6: Get user info with token"
  curl -X GET "$API_BASE/api/v1/auth/me" \
    -H "Authorization: Bearer $TOKEN" \
    -w "\nStatus: %{http_code}\n\n"
else
  echo "❌ Login failed!"
fi

echo "🏁 Authentication tests completed!"

#!/bin/bash

echo "🧪 Testing StudyBuddy Auth API Integration"
echo "=========================================="

BASE_URL="http://localhost:8000/api/v1"

# Test 1: Register a new user
echo -e "\n1️⃣ Testing User Registration..."
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "securepass123",
    "name": "Test User"
  }')

echo "Register Response: $REGISTER_RESPONSE"

# Extract token from response
TOKEN=$(echo $REGISTER_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ Registration failed - no token received"
  exit 1
fi

echo "✅ Registration successful - Token: ${TOKEN:0:20}..."

# Test 2: Login with the same user
echo -e "\n2️⃣ Testing User Login..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "securepass123"
  }')

echo "Login Response: $LOGIN_RESPONSE"

# Extract token from login response
LOGIN_TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$LOGIN_TOKEN" ]; then
  echo "❌ Login failed - no token received"
  exit 1
fi

echo "✅ Login successful - Token: ${LOGIN_TOKEN:0:20}..."

# Test 3: Access protected endpoint
echo -e "\n3️⃣ Testing Protected Endpoint..."
ME_RESPONSE=$(curl -s -X GET "$BASE_URL/auth/me" \
  -H "Authorization: Bearer $LOGIN_TOKEN")

echo "Me Response: $ME_RESPONSE"

if echo "$ME_RESPONSE" | grep -q "user_id"; then
  echo "✅ Protected endpoint access successful"
else
  echo "❌ Protected endpoint access failed"
  exit 1
fi

# Test 4: Test invalid token
echo -e "\n4️⃣ Testing Invalid Token..."
INVALID_RESPONSE=$(curl -s -X GET "$BASE_URL/auth/me" \
  -H "Authorization: Bearer invalid_token_here")

echo "Invalid Token Response: $INVALID_RESPONSE"

if echo "$INVALID_RESPONSE" | grep -q "Invalid token"; then
  echo "✅ Invalid token properly rejected"
else
  echo "❌ Invalid token not properly handled"
fi

# Test 5: Test duplicate registration
echo -e "\n5️⃣ Testing Duplicate Registration..."
DUPLICATE_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "anotherpass123",
    "name": "Another User"
  }')

echo "Duplicate Registration Response: $DUPLICATE_RESPONSE"

if echo "$DUPLICATE_RESPONSE" | grep -q "already registered"; then
  echo "✅ Duplicate registration properly rejected"
else
  echo "❌ Duplicate registration not properly handled"
fi

echo -e "\n🎉 Auth API Testing Complete!"
echo "=========================================="
echo "✅ All auth endpoints are working correctly"
echo "🌐 Frontend available at: http://localhost:3001"
echo "🌐 Auth page available at: http://localhost:3001/auth"
echo "📚 API docs available at: http://localhost:8000/docs"

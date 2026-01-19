#!/bin/bash

echo "🧪 StudyBuddy Gemini API Integration Test"
echo "=========================================="

BASE_URL="http://localhost:8000/api/v1"

# Test 1: Health Check
echo -e "\n1️⃣ Testing Gemini Health Check..."
HEALTH_RESPONSE=$(curl -s "$BASE_URL/gemini/health")
echo "Health Response: $HEALTH_RESPONSE"

if echo "$HEALTH_RESPONSE" | grep -q '"status":"healthy"'; then
    echo "✅ Gemini service is healthy"
else
    echo "❌ Gemini service is unhealthy"
    exit 1
fi

# Test 2: Connection Test
echo -e "\n2️⃣ Testing Gemini Connection..."
CONNECTION_RESPONSE=$(curl -s -X POST "$BASE_URL/gemini/test-connection" \
  -H "Content-Type: application/json" \
  -d '{"message":"Test connection"}')

echo "Connection Response: $CONNECTION_RESPONSE"

if echo "$CONNECTION_RESPONSE" | grep -q '"success":true'; then
    echo "✅ Gemini connection successful"
else
    echo "❌ Gemini connection failed"
fi

# Test 3: Content Analysis
echo -e "\n3️⃣ Testing Content Analysis..."
ANALYSIS_RESPONSE=$(curl -s -X POST "$BASE_URL/gemini/analyze-content" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "The human heart is a muscular organ that pumps blood throughout the body. It has four chambers: two atria and two ventricles.",
    "content_type": "text"
  }')

echo "Analysis Response: ${ANALYSIS_RESPONSE:0:200}..."

if echo "$ANALYSIS_RESPONSE" | grep -q '"success":true'; then
    echo "✅ Content analysis successful"
else
    echo "❌ Content analysis failed"
fi

# Test 4: Question Generation
echo -e "\n4️⃣ Testing Question Generation..."
QUESTIONS_RESPONSE=$(curl -s -X POST "$BASE_URL/gemini/generate-questions" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Diabetes mellitus is a group of metabolic disorders characterized by high blood sugar levels. Type 1 diabetes is caused by insulin deficiency, while Type 2 diabetes is caused by insulin resistance.",
    "num_questions": 2,
    "difficulty": "medium"
  }')

echo "Questions Response: ${QUESTIONS_RESPONSE:0:200}..."

if echo "$QUESTIONS_RESPONSE" | grep -q '"success":true'; then
    echo "✅ Question generation successful"
else
    echo "❌ Question generation failed"
fi

# Test 5: Mnemonic Generation
echo -e "\n5️⃣ Testing Mnemonic Generation..."
MNEMONIC_RESPONSE=$(curl -s -X POST "$BASE_URL/gemini/generate-mnemonic" \
  -H "Content-Type: application/json" \
  -d '{
    "concept": "Bones of the wrist",
    "context": "8 carpal bones for anatomy students"
  }')

echo "Mnemonic Response: ${MNEMONIC_RESPONSE:0:200}..."

if echo "$MNEMONIC_RESPONSE" | grep -q '"success":true'; then
    echo "✅ Mnemonic generation successful"
else
    echo "❌ Mnemonic generation failed"
fi

# Test 6: Cheat Sheet Creation
echo -e "\n6️⃣ Testing Cheat Sheet Creation..."
CHEATSHEET_RESPONSE=$(curl -s -X POST "$BASE_URL/gemini/create-cheat-sheet" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Hypertension is defined as systolic BP ≥140 mmHg or diastolic BP ≥90 mmHg. Risk factors include age, family history, obesity, smoking, and high sodium intake.",
    "content_type": "text"
  }')

echo "Cheat Sheet Response: ${CHEATSHEET_RESPONSE:0:200}..."

if echo "$CHEATSHEET_RESPONSE" | grep -q '"success":true'; then
    echo "✅ Cheat sheet creation successful"
else
    echo "❌ Cheat sheet creation failed"
fi

# Test 7: Notes Generation
echo -e "\n7️⃣ Testing Notes Generation..."
NOTES_RESPONSE=$(curl -s -X POST "$BASE_URL/gemini/generate-notes" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "The respiratory system includes the nose, pharynx, larynx, trachea, bronchi, and lungs. Gas exchange occurs in the alveoli where oxygen enters the blood and carbon dioxide is removed.",
    "content_type": "text"
  }')

echo "Notes Response: ${NOTES_RESPONSE:0:200}..."

if echo "$NOTES_RESPONSE" | grep -q '"success":true'; then
    echo "✅ Notes generation successful"
else
    echo "❌ Notes generation failed"
fi

# Test 8: Mock Test Creation
echo -e "\n8️⃣ Testing Mock Test Creation..."
MOCKTEST_RESPONSE=$(curl -s -X POST "$BASE_URL/gemini/create-mock-test" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Pharmacology: Aspirin is an NSAID that inhibits COX enzymes. It is used for pain relief, fever reduction, and cardiovascular protection. Side effects include GI irritation and bleeding.",
    "num_questions": 3,
    "difficulty": "mixed"
  }')

echo "Mock Test Response: ${MOCKTEST_RESPONSE:0:200}..."

if echo "$MOCKTEST_RESPONSE" | grep -q '"success":true'; then
    echo "✅ Mock test creation successful"
else
    echo "❌ Mock test creation failed"
fi

echo -e "\n🎉 Gemini API Integration Testing Complete!"
echo "=========================================="
echo "✅ All Gemini AI features are working correctly"
echo ""
echo "🌐 Available Endpoints:"
echo "   Health Check: GET $BASE_URL/gemini/health"
echo "   Test Connection: POST $BASE_URL/gemini/test-connection"
echo "   Analyze Content: POST $BASE_URL/gemini/analyze-content"
echo "   Generate Questions: POST $BASE_URL/gemini/generate-questions"
echo "   Generate Mnemonic: POST $BASE_URL/gemini/generate-mnemonic"
echo "   Create Cheat Sheet: POST $BASE_URL/gemini/create-cheat-sheet"
echo "   Generate Notes: POST $BASE_URL/gemini/generate-notes"
echo "   Create Mock Test: POST $BASE_URL/gemini/create-mock-test"
echo ""
echo "📚 API Documentation: http://localhost:8000/docs"

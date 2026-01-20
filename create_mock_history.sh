#!/bin/bash

# Create mock session data for testing history feature
echo "🗂️ Creating mock session data for history testing..."

API_BASE="http://localhost:8000"

# Get a valid token first
echo "Getting authentication token..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_BASE/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "mobile_number": "+919876543210",
    "password": "password123"
  }')

TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ Failed to get authentication token"
  exit 1
fi

echo "✅ Got token: ${TOKEN:0:20}..."

# Create mock sessions directly in MongoDB
echo "Creating mock session data..."

# Use Python to insert mock data
python3 << EOF
import pymongo
from datetime import datetime, timedelta
import uuid

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017")
db = client["studybuddy"]

# User ID from the test user
user_id = "696e8e19432fab8ded1a8c30"

# Create mock sessions
sessions = [
    {
        "session_id": str(uuid.uuid4()),
        "user_id": user_id,
        "session_name": "Anatomy Study Session",
        "created_at": datetime.utcnow() - timedelta(days=1),
        "status": "completed",
        "files_uploaded": ["anatomy_notes.pdf", "skeletal_system.jpg"],
        "processing_mode": "default"
    },
    {
        "session_id": str(uuid.uuid4()),
        "user_id": user_id,
        "session_name": "Physiology Mock Test Prep",
        "created_at": datetime.utcnow() - timedelta(hours=6),
        "status": "completed",
        "files_uploaded": ["physiology_slides.pptx"],
        "processing_mode": "ai_based"
    },
    {
        "session_id": str(uuid.uuid4()),
        "user_id": user_id,
        "session_name": "Pathology Quick Review",
        "created_at": datetime.utcnow() - timedelta(hours=2),
        "status": "processing",
        "files_uploaded": ["pathology_textbook.pdf", "disease_charts.png"],
        "processing_mode": "ocr"
    },
    {
        "session_id": str(uuid.uuid4()),
        "user_id": user_id,
        "session_name": "Pharmacology Notes",
        "created_at": datetime.utcnow() - timedelta(minutes=30),
        "status": "completed",
        "files_uploaded": ["drug_interactions.pdf"],
        "processing_mode": "default"
    }
]

# Insert sessions
for session in sessions:
    db.study_sessions.insert_one(session)
    print(f"✅ Created session: {session['session_name']}")

# Create some mock content for completed sessions
completed_sessions = [s for s in sessions if s["status"] == "completed"]

for session in completed_sessions:
    session_id = session["session_id"]
    
    # Mock questions
    for i in range(5):
        db.questions.insert_one({
            "session_id": session_id,
            "question_text": f"Sample question {i+1} for {session['session_name']}",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": 0,
            "explanation": "Sample explanation",
            "difficulty": "medium",
            "created_at": session["created_at"]
        })
    
    # Mock mock tests
    db.mock_tests.insert_one({
        "session_id": session_id,
        "test_name": f"Mock Test - {session['session_name']}",
        "questions": [],
        "duration_minutes": 60,
        "created_at": session["created_at"]
    })
    
    # Mock mnemonics
    for i in range(2):
        db.mnemonics.insert_one({
            "session_id": session_id,
            "topic": f"Topic {i+1}",
            "mnemonic_text": f"Sample mnemonic for {session['session_name']}",
            "explanation": "Memory aid explanation",
            "created_at": session["created_at"]
        })
    
    # Mock cheat sheet
    db.cheat_sheets.insert_one({
        "session_id": session_id,
        "title": f"Cheat Sheet - {session['session_name']}",
        "key_points": ["Point 1", "Point 2", "Point 3"],
        "created_at": session["created_at"]
    })
    
    # Mock notes
    db.notes.insert_one({
        "session_id": session_id,
        "title": f"Notes - {session['session_name']}",
        "content": "Compiled study notes content",
        "created_at": session["created_at"]
    })

print("🎉 Mock session data created successfully!")
client.close()
EOF

echo "✅ Mock data creation completed!"
echo ""
echo "🧪 Testing history API..."
curl -s -X GET "$API_BASE/api/v1/history/sessions" \
  -H "Authorization: Bearer $TOKEN" | head -200

echo ""
echo "🎉 History feature is ready for testing!"

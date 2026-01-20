#!/bin/bash

echo "🧪 Testing Mock Test Generation from PDF"
echo "======================================="

# Create a simple test PDF content
echo "Creating test PDF with medical content..."
echo "Human Anatomy - Cardiovascular System

The heart is a muscular organ that pumps blood throughout the body. It has four chambers: two atria and two ventricles.

Key Points:
- Right atrium receives deoxygenated blood from the body
- Left atrium receives oxygenated blood from the lungs  
- Right ventricle pumps blood to the lungs
- Left ventricle pumps blood to the body

The cardiac cycle consists of systole (contraction) and diastole (relaxation).

Important structures:
- Aorta: Main artery carrying blood from left ventricle
- Pulmonary artery: Carries blood from right ventricle to lungs
- Tricuspid valve: Between right atrium and ventricle
- Mitral valve: Between left atrium and ventricle

Clinical correlations:
- Heart failure occurs when the heart cannot pump effectively
- Myocardial infarction (heart attack) results from blocked coronary arteries
- Arrhythmias are abnormal heart rhythms" > test_medical_content.txt

# Upload the content and test processing
echo ""
echo "Testing upload and processing..."

response=$(curl -s -X POST "http://localhost:8000/api/v1/upload/" \
  -F "processing_mode=default" \
  -F "user_id=demo-user-123" \
  -F "files=@test_medical_content.txt")

if echo "$response" | grep -q "session_id"; then
    session_id=$(echo "$response" | grep -o '"session_id":"[^"]*"' | cut -d'"' -f4)
    echo "✅ Upload successful. Session ID: $session_id"
    
    # Wait for processing to complete
    echo "Waiting for processing to complete..."
    sleep 10
    
    # Check mock tests
    echo "Checking generated mock tests..."
    mock_tests=$(curl -s "http://localhost:8000/api/v1/mock-tests/$session_id")
    
    if echo "$mock_tests" | grep -q "mock_tests"; then
        test_count=$(echo "$mock_tests" | grep -o '"test_id"' | wc -l)
        echo "✅ Generated $test_count mock test(s)"
        
        # Show test details
        echo "$mock_tests" | python3 -m json.tool 2>/dev/null || echo "$mock_tests"
    else
        echo "❌ No mock tests generated"
        echo "Response: $mock_tests"
    fi
    
    # Check questions
    echo ""
    echo "Checking generated questions..."
    questions=$(curl -s "http://localhost:8000/api/v1/questions/$session_id")
    
    if echo "$questions" | grep -q "questions"; then
        question_count=$(echo "$questions" | grep -o '"question_id"' | wc -l)
        echo "✅ Generated $question_count questions for mock test"
    else
        echo "❌ No questions generated"
    fi
    
else
    echo "❌ Upload failed"
    echo "Response: $response"
fi

# Cleanup
rm -f test_medical_content.txt

echo ""
echo "🎯 Mock Test Generation Test Complete"

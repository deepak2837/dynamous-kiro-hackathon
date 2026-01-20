#!/bin/bash

echo "🧪 Testing Image Upload Limit (Max 25 images)"
echo "=============================================="

# Create test directory
mkdir -p test_images
cd test_images

# Create 30 small test images (more than the limit)
echo "Creating 30 test images..."
for i in {1..30}; do
    # Create a small 1x1 pixel PNG image
    echo -e '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82' > "test_image_$i.png"
done

echo "✅ Created 30 test images"

# Test with curl (simulate 26 images - should fail)
echo ""
echo "Testing backend API with 26 images (should fail)..."

# Create form data with 26 images
form_data=""
for i in {1..26}; do
    form_data="$form_data -F files=@test_image_$i.png"
done

response=$(curl -s -X POST "http://localhost:8000/api/v1/upload" \
  -F "processing_mode=default" \
  -F "user_id=demo-user-123" \
  $form_data)

echo "Response: $response"

if echo "$response" | grep -q "Too many images"; then
    echo "✅ Image limit validation working - rejected 26 images"
else
    echo "❌ Image limit validation failed"
fi

# Test with 25 images (should succeed)
echo ""
echo "Testing backend API with 25 images (should succeed)..."

form_data=""
for i in {1..25}; do
    form_data="$form_data -F files=@test_image_$i.png"
done

response=$(curl -s -X POST "http://localhost:8000/api/v1/upload" \
  -F "processing_mode=default" \
  -F "user_id=demo-user-123" \
  $form_data)

if echo "$response" | grep -q "session_id"; then
    echo "✅ 25 images accepted successfully"
else
    echo "❌ 25 images rejected (should be accepted)"
    echo "Response: $response"
fi

# Cleanup
cd ..
rm -rf test_images

echo ""
echo "🎯 Image Upload Limit Test Complete"
echo "Configuration: MAX_IMAGES_PER_UPLOAD=25"

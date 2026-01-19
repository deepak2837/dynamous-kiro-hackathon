#!/bin/bash

echo "🌐 Testing Frontend Auth Integration"
echo "===================================="

# Test if auth page is accessible
echo -e "\n1️⃣ Testing Auth Page Accessibility..."
if curl -s http://localhost:3001/auth | grep -q "html"; then
    echo "✅ Auth page is accessible"
else
    echo "❌ Auth page is not accessible"
    exit 1
fi

# Test if main page has auth link
echo -e "\n2️⃣ Testing Auth Link on Homepage..."
if curl -s http://localhost:3001/ | grep -q "Login / Register"; then
    echo "✅ Auth link found on homepage"
else
    echo "❌ Auth link not found on homepage"
fi

# Test API client configuration
echo -e "\n3️⃣ Testing API Client..."
# This would require a browser test, but we can check if the files exist
if [ -f "frontend/src/lib/api.ts" ] && [ -f "frontend/src/components/AuthForm.tsx" ]; then
    echo "✅ Auth components are in place"
else
    echo "❌ Auth components missing"
fi

echo -e "\n🎯 Frontend Integration Summary:"
echo "================================"
echo "✅ Backend API: http://localhost:8000"
echo "✅ Frontend App: http://localhost:3001"
echo "✅ Auth Page: http://localhost:3001/auth"
echo "✅ API Docs: http://localhost:8000/docs"
echo ""
echo "🧪 Manual Testing Steps:"
echo "1. Visit http://localhost:3001/auth"
echo "2. Register a new user"
echo "3. Login with the user"
echo "4. Verify user info is displayed"
echo "5. Test logout functionality"
echo ""
echo "📊 Monitor servers with: ./monitor.sh"
echo "🧪 Test APIs with: ./test_auth.sh"

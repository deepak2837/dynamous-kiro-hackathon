#!/bin/bash

echo "🚀 Both servers are running!"
echo "📊 Backend: http://localhost:8000"
echo "🌐 Frontend: http://localhost:3000"
echo "📋 API Docs: http://localhost:8000/docs"
echo ""
echo "🔍 Monitoring for errors... (Press Ctrl+C to stop)"
echo "=================================================="

# Test upload restrictions endpoint
echo "Testing upload restrictions endpoint..."
curl -s http://localhost:8000/api/v1/upload/check-upload-allowed/demo-user-123 | jq . 2>/dev/null || echo "❌ Upload restrictions endpoint error"

echo ""
echo "📊 Server Status:"
echo "Backend PID: $(cat .backend.pid 2>/dev/null || echo 'Not found')"
echo "Frontend PID: $(cat .frontend.pid 2>/dev/null || echo 'Not found')"
echo ""

# Monitor logs in real-time
echo "📝 Live logs (last 10 lines):"
echo "--- Backend ---"
tail -n 5 logs/backend.log 2>/dev/null || echo "No backend logs yet"
echo ""
echo "--- Frontend ---" 
tail -n 5 logs/frontend.log 2>/dev/null || echo "No frontend logs yet"
echo ""

echo "🔄 Monitoring... (showing new errors only)"
echo "=================================================="

# Monitor for new errors
tail -f logs/backend.log logs/frontend.log 2>/dev/null | while read line; do
    if echo "$line" | grep -iE "(error|exception|failed|traceback)" > /dev/null; then
        echo "🚨 ERROR: $line"
    fi
done

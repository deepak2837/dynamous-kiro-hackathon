#!/usr/bin/env python3
"""
Test script for mock test functionality
"""
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.api.v1.endpoints.mock_tests import get_mock_test
from backend.app.db.mongodb import get_database

async def test_mock_test_endpoint():
    """Test the mock test endpoint"""
    try:
        # Get database connection
        db = await get_database()
        
        # Find a mock test
        mock_test = await db.mock_tests.find_one()
        if not mock_test:
            print("No mock tests found in database")
            return
            
        print(f"Testing mock test: {mock_test['test_name']}")
        print(f"Test ID: {mock_test['test_id']}")
        print(f"Questions: {len(mock_test.get('questions', []))}")
        
        # Test the endpoint
        result = await get_mock_test(mock_test['test_id'], db)
        
        print(f"✅ Mock test endpoint working!")
        print(f"Test: {result['test'].test_name}")
        print(f"Questions returned: {len(result['questions'])}")
        
        # Check if questions have required fields
        for i, q in enumerate(result['questions'][:2]):  # Check first 2 questions
            print(f"\nQuestion {i+1}:")
            print(f"  ID: {q.get('question_id', 'Missing')}")
            print(f"  Text: {q.get('question_text', 'Missing')[:50]}...")
            print(f"  Options: {len(q.get('options', []))}")
            
            # Check options
            for j, opt in enumerate(q.get('options', [])[:2]):  # Check first 2 options
                print(f"    Option {j+1}: {opt.get('text', 'Missing')[:30]}... (Correct: {opt.get('is_correct', False)})")
        
    except Exception as e:
        print(f"❌ Error testing mock test endpoint: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mock_test_endpoint())

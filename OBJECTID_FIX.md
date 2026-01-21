# ObjectId Serialization Fix

## Problem
When clicking "Start Test" on mock tests, the backend was throwing:
```
TypeError: 'ObjectId' object is not iterable
TypeError: vars() argument must have __dict__ attribute
ValueError: [TypeError("'ObjectId' object is not iterable"), TypeError('vars() argument must have __dict__ attribute')]
```

## Root Cause
MongoDB documents contain `_id` fields with ObjectId values that cannot be serialized to JSON by FastAPI/Pydantic.

## Solution
1. **Created utility helper** (`backend/app/utils/db_helpers.py`):
   - `remove_object_id()` - Remove _id from single document
   - `remove_object_ids()` - Remove _id from list of documents  
   - `clean_mongo_document()` - Universal cleaner for documents/lists

2. **Fixed affected endpoints**:
   - `backend/app/api/v1/endpoints/mock_tests.py`
     - `get_session_mock_tests()` - Clean mock test documents
     - `get_mock_test()` - Clean test and question documents
   - `backend/app/api/v1/endpoints/questions.py`
     - `get_questions_by_session()` - Clean question documents

## Changes Made
- Added `clean_mongo_document()` calls before creating Pydantic models
- Replaced manual `del doc["_id"]` loops with utility function
- Consistent ObjectId handling across all endpoints

## Result
✅ Mock test "Start Test" button now works without ObjectId serialization errors
✅ Questions and test data properly serialized to JSON
✅ Frontend can successfully load test questions and display test interface

## Testing
- Created test script to verify ObjectId removal works correctly
- All MongoDB documents now properly cleaned before API responses

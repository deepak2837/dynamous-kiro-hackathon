import pytest
import sys
import os

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(backend_dir, '..'))

# Simple test fixtures without complex imports
@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "id": "test_user_123",
        "mobile": "9876543210",
        "created_at": "2026-01-22T10:00:00Z",
        "is_active": True
    }

@pytest.fixture
def sample_session_data():
    """Sample session data for testing"""
    return {
        "session_id": "session_123",
        "user_id": "user_123",
        "session_name": "Test Session",
        "status": "completed"
    }

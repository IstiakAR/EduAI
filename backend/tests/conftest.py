"""
Test configuration and fixtures for EduAI backend tests.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
import os
from unittest.mock import Mock

# Set test environment
os.environ["TESTING"] = "true"

from main import app
from app.core.config import get_settings
from app.db.database import db_manager

settings = get_settings()


@pytest.fixture
def client():
    """Test client for synchronous tests."""
    return TestClient(app)


@pytest_asyncio.fixture
async def async_client():
    """Async test client for async tests."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_supabase():
    """Mock Supabase client for testing."""
    mock_client = Mock()
    mock_client.table.return_value = mock_client
    mock_client.select.return_value = mock_client
    mock_client.insert.return_value = mock_client
    mock_client.update.return_value = mock_client
    mock_client.delete.return_value = mock_client
    mock_client.eq.return_value = mock_client
    mock_client.execute.return_value.data = []
    return mock_client


@pytest.fixture
def sample_user():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "password": "testpassword123"
    }


@pytest.fixture
def sample_question():
    """Sample question data for testing."""
    return {
        "content": "What is 2 + 2?",
        "question_type": "mcq",
        "subject": "Mathematics",
        "topic": "Basic Arithmetic",
        "difficulty": "easy",
        "options": ["3", "4", "5", "6"],
        "correct_answer": "4",
        "explanation": "2 + 2 equals 4"
    }


@pytest.fixture
def sample_exam():
    """Sample exam data for testing."""
    return {
        "title": "Basic Math Test",
        "description": "A simple mathematics test",
        "subject": "Mathematics",
        "difficulty": "easy",
        "duration_minutes": 30,
        "total_marks": 50
    }


@pytest.fixture
def auth_headers(client, sample_user):
    """Create authenticated user and return auth headers."""
    # Register user
    response = client.post("/api/v1/auth/register", json=sample_user)
    assert response.status_code == 201
    
    # Login to get token
    login_data = {
        "username": sample_user["email"],
        "password": sample_user["password"]
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class MockGeminiService:
    """Mock Gemini service for testing."""
    
    async def generate_question(self, subject, topic, difficulty, question_type):
        return {
            "content": f"Sample {question_type} question about {topic}",
            "question_type": question_type,
            "subject": subject,
            "topic": topic,
            "difficulty": difficulty,
            "options": ["A", "B", "C", "D"] if question_type == "mcq" else None,
            "correct_answer": "A" if question_type == "mcq" else "Sample answer",
            "explanation": "Sample explanation"
        }
    
    async def evaluate_answer(self, question, answer, question_type):
        return {
            "is_correct": True,
            "score": 0.85,
            "feedback": "Good answer!",
            "explanation": "Sample explanation"
        }
    
    async def answer_question(self, question):
        return {
            "answer": "Sample answer",
            "explanation": "Sample explanation",
            "sources": []
        }


@pytest.fixture
def mock_gemini_service():
    """Mock Gemini service fixture."""
    return MockGeminiService()


# Test utilities
def assert_response_success(response, expected_status=200):
    """Assert that response is successful."""
    assert response.status_code == expected_status
    assert "detail" not in response.json() or response.json()["detail"] is None


def assert_response_error(response, expected_status, expected_detail=None):
    """Assert that response contains expected error."""
    assert response.status_code == expected_status
    if expected_detail:
        assert expected_detail in response.json()["detail"]


def create_test_question(client, headers, question_data=None):
    """Helper to create a test question."""
    if question_data is None:
        question_data = {
            "content": "Test question?",
            "question_type": "mcq",
            "subject": "Test Subject",
            "topic": "Test Topic",
            "difficulty": "easy",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A",
            "explanation": "Test explanation"
        }
    
    response = client.post("/api/v1/questions/create", json=question_data, headers=headers)
    assert_response_success(response, 201)
    return response.json()


def create_test_exam(client, headers, exam_data=None):
    """Helper to create a test exam."""
    if exam_data is None:
        exam_data = {
            "title": "Test Exam",
            "description": "A test exam",
            "subject": "Test Subject",
            "difficulty": "easy",
            "duration_minutes": 30,
            "total_marks": 50
        }
    
    response = client.post("/api/v1/exams/create", json=exam_data, headers=headers)
    assert_response_success(response, 201)
    return response.json()
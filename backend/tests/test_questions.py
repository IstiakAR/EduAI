"""
Test suite for question generation and management endpoints.
"""
import pytest
from unittest.mock import patch
from tests.conftest import assert_response_success, assert_response_error, create_test_question


class TestQuestionGeneration:
    """Test question generation endpoints."""
    
    @patch('app.services.gemini_service.GeminiService.generate_question')
    def test_generate_single_question(self, mock_generate, client, auth_headers):
        """Test generating a single question."""
        mock_generate.return_value = {
            "content": "What is 2 + 2?",
            "question_type": "mcq",
            "subject": "Mathematics",
            "topic": "Basic Arithmetic",
            "difficulty": "easy",
            "options": ["3", "4", "5", "6"],
            "correct_answer": "4",
            "explanation": "2 + 2 equals 4"
        }
        
        request_data = {
            "subject": "Mathematics",
            "topic": "Basic Arithmetic",
            "difficulty": "easy",
            "question_type": "mcq"
        }
        
        response = client.post("/api/v1/questions/generate", json=request_data, headers=auth_headers)
        assert_response_success(response, 201)
        
        data = response.json()
        assert data["content"] == "What is 2 + 2?"
        assert data["question_type"] == "mcq"
        assert data["subject"] == "Mathematics"
        assert len(data["options"]) == 4
        assert "id" in data
    
    @patch('app.services.gemini_service.GeminiService.generate_question')
    def test_generate_bulk_questions(self, mock_generate, client, auth_headers):
        """Test generating multiple questions."""
        mock_generate.return_value = {
            "content": "Sample question",
            "question_type": "mcq",
            "subject": "Mathematics",
            "topic": "Algebra",
            "difficulty": "medium",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A",
            "explanation": "Sample explanation"
        }
        
        request_data = {
            "count": 3,
            "subject": "Mathematics",
            "topic": "Algebra",
            "difficulty": "medium",
            "question_type": "mcq"
        }
        
        response = client.post("/api/v1/questions/generate/bulk", json=request_data, headers=auth_headers)
        assert_response_success(response, 201)
        
        data = response.json()
        assert len(data["questions"]) == 3
        assert data["total_generated"] == 3
        assert all(q["subject"] == "Mathematics" for q in data["questions"])
    
    def test_generate_question_unauthorized(self, client):
        """Test generating question without authorization."""
        request_data = {
            "subject": "Mathematics",
            "topic": "Basic Arithmetic",
            "difficulty": "easy",
            "question_type": "mcq"
        }
        
        response = client.post("/api/v1/questions/generate", json=request_data)
        assert_response_error(response, 401)
    
    def test_generate_question_invalid_type(self, client, auth_headers):
        """Test generating question with invalid type."""
        request_data = {
            "subject": "Mathematics",
            "topic": "Basic Arithmetic",
            "difficulty": "easy",
            "question_type": "invalid_type"
        }
        
        response = client.post("/api/v1/questions/generate", json=request_data, headers=auth_headers)
        assert_response_error(response, 422)
    
    def test_generate_question_invalid_difficulty(self, client, auth_headers):
        """Test generating question with invalid difficulty."""
        request_data = {
            "subject": "Mathematics",
            "topic": "Basic Arithmetic",
            "difficulty": "invalid_difficulty",
            "question_type": "mcq"
        }
        
        response = client.post("/api/v1/questions/generate", json=request_data, headers=auth_headers)
        assert_response_error(response, 422)


class TestQuestionManagement:
    """Test question management endpoints."""
    
    def test_create_question_manual(self, client, auth_headers, sample_question):
        """Test creating a question manually."""
        response = client.post("/api/v1/questions/create", json=sample_question, headers=auth_headers)
        assert_response_success(response, 201)
        
        data = response.json()
        assert data["content"] == sample_question["content"]
        assert data["question_type"] == sample_question["question_type"]
        assert data["subject"] == sample_question["subject"]
        assert "id" in data
        assert "created_at" in data
    
    def test_get_question_by_id(self, client, auth_headers, sample_question):
        """Test getting a question by ID."""
        # Create question first
        create_response = client.post("/api/v1/questions/create", json=sample_question, headers=auth_headers)
        question_id = create_response.json()["id"]
        
        # Get question
        response = client.get(f"/api/v1/questions/{question_id}", headers=auth_headers)
        assert_response_success(response)
        
        data = response.json()
        assert data["id"] == question_id
        assert data["content"] == sample_question["content"]
    
    def test_get_question_not_found(self, client, auth_headers):
        """Test getting non-existent question."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/v1/questions/{fake_id}", headers=auth_headers)
        assert_response_error(response, 404)
    
    def test_update_question(self, client, auth_headers, sample_question):
        """Test updating a question."""
        # Create question first
        create_response = client.post("/api/v1/questions/create", json=sample_question, headers=auth_headers)
        question_id = create_response.json()["id"]
        
        # Update question
        update_data = {
            "content": "Updated question content",
            "explanation": "Updated explanation"
        }
        response = client.patch(f"/api/v1/questions/{question_id}", json=update_data, headers=auth_headers)
        assert_response_success(response)
        
        data = response.json()
        assert data["content"] == update_data["content"]
        assert data["explanation"] == update_data["explanation"]
    
    def test_delete_question(self, client, auth_headers, sample_question):
        """Test deleting a question."""
        # Create question first
        create_response = client.post("/api/v1/questions/create", json=sample_question, headers=auth_headers)
        question_id = create_response.json()["id"]
        
        # Delete question
        response = client.delete(f"/api/v1/questions/{question_id}", headers=auth_headers)
        assert_response_success(response, 204)
        
        # Verify deletion
        get_response = client.get(f"/api/v1/questions/{question_id}", headers=auth_headers)
        assert_response_error(get_response, 404)


class TestQuestionSearch:
    """Test question search and filtering endpoints."""
    
    def test_search_questions_by_subject(self, client, auth_headers):
        """Test searching questions by subject."""
        # Create test questions
        math_question = {
            "content": "Math question",
            "question_type": "mcq",
            "subject": "Mathematics",
            "topic": "Algebra",
            "difficulty": "easy",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A",
            "explanation": "Math explanation"
        }
        
        physics_question = {
            "content": "Physics question",
            "question_type": "short",
            "subject": "Physics",
            "topic": "Mechanics",
            "difficulty": "medium",
            "correct_answer": "Physics answer",
            "explanation": "Physics explanation"
        }
        
        client.post("/api/v1/questions/create", json=math_question, headers=auth_headers)
        client.post("/api/v1/questions/create", json=physics_question, headers=auth_headers)
        
        # Search for math questions
        response = client.get("/api/v1/questions/search?subject=Mathematics", headers=auth_headers)
        assert_response_success(response)
        
        data = response.json()
        assert len(data["questions"]) >= 1
        assert all(q["subject"] == "Mathematics" for q in data["questions"])
    
    def test_filter_questions_by_difficulty(self, client, auth_headers):
        """Test filtering questions by difficulty."""
        response = client.get("/api/v1/questions/search?difficulty=easy", headers=auth_headers)
        assert_response_success(response)
        
        data = response.json()
        # Should return questions (may be empty if none exist)
        assert "questions" in data
        assert "total" in data
    
    def test_filter_questions_by_type(self, client, auth_headers):
        """Test filtering questions by type."""
        response = client.get("/api/v1/questions/search?question_type=mcq", headers=auth_headers)
        assert_response_success(response)
        
        data = response.json()
        assert "questions" in data
        if data["questions"]:
            assert all(q["question_type"] == "mcq" for q in data["questions"])
    
    def test_search_questions_pagination(self, client, auth_headers):
        """Test question search with pagination."""
        response = client.get("/api/v1/questions/search?limit=5&offset=0", headers=auth_headers)
        assert_response_success(response)
        
        data = response.json()
        assert "questions" in data
        assert "total" in data
        assert len(data["questions"]) <= 5
    
    def test_get_subjects(self, client, auth_headers):
        """Test getting available subjects."""
        response = client.get("/api/v1/questions/subjects", headers=auth_headers)
        assert_response_success(response)
        
        data = response.json()
        assert "subjects" in data
        assert isinstance(data["subjects"], list)
    
    def test_get_topics_by_subject(self, client, auth_headers):
        """Test getting topics for a specific subject."""
        response = client.get("/api/v1/questions/topics?subject=Mathematics", headers=auth_headers)
        assert_response_success(response)
        
        data = response.json()
        assert "topics" in data
        assert isinstance(data["topics"], list)


class TestQuestionValidation:
    """Test question validation."""
    
    def test_create_question_missing_content(self, client, auth_headers):
        """Test creating question without content."""
        invalid_question = {
            "question_type": "mcq",
            "subject": "Mathematics",
            "difficulty": "easy"
        }
        
        response = client.post("/api/v1/questions/create", json=invalid_question, headers=auth_headers)
        assert_response_error(response, 422)
    
    def test_create_mcq_without_options(self, client, auth_headers):
        """Test creating MCQ without options."""
        invalid_mcq = {
            "content": "What is 2 + 2?",
            "question_type": "mcq",
            "subject": "Mathematics",
            "difficulty": "easy",
            "correct_answer": "4"
        }
        
        response = client.post("/api/v1/questions/create", json=invalid_mcq, headers=auth_headers)
        assert_response_error(response, 422)
    
    def test_create_question_invalid_difficulty(self, client, auth_headers):
        """Test creating question with invalid difficulty."""
        invalid_question = {
            "content": "Test question",
            "question_type": "short",
            "subject": "Mathematics",
            "difficulty": "invalid",
            "correct_answer": "Answer"
        }
        
        response = client.post("/api/v1/questions/create", json=invalid_question, headers=auth_headers)
        assert_response_error(response, 422)
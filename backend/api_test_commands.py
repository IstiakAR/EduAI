#!/usr/bin/env python3
"""
Quick API endpoint test commands for Gemini integration
"""

# First, make sure your FastAPI server is running with:
# uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Then you can test individual endpoints:

# 1. Test Health Endpoint
print("1. Test Health Endpoint:")
print("curl http://localhost:8000/health")
print()

# 2. Test Question Generation (requires authentication)
print("2. Test Question Generation:")
print("""curl -X POST "http://localhost:8000/api/v1/questions/generate" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  -d '{
    "subject": "Mathematics",
    "topic": "Algebra",
    "difficulty": "easy",
    "question_type": "mcq",
    "num_questions": 2
  }'""")
print()

# 3. Test Answer Evaluation
print("3. Test Answer Evaluation:")
print("""curl -X POST "http://localhost:8000/api/v1/evaluation/answer" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  -d '{
    "question_id": "some-uuid",
    "question_text": "What is 2 + 2?",
    "user_answer": "4",
    "correct_answer": "4",
    "question_type": "short"
  }'""")
print()

# 4. Test AI Assistant
print("4. Test AI Assistant:")
print("""curl -X POST "http://localhost:8000/api/v1/assistant/ask" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  -d '{
    "question": "What is a variable in programming?",
    "subject": "Computer Science",
    "difficulty": "easy",
    "context": {}
  }'""")
print()

# 5. Simple Python test script to check without authentication
print("5. Simple Python test (no auth needed):")
print("""
import requests

# Test health endpoint
response = requests.get("http://localhost:8000/health")
print(f"Health check: {response.status_code} - {response.json()}")

# Note: Other endpoints require authentication token
""")
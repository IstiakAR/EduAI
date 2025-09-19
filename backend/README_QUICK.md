# EduAI Backend - Quick Setup Guide

## 🎯 What This Is
- AI-powered educational platform backend
- FastAPI + Supabase + Google Gemini 2.0 Flash
- Question generation, answer evaluation, academic assistance

## 📋 Quick Setup

### Prerequisites
- Python 3.8+
- Supabase account
- Google Gemini API key

### Installation
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Environment Setup
- Create `.env` file in project root
- Add required variables:
```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=your_jwt_secret_key
```

### Database Setup
- Go to Supabase Dashboard → SQL Editor
- Run: `python init_db.py`
- Copy generated SQL and execute in Supabase

### Run Server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
- Server: http://localhost:8000
- Docs: http://localhost:8000/docs

## 🧪 Test Everything
```bash
# Test Gemini API
python test_gemini.py

# Test health endpoint
curl http://localhost:8000/health
```

## 🔑 Main API Endpoints

### Authentication
- `POST /api/v1/auth/signup` - Register user
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/refresh` - Refresh token

### Questions (AI-Powered)
- `POST /api/v1/questions/generate` - Generate questions with AI
- `GET /api/v1/questions/` - List questions
- `GET /api/v1/questions/{id}` - Get specific question

### Evaluation (AI-Powered)
- `POST /api/v1/evaluation/answer` - Evaluate single answer
- `POST /api/v1/evaluation/exam` - Evaluate full exam
- `POST /api/v1/evaluation/batch` - Batch evaluation

### AI Assistant
- `POST /api/v1/assistant/ask` - Ask academic questions
- `POST /api/v1/assistant/explain` - Get concept explanations
- `POST /api/v1/assistant/solve` - Get problem solutions

### Analytics
- `GET /api/v1/analytics/progress` - User progress
- `GET /api/v1/analytics/dashboard` - Dashboard data
- `GET /api/v1/analytics/performance` - Performance metrics

## 🏗️ Architecture

### Key Components
- **FastAPI**: Web framework
- **Supabase**: Database (PostgreSQL)
- **Gemini 2.0 Flash**: AI for questions/evaluation
- **JWT**: Authentication
- **Pydantic**: Data validation

### Database Tables
- `users` - User accounts
- `questions` - Generated questions
- `exams` - Exam sessions
- `answers` - User answers
- `results` - Evaluation results
- `progress` - Learning progress

### AI Integration Points
- **Question Generation**: Gemini creates MCQ/short/long questions
- **Answer Evaluation**: AI scoring with detailed feedback
- **Academic Assistant**: AI tutor for explanations and help
- **Content Enhancement**: AI-powered question improvements

## 🔧 Development

### Project Structure
```
app/
├── api/          # Route handlers
├── core/         # Configuration
├── db/           # Database layer
├── schemas/      # API models
└── services/     # Business logic
```

### Key Files
- `main.py` - Application entry point
- `app/core/config.py` - Settings
- `app/services/gemini_service.py` - AI integration
- `app/db/database.py` - Supabase connection
- `init_db.py` - Database setup

### Testing
```bash
# Run all tests
pytest

# Test specific component
python test_gemini.py

# Test API endpoints
python api_test_commands.py
```

## 🚨 Common Issues

### Connection Errors
- Check Supabase URL/keys in `.env`
- Verify Supabase project is active
- Ensure tables are created

### AI Errors
- Verify GEMINI_API_KEY is correct
- Check API quota limits
- Test with `python test_gemini.py`

### Import Errors
- Activate virtual environment
- Install requirements: `pip install -r requirements.txt`
- Check Python path

### Database Errors
- Run database initialization: `python init_db.py`
- Check Supabase connection
- Verify table schemas

## 📱 Frontend Integration

### CORS Setup
- Frontend URLs configured in `ALLOWED_ORIGINS`
- Default: localhost:3000, localhost:5173

### Authentication Flow
1. POST to `/api/v1/auth/login`
2. Get `access_token` and `refresh_token`
3. Include `Authorization: Bearer <token>` in requests
4. Refresh token before expiry

### Example Frontend Usage
```javascript
// Login
const response = await fetch('/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password })
});

// Use token
const token = response.access_token;
const questions = await fetch('/api/v1/questions/generate', {
  method: 'POST',
  headers: { 
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ topic: 'Python', difficulty: 'easy' })
});
```

## 🎯 Quick Commands

```bash
# Start development server
uvicorn main:app --reload

# Test AI integration
python test_gemini.py

# Initialize database
python init_db.py

# Check health
curl http://localhost:8000/health

# View API docs
open http://localhost:8000/docs
```

## 🔗 Resources

- **API Documentation**: http://localhost:8000/docs
- **Supabase Dashboard**: https://supabase.com/dashboard
- **Gemini AI**: https://ai.google.dev/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
# EduAI Backend - AI-Based Exam Preparation & Assessment Tool

A comprehensive FastAPI-based backend for an AI-powered educational platform that provides intelligent question generation, answer evaluation, academic assistance, and learning analytics using Google Gemini 2.0 Flash API and Supabase.

## 🚀 Features

### 🎯 Core Functionality
- **AI Question Generation**: Generate MCQ, short, and long questions using Google Gemini 2.0 Flash
- **Intelligent Evaluation**: AI-powered answer assessment with detailed feedback
- **Academic Assistant**: Interactive AI tutor for academic questions and explanations
- **Learning Analytics**: Comprehensive progress tracking and performance metrics
- **User Management**: JWT-based authentication with Supabase integration

### 🔐 Authentication & Security
- JWT-based authentication with refresh tokens
- Secure password hashing with bcrypt
- Rate limiting and security middleware
- CORS protection for frontend integration

## 🛠 Technology Stack

- **Framework**: FastAPI (Python 3.8+)
- **Database**: Supabase (PostgreSQL) - NO LOCAL DATABASE REQUIRED
- **AI Service**: Google Gemini 2.0 Flash API
- **Authentication**: JWT tokens
- **Validation**: Pydantic schemas
- **Testing**: Pytest with async support

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/                 # API route handlers
│   │   ├── auth.py         # Authentication endpoints
│   │   ├── questions.py    # Question generation & management
│   │   ├── evaluation.py   # Answer evaluation endpoints
│   │   ├── assistant.py    # AI assistant endpoints
│   │   └── analytics.py    # Analytics & progress endpoints
│   ├── core/               # Core configuration
│   │   ├── config.py       # Application settings
│   │   └── security.py     # Security utilities
│   ├── db/                 # Database layer
│   │   ├── models.py       # Pydantic models
│   │   ├── database.py     # Supabase connection
│   │   ├── crud.py         # CRUD operations
│   │   └── schema.py       # SQL table definitions
│   ├── schemas/            # API schemas
│   │   ├── auth.py         # Authentication schemas
│   │   ├── user.py         # User schemas
│   │   ├── question.py     # Question schemas
│   │   ├── exam.py         # Exam schemas
│   │   └── analytics.py    # Analytics schemas
│   └── services/           # Business logic
│       ├── gemini_service.py      # Google Gemini AI integration
│       ├── evaluation_service.py  # Answer evaluation logic
│       └── assistant_service.py   # Academic assistance
├── tests/                  # Test suite
├── main.py                # Application entry point
├── requirements.txt       # Python dependencies
├── init_db.py            # Database initialization
└── .env.example          # Environment template
```

## 🔧 Installation & Setup

### Prerequisites

- Python 3.8 or higher
- Supabase account and project
- Google Gemini API key

### 1. Clone and Setup

```bash
git clone <repository-url>
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
cp .env.example .env
```

Edit `.env` file with your actual values:

```env
# Application Settings
APP_NAME=EduAI
VERSION=1.0.0
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Security Settings
SECRET_KEY=your-super-secret-key-here-generate-a-strong-one
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Supabase Configuration (ONLY DATABASE NEEDED)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-role-key

# Google Gemini AI Configuration
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.0-flash
GEMINI_API_URL=https://generativelanguage.googleapis.com/v1beta

# CORS Settings (for frontend integration)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000
```

### 3. Database Setup

Initialize your Supabase database:

```bash
python init_db.py
```

This will create all necessary tables in your Supabase project. **No local PostgreSQL installation required!**

### 4. Run the Application

```bash
# Development mode with auto-reload
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or use the convenient start script
python start_dev.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## 📚 API Documentation for Frontend Integration

### Base URL
```
http://localhost:8000
```

### Authentication Headers
```javascript
// For authenticated endpoints, include JWT token
headers: {
  'Authorization': 'Bearer your-jwt-token',
  'Content-Type': 'application/json'
}
```

---

## 🔐 Authentication Endpoints

### 1. User Registration
```http
POST /api/v1/auth/register
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "johndoe",
    "full_name": "John Doe",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### 2. User Login
```http
POST /api/v1/auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:** Same as registration

### 3. Refresh Token
```http
POST /api/v1/auth/refresh
```

**Request Body:**
```json
{
  "refresh_token": "your-refresh-token"
}
```

**Response:**
```json
{
  "access_token": "new-access-token",
  "token_type": "bearer"
}
```

### 4. Get User Profile
```http
GET /api/v1/auth/profile
```

**Headers:** `Authorization: Bearer {token}`

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "avatar_url": null,
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-01T00:00:00Z",
  "last_login": "2024-01-01T00:00:00Z"
}
```

---

## 📝 Question Management Endpoints

### 1. Generate Single Question
```http
POST /api/v1/questions/generate
```

**Headers:** `Authorization: Bearer {token}`

**Request Body:**
```json
{
  "subject": "Mathematics",
  "topic": "Algebra",
  "difficulty": "medium",
  "question_type": "mcq",
  "context": "Basic algebraic equations"
}
```

**Response:**
```json
{
  "id": "question-uuid",
  "question_text": "Solve for x: 2x + 5 = 15",
  "question_type": "mcq",
  "subject": "Mathematics",
  "topic": "Algebra",
  "difficulty": "medium",
  "options": ["x = 5", "x = 10", "x = 3", "x = 7"],
  "correct_answer": "x = 5",
  "explanation": "Subtract 5 from both sides: 2x = 10, then divide by 2: x = 5",
  "points": 1,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### 2. Generate Multiple Questions
```http
POST /api/v1/questions/generate/bulk
```

**Request Body:**
```json
{
  "subject": "Physics",
  "topic": "Mechanics",
  "difficulty": "hard",
  "question_type": "mcq",
  "count": 5,
  "context": "Newton's laws of motion"
}
```

**Response:**
```json
{
  "questions": [
    {
      "id": "uuid1",
      "question_text": "What is Newton's first law?",
      // ... other question fields
    },
    // ... more questions
  ],
  "total_generated": 5,
  "generation_time": 3.2
}
```

### 3. Search Questions
```http
GET /api/v1/questions/search?subject=Mathematics&topic=Algebra&difficulty=medium&limit=10&offset=0
```

**Response:**
```json
{
  "questions": [
    {
      "id": "uuid",
      "question_text": "Solve for x...",
      // ... question fields
    }
  ],
  "total": 25,
  "limit": 10,
  "offset": 0
}
```

### 4. Get Available Subjects
```http
GET /api/v1/questions/subjects
```

**Response:**
```json
{
  "subjects": [
    "Mathematics",
    "Physics", 
    "Chemistry",
    "Biology",
    "Computer Science",
    "English",
    "History"
  ]
}
```

### 5. Get Topics by Subject
```http
GET /api/v1/questions/topics?subject=Mathematics
```

**Response:**
```json
{
  "subject": "Mathematics",
  "topics": [
    "Algebra",
    "Geometry", 
    "Calculus",
    "Statistics",
    "Trigonometry"
  ]
}
```

---

## 🎯 Answer Evaluation Endpoints

### 1. Evaluate Single Answer
```http
POST /api/v1/evaluation/answer
```

**Headers:** `Authorization: Bearer {token}`

**Request Body:**
```json
{
  "question_id": "question-uuid",
  "answer_text": "x = 5",
  "time_taken_seconds": 45
}
```

**Response:**
```json
{
  "answer_id": "answer-uuid",
  "question_id": "question-uuid",
  "is_correct": true,
  "score": 1.0,
  "max_score": 1.0,
  "feedback": "Correct! You solved the equation properly.",
  "detailed_feedback": {
    "accuracy": "Perfect",
    "approach": "Correct algebraic manipulation",
    "suggestions": []
  },
  "time_taken_seconds": 45
}
```

### 2. Evaluate Exam Submission
```http
POST /api/v1/evaluation/exam
```

**Request Body:**
```json
{
  "exam_id": "exam-uuid",
  "answers": [
    {
      "question_id": "q1-uuid",
      "answer_text": "Answer 1",
      "time_taken_seconds": 60
    },
    {
      "question_id": "q2-uuid", 
      "answer_text": "Answer 2",
      "time_taken_seconds": 90
    }
  ]
}
```

**Response:**
```json
{
  "result_id": "result-uuid",
  "exam_id": "exam-uuid",
  "total_questions": 2,
  "correct_answers": 1,
  "total_score": 1.0,
  "max_score": 2.0,
  "percentage": 50.0,
  "time_taken_minutes": 3,
  "subject": "Mathematics",
  "difficulty": "medium",
  "answers": [
    {
      "question_id": "q1-uuid",
      "is_correct": true,
      "score": 1.0,
      "feedback": "Excellent work!"
    },
    {
      "question_id": "q2-uuid", 
      "is_correct": false,
      "score": 0.0,
      "feedback": "Review the concept of..."
    }
  ],
  "strengths": ["Algebra", "Problem solving"],
  "weaknesses": ["Geometry"],
  "recommendations": [
    "Practice more geometry problems",
    "Review basic geometric formulas"
  ]
}
```

---

## 🤖 AI Assistant Endpoints

### 1. Ask Academic Question
```http
POST /api/v1/assistant/ask
```

**Headers:** `Authorization: Bearer {token}`

**Request Body:**
```json
{
  "question": "What is the quadratic formula?",
  "subject": "Mathematics",
  "context": {
    "level": "high_school",
    "previous_topics": ["algebra", "equations"]
  },
  "use_web_search": true
}
```

**Response:**
```json
{
  "question": "What is the quadratic formula?",
  "answer": "The quadratic formula is x = (-b ± √(b²-4ac)) / 2a, used to solve quadratic equations of the form ax² + bx + c = 0.",
  "sources": [
    {
      "title": "Quadratic Formula",
      "url": "https://en.wikipedia.org/wiki/Quadratic_formula",
      "type": "wikipedia"
    }
  ],
  "confidence": "high",
  "subject": "Mathematics",
  "related_topics": ["discriminant", "parabola", "completing_the_square"],
  "follow_up_questions": [
    "How do you derive the quadratic formula?",
    "When do you use the quadratic formula?",
    "What is the discriminant?"
  ]
}
```

### 2. Explain Concept
```http
POST /api/v1/assistant/explain
```

**Request Body:**
```json
{
  "concept": "Photosynthesis",
  "subject": "Biology",
  "level": "intermediate",
  "include_examples": true
}
```

**Response:**
```json
{
  "concept": "Photosynthesis",
  "subject": "Biology", 
  "level": "intermediate",
  "explanation": "Photosynthesis is the process by which plants convert light energy into chemical energy...",
  "key_points": [
    "Occurs in chloroplasts",
    "Requires light, carbon dioxide, and water",
    "Produces glucose and oxygen",
    "Two main stages: light reactions and Calvin cycle"
  ],
  "examples": [
    "Green plants producing oxygen during daylight",
    "Algae in aquatic environments"
  ],
  "related_concepts": ["chlorophyll", "cellular_respiration", "carbon_cycle"]
}
```

### 3. Get Study Suggestions
```http
GET /api/v1/assistant/suggestions?subject=Physics&current_topic=mechanics&difficulty=medium
```

**Response:**
```json
{
  "subject": "Physics",
  "current_topic": "mechanics",
  "suggestions": [
    {
      "type": "practice",
      "title": "Practice Force Problems",
      "description": "Work on problems involving Newton's laws",
      "estimated_time_minutes": 30,
      "difficulty": "medium"
    },
    {
      "type": "concept_review",
      "title": "Review Energy Conservation",
      "description": "Study kinetic and potential energy relationships",
      "estimated_time_minutes": 20,
      "difficulty": "medium"
    }
  ],
  "recommended_topics": ["energy", "momentum", "oscillations"],
  "difficulty_progression": "Consider moving to thermodynamics next"
}
```

---

## 📊 Analytics & Progress Endpoints

### 1. User Progress Summary
```http
GET /api/v1/analytics/progress?subject=Mathematics
```

**Headers:** `Authorization: Bearer {token}`

**Response:**
```json
{
  "user_id": "user-uuid",
  "subject": "Mathematics",
  "overall_progress": {
    "total_questions_attempted": 150,
    "total_questions_correct": 120,
    "average_accuracy": 80.0,
    "total_score": 145.5,
    "current_streak": 5,
    "best_streak": 12,
    "total_study_time_minutes": 720,
    "level": 3,
    "total_points": 1455
  },
  "topic_progress": [
    {
      "topic": "Algebra",
      "questions_attempted": 50,
      "questions_correct": 45,
      "accuracy": 90.0,
      "last_activity": "2024-01-01T10:00:00Z"
    },
    {
      "topic": "Geometry", 
      "questions_attempted": 30,
      "questions_correct": 20,
      "accuracy": 66.7,
      "last_activity": "2024-01-01T09:00:00Z"
    }
  ],
  "recent_results": [
    {
      "date": "2024-01-01",
      "score": 8.5,
      "max_score": 10,
      "topic": "Algebra"
    }
  ]
}
```

### 2. Performance Metrics
```http
GET /api/v1/analytics/performance?period=weekly
```

**Response:**
```json
{
  "period": "weekly",
  "metrics": {
    "accuracy_trend": [
      {"date": "2024-01-01", "accuracy": 75.0},
      {"date": "2024-01-02", "accuracy": 78.0},
      {"date": "2024-01-03", "accuracy": 82.0}
    ],
    "study_time_trend": [
      {"date": "2024-01-01", "minutes": 45},
      {"date": "2024-01-02", "minutes": 60},
      {"date": "2024-01-03", "minutes": 30}
    ],
    "questions_per_day": [
      {"date": "2024-01-01", "count": 15},
      {"date": "2024-01-02", "count": 20},
      {"date": "2024-01-03", "count": 10}
    ]
  },
  "improvement_areas": ["Geometry", "Statistics"],
  "strong_areas": ["Algebra", "Calculus"]
}
```

### 3. Dashboard Data
```http
GET /api/v1/analytics/dashboard
```

**Response:**
```json
{
  "user_stats": {
    "total_questions": 500,
    "correct_answers": 400,
    "accuracy": 80.0,
    "current_level": 5,
    "points": 4000,
    "rank": 15
  },
  "recent_activity": [
    {
      "type": "quiz_completed",
      "subject": "Physics",
      "score": "8/10",
      "time": "2024-01-01T10:00:00Z"
    }
  ],
  "upcoming_goals": [
    {
      "type": "accuracy",
      "target": 85,
      "current": 80,
      "deadline": "2024-01-07"
    }
  ],
  "recommendations": [
    "Practice more Physics problems",
    "Review Chemistry fundamentals"
  ]
}
```

---

## 🏥 Health & Utility Endpoints

### 1. Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": 1640995200.0,
  "database": "connected",
  "version": "1.0.0"
}
```

---

## 🚨 Error Handling

All endpoints return consistent error responses:

### Error Response Format
```json
{
  "detail": "Error message",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Common HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `422` - Unprocessable Entity (validation error)
- `429` - Too Many Requests (rate limited)
- `500` - Internal Server Error

---

## 💡 Frontend Integration Examples

### React/JavaScript Example

```javascript
// API client setup
const API_BASE_URL = 'http://localhost:8000';

class EduAIClient {
  constructor() {
    this.token = localStorage.getItem('access_token');
  }

  async login(email, password) {
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });
    
    if (response.ok) {
      const data = await response.json();
      this.token = data.access_token;
      localStorage.setItem('access_token', this.token);
      localStorage.setItem('refresh_token', data.refresh_token);
      return data;
    }
    throw new Error('Login failed');
  }

  async generateQuestion(subject, topic, difficulty, questionType) {
    const response = await fetch(`${API_BASE_URL}/api/v1/questions/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`,
      },
      body: JSON.stringify({
        subject,
        topic,
        difficulty,
        question_type: questionType,
      }),
    });
    
    if (response.ok) {
      return await response.json();
    }
    throw new Error('Question generation failed');
  }

  async evaluateAnswer(questionId, answerText, timeTaken) {
    const response = await fetch(`${API_BASE_URL}/api/v1/evaluation/answer`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`,
      },
      body: JSON.stringify({
        question_id: questionId,
        answer_text: answerText,
        time_taken_seconds: timeTaken,
      }),
    });
    
    if (response.ok) {
      return await response.json();
    }
    throw new Error('Answer evaluation failed');
  }

  async getUserProgress(subject = null) {
    const url = subject 
      ? `${API_BASE_URL}/api/v1/analytics/progress?subject=${subject}`
      : `${API_BASE_URL}/api/v1/analytics/progress`;
      
    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${this.token}`,
      },
    });
    
    if (response.ok) {
      return await response.json();
    }
    throw new Error('Failed to fetch progress');
  }
}

// Usage example
const client = new EduAIClient();

// Login
await client.login('user@example.com', 'password');

// Generate a question
const question = await client.generateQuestion(
  'Mathematics', 
  'Algebra', 
  'medium', 
  'mcq'
);

// Evaluate answer
const evaluation = await client.evaluateAnswer(
  question.id, 
  'x = 5', 
  45
);

// Get progress
const progress = await client.getUserProgress('Mathematics');
```

### Frontend State Management

```javascript
// React context for authentication
import React, { createContext, useContext, useReducer } from 'react';

const AuthContext = createContext();

const authReducer = (state, action) => {
  switch (action.type) {
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        isAuthenticated: true,
        user: action.payload.user,
        token: action.payload.access_token,
      };
    case 'LOGOUT':
      return {
        ...state,
        isAuthenticated: false,
        user: null,
        token: null,
      };
    default:
      return state;
  }
};

export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, {
    isAuthenticated: false,
    user: null,
    token: localStorage.getItem('access_token'),
  });

  return (
    <AuthContext.Provider value={{ state, dispatch }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
```

---

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py -v
```

---

## 🚀 Deployment

### Environment Variables for Production

```env
DEBUG=false
HOST=0.0.0.0
PORT=8000
SECRET_KEY=production-secret-key-very-long-and-secure
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Using Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 📞 Support & Contributing

For support and questions:
- 📖 **API Documentation**: http://localhost:8000/docs
- 🐛 **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- 📧 **Email**: support@eduai.com

**Built with ❤️ for better education through AI**
- **Gamification**: Points, levels, badges, and leaderboards to motivate learning

### 🔐 Authentication & Security
- JWT-based authentication with refresh tokens
- Secure password hashing with bcrypt
- Role-based access control
- Rate limiting and security middleware

### 📊 Analytics & Insights
- Individual progress tracking by subject and topic
- Performance metrics and improvement trends
- Personalized study recommendations
- Strengths and weaknesses analysis
- Interactive dashboards and leaderboards

## 🛠 Technology Stack

- **Framework**: FastAPI (Python 3.8+)
- **Database**: Supabase (PostgreSQL)
- **AI Service**: Google Gemini API
- **Authentication**: JWT tokens
- **ORM**: SQLAlchemy with async support
- **Validation**: Pydantic schemas
- **Testing**: Pytest with async support
- **Documentation**: Auto-generated OpenAPI/Swagger

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/                 # API route handlers
│   │   ├── auth.py         # Authentication endpoints
│   │   ├── questions.py    # Question generation & management
│   │   ├── evaluation.py   # Answer evaluation endpoints
│   │   ├── assistant.py    # AI assistant endpoints
│   │   └── analytics.py    # Analytics & progress endpoints
│   ├── core/               # Core configuration
│   │   ├── config.py       # Application settings
│   │   └── security.py     # Security utilities
│   ├── db/                 # Database layer
│   │   ├── models.py       # SQLAlchemy models
│   │   ├── database.py     # Database connection
│   │   └── crud.py         # CRUD operations
│   ├── schemas/            # Pydantic schemas
│   │   ├── auth.py         # Authentication schemas
│   │   ├── questions.py    # Question schemas
│   │   ├── evaluation.py   # Evaluation schemas
│   │   ├── assistant.py    # Assistant schemas
│   │   └── analytics.py    # Analytics schemas
│   └── services/           # Business logic
│       ├── gemini_service.py      # AI service integration
│       ├── evaluation_service.py  # Answer evaluation logic
│       └── assistant_service.py   # Academic assistance
├── tests/                  # Test suite
├── main.py                # Application entry point
├── requirements.txt       # Python dependencies
├── init_db.py            # Database initialization
└── .env.example          # Environment template
```

## 🔧 Installation & Setup

### Prerequisites

- Python 3.8 or higher
- Supabase account and project
- Google Gemini API key

### 1. Clone and Setup

```bash
git clone <repository-url>
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
cp .env.example .env
```

Edit `.env` file with your actual values:

```env
# Application Settings
APP_NAME=EduAI
DEBUG=true
SECRET_KEY=your-super-secret-key-here

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-role-key

# Google Gemini AI
GEMINI_API_KEY=your-gemini-api-key

# CORS Settings
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 3. Database Setup

Initialize your Supabase database:

```bash
python init_db.py
```

This will create all necessary tables and seed initial data.

### 4. Run the Application

```bash
# Development mode with auto-reload
python -m uvicorn main:app --reload

# Production mode
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## 📚 API Documentation

### Authentication Endpoints

```
POST   /api/v1/auth/register     # User registration
POST   /api/v1/auth/login        # User login
POST   /api/v1/auth/refresh      # Refresh access token
GET    /api/v1/auth/profile      # Get user profile
PATCH  /api/v1/auth/profile      # Update user profile
POST   /api/v1/auth/change-password  # Change password
```

### Question Management

```
POST   /api/v1/questions/generate     # Generate single question
POST   /api/v1/questions/generate/bulk # Generate multiple questions
POST   /api/v1/questions/create       # Create question manually
GET    /api/v1/questions/{id}         # Get question by ID
PATCH  /api/v1/questions/{id}         # Update question
DELETE /api/v1/questions/{id}         # Delete question
GET    /api/v1/questions/search       # Search questions
GET    /api/v1/questions/subjects     # Get available subjects
GET    /api/v1/questions/topics       # Get topics by subject
```

### Answer Evaluation

```
POST   /api/v1/evaluate/answer        # Evaluate single answer
POST   /api/v1/evaluate/exam          # Evaluate exam submission
POST   /api/v1/evaluate/batch         # Batch evaluate answers
GET    /api/v1/evaluate/results/{id}  # Get evaluation result
```

### AI Assistant

```
POST   /api/v1/assistant/ask          # Ask academic question
POST   /api/v1/assistant/explain      # Explain concept
POST   /api/v1/assistant/solve        # Solve problem step-by-step
GET    /api/v1/assistant/suggestions  # Get study suggestions
```

### Analytics & Progress

```
GET    /api/v1/analytics/progress         # User progress summary
GET    /api/v1/analytics/progress/overall # Overall progress stats
GET    /api/v1/analytics/performance      # Performance metrics
GET    /api/v1/analytics/dashboard        # Dashboard data
GET    /api/v1/analytics/leaderboard      # Global leaderboard
GET    /api/v1/analytics/recommendations  # Study recommendations
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

## 🚀 Deployment

### Using Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables for Production

```env
DEBUG=false
HOST=0.0.0.0
PORT=8000
SECRET_KEY=production-secret-key
ALLOWED_ORIGINS=https://yourdomain.com
```

## 📊 Database Schema

### Core Tables

- **users**: User accounts with authentication and profile data
- **questions**: Generated and manually created questions
- **exams**: Exam configurations and metadata
- **answers**: User answers with AI evaluation results
- **results**: Exam results and performance metrics
- **progress**: Learning progress tracking by subject/topic

### Key Relationships

- Users can create questions and take exams
- Questions can be part of multiple exams
- Answers link users, questions, and exams
- Progress tracks user learning across subjects

## 🤖 AI Integration

### Gemini AI Features

- **Question Generation**: Create contextual questions based on subject/topic
- **Answer Evaluation**: Intelligent scoring with detailed feedback
- **Concept Explanation**: Academic assistance and tutoring
- **Personalization**: Adaptive learning recommendations

### Evaluation Criteria

- **Accuracy**: Correctness of the answer
- **Completeness**: Thoroughness of explanation
- **Clarity**: Clear communication of concepts
- **Depth**: Level of understanding demonstrated

## 🔐 Security Features

- **JWT Authentication**: Secure stateless authentication
- **Password Security**: Bcrypt hashing with salt
- **CORS Protection**: Configurable cross-origin policies
- **Rate Limiting**: API endpoint protection
- **Input Validation**: Pydantic schema validation
- **SQL Injection Prevention**: SQLAlchemy ORM protection

## 📈 Performance & Scalability

- **Async/Await**: Non-blocking database operations
- **Connection Pooling**: Efficient database connections
- **Caching**: Redis integration for performance
- **Pagination**: Efficient large dataset handling
- **Background Tasks**: Async processing for heavy operations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation as needed
- Use type hints for better code clarity

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:

- 📧 Email: support@eduai.com
- 📖 Documentation: http://localhost:8000/docs
- 🐛 Issues: [GitHub Issues](https://github.com/your-repo/issues)

## 🗺 Roadmap

### Upcoming Features

- [ ] Real-time collaboration
- [ ] Video content integration
- [ ] Advanced analytics dashboard
- [ ] Mobile app support
- [ ] Multilingual support
- [ ] Integration with LMS platforms

### Performance Improvements

- [ ] Advanced caching strategies
- [ ] Database query optimization
- [ ] CDN integration for static content
- [ ] Microservices architecture

---

**Built with ❤️ for better education through AI**
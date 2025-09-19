"""
Data models for the EduAI application (Pydantic Models for Validation).

Note: These are Pydantic models for data validation and API documentation.
The actual database tables are created and managed through Supabase.
See app/db/schema.py for the SQL table definitions.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr
import uuid


class User(BaseModel):
    """User model for authentication and profile management."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    username: str
    hashed_password: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Question(BaseModel):
    """Question model for storing generated questions."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question_text: str
    question_type: str  # mcq, short, long
    subject: str
    topic: str
    difficulty: str  # easy, medium, hard
    options: Optional[List[str]] = None  # For MCQ options
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    points: int = 1
    tags: Optional[List[str]] = None  # Additional tags for categorization
    created_by: Optional[str] = None  # AI or specific user
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Exam(BaseModel):
    """Exam model for organizing questions into assessments."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = None
    subject: str
    total_questions: int
    total_points: int
    time_limit_minutes: Optional[int] = None
    difficulty: str
    is_adaptive: bool = False
    is_published: bool = False
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ExamQuestion(BaseModel):
    """Junction model for exam-question relationship."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    exam_id: str
    question_id: str
    order: int
    points: int = 1
    
    class Config:
        from_attributes = True


class Answer(BaseModel):
    """Answer model for storing user responses."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question_id: str
    user_id: str
    result_id: Optional[str] = None
    answer_text: str
    is_correct: Optional[bool] = None
    score: Optional[float] = None  # For partial credit
    feedback: Optional[str] = None
    time_taken_seconds: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class Result(BaseModel):
    """Result model for storing exam/quiz results."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    exam_id: Optional[str] = None
    total_questions: int
    correct_answers: int
    total_score: float
    max_score: float
    percentage: float
    time_taken_minutes: Optional[int] = None
    completed_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Additional metrics
    subject: str
    difficulty: str
    topics_covered: Optional[List[str]] = None
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    
    class Config:
        from_attributes = True


class Progress(BaseModel):
    """Progress tracking model for gamification and analytics."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    subject: str
    topic: Optional[str] = None
    
    # Progress metrics
    total_questions_attempted: int = 0
    total_questions_correct: int = 0
    total_score: float = 0.0
    average_accuracy: float = 0.0
    streak_count: int = 0
    best_streak: int = 0
    
    # Gamification
    total_points: int = 0
    level: int = 1
    badges: Optional[List[str]] = None
    
    # Time tracking
    total_study_time_minutes: int = 0
    last_activity: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class StudySession(BaseModel):
    """Study session model for tracking learning activities."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    session_type: str  # quiz, study, practice
    subject: str
    topics: Optional[List[str]] = None
    duration_minutes: int
    questions_attempted: int = 0
    questions_correct: int = 0
    score: float = 0.0
    started_at: datetime
    completed_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class AIInteraction(BaseModel):
    """Model for tracking AI assistant interactions."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    interaction_type: str  # question_generation, evaluation, assistant
    prompt: str
    response: str
    context: Optional[Dict[str, Any]] = None  # Additional context data
    tokens_used: Optional[int] = None
    response_time_ms: Optional[int] = None
    feedback_rating: Optional[int] = None  # 1-5 rating
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


# Request/Response schemas for API endpoints
class UserCreate(BaseModel):
    """Schema for creating a new user."""
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    """Schema for user response (without password)."""
    id: str
    email: str
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None


class QuestionCreate(BaseModel):
    """Schema for creating a new question."""
    question_text: str
    question_type: str
    subject: str
    topic: str
    difficulty: str
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    points: int = 1
    tags: Optional[List[str]] = None


class ExamCreate(BaseModel):
    """Schema for creating a new exam."""
    title: str
    description: Optional[str] = None
    subject: str
    total_questions: int
    total_points: int
    time_limit_minutes: Optional[int] = None
    difficulty: str
    is_adaptive: bool = False


class AnswerSubmit(BaseModel):
    """Schema for submitting an answer."""
    question_id: str
    answer_text: str
    time_taken_seconds: Optional[int] = None


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token data."""
    user_id: Optional[str] = None
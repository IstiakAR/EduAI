"""
Pydantic schemas for question-related operations.
"""
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class QuestionType(str, Enum):
    """Question type enumeration."""
    MCQ = "mcq"
    SHORT = "short"
    LONG = "long"


class Difficulty(str, Enum):
    """Difficulty level enumeration."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class MCQOption(BaseModel):
    """MCQ option schema."""
    option_id: str = Field(..., description="Unique identifier for the option (A, B, C, D)")
    text: str = Field(..., min_length=1, max_length=500)
    is_correct: bool = False


class QuestionBase(BaseModel):
    """Base question schema."""
    question_text: str = Field(..., min_length=10, max_length=2000)
    question_type: QuestionType
    subject: str = Field(..., min_length=1, max_length=100)
    topic: str = Field(..., min_length=1, max_length=100)
    difficulty: Difficulty
    explanation: Optional[str] = Field(None, max_length=1000)
    points: int = Field(default=1, ge=1, le=10)
    tags: Optional[List[str]] = []


class QuestionCreate(QuestionBase):
    """Schema for question creation."""
    options: Optional[List[MCQOption]] = None
    correct_answer: Optional[str] = Field(None, max_length=1000)


class QuestionResponse(QuestionBase):
    """Schema for question responses."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    options: Optional[List[Dict[str, Any]]] = None
    correct_answer: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class QuestionForExam(BaseModel):
    """Schema for questions in exams (without correct answers)."""
    id: str
    question_text: str
    question_type: QuestionType
    options: Optional[List[Dict[str, str]]] = None  # Without is_correct field
    points: int
    tags: Optional[List[str]] = []


class QuestionGenerationRequest(BaseModel):
    """Schema for question generation requests."""
    subject: str = Field(..., min_length=1, max_length=100)
    topic: str = Field(..., min_length=1, max_length=100)
    difficulty: Difficulty
    question_type: QuestionType
    num_questions: int = Field(default=5, ge=1, le=50)
    additional_context: Optional[str] = Field(None, max_length=500)
    include_explanations: bool = True


class QuestionGenerationResponse(BaseModel):
    """Schema for question generation responses."""
    questions: List[QuestionResponse]
    total_generated: int
    generation_time_seconds: float
    metadata: Dict[str, Any] = {}


class QuestionBulkCreate(BaseModel):
    """Schema for bulk question creation."""
    questions: List[QuestionCreate]


class QuestionSearchRequest(BaseModel):
    """Schema for question search requests."""
    subject: Optional[str] = None
    topic: Optional[str] = None
    difficulty: Optional[Difficulty] = None
    question_type: Optional[QuestionType] = None
    tags: Optional[List[str]] = None
    search_text: Optional[str] = Field(None, max_length=200)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class QuestionSearchResponse(BaseModel):
    """Schema for question search responses."""
    questions: List[QuestionResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int


class QuestionUpdate(BaseModel):
    """Schema for question updates."""
    question_text: Optional[str] = Field(None, min_length=10, max_length=2000)
    explanation: Optional[str] = Field(None, max_length=1000)
    points: Optional[int] = Field(None, ge=1, le=10)
    tags: Optional[List[str]] = None
    options: Optional[List[MCQOption]] = None
    correct_answer: Optional[str] = Field(None, max_length=1000)


class QuestionStats(BaseModel):
    """Schema for question statistics."""
    question_id: str
    total_attempts: int
    correct_attempts: int
    accuracy_percentage: float
    average_time_seconds: float
    difficulty_rating: float
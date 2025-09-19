"""
Pydantic schemas for exam-related operations.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.question import QuestionForExam, Difficulty


class ExamBase(BaseModel):
    """Base exam schema."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    subject: str = Field(..., min_length=1, max_length=100)
    difficulty: Difficulty
    time_limit_minutes: Optional[int] = Field(None, ge=1, le=300)
    is_adaptive: bool = False


class ExamCreate(ExamBase):
    """Schema for exam creation."""
    question_ids: List[str] = Field(..., min_items=1, max_items=100)


class ExamGenerate(BaseModel):
    """Schema for auto-generating exams."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    subject: str = Field(..., min_length=1, max_length=100)
    topics: List[str] = Field(..., min_items=1, max_items=10)
    difficulty: Difficulty
    num_questions: int = Field(..., ge=5, le=100)
    question_types: List[str] = Field(default=["mcq"], min_items=1)
    time_limit_minutes: Optional[int] = Field(None, ge=1, le=300)
    is_adaptive: bool = False


class ExamResponse(ExamBase):
    """Schema for exam responses."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    total_questions: int
    total_points: int
    is_published: bool
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class ExamWithQuestions(ExamResponse):
    """Schema for exam with questions."""
    questions: List[QuestionForExam]


class ExamUpdate(BaseModel):
    """Schema for exam updates."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    time_limit_minutes: Optional[int] = Field(None, ge=1, le=300)
    is_published: Optional[bool] = None


class ExamSubmission(BaseModel):
    """Schema for exam submission."""
    exam_id: str
    answers: List[Dict[str, Any]] = Field(..., min_items=1)
    time_taken_minutes: Optional[int] = Field(None, ge=1)


class ExamAnswer(BaseModel):
    """Schema for individual exam answers."""
    question_id: str
    answer_text: str = Field(..., min_length=1, max_length=5000)
    time_taken_seconds: Optional[int] = Field(None, ge=1)


class ExamResult(BaseModel):
    """Schema for exam results."""
    result_id: str
    exam_id: str
    total_questions: int
    correct_answers: int
    total_score: float
    max_score: float
    percentage: float
    time_taken_minutes: Optional[int]
    completed_at: datetime
    strengths: List[str] = []
    weaknesses: List[str] = []
    feedback: str = ""


class ExamResultDetailed(ExamResult):
    """Detailed exam results with question-by-question breakdown."""
    question_results: List[Dict[str, Any]]


class ExamAttemptStart(BaseModel):
    """Schema for starting an exam attempt."""
    exam_id: str


class ExamAttemptResponse(BaseModel):
    """Schema for exam attempt response."""
    attempt_id: str
    exam: ExamWithQuestions
    started_at: datetime
    time_limit_minutes: Optional[int]
    instructions: str = ""


class ExamList(BaseModel):
    """Schema for exam list responses."""
    exams: List[ExamResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int


class ExamSearchRequest(BaseModel):
    """Schema for exam search requests."""
    subject: Optional[str] = None
    difficulty: Optional[Difficulty] = None
    is_published: Optional[bool] = None
    search_text: Optional[str] = Field(None, max_length=200)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class ExamStats(BaseModel):
    """Schema for exam statistics."""
    exam_id: str
    total_attempts: int
    average_score: float
    highest_score: float
    lowest_score: float
    average_completion_time_minutes: float
    completion_rate: float
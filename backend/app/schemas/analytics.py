"""
Pydantic schemas for analytics and progress tracking.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field, ConfigDict


class ProgressBase(BaseModel):
    """Base progress schema."""
    subject: str = Field(..., min_length=1, max_length=100)
    topic: Optional[str] = Field(None, max_length=100)


class ProgressResponse(ProgressBase):
    """Schema for progress responses."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    user_id: str
    total_questions_attempted: int
    total_questions_correct: int
    total_score: float
    average_accuracy: float
    streak_count: int
    best_streak: int
    total_points: int
    level: int
    badges: List[str] = []
    total_study_time_minutes: int
    last_activity: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class ProgressUpdate(BaseModel):
    """Schema for progress updates."""
    questions_attempted: int = Field(default=0, ge=0)
    questions_correct: int = Field(default=0, ge=0)
    score_gained: float = Field(default=0.0, ge=0.0)
    study_time_minutes: int = Field(default=0, ge=0)
    is_correct_streak: bool = False


class SubjectProgress(BaseModel):
    """Schema for subject-level progress."""
    subject: str
    total_questions: int
    correct_answers: int
    accuracy_percentage: float
    total_study_time_minutes: int
    level: int
    points: int
    topics: List[Dict[str, Any]] = []


class OverallProgress(BaseModel):
    """Schema for overall user progress."""
    user_id: str
    total_questions_attempted: int
    total_questions_correct: int
    overall_accuracy: float
    total_study_time_minutes: int
    total_points: int
    current_level: int
    total_badges: int
    subjects: List[SubjectProgress]


class PerformanceMetrics(BaseModel):
    """Schema for performance metrics."""
    period: str  # daily, weekly, monthly
    date_range: Dict[str, date]
    total_sessions: int
    total_time_minutes: int
    questions_attempted: int
    questions_correct: int
    accuracy_percentage: float
    average_session_duration: float
    improvement_rate: float


class StrengthWeaknessAnalysis(BaseModel):
    """Schema for strength and weakness analysis."""
    strengths: List[Dict[str, Any]]
    weaknesses: List[Dict[str, Any]]
    recommendations: List[str]
    focus_areas: List[str]


class LearningAnalytics(BaseModel):
    """Schema for learning analytics."""
    user_id: str
    date_range: Dict[str, date]
    performance_metrics: PerformanceMetrics
    subject_breakdown: List[SubjectProgress]
    strength_weakness: StrengthWeaknessAnalysis
    learning_velocity: float
    consistency_score: float
    difficulty_progression: Dict[str, float]


class StudySessionBase(BaseModel):
    """Base study session schema."""
    session_type: str = Field(..., pattern="^(quiz|study|practice)$")
    subject: str = Field(..., min_length=1, max_length=100)
    topics: List[str] = []
    duration_minutes: int = Field(..., ge=1)


class StudySessionCreate(StudySessionBase):
    """Schema for creating study sessions."""
    pass


class StudySessionResponse(StudySessionBase):
    """Schema for study session responses."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    user_id: str
    questions_attempted: int
    questions_correct: int
    score: float
    started_at: datetime
    completed_at: datetime


class DashboardData(BaseModel):
    """Schema for dashboard data."""
    user_id: str
    overall_progress: OverallProgress
    recent_performance: PerformanceMetrics
    upcoming_goals: List[Dict[str, Any]]
    achievements: List[Dict[str, Any]]
    study_streak: int
    daily_goal_progress: float
    weekly_summary: Dict[str, Any]


class GoalBase(BaseModel):
    """Base goal schema."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    target_value: float = Field(..., gt=0)
    current_value: float = Field(default=0.0, ge=0)
    goal_type: str = Field(..., pattern="^(questions|accuracy|study_time|streak)$")
    target_date: Optional[date] = None


class GoalCreate(GoalBase):
    """Schema for goal creation."""
    pass


class GoalResponse(GoalBase):
    """Schema for goal responses."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    user_id: str
    is_completed: bool
    completion_percentage: float
    created_at: datetime
    completed_at: Optional[datetime] = None


class LeaderboardEntry(BaseModel):
    """Schema for leaderboard entries."""
    user_id: str
    username: str
    points: int
    level: int
    accuracy: float
    streak: int
    rank: int


class LeaderboardResponse(BaseModel):
    """Schema for leaderboard responses."""
    period: str  # weekly, monthly, all_time
    subject: Optional[str] = None
    entries: List[LeaderboardEntry]
    user_rank: Optional[int] = None
    total_participants: int


class RecommendationBase(BaseModel):
    """Base recommendation schema."""
    title: str
    description: str
    recommendation_type: str  # study_topic, difficulty_adjustment, break_suggestion
    priority: int = Field(..., ge=1, le=5)
    estimated_time_minutes: Optional[int] = None


class StudyRecommendations(BaseModel):
    """Schema for study recommendations."""
    user_id: str
    recommendations: List[RecommendationBase]
    generated_at: datetime
    valid_until: datetime
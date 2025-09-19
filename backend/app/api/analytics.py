"""
Analytics API endpoints for performance tracking and insights.
"""
from typing import List, Optional
from datetime import datetime, date, timedelta
from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.schemas.analytics import (
    ProgressResponse, OverallProgress, PerformanceMetrics,
    LearningAnalytics, StudySessionResponse, DashboardData,
    GoalCreate, GoalResponse, LeaderboardResponse, StudyRecommendations
)
from app.core.security import get_current_user_id
from app.db.crud import progress_crud, result_crud, user_crud

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/progress", response_model=List[ProgressResponse])
async def get_user_progress(
    subject: Optional[str] = Query(None),
    user_id: str = Depends(get_current_user_id)
):
    """Get user's learning progress across subjects."""
    
    try:
        progress_records = await progress_crud.get_user_progress(user_id, subject)
        return [ProgressResponse(**record) for record in progress_records]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get progress: {str(e)}"
        )


@router.get("/progress/overall", response_model=OverallProgress)
async def get_overall_progress(
    user_id: str = Depends(get_current_user_id)
):
    """Get overall progress summary for the user."""
    
    try:
        # Get all progress records
        progress_records = await progress_crud.get_user_progress(user_id)
        
        # Calculate overall metrics
        total_questions = sum(p["total_questions_attempted"] for p in progress_records)
        total_correct = sum(p["total_questions_correct"] for p in progress_records)
        total_study_time = sum(p["total_study_time_minutes"] for p in progress_records)
        total_points = sum(p["total_points"] for p in progress_records)
        
        overall_accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0
        current_level = max((p["level"] for p in progress_records), default=1)
        
        # Group by subject
        subject_progress = {}
        for record in progress_records:
            subject = record["subject"]
            if subject not in subject_progress:
                subject_progress[subject] = {
                    "subject": subject,
                    "total_questions": 0,
                    "correct_answers": 0,
                    "accuracy_percentage": 0,
                    "total_study_time_minutes": 0,
                    "level": 1,
                    "points": 0,
                    "topics": []
                }
            
            subj_prog = subject_progress[subject]
            subj_prog["total_questions"] += record["total_questions_attempted"]
            subj_prog["correct_answers"] += record["total_questions_correct"]
            subj_prog["total_study_time_minutes"] += record["total_study_time_minutes"]
            subj_prog["level"] = max(subj_prog["level"], record["level"])
            subj_prog["points"] += record["total_points"]
            
            if record["topic"]:
                subj_prog["topics"].append({
                    "topic": record["topic"],
                    "accuracy": record["average_accuracy"]
                })
        
        # Calculate accuracy for each subject
        for subj_prog in subject_progress.values():
            if subj_prog["total_questions"] > 0:
                subj_prog["accuracy_percentage"] = (
                    subj_prog["correct_answers"] / subj_prog["total_questions"] * 100
                )
        
        return OverallProgress(
            user_id=user_id,
            total_questions_attempted=total_questions,
            total_questions_correct=total_correct,
            overall_accuracy=overall_accuracy,
            total_study_time_minutes=total_study_time,
            total_points=total_points,
            current_level=current_level,
            total_badges=0,  # TODO: Implement badge counting
            subjects=list(subject_progress.values())
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get overall progress: {str(e)}"
        )


@router.get("/performance", response_model=PerformanceMetrics)
async def get_performance_metrics(
    period: str = Query("weekly", pattern="^(daily|weekly|monthly)$"),
    user_id: str = Depends(get_current_user_id)
):
    """Get performance metrics for a specific period."""
    
    try:
        # Calculate date range based on period
        end_date = date.today()
        if period == "daily":
            start_date = end_date - timedelta(days=1)
        elif period == "weekly":
            start_date = end_date - timedelta(weeks=1)
        else:  # monthly
            start_date = end_date - timedelta(days=30)
        
        # Get results for the period
        results = await result_crud.get_user_results(user_id, limit=100)
        
        # Filter results by date range
        period_results = [
            r for r in results 
            if start_date <= datetime.fromisoformat(r["completed_at"]).date() <= end_date
        ]
        
        if not period_results:
            return PerformanceMetrics(
                period=period,
                date_range={"start": start_date, "end": end_date},
                total_sessions=0,
                total_time_minutes=0,
                questions_attempted=0,
                questions_correct=0,
                accuracy_percentage=0,
                average_session_duration=0,
                improvement_rate=0
            )
        
        # Calculate metrics
        total_sessions = len(period_results)
        total_time = sum(r.get("time_taken_minutes", 0) for r in period_results)
        total_questions = sum(r["total_questions"] for r in period_results)
        total_correct = sum(r["correct_answers"] for r in period_results)
        
        accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0
        avg_session_duration = total_time / total_sessions if total_sessions > 0 else 0
        
        # Calculate improvement rate (simplified)
        improvement_rate = 0
        if len(period_results) > 1:
            first_half = period_results[:len(period_results)//2]
            second_half = period_results[len(period_results)//2:]
            
            first_accuracy = sum(r["percentage"] for r in first_half) / len(first_half)
            second_accuracy = sum(r["percentage"] for r in second_half) / len(second_half)
            
            improvement_rate = second_accuracy - first_accuracy
        
        return PerformanceMetrics(
            period=period,
            date_range={"start": start_date, "end": end_date},
            total_sessions=total_sessions,
            total_time_minutes=total_time,
            questions_attempted=total_questions,
            questions_correct=total_correct,
            accuracy_percentage=accuracy,
            average_session_duration=avg_session_duration,
            improvement_rate=improvement_rate
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance metrics: {str(e)}"
        )


@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard_data(
    user_id: str = Depends(get_current_user_id)
):
    """Get comprehensive dashboard data for the user."""
    
    try:
        # Get overall progress
        overall_progress = await get_overall_progress(user_id)
        
        # Get recent performance
        recent_performance = await get_performance_metrics("weekly", user_id)
        
        # Mock data for other dashboard elements
        dashboard_data = DashboardData(
            user_id=user_id,
            overall_progress=overall_progress,
            recent_performance=recent_performance,
            upcoming_goals=[
                {"title": "Complete 50 math problems", "progress": 75, "deadline": "2024-01-15"},
                {"title": "Achieve 90% accuracy in physics", "progress": 60, "deadline": "2024-01-20"}
            ],
            achievements=[
                {"title": "First Perfect Score", "description": "Scored 100% on a quiz", "date": "2024-01-01"},
                {"title": "Study Streak", "description": "7 days of continuous study", "date": "2024-01-05"}
            ],
            study_streak=7,  # TODO: Calculate from actual data
            daily_goal_progress=75.0,  # TODO: Calculate from goals
            weekly_summary={
                "total_study_time": recent_performance.total_time_minutes,
                "questions_completed": recent_performance.questions_attempted,
                "average_score": recent_performance.accuracy_percentage,
                "subjects_studied": 3  # TODO: Calculate from actual data
            }
        )
        
        return dashboard_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard data: {str(e)}"
        )


@router.get("/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard(
    period: str = Query("weekly", pattern="^(weekly|monthly|all_time)$"),
    subject: Optional[str] = Query(None),
    user_id: str = Depends(get_current_user_id)
):
    """Get leaderboard for competitive learning."""
    
    try:
        # TODO: Implement actual leaderboard calculation
        # This would require aggregating user progress and ranking
        
        mock_entries = [
            {
                "user_id": "user1",
                "username": "TopLearner",
                "points": 15000,
                "level": 15,
                "accuracy": 95.5,
                "streak": 25,
                "rank": 1
            },
            {
                "user_id": "user2", 
                "username": "StudyMaster",
                "points": 12000,
                "level": 12,
                "accuracy": 92.0,
                "streak": 18,
                "rank": 2
            },
            {
                "user_id": user_id,
                "username": "You",
                "points": 8000,
                "level": 8,
                "accuracy": 88.5,
                "streak": 12,
                "rank": 5
            }
        ]
        
        return LeaderboardResponse(
            period=period,
            subject=subject,
            entries=mock_entries,
            user_rank=5,
            total_participants=100
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get leaderboard: {str(e)}"
        )


@router.get("/recommendations", response_model=StudyRecommendations)
async def get_study_recommendations(
    user_id: str = Depends(get_current_user_id)
):
    """Get personalized study recommendations."""
    
    try:
        # TODO: Implement AI-powered recommendation system
        # This would analyze user performance and suggest improvements
        
        recommendations = [
            {
                "title": "Focus on Algebra",
                "description": "Your accuracy in algebra is below average. Spend more time on practice problems.",
                "recommendation_type": "study_topic",
                "priority": 5,
                "estimated_time_minutes": 30
            },
            {
                "title": "Take a Break",
                "description": "You've been studying for 3 hours. Consider taking a 15-minute break.",
                "recommendation_type": "break_suggestion",
                "priority": 3,
                "estimated_time_minutes": 15
            },
            {
                "title": "Increase Difficulty",
                "description": "You're consistently scoring above 90% on medium questions. Try hard level.",
                "recommendation_type": "difficulty_adjustment",
                "priority": 4,
                "estimated_time_minutes": None
            }
        ]
        
        return StudyRecommendations(
            user_id=user_id,
            recommendations=recommendations,
            generated_at=datetime.utcnow(),
            valid_until=datetime.utcnow() + timedelta(hours=24)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recommendations: {str(e)}"
        )


@router.get("/strengths-weaknesses")
async def get_strengths_weaknesses(
    subject: Optional[str] = Query(None),
    user_id: str = Depends(get_current_user_id)
):
    """Get detailed analysis of strengths and weaknesses."""
    
    try:
        # TODO: Implement actual analysis based on user performance data
        
        return {
            "subject": subject or "All subjects",
            "strengths": [
                {
                    "area": "Basic Algebra",
                    "accuracy": 95.0,
                    "confidence": "high",
                    "note": "Consistently strong performance"
                },
                {
                    "area": "Geometry Basics",
                    "accuracy": 88.0,
                    "confidence": "medium",
                    "note": "Good understanding with room for improvement"
                }
            ],
            "weaknesses": [
                {
                    "area": "Advanced Calculus",
                    "accuracy": 65.0,
                    "confidence": "low",
                    "note": "Needs significant practice and review"
                },
                {
                    "area": "Word Problems",
                    "accuracy": 72.0,
                    "confidence": "low",
                    "note": "Difficulty in problem interpretation"
                }
            ],
            "recommendations": [
                "Focus on calculus fundamentals",
                "Practice more word problems",
                "Review mathematical reasoning skills"
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze strengths and weaknesses: {str(e)}"
        )


@router.get("/trends")
async def get_learning_trends(
    days: int = Query(30, ge=7, le=365),
    user_id: str = Depends(get_current_user_id)
):
    """Get learning trends over time."""
    
    try:
        # TODO: Implement actual trend analysis
        
        # Generate mock trend data
        trends = {
            "accuracy_trend": [
                {"date": "2024-01-01", "accuracy": 75.0},
                {"date": "2024-01-02", "accuracy": 78.0},
                {"date": "2024-01-03", "accuracy": 82.0},
                {"date": "2024-01-04", "accuracy": 85.0},
                {"date": "2024-01-05", "accuracy": 88.0}
            ],
            "study_time_trend": [
                {"date": "2024-01-01", "minutes": 45},
                {"date": "2024-01-02", "minutes": 60},
                {"date": "2024-01-03", "minutes": 30},
                {"date": "2024-01-04", "minutes": 75},
                {"date": "2024-01-05", "minutes": 90}
            ],
            "subject_performance": {
                "Mathematics": {"accuracy": 85.0, "trend": "improving"},
                "Physics": {"accuracy": 78.0, "trend": "stable"},
                "Chemistry": {"accuracy": 82.0, "trend": "declining"}
            },
            "insights": [
                "Your accuracy has improved by 13% over the past week",
                "You're most productive during evening study sessions",
                "Mathematics shows the strongest improvement trend"
            ]
        }
        
        return trends
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get learning trends: {str(e)}"
        )
"""
Evaluation API endpoints for answer assessment.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.question import QuestionType
from app.core.security import get_current_user_id
from app.services.evaluation_service import evaluation_service
from app.db.crud import question_crud
from pydantic import BaseModel, Field

router = APIRouter(prefix="/evaluate", tags=["Evaluation"])


class SingleAnswerRequest(BaseModel):
    """Request schema for single answer evaluation."""
    question_id: str
    answer_text: str = Field(..., min_length=1, max_length=5000)
    time_taken_seconds: int = Field(None, ge=1)


class SingleAnswerResponse(BaseModel):
    """Response schema for single answer evaluation."""
    answer_id: str
    score: float
    max_score: float
    is_correct: bool
    feedback: str
    strengths: List[str] = []
    improvements: List[str] = []
    partial_credit_reason: str = ""


class ExamAnswerRequest(BaseModel):
    """Request schema for exam answer."""
    question_id: str
    answer_text: str = Field(..., min_length=1, max_length=5000)
    time_taken_seconds: int = Field(None, ge=1)


class ExamSubmissionRequest(BaseModel):
    """Request schema for exam submission."""
    exam_id: str = Field(None)  # Optional for practice mode
    answers: List[ExamAnswerRequest] = Field(..., min_items=1)
    time_taken_minutes: int = Field(None, ge=1)


class ExamSubmissionResponse(BaseModel):
    """Response schema for exam submission."""
    result_id: str
    total_questions: int
    correct_answers: int
    total_score: float
    max_score: float
    percentage: float
    time_taken_minutes: int = None
    strengths: List[str] = []
    weaknesses: List[str] = []
    overall_feedback: str
    question_results: List[Dict[str, Any]] = []


@router.post("/answer", response_model=SingleAnswerResponse)
async def evaluate_single_answer(
    request: SingleAnswerRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Evaluate a single answer."""
    
    # Get question details
    question = await question_crud.get_question_by_id(request.question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    try:
        result = await evaluation_service.evaluate_single_answer(
            question_id=request.question_id,
            question_text=question["question_text"],
            question_type=QuestionType(question["question_type"]),
            correct_answer=question.get("correct_answer", ""),
            user_answer=request.answer_text,
            user_id=user_id,
            points=question.get("points", 1)
        )
        
        return SingleAnswerResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to evaluate answer: {str(e)}"
        )


@router.post("/exam", response_model=ExamSubmissionResponse)
async def evaluate_exam_submission(
    request: ExamSubmissionRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Evaluate a complete exam submission."""
    
    try:
        # Prepare answers with question details
        answers_with_details = []
        
        for answer_req in request.answers:
            # Get question details
            question = await question_crud.get_question_by_id(answer_req.question_id)
            if not question:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Question {answer_req.question_id} not found"
                )
            
            answer_data = {
                "question_id": answer_req.question_id,
                "answer_text": answer_req.answer_text,
                "time_taken_seconds": answer_req.time_taken_seconds,
                "question_text": question["question_text"],
                "question_type": question["question_type"],
                "correct_answer": question.get("correct_answer", ""),
                "points": question.get("points", 1),
                "subject": question["subject"],
                "topic": question["topic"],
                "difficulty": question["difficulty"]
            }
            answers_with_details.append(answer_data)
        
        # Evaluate the submission
        result = await evaluation_service.evaluate_exam_submission(
            exam_id=request.exam_id,
            user_id=user_id,
            answers=answers_with_details,
            time_taken_minutes=request.time_taken_minutes
        )
        
        return ExamSubmissionResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to evaluate exam submission: {str(e)}"
        )


@router.post("/batch", response_model=List[SingleAnswerResponse])
async def evaluate_batch_answers(
    answers: List[SingleAnswerRequest],
    user_id: str = Depends(get_current_user_id)
):
    """Evaluate multiple answers in batch."""
    
    if len(answers) > 50:  # Limit batch size
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 50 answers allowed per batch"
        )
    
    try:
        results = []
        
        for answer_req in answers:
            # Get question details
            question = await question_crud.get_question_by_id(answer_req.question_id)
            if not question:
                continue  # Skip invalid questions
            
            result = await evaluation_service.evaluate_single_answer(
                question_id=answer_req.question_id,
                question_text=question["question_text"],
                question_type=QuestionType(question["question_type"]),
                correct_answer=question.get("correct_answer", ""),
                user_answer=answer_req.answer_text,
                user_id=user_id,
                points=question.get("points", 1)
            )
            
            results.append(SingleAnswerResponse(**result))
        
        return results
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to evaluate batch answers: {str(e)}"
        )


@router.get("/feedback/{answer_id}")
async def get_detailed_feedback(
    answer_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get detailed feedback for a specific answer."""
    
    # TODO: Implement detailed feedback retrieval
    # This would get the stored answer and provide additional insights
    
    return {
        "answer_id": answer_id,
        "detailed_feedback": "Detailed feedback would be provided here",
        "improvement_suggestions": [
            "Review the fundamental concepts",
            "Practice similar problems",
            "Focus on specific areas mentioned in feedback"
        ],
        "related_resources": [
            {"type": "article", "title": "Understanding the concept", "url": "#"},
            {"type": "video", "title": "Video explanation", "url": "#"}
        ]
    }


@router.post("/compare")
async def compare_answers(
    question_id: str,
    user_answer: str,
    comparison_answers: List[str],
    user_id: str = Depends(get_current_user_id)
):
    """Compare user answer with other sample answers."""
    
    # Get question details
    question = await question_crud.get_question_by_id(question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    try:
        # This would use AI to compare different answers
        comparison_result = {
            "user_answer": user_answer,
            "comparisons": [],
            "insights": [
                "Your answer demonstrates good understanding of key concepts",
                "Consider including more specific examples",
                "The structure of your response is clear and logical"
            ],
            "ranking": "Above average compared to sample answers"
        }
        
        for i, comp_answer in enumerate(comparison_answers[:5]):  # Limit to 5 comparisons
            comparison_result["comparisons"].append({
                "answer_id": f"sample_{i+1}",
                "similarity_score": 0.75,  # Would be calculated by AI
                "key_differences": [
                    "Different approach to problem solving",
                    "More detailed explanation in some areas"
                ]
            })
        
        return comparison_result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compare answers: {str(e)}"
        )
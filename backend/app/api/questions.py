"""
Questions API endpoints for generation and management.
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.schemas.question import (
    QuestionCreate, QuestionResponse, QuestionGenerationRequest,
    QuestionGenerationResponse, QuestionSearchRequest, QuestionSearchResponse,
    QuestionUpdate, QuestionStats, QuestionBulkCreate
)
from app.core.security import get_current_user_id
from app.services.gemini_service import gemini_service
from app.db.crud import question_crud, user_crud
from app.core.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/questions", tags=["Questions"])


@router.post("/generate", response_model=QuestionGenerationResponse)
async def generate_questions(
    request: QuestionGenerationRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Generate questions using AI."""
    
    # Validate request
    if request.num_questions > settings.MAX_QUESTIONS_PER_REQUEST:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {settings.MAX_QUESTIONS_PER_REQUEST} questions allowed per request"
        )
    
    try:
        import time
        start_time = time.time()
        
        # Generate questions using Gemini
        generated_questions = await gemini_service.generate_questions(
            subject=request.subject,
            topic=request.topic,
            difficulty=request.difficulty,
            question_type=request.question_type,
            num_questions=request.num_questions,
            additional_context=request.additional_context
        )
        
        # Store questions in database
        questions_data = []
        for question in generated_questions:
            question_dict = question.dict()
            question_dict["created_by"] = user_id
            questions_data.append(question_dict)
        
        stored_questions = await question_crud.create_questions_batch(questions_data)
        
        generation_time = time.time() - start_time
        
        # Convert to response format
        question_responses = [QuestionResponse(**q) for q in stored_questions]
        
        return QuestionGenerationResponse(
            questions=question_responses,
            total_generated=len(question_responses),
            generation_time_seconds=generation_time,
            metadata={
                "subject": request.subject,
                "topic": request.topic,
                "difficulty": request.difficulty.value,
                "question_type": request.question_type.value,
                "include_explanations": request.include_explanations
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate questions: {str(e)}"
        )


@router.post("/bulk", response_model=List[QuestionResponse])
async def create_questions_bulk(
    questions_data: QuestionBulkCreate,
    user_id: str = Depends(get_current_user_id)
):
    """Create multiple questions in bulk."""
    
    if len(questions_data.questions) > settings.MAX_QUESTIONS_PER_REQUEST:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {settings.MAX_QUESTIONS_PER_REQUEST} questions allowed per request"
        )
    
    try:
        # Prepare questions for database storage
        questions_for_db = []
        for question in questions_data.questions:
            question_dict = question.dict()
            question_dict["created_by"] = user_id
            questions_for_db.append(question_dict)
        
        # Store in database
        stored_questions = await question_crud.create_questions_batch(questions_for_db)
        
        # Convert to response format
        return [QuestionResponse(**q) for q in stored_questions]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create questions: {str(e)}"
        )


@router.post("/search", response_model=QuestionSearchResponse)
async def search_questions(
    search_request: QuestionSearchRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Search questions with filters."""
    
    try:
        # Calculate offset
        offset = (search_request.page - 1) * search_request.page_size
        
        # Search questions
        questions = await question_crud.get_questions_by_criteria(
            subject=search_request.subject,
            topic=search_request.topic,
            difficulty=search_request.difficulty.value if search_request.difficulty else None,
            question_type=search_request.question_type.value if search_request.question_type else None,
            limit=search_request.page_size,
            offset=offset
        )
        
        # TODO: Get total count for pagination
        # For now, using a simple approach
        total_count = len(questions) + offset  # This is approximate
        total_pages = (total_count + search_request.page_size - 1) // search_request.page_size
        
        # Convert to response format
        question_responses = [QuestionResponse(**q) for q in questions]
        
        return QuestionSearchResponse(
            questions=question_responses,
            total_count=total_count,
            page=search_request.page,
            page_size=search_request.page_size,
            total_pages=total_pages
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search questions: {str(e)}"
        )


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get a specific question by ID."""
    
    question = await question_crud.get_question_by_id(question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    return QuestionResponse(**question)


@router.put("/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: str,
    update_data: QuestionUpdate,
    user_id: str = Depends(get_current_user_id)
):
    """Update a question."""
    
    # Check if question exists
    existing_question = await question_crud.get_question_by_id(question_id)
    if not existing_question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    # Check if user has permission to update (owner or admin)
    if existing_question.get("created_by") != user_id:
        # TODO: Add admin check
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this question"
        )
    
    try:
        # Update question
        update_dict = update_data.dict(exclude_unset=True)
        updated_question = await question_crud.update_question(question_id, update_dict)
        
        return QuestionResponse(**updated_question)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update question: {str(e)}"
        )


@router.delete("/{question_id}")
async def delete_question(
    question_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Delete a question."""
    
    # Check if question exists
    existing_question = await question_crud.get_question_by_id(question_id)
    if not existing_question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    # Check if user has permission to delete (owner or admin)
    if existing_question.get("created_by") != user_id:
        # TODO: Add admin check and implement delete functionality in CRUD
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this question"
        )
    
    # TODO: Implement delete in CRUD
    return {"message": "Question deleted successfully"}


@router.get("/{question_id}/stats", response_model=QuestionStats)
async def get_question_stats(
    question_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get statistics for a specific question."""
    
    # Check if question exists
    question = await question_crud.get_question_by_id(question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    # TODO: Implement statistics calculation
    # This would require analyzing answers from the database
    
    return QuestionStats(
        question_id=question_id,
        total_attempts=0,
        correct_attempts=0,
        accuracy_percentage=0.0,
        average_time_seconds=0.0,
        difficulty_rating=0.0
    )


@router.post("/{question_id}/explanation")
async def generate_explanation(
    question_id: str,
    context: dict = None,
    user_id: str = Depends(get_current_user_id)
):
    """Generate explanation for a question."""
    
    # Get question
    question = await question_crud.get_question_by_id(question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    try:
        explanation = await gemini_service.generate_explanation(
            question=question["question_text"],
            correct_answer=question.get("correct_answer", ""),
            context=context
        )
        
        return {"explanation": explanation}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate explanation: {str(e)}"
        )


@router.get("/", response_model=QuestionSearchResponse)
async def list_questions(
    subject: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    question_type: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: str = Depends(get_current_user_id)
):
    """List questions with optional filters."""
    
    try:
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get questions
        questions = await question_crud.get_questions_by_criteria(
            subject=subject,
            topic=topic,
            difficulty=difficulty,
            question_type=question_type,
            limit=page_size,
            offset=offset
        )
        
        # TODO: Get actual total count
        total_count = len(questions) + offset
        total_pages = (total_count + page_size - 1) // page_size
        
        # Convert to response format
        question_responses = [QuestionResponse(**q) for q in questions]
        
        return QuestionSearchResponse(
            questions=question_responses,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list questions: {str(e)}"
        )
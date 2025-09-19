"""
AI Assistant API endpoints for academic help.
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel, Field
from app.core.security import get_current_user_id
from app.services.assistant_service import assistant_service

router = APIRouter(prefix="/assistant", tags=["AI Assistant"])


class QuestionRequest(BaseModel):
    """Request schema for asking questions."""
    question: str = Field(..., min_length=10, max_length=1000)
    subject: Optional[str] = Field(None, max_length=100)
    context: Optional[Dict[str, Any]] = None
    use_web_search: bool = True


class QuestionResponse(BaseModel):
    """Response schema for question answers."""
    question: str
    answer: str
    sources: List[Dict[str, str]] = []
    confidence: str
    subject: Optional[str] = None
    related_topics: List[str] = []
    follow_up_questions: List[str] = []


class ConceptExplanationRequest(BaseModel):
    """Request schema for concept explanation."""
    concept: str = Field(..., min_length=1, max_length=200)
    subject: str = Field(..., min_length=1, max_length=100)
    level: str = Field(default="intermediate", pattern="^(beginner|intermediate|advanced)$")
    include_examples: bool = True


class ConceptExplanationResponse(BaseModel):
    """Response schema for concept explanation."""
    concept: str
    subject: str
    level: str
    explanation: str
    key_points: List[str] = []
    related_concepts: List[str] = []


class StudySuggestionsRequest(BaseModel):
    """Request schema for study suggestions."""
    subject: str = Field(..., min_length=1, max_length=100)
    topics: List[str] = Field(..., min_items=1, max_items=10)
    difficulty_level: str = Field(default="medium", pattern="^(easy|medium|hard)$")
    learning_goals: Optional[List[str]] = None
    time_available_minutes: int = Field(default=60, ge=15, le=480)


class StudySuggestionsResponse(BaseModel):
    """Response schema for study suggestions."""
    subject: str
    topics: List[str]
    difficulty_level: str
    time_available_minutes: int
    study_plan: str
    estimated_completion_time: int
    recommended_resources: List[Dict[str, str]] = []


class ProblemSolvingRequest(BaseModel):
    """Request schema for problem solving."""
    problem: str = Field(..., min_length=10, max_length=2000)
    subject: str = Field(..., min_length=1, max_length=100)
    show_work: bool = True


class ProblemSolvingResponse(BaseModel):
    """Response schema for problem solving."""
    problem: str
    subject: str
    solution: str
    steps: List[str] = []
    key_concepts_used: List[str] = []


@router.post("/ask", response_model=QuestionResponse)
async def ask_question(
    request: QuestionRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Ask the AI assistant a question."""
    
    try:
        result = await assistant_service.answer_question(
            question=request.question,
            subject=request.subject,
            context=request.context,
            use_web_search=request.use_web_search
        )
        
        return QuestionResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to answer question: {str(e)}"
        )


@router.post("/explain", response_model=ConceptExplanationResponse)
async def explain_concept(
    request: ConceptExplanationRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Get detailed explanation of a concept."""
    
    try:
        result = await assistant_service.explain_concept(
            concept=request.concept,
            subject=request.subject,
            level=request.level,
            include_examples=request.include_examples
        )
        
        return ConceptExplanationResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to explain concept: {str(e)}"
        )


@router.post("/study-suggestions", response_model=StudySuggestionsResponse)
async def get_study_suggestions(
    request: StudySuggestionsRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Get personalized study suggestions."""
    
    try:
        result = await assistant_service.get_study_suggestions(
            subject=request.subject,
            topics=request.topics,
            difficulty_level=request.difficulty_level,
            learning_goals=request.learning_goals,
            time_available_minutes=request.time_available_minutes
        )
        
        return StudySuggestionsResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get study suggestions: {str(e)}"
        )


@router.post("/solve", response_model=ProblemSolvingResponse)
async def solve_problem(
    request: ProblemSolvingRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Solve a problem step by step."""
    
    try:
        result = await assistant_service.solve_problem_step_by_step(
            problem=request.problem,
            subject=request.subject,
            show_work=request.show_work
        )
        
        return ProblemSolvingResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to solve problem: {str(e)}"
        )


@router.get("/subjects")
async def get_supported_subjects(
    user_id: str = Depends(get_current_user_id)
):
    """Get list of supported subjects."""
    
    subjects = [
        {"name": "Mathematics", "topics": ["Algebra", "Calculus", "Geometry", "Statistics"]},
        {"name": "Physics", "topics": ["Mechanics", "Thermodynamics", "Electromagnetism", "Quantum Physics"]},
        {"name": "Chemistry", "topics": ["Organic Chemistry", "Inorganic Chemistry", "Physical Chemistry", "Biochemistry"]},
        {"name": "Biology", "topics": ["Cell Biology", "Genetics", "Ecology", "Human Biology"]},
        {"name": "Computer Science", "topics": ["Programming", "Data Structures", "Algorithms", "Database Systems"]},
        {"name": "History", "topics": ["World History", "Ancient History", "Modern History", "Regional History"]},
        {"name": "Literature", "topics": ["Poetry", "Drama", "Fiction", "Literary Analysis"]},
        {"name": "Economics", "topics": ["Microeconomics", "Macroeconomics", "International Economics", "Economic Theory"]}
    ]
    
    return {"subjects": subjects}


@router.get("/conversation-history")
async def get_conversation_history(
    limit: int = Query(20, ge=1, le=100),
    subject: Optional[str] = Query(None),
    user_id: str = Depends(get_current_user_id)
):
    """Get user's conversation history with the AI assistant."""
    
    # TODO: Implement conversation history storage and retrieval
    # This would typically store interactions in the database
    
    return {
        "conversations": [
            {
                "id": "conv_1",
                "timestamp": "2024-01-01T10:00:00Z",
                "question": "What is photosynthesis?",
                "subject": "Biology",
                "answer_preview": "Photosynthesis is the process by which plants..."
            }
        ],
        "total_count": 1,
        "limit": limit
    }


@router.post("/feedback")
async def provide_feedback(
    conversation_id: str = Query(...),
    rating: int = Query(..., ge=1, le=5),
    feedback_text: Optional[str] = Query(None),
    user_id: str = Depends(get_current_user_id)
):
    """Provide feedback on AI assistant responses."""
    
    # TODO: Store feedback in database for improving the service
    
    return {
        "message": "Feedback received successfully",
        "conversation_id": conversation_id,
        "rating": rating
    }


@router.get("/quick-help")
async def get_quick_help(
    topic: str = Query(..., min_length=1),
    user_id: str = Depends(get_current_user_id)
):
    """Get quick help and tips for a topic."""
    
    try:
        # Generate quick tips for the topic
        quick_tips = [
            f"Key concept: Understanding {topic} requires foundation knowledge",
            f"Practice: Regular practice problems help master {topic}",
            f"Application: Look for real-world applications of {topic}",
            f"Resources: Use multiple sources to understand {topic} better"
        ]
        
        return {
            "topic": topic,
            "quick_tips": quick_tips,
            "common_mistakes": [
                "Not understanding the fundamental concepts",
                "Skipping practice problems",
                "Not connecting theory to practice"
            ],
            "study_methods": [
                "Active reading and note-taking",
                "Practice with examples",
                "Teaching others",
                "Regular review sessions"
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get quick help: {str(e)}"
        )


@router.post("/clarification")
async def ask_clarification(
    original_question: str,
    clarification_request: str,
    context: Optional[Dict[str, Any]] = None,
    user_id: str = Depends(get_current_user_id)
):
    """Ask for clarification on a previous answer."""
    
    try:
        # Build clarification prompt
        prompt = f"""
        Original Question: {original_question}
        Clarification Needed: {clarification_request}
        
        Please provide a clear clarification addressing the specific point raised.
        """
        
        # Use assistant service to get clarification
        result = await assistant_service.answer_question(
            question=prompt,
            context=context,
            use_web_search=False
        )
        
        return {
            "original_question": original_question,
            "clarification_request": clarification_request,
            "clarification": result["answer"],
            "additional_resources": result.get("sources", [])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to provide clarification: {str(e)}"
        )
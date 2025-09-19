from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import os
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
import uuid
from datetime import datetime
import json

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="EduAI - Ultra Simple",
    description="AI Chat for Education - No Auth Required",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple AI service using Gemini
class SimpleAI:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-2.0-flash')
                logger.info("✅ Gemini AI initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Gemini AI: {e}")
                self.model = None
        else:
            logger.warning("⚠️ GEMINI_API_KEY not found. AI will return demo responses.")
            self.model = None
    
    def get_response(self, message: str) -> str:
        """Get AI response to user message."""
        try:
            if self.model:
                response = self.model.generate_content(f"You are an educational AI assistant. Please respond helpfully to: {message}")
                return response.text
            else:
                # Demo response when no API key
                return f"🤖 Demo AI Response: I understand you asked about '{message}'. This is a demo response since no Gemini API key is configured. Please add GEMINI_API_KEY to your .env file for real AI responses."
        except Exception as e:
            logger.error(f"AI Error: {e}")
            return f"Sorry, I encountered an error while processing your request: {str(e)}"

# Initialize AI service
ai_service = SimpleAI()

# Simple in-memory storage for demo (replace with real database)
class ExamStorage:
    def __init__(self):
        self.exams = {}  # exam_id -> exam_data
        self.user_exams = {}  # user_id -> [exam_ids]
    
    def create_exam(self, exam_data: dict) -> str:
        exam_id = str(uuid.uuid4())
        exam_data['exam_id'] = exam_id
        exam_data['created_at'] = datetime.now().isoformat()
        exam_data['status'] = 'in_progress'
        self.exams[exam_id] = exam_data
        
        user_id = exam_data.get('user_id')
        if user_id not in self.user_exams:
            self.user_exams[user_id] = []
        self.user_exams[user_id].append(exam_id)
        
        return exam_id
    
    def get_exam(self, exam_id: str) -> Optional[dict]:
        return self.exams.get(exam_id)
    
    def update_exam(self, exam_id: str, updates: dict) -> bool:
        if exam_id in self.exams:
            self.exams[exam_id].update(updates)
            self.exams[exam_id]['updated_at'] = datetime.now().isoformat()
            return True
        return False
    
    def get_user_exams(self, user_id: str) -> List[dict]:
        exam_ids = self.user_exams.get(user_id, [])
        return [self.exams[exam_id] for exam_id in exam_ids if exam_id in self.exams]

# Initialize storage
exam_storage = ExamStorage()

# Request/Response models
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    success: bool = True

# Exam models
class ExamGenerateRequest(BaseModel):
    user_id: str
    chat_id: Optional[str] = None
    title: str
    subject: str
    exam_type: str  # "mcq" or "written"
    num_questions: int = 10
    difficulty: str = "medium"  # "easy", "medium", "hard"
    topic: Optional[str] = None

class MCQOption(BaseModel):
    id: str
    text: str
    is_correct: bool = False

class MCQQuestion(BaseModel):
    id: str
    question: str
    options: List[MCQOption]
    correct_answer: str
    explanation: Optional[str] = None

class WrittenQuestion(BaseModel):
    id: str
    question: str
    max_points: int = 10
    sample_answer: Optional[str] = None

class ExamGenerateResponse(BaseModel):
    exam_id: str
    title: str
    subject: str
    exam_type: str
    questions: List[Dict[str, Any]]
    total_questions: int
    max_score: int
    success: bool = True

class ExamSubmitRequest(BaseModel):
    exam_id: str
    user_id: str
    answers: List[Dict[str, Any]]  # {"question_id": "...", "answer": "..."}

class ExamSubmitResponse(BaseModel):
    exam_id: str
    score: float
    max_score: int
    percentage: float
    results: Dict[str, Any]
    success: bool = True

class ExamListResponse(BaseModel):
    exams: List[Dict[str, Any]]
    success: bool = True

# Routes
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "EduAI Ultra Simple",
        "ai_available": ai_service.model is not None
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Simple chat endpoint - no auth required."""
    try:
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        logger.info(f"💬 Processing message: {request.message[:50]}...")
        
        # Get AI response
        ai_response = ai_service.get_response(request.message)
        
        logger.info(f"✅ AI response generated successfully")
        
        return ChatResponse(
            response=ai_response,
            success=True
        )
        
    except Exception as e:
        logger.error(f"❌ Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@app.post("/exams/generate", response_model=ExamGenerateResponse)
async def generate_exam(request: ExamGenerateRequest):
    """Generate an MCQ or written exam using AI."""
    try:
        logger.info(f"📝 Generating {request.exam_type} exam: {request.title}")
        
        if request.exam_type not in ["mcq", "written"]:
            raise HTTPException(status_code=400, detail="exam_type must be 'mcq' or 'written'")
        
        # Create AI prompt for exam generation
        if request.exam_type == "mcq":
            prompt = f"""Generate {request.num_questions} multiple choice questions for {request.subject}.
Title: {request.title}
Difficulty: {request.difficulty}
{f'Topic: {request.topic}' if request.topic else ''}

For each question, provide:
1. The question text
2. 4 answer options (A, B, C, D)
3. The correct answer
4. A brief explanation

Format the response as JSON with this structure:
{{
  "questions": [
    {{
      "id": "q1",
      "question": "Question text here?",
      "options": [
        {{"id": "A", "text": "Option A text", "is_correct": false}},
        {{"id": "B", "text": "Option B text", "is_correct": true}},
        {{"id": "C", "text": "Option C text", "is_correct": false}},
        {{"id": "D", "text": "Option D text", "is_correct": false}}
      ],
      "correct_answer": "B",
      "explanation": "Explanation here"
    }}
  ]
}}"""
        else:  # written exam
            prompt = f"""Generate {request.num_questions} written/essay questions for {request.subject}.
Title: {request.title}
Difficulty: {request.difficulty}
{f'Topic: {request.topic}' if request.topic else ''}

For each question, provide:
1. The question text
2. Maximum points (distribute 100 points total across all questions)
3. A sample answer or key points

Format the response as JSON with this structure:
{{
  "questions": [
    {{
      "id": "q1",
      "question": "Question text here?",
      "max_points": 20,
      "sample_answer": "Sample answer or key points here"
    }}
  ]
}}"""
        
        # Get AI response
        ai_response = ai_service.get_response(prompt)
        
        # Try to parse JSON from AI response
        try:
            # Extract JSON from AI response (in case there's extra text)
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                json_str = ai_response[start_idx:end_idx]
                exam_data = json.loads(json_str)
            else:
                raise ValueError("No JSON found in AI response")
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            # Fallback: create a simple exam structure
            if request.exam_type == "mcq":
                exam_data = {
                    "questions": [
                        {
                            "id": f"q{i+1}",
                            "question": f"Sample {request.subject} question {i+1}?",
                            "options": [
                                {"id": "A", "text": "Option A", "is_correct": i == 0},
                                {"id": "B", "text": "Option B", "is_correct": i == 1},
                                {"id": "C", "text": "Option C", "is_correct": i == 2},
                                {"id": "D", "text": "Option D", "is_correct": i == 3}
                            ],
                            "correct_answer": chr(65 + (i % 4)),
                            "explanation": f"Explanation for question {i+1}"
                        }
                        for i in range(request.num_questions)
                    ]
                }
            else:
                exam_data = {
                    "questions": [
                        {
                            "id": f"q{i+1}",
                            "question": f"Sample {request.subject} essay question {i+1}?",
                            "max_points": 100 // request.num_questions,
                            "sample_answer": f"Sample answer for question {i+1}"
                        }
                        for i in range(request.num_questions)
                    ]
                }
        
        # Calculate max score
        if request.exam_type == "mcq":
            max_score = len(exam_data["questions"])
        else:
            max_score = sum(q.get("max_points", 10) for q in exam_data["questions"])
        
        # Store exam in database
        exam_record = {
            "user_id": request.user_id,
            "chat_id": request.chat_id,
            "title": request.title,
            "subject": request.subject,
            "exam_type": request.exam_type,
            "exam_data": {
                "questions": exam_data["questions"],
                "user_answers": [],
                "results": {}
            },
            "max_score": max_score,
            "status": "in_progress"
        }
        
        exam_id = exam_storage.create_exam(exam_record)
        
        logger.info(f"✅ Exam generated successfully: {exam_id}")
        
        return ExamGenerateResponse(
            exam_id=exam_id,
            title=request.title,
            subject=request.subject,
            exam_type=request.exam_type,
            questions=exam_data["questions"],
            total_questions=len(exam_data["questions"]),
            max_score=max_score,
            success=True
        )
        
    except Exception as e:
        logger.error(f"❌ Exam generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Exam generation failed: {str(e)}")

@app.get("/exams/user/{user_id}", response_model=ExamListResponse)
async def get_user_exams(user_id: str):
    """Get all exams for a specific user."""
    try:
        logger.info(f"📋 Getting exams for user: {user_id}")
        
        exams = exam_storage.get_user_exams(user_id)
        
        # Remove detailed exam data for list view
        exam_list = []
        for exam in exams:
            exam_summary = {
                "exam_id": exam["exam_id"],
                "title": exam["title"],
                "subject": exam["subject"],
                "exam_type": exam["exam_type"],
                "status": exam["status"],
                "created_at": exam["created_at"],
                "updated_at": exam.get("updated_at", exam["created_at"]),
                "total_questions": len(exam["exam_data"]["questions"]),
                "max_score": exam["max_score"]
            }
            
            # Add score if completed
            if exam["status"] == "completed" and "results" in exam["exam_data"]:
                exam_summary["score"] = exam["exam_data"]["results"].get("score", 0)
                exam_summary["percentage"] = exam["exam_data"]["results"].get("percentage", 0)
            
            exam_list.append(exam_summary)
        
        logger.info(f"✅ Found {len(exam_list)} exams for user")
        
        return ExamListResponse(
            exams=exam_list,
            success=True
        )
        
    except Exception as e:
        logger.error(f"❌ Error getting user exams: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get user exams: {str(e)}")

@app.get("/exams/{exam_id}")
async def get_exam(exam_id: str):
    """Get specific exam details."""
    try:
        logger.info(f"📄 Getting exam: {exam_id}")
        
        exam = exam_storage.get_exam(exam_id)
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found")
        
        logger.info(f"✅ Exam retrieved successfully")
        
        return {
            "exam_id": exam["exam_id"],
            "title": exam["title"],
            "subject": exam["subject"],
            "exam_type": exam["exam_type"],
            "status": exam["status"],
            "questions": exam["exam_data"]["questions"],
            "total_questions": len(exam["exam_data"]["questions"]),
            "max_score": exam["max_score"],
            "created_at": exam["created_at"],
            "updated_at": exam.get("updated_at", exam["created_at"]),
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting exam: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get exam: {str(e)}")

@app.post("/exams/submit", response_model=ExamSubmitResponse)
async def submit_exam(request: ExamSubmitRequest):
    """Submit exam answers and get graded results."""
    try:
        logger.info(f"📝 Submitting exam: {request.exam_id}")
        
        exam = exam_storage.get_exam(request.exam_id)
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found")
        
        if exam["user_id"] != request.user_id:
            raise HTTPException(status_code=403, detail="Not authorized to submit this exam")
        
        if exam["status"] == "completed":
            raise HTTPException(status_code=400, detail="Exam already submitted")
        
        # Grade the exam based on type
        if exam["exam_type"] == "mcq":
            results = await grade_mcq_exam(exam, request.answers)
        else:  # written exam
            results = await grade_written_exam(exam, request.answers)
        
        # Update exam with results
        exam_updates = {
            "status": "completed",
            "exam_data": {
                **exam["exam_data"],
                "user_answers": request.answers,
                "results": results
            }
        }
        
        exam_storage.update_exam(request.exam_id, exam_updates)
        
        logger.info(f"✅ Exam submitted and graded successfully")
        
        return ExamSubmitResponse(
            exam_id=request.exam_id,
            score=results["score"],
            max_score=results["max_score"],
            percentage=results["percentage"],
            results=results,
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error submitting exam: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit exam: {str(e)}")

async def grade_mcq_exam(exam: dict, answers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Grade an MCQ exam automatically."""
    questions = exam["exam_data"]["questions"]
    score = 0
    total_questions = len(questions)
    question_results = []
    
    # Create answer lookup
    answer_map = {ans["question_id"]: ans["answer"] for ans in answers}
    
    for question in questions:
        question_id = question["id"]
        user_answer = answer_map.get(question_id, "")
        correct_answer = question["correct_answer"]
        
        is_correct = user_answer.upper() == correct_answer.upper()
        if is_correct:
            score += 1
        
        question_results.append({
            "question_id": question_id,
            "question": question["question"],
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "explanation": question.get("explanation", "")
        })
    
    percentage = (score / total_questions) * 100 if total_questions > 0 else 0
    
    return {
        "score": score,
        "max_score": total_questions,
        "percentage": round(percentage, 2),
        "question_results": question_results,
        "exam_type": "mcq"
    }

async def grade_written_exam(exam: dict, answers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Grade a written exam using AI assistance."""
    questions = exam["exam_data"]["questions"]
    total_score = 0
    max_score = sum(q.get("max_points", 10) for q in questions)
    question_results = []
    
    # Create answer lookup
    answer_map = {ans["question_id"]: ans["answer"] for ans in answers}
    
    for question in questions:
        question_id = question["id"]
        user_answer = answer_map.get(question_id, "")
        question_text = question["question"]
        max_points = question.get("max_points", 10)
        sample_answer = question.get("sample_answer", "")
        
        if not user_answer.strip():
            # No answer provided
            question_score = 0
            feedback = "No answer provided."
        else:
            # Use AI to grade the written answer
            grading_prompt = f"""Grade this written answer on a scale of 0 to {max_points}.

Question: {question_text}

Student Answer: {user_answer}

Sample Answer/Key Points: {sample_answer}

Please provide:
1. A score from 0 to {max_points}
2. Brief feedback explaining the score
3. What was good about the answer
4. What could be improved

Format your response as JSON:
{{
  "score": [number from 0 to {max_points}],
  "feedback": "Brief feedback here",
  "strengths": "What was good",
  "improvements": "What could be improved"
}}"""
            
            try:
                ai_response = ai_service.get_response(grading_prompt)
                
                # Try to parse JSON from AI response
                start_idx = ai_response.find('{')
                end_idx = ai_response.rfind('}') + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = ai_response[start_idx:end_idx]
                    grading_data = json.loads(json_str)
                    question_score = min(max(grading_data.get("score", 0), 0), max_points)
                    feedback = grading_data.get("feedback", "AI grading completed")
                    strengths = grading_data.get("strengths", "")
                    improvements = grading_data.get("improvements", "")
                else:
                    raise ValueError("No JSON found in AI response")
                    
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Failed to parse AI grading response: {e}")
                # Fallback grading (simple length-based scoring)
                answer_length = len(user_answer.strip())
                if answer_length >= 100:
                    question_score = max_points * 0.8
                elif answer_length >= 50:
                    question_score = max_points * 0.6
                elif answer_length >= 20:
                    question_score = max_points * 0.4
                else:
                    question_score = max_points * 0.2
                
                feedback = "Answer received and graded based on length and effort."
                strengths = "Answer provided"
                improvements = "Consider providing more detailed responses"
        
        total_score += question_score
        
        question_results.append({
            "question_id": question_id,
            "question": question_text,
            "user_answer": user_answer,
            "score": question_score,
            "max_points": max_points,
            "feedback": feedback,
            "strengths": strengths if 'strengths' in locals() else "",
            "improvements": improvements if 'improvements' in locals() else ""
        })
    
    percentage = (total_score / max_score) * 100 if max_score > 0 else 0
    
    return {
        "score": round(total_score, 2),
        "max_score": max_score,
        "percentage": round(percentage, 2),
        "question_results": question_results,
        "exam_type": "written"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001)
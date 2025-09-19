"""
CRUD operations for database models using Supabase.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from app.db.database import get_supabase
from app.db.models import User, Question, Exam, Answer, Result, Progress
from app.core.security import hash_password


class BaseCRUD:
    """Base CRUD operations."""
    
    def __init__(self, table_name: str):
        self.supabase = get_supabase()
        self.table_name = table_name
    
    def generate_id(self) -> str:
        """Generate a unique ID."""
        return str(uuid.uuid4())


class UserCRUD(BaseCRUD):
    """CRUD operations for User model."""
    
    def __init__(self):
        super().__init__("users")
    
    async def create_user(self, email: str, username: str, password: str, full_name: str = None) -> Dict[str, Any]:
        """Create a new user."""
        user_data = {
            "id": self.generate_id(),
            "email": email,
            "username": username,
            "hashed_password": hash_password(password),
            "full_name": full_name,
            "is_active": True,
            "is_verified": False,
            "created_at": datetime.utcnow().isoformat(),
        }
        
        result = self.supabase.table(self.table_name).insert(user_data).execute()
        return result.data[0] if result.data else None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email."""
        result = self.supabase.table(self.table_name).select("*").eq("email", email).execute()
        return result.data[0] if result.data else None
    
    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username."""
        result = self.supabase.table(self.table_name).select("*").eq("username", username).execute()
        return result.data[0] if result.data else None
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        result = self.supabase.table(self.table_name).select("*").eq("id", user_id).execute()
        return result.data[0] if result.data else None
    
    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update user information."""
        update_data["updated_at"] = datetime.utcnow().isoformat()
        result = self.supabase.table(self.table_name).update(update_data).eq("id", user_id).execute()
        return result.data[0] if result.data else None
    
    async def update_last_login(self, user_id: str) -> None:
        """Update user's last login time."""
        await self.update_user(user_id, {"last_login": datetime.utcnow().isoformat()})


class QuestionCRUD(BaseCRUD):
    """CRUD operations for Question model."""
    
    def __init__(self):
        super().__init__("questions")
    
    async def create_question(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new question."""
        question_data.update({
            "id": self.generate_id(),
            "created_at": datetime.utcnow().isoformat(),
        })
        
        result = self.supabase.table(self.table_name).insert(question_data).execute()
        return result.data[0] if result.data else None
    
    async def create_questions_batch(self, questions_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create multiple questions in batch."""
        for question in questions_data:
            question.update({
                "id": self.generate_id(),
                "created_at": datetime.utcnow().isoformat(),
            })
        
        result = self.supabase.table(self.table_name).insert(questions_data).execute()
        return result.data if result.data else []
    
    async def get_questions_by_criteria(
        self, 
        subject: str = None, 
        topic: str = None, 
        difficulty: str = None,
        question_type: str = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get questions by various criteria."""
        query = self.supabase.table(self.table_name).select("*")
        
        if subject:
            query = query.eq("subject", subject)
        if topic:
            query = query.eq("topic", topic)
        if difficulty:
            query = query.eq("difficulty", difficulty)
        if question_type:
            query = query.eq("question_type", question_type)
        
        result = query.range(offset, offset + limit - 1).execute()
        return result.data if result.data else []
    
    async def get_question_by_id(self, question_id: str) -> Optional[Dict[str, Any]]:
        """Get question by ID."""
        result = self.supabase.table(self.table_name).select("*").eq("id", question_id).execute()
        return result.data[0] if result.data else None
    
    async def update_question(self, question_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update question."""
        update_data["updated_at"] = datetime.utcnow().isoformat()
        result = self.supabase.table(self.table_name).update(update_data).eq("id", question_id).execute()
        return result.data[0] if result.data else None


class ExamCRUD(BaseCRUD):
    """CRUD operations for Exam model."""
    
    def __init__(self):
        super().__init__("exams")
    
    async def create_exam(self, exam_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new exam."""
        exam_data.update({
            "id": self.generate_id(),
            "created_at": datetime.utcnow().isoformat(),
        })
        
        result = self.supabase.table(self.table_name).insert(exam_data).execute()
        return result.data[0] if result.data else None
    
    async def get_user_exams(self, user_id: str, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Get exams for a specific user."""
        result = self.supabase.table(self.table_name)\
            .select("*")\
            .eq("user_id", user_id)\
            .range(offset, offset + limit - 1)\
            .execute()
        return result.data if result.data else []
    
    async def get_exam_by_id(self, exam_id: str) -> Optional[Dict[str, Any]]:
        """Get exam by ID."""
        result = self.supabase.table(self.table_name).select("*").eq("id", exam_id).execute()
        return result.data[0] if result.data else None


class AnswerCRUD(BaseCRUD):
    """CRUD operations for Answer model."""
    
    def __init__(self):
        super().__init__("answers")
    
    async def create_answer(self, answer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new answer."""
        answer_data.update({
            "id": self.generate_id(),
            "created_at": datetime.utcnow().isoformat(),
        })
        
        result = self.supabase.table(self.table_name).insert(answer_data).execute()
        return result.data[0] if result.data else None
    
    async def get_user_answers(self, user_id: str, question_id: str = None) -> List[Dict[str, Any]]:
        """Get answers for a user, optionally filtered by question."""
        query = self.supabase.table(self.table_name).select("*").eq("user_id", user_id)
        
        if question_id:
            query = query.eq("question_id", question_id)
        
        result = query.execute()
        return result.data if result.data else []


class ResultCRUD(BaseCRUD):
    """CRUD operations for Result model."""
    
    def __init__(self):
        super().__init__("results")
    
    async def create_result(self, result_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new result."""
        result_data.update({
            "id": self.generate_id(),
            "completed_at": datetime.utcnow().isoformat(),
        })
        
        result = self.supabase.table(self.table_name).insert(result_data).execute()
        return result.data[0] if result.data else None
    
    async def get_user_results(
        self, 
        user_id: str, 
        subject: str = None,
        limit: int = 20, 
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get results for a user."""
        query = self.supabase.table(self.table_name).select("*").eq("user_id", user_id)
        
        if subject:
            query = query.eq("subject", subject)
        
        result = query.order("completed_at", desc=True).range(offset, offset + limit - 1).execute()
        return result.data if result.data else []
    
    async def get_result_by_id(self, result_id: str) -> Optional[Dict[str, Any]]:
        """Get result by ID."""
        result = self.supabase.table(self.table_name).select("*").eq("id", result_id).execute()
        return result.data[0] if result.data else None


class ProgressCRUD(BaseCRUD):
    """CRUD operations for Progress model."""
    
    def __init__(self):
        super().__init__("progress")
    
    async def get_or_create_progress(self, user_id: str, subject: str, topic: str = None) -> Dict[str, Any]:
        """Get existing progress or create new one."""
        query = self.supabase.table(self.table_name)\
            .select("*")\
            .eq("user_id", user_id)\
            .eq("subject", subject)
        
        if topic:
            query = query.eq("topic", topic)
        else:
            query = query.is_("topic", "null")
        
        result = query.execute()
        
        if result.data:
            return result.data[0]
        
        # Create new progress record
        progress_data = {
            "id": self.generate_id(),
            "user_id": user_id,
            "subject": subject,
            "topic": topic,
            "created_at": datetime.utcnow().isoformat(),
        }
        
        result = self.supabase.table(self.table_name).insert(progress_data).execute()
        return result.data[0] if result.data else None
    
    async def update_progress(self, progress_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update progress record."""
        update_data["updated_at"] = datetime.utcnow().isoformat()
        result = self.supabase.table(self.table_name).update(update_data).eq("id", progress_id).execute()
        return result.data[0] if result.data else None
    
    async def get_user_progress(self, user_id: str, subject: str = None) -> List[Dict[str, Any]]:
        """Get progress for a user."""
        query = self.supabase.table(self.table_name).select("*").eq("user_id", user_id)
        
        if subject:
            query = query.eq("subject", subject)
        
        result = query.execute()
        return result.data if result.data else []


# CRUD instances
user_crud = UserCRUD()
question_crud = QuestionCRUD()
exam_crud = ExamCRUD()
answer_crud = AnswerCRUD()
result_crud = ResultCRUD()
progress_crud = ProgressCRUD()
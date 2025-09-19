"""
Database schema definitions for Supabase tables.
This file serves as documentation for the database structure.
Tables are created and managed through Supabase Dashboard or init_db.py script.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class QuestionType(str, Enum):
    """Question types enum."""
    MCQ = "mcq"
    SHORT = "short"
    LONG = "long"


class Difficulty(str, Enum):
    """Difficulty levels enum."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


# Database Schema Documentation
# All tables are created and managed in Supabase

SUPABASE_TABLES = {
    "users": {
        "description": "User accounts and profiles",
        "columns": {
            "id": "UUID PRIMARY KEY",
            "email": "VARCHAR(255) UNIQUE NOT NULL",
            "username": "VARCHAR(100) UNIQUE NOT NULL", 
            "full_name": "VARCHAR(255)",
            "hashed_password": "VARCHAR(255) NOT NULL",
            "is_active": "BOOLEAN DEFAULT true",
            "is_verified": "BOOLEAN DEFAULT false",
            "created_at": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP",
            "profile_picture": "VARCHAR(500)",
            "bio": "TEXT",
            "level": "INTEGER DEFAULT 1",
            "points": "INTEGER DEFAULT 0",
            "badges": "TEXT[] DEFAULT '{}'",
            "preferences": "JSONB DEFAULT '{}'",
            "last_login": "TIMESTAMP WITH TIME ZONE"
        }
    },
    
    "questions": {
        "description": "Generated and manual questions",
        "columns": {
            "id": "UUID PRIMARY KEY",
            "content": "TEXT NOT NULL",
            "question_type": "VARCHAR(20) NOT NULL CHECK (question_type IN ('mcq', 'short', 'long'))",
            "subject": "VARCHAR(100) NOT NULL",
            "topic": "VARCHAR(100)",
            "difficulty": "VARCHAR(20) DEFAULT 'medium' CHECK (difficulty IN ('easy', 'medium', 'hard'))",
            "options": "JSONB",
            "correct_answer": "TEXT",
            "explanation": "TEXT",
            "created_by": "UUID REFERENCES users(id)",
            "created_at": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP",
            "tags": "TEXT[] DEFAULT '{}'",
            "metadata": "JSONB DEFAULT '{}'"
        }
    },
    
    "exams": {
        "description": "Exam configurations",
        "columns": {
            "id": "UUID PRIMARY KEY",
            "title": "VARCHAR(255) NOT NULL",
            "description": "TEXT",
            "subject": "VARCHAR(100) NOT NULL",
            "difficulty": "VARCHAR(20) DEFAULT 'medium'",
            "duration_minutes": "INTEGER DEFAULT 60",
            "total_marks": "INTEGER DEFAULT 100",
            "created_by": "UUID REFERENCES users(id)",
            "created_at": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP",
            "is_active": "BOOLEAN DEFAULT true",
            "exam_type": "VARCHAR(50) DEFAULT 'practice'",
            "instructions": "TEXT",
            "metadata": "JSONB DEFAULT '{}'"
        }
    },
    
    "exam_questions": {
        "description": "Junction table for exam-question relationships",
        "columns": {
            "exam_id": "UUID REFERENCES exams(id) ON DELETE CASCADE",
            "question_id": "UUID REFERENCES questions(id) ON DELETE CASCADE",
            "question_order": "INTEGER NOT NULL",
            "marks": "INTEGER DEFAULT 1",
            "PRIMARY KEY": "(exam_id, question_id)"
        }
    },
    
    "answers": {
        "description": "User answers to questions",
        "columns": {
            "id": "UUID PRIMARY KEY",
            "user_id": "UUID REFERENCES users(id) NOT NULL",
            "question_id": "UUID REFERENCES questions(id) NOT NULL",
            "exam_id": "UUID REFERENCES exams(id)",
            "answer_text": "TEXT NOT NULL",
            "is_correct": "BOOLEAN",
            "score": "DECIMAL(5,2)",
            "time_taken": "INTEGER",
            "created_at": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP",
            "ai_feedback": "TEXT",
            "metadata": "JSONB DEFAULT '{}'"
        }
    },
    
    "results": {
        "description": "Exam results and scores",
        "columns": {
            "id": "UUID PRIMARY KEY",
            "user_id": "UUID REFERENCES users(id) NOT NULL",
            "exam_id": "UUID REFERENCES exams(id) NOT NULL",
            "total_score": "DECIMAL(5,2) NOT NULL",
            "max_score": "DECIMAL(5,2) NOT NULL",
            "percentage": "DECIMAL(5,2) NOT NULL",
            "time_taken": "INTEGER",
            "completed_at": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP",
            "feedback": "TEXT",
            "strengths": "TEXT[]",
            "weaknesses": "TEXT[]",
            "recommendations": "TEXT[]",
            "metadata": "JSONB DEFAULT '{}'"
        }
    },
    
    "progress": {
        "description": "User learning progress tracking",
        "columns": {
            "id": "UUID PRIMARY KEY",
            "user_id": "UUID REFERENCES users(id) NOT NULL",
            "subject": "VARCHAR(100) NOT NULL",
            "topic": "VARCHAR(100)",
            "total_questions": "INTEGER DEFAULT 0",
            "correct_answers": "INTEGER DEFAULT 0",
            "total_time": "INTEGER DEFAULT 0",
            "average_score": "DECIMAL(5,2) DEFAULT 0",
            "last_practiced": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP",
            "streak_days": "INTEGER DEFAULT 0",
            "best_score": "DECIMAL(5,2) DEFAULT 0",
            "improvement_rate": "DECIMAL(5,2) DEFAULT 0",
            "metadata": "JSONB DEFAULT '{}'",
            "UNIQUE": "(user_id, subject, topic)"
        }
    }
}

# Indexes for better performance
SUPABASE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
    "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
    "CREATE INDEX IF NOT EXISTS idx_questions_subject ON questions(subject)",
    "CREATE INDEX IF NOT EXISTS idx_questions_topic ON questions(topic)",
    "CREATE INDEX IF NOT EXISTS idx_questions_difficulty ON questions(difficulty)",
    "CREATE INDEX IF NOT EXISTS idx_questions_type ON questions(question_type)",
    "CREATE INDEX IF NOT EXISTS idx_answers_user_id ON answers(user_id)",
    "CREATE INDEX IF NOT EXISTS idx_answers_question_id ON answers(question_id)",
    "CREATE INDEX IF NOT EXISTS idx_answers_exam_id ON answers(exam_id)",
    "CREATE INDEX IF NOT EXISTS idx_results_user_id ON results(user_id)",
    "CREATE INDEX IF NOT EXISTS idx_results_exam_id ON results(exam_id)",
    "CREATE INDEX IF NOT EXISTS idx_progress_user_id ON progress(user_id)",
    "CREATE INDEX IF NOT EXISTS idx_progress_subject ON progress(subject)"
]
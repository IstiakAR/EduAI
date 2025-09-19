"""
Database initialization script for EduAI.
Creates tables and sets up initial data in Supabase.
NO LOCAL POSTGRESQL REQUIRED - Uses Supabase hosted database only.
"""
import asyncio
import sys
from pathlib import Path

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent))

from app.db.database import db_manager
from app.db.schema import SUPABASE_TABLES, SUPABASE_INDEXES
from app.core.config import get_settings

settings = get_settings()


async def create_tables():
    """Create all database tables in Supabase."""
    print("🗄️  Creating Supabase database tables...")
    
    # SQL for creating tables (to be run in Supabase SQL Editor)
    create_tables_sql = """
    -- Enable UUID extension
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    
    -- Users table
    CREATE TABLE IF NOT EXISTS users (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        email VARCHAR(255) UNIQUE NOT NULL,
        username VARCHAR(100) UNIQUE NOT NULL,
        full_name VARCHAR(255),
        hashed_password VARCHAR(255) NOT NULL,
        is_active BOOLEAN DEFAULT true,
        is_verified BOOLEAN DEFAULT false,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        profile_picture VARCHAR(500),
        bio TEXT,
        level INTEGER DEFAULT 1,
        points INTEGER DEFAULT 0,
        badges TEXT[] DEFAULT '{}',
        preferences JSONB DEFAULT '{}',
        last_login TIMESTAMP WITH TIME ZONE
    );
    
    -- Questions table
    CREATE TABLE IF NOT EXISTS questions (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        content TEXT NOT NULL,
        question_type VARCHAR(20) NOT NULL CHECK (question_type IN ('mcq', 'short', 'long')),
        subject VARCHAR(100) NOT NULL,
        topic VARCHAR(100),
        difficulty VARCHAR(20) DEFAULT 'medium' CHECK (difficulty IN ('easy', 'medium', 'hard')),
        options JSONB,
        correct_answer TEXT,
        explanation TEXT,
        created_by UUID REFERENCES users(id),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        tags TEXT[] DEFAULT '{}',
        metadata JSONB DEFAULT '{}'
    );
    
    -- Exams table
    CREATE TABLE IF NOT EXISTS exams (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        title VARCHAR(255) NOT NULL,
        description TEXT,
        subject VARCHAR(100) NOT NULL,
        difficulty VARCHAR(20) DEFAULT 'medium',
        duration_minutes INTEGER DEFAULT 60,
        total_marks INTEGER DEFAULT 100,
        created_by UUID REFERENCES users(id),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT true,
        exam_type VARCHAR(50) DEFAULT 'practice',
        instructions TEXT,
        metadata JSONB DEFAULT '{}'
    );
    
    -- Exam Questions junction table
    CREATE TABLE IF NOT EXISTS exam_questions (
        exam_id UUID REFERENCES exams(id) ON DELETE CASCADE,
        question_id UUID REFERENCES questions(id) ON DELETE CASCADE,
        question_order INTEGER NOT NULL,
        marks INTEGER DEFAULT 1,
        PRIMARY KEY (exam_id, question_id)
    );
    
    -- Answers table
    CREATE TABLE IF NOT EXISTS answers (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id UUID REFERENCES users(id) NOT NULL,
        question_id UUID REFERENCES questions(id) NOT NULL,
        exam_id UUID REFERENCES exams(id),
        answer_text TEXT NOT NULL,
        is_correct BOOLEAN,
        score DECIMAL(5,2),
        time_taken INTEGER,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        ai_feedback TEXT,
        metadata JSONB DEFAULT '{}'
    );
    
    -- Results table
    CREATE TABLE IF NOT EXISTS results (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id UUID REFERENCES users(id) NOT NULL,
        exam_id UUID REFERENCES exams(id) NOT NULL,
        total_score DECIMAL(5,2) NOT NULL,
        max_score DECIMAL(5,2) NOT NULL,
        percentage DECIMAL(5,2) NOT NULL,
        time_taken INTEGER,
        completed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        feedback TEXT,
        strengths TEXT[],
        weaknesses TEXT[],
        recommendations TEXT[],
        metadata JSONB DEFAULT '{}'
    );
    
    -- Progress table
    CREATE TABLE IF NOT EXISTS progress (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id UUID REFERENCES users(id) NOT NULL,
        subject VARCHAR(100) NOT NULL,
        topic VARCHAR(100),
        total_questions INTEGER DEFAULT 0,
        correct_answers INTEGER DEFAULT 0,
        total_time INTEGER DEFAULT 0,
        average_score DECIMAL(5,2) DEFAULT 0,
        last_practiced TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        streak_days INTEGER DEFAULT 0,
        best_score DECIMAL(5,2) DEFAULT 0,
        improvement_rate DECIMAL(5,2) DEFAULT 0,
        metadata JSONB DEFAULT '{}',
        UNIQUE(user_id, subject, topic)
    );
    """
    
    # Create indexes for better performance
    indexes_sql = """
    -- Create indexes for better performance
    CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
    CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
    CREATE INDEX IF NOT EXISTS idx_questions_subject ON questions(subject);
    CREATE INDEX IF NOT EXISTS idx_questions_topic ON questions(topic);
    CREATE INDEX IF NOT EXISTS idx_questions_difficulty ON questions(difficulty);
    CREATE INDEX IF NOT EXISTS idx_questions_type ON questions(question_type);
    CREATE INDEX IF NOT EXISTS idx_answers_user_id ON answers(user_id);
    CREATE INDEX IF NOT EXISTS idx_answers_question_id ON answers(question_id);
    CREATE INDEX IF NOT EXISTS idx_answers_exam_id ON answers(exam_id);
    CREATE INDEX IF NOT EXISTS idx_results_user_id ON results(user_id);
    CREATE INDEX IF NOT EXISTS idx_results_exam_id ON results(exam_id);
    CREATE INDEX IF NOT EXISTS idx_progress_user_id ON progress(user_id);
    CREATE INDEX IF NOT EXISTS idx_progress_subject ON progress(subject);
    
    -- Create updated_at trigger function
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    $$ language 'plpgsql';
    
    -- Create triggers for updated_at
    DROP TRIGGER IF EXISTS update_users_updated_at ON users;
    CREATE TRIGGER update_users_updated_at 
        BEFORE UPDATE ON users 
        FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
    
    DROP TRIGGER IF EXISTS update_questions_updated_at ON questions;
    CREATE TRIGGER update_questions_updated_at 
        BEFORE UPDATE ON questions 
        FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
    
    DROP TRIGGER IF EXISTS update_exams_updated_at ON exams;
    CREATE TRIGGER update_exams_updated_at 
        BEFORE UPDATE ON exams 
        FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
    """
    
    print("📋 SQL script ready for Supabase!")
    print("🔧 Please run this SQL in your Supabase SQL Editor:")
    print("\n" + "="*50)
    print(create_tables_sql + indexes_sql)
    print("="*50 + "\n")
    
    return True


async def seed_initial_data():
    """Seed initial data into the database."""
    print("🌱 Seeding initial data...")
    
    # Sample subjects and topics
    sample_data = [
        {
            "subject": "Mathematics",
            "topics": ["Algebra", "Geometry", "Calculus", "Statistics"]
        },
        {
            "subject": "Physics", 
            "topics": ["Mechanics", "Thermodynamics", "Electromagnetism", "Optics"]
        },
        {
            "subject": "Chemistry",
            "topics": ["Organic Chemistry", "Inorganic Chemistry", "Physical Chemistry"]
        },
        {
            "subject": "Biology",
            "topics": ["Cell Biology", "Genetics", "Ecology", "Human Physiology"]
        },
        {
            "subject": "Computer Science",
            "topics": ["Data Structures", "Algorithms", "Programming", "Database Systems"]
        }
    ]
    
    try:
        # Insert sample questions for each subject
        for subject_data in sample_data:
            subject = subject_data["subject"]
            topics = subject_data["topics"]
            
            for topic in topics:
                # Create a sample MCQ
                question_data = {
                    "content": f"What is a fundamental concept in {topic}?",
                    "question_type": "mcq",
                    "subject": subject,
                    "topic": topic,
                    "difficulty": "medium",
                    "options": [
                        "Option A",
                        "Option B", 
                        "Option C",
                        "Option D"
                    ],
                    "correct_answer": "Option A",
                    "explanation": f"This is a sample explanation for {topic} in {subject}.",
                    "tags": [topic.lower(), subject.lower()],
                    "metadata": {"auto_generated": True, "seed_data": True}
                }
                
                # Insert question using Supabase
                result = db_manager.supabase.table("questions").insert(question_data).execute()
                print(f"✅ Created sample question for {subject} - {topic}")
        
        print("✅ Initial data seeded successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        print("🔧 Make sure tables are created first!")
        return False


async def init_database():
    """Initialize the complete Supabase database."""
    print("🚀 Initializing EduAI Database (Supabase Only)")
    print(f"📡 Supabase URL: {settings.SUPABASE_URL}")
    print("=" * 60)
    
    # Check connection
    print("🔍 Testing Supabase connection...")
    if await db_manager.health_check():
        print("✅ Supabase connection successful!")
    else:
        print("❌ Supabase connection failed!")
        print("🔧 Please check your SUPABASE_URL and SUPABASE_ANON_KEY in .env")
        return False
    
    # Create tables
    print("\n📋 Generating table creation script...")
    if not await create_tables():
        return False
    
    print("⚠️  IMPORTANT: Please run the SQL script above in your Supabase SQL Editor")
    print("   1. Go to your Supabase Dashboard")
    print("   2. Navigate to SQL Editor")
    print("   3. Copy and paste the SQL script above")
    print("   4. Run the script to create tables")
    print("   5. Come back and run this script again to seed data")
    
    # Ask if tables are created
    try:
        response = input("\n❓ Have you run the SQL script in Supabase? (y/n): ").lower()
        if response == 'y':
            # Seed initial data
            if not await seed_initial_data():
                return False
        else:
            print("📝 Please create the tables first, then run this script again")
            return True
    except KeyboardInterrupt:
        print("\n👋 Setup cancelled by user")
        return False
    
    print("\n🎉 Database initialization completed successfully!")
    print("\n📝 Next steps:")
    print("1. Start the backend: cd backend && python -m uvicorn main:app --reload")
    print("2. Visit API docs: http://localhost:8000/docs")
    print("3. Start the frontend: npm run dev")
    
    return True


if __name__ == "__main__":
    try:
        asyncio.run(init_database())
    except KeyboardInterrupt:
        print("\n👋 Database initialization cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
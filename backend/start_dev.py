#!/usr/bin/env python
"""
EduAI Backend Development Startup Script
Handles environment setup, database initialization, and server startup.
"""
import asyncio
import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is supported."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def check_environment_file():
    """Check if .env file exists."""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found!")
        print("📋 Creating .env from template...")
        
        example_file = Path(".env.example")
        if example_file.exists():
            import shutil
            shutil.copy(".env.example", ".env")
            print("✅ .env file created from template")
            print("🔧 Please edit .env file with your actual configuration values")
            return False
        else:
            print("❌ .env.example template not found!")
            return False
    
    print("✅ .env file found")
    return True

def install_dependencies():
    """Install Python dependencies."""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True, text=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("🔧 Try running: pip install -r requirements.txt")
        return False

async def initialize_database():
    """Initialize database if needed."""
    print("🗄️  Initializing database...")
    try:
        # Import here to avoid import errors if dependencies aren't installed
        from app.db.database import db_manager
        
        # Check database connection
        if await db_manager.health_check():
            print("✅ Database connection successful")
            return True
        else:
            print("⚠️  Database connection failed")
            print("🔧 Please check your Supabase configuration in .env")
            return False
            
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        print("🔧 You may need to run: python init_db.py")
        return False

def start_server():
    """Start the FastAPI development server."""
    print("🚀 Starting EduAI Backend Server...")
    print("📖 API Documentation will be available at: http://localhost:8000/docs")
    print("🔍 Health check endpoint: http://localhost:8000/health")
    print("⏹️  Press Ctrl+C to stop the server")
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

async def main():
    """Main startup routine."""
    print("🎓 EduAI Backend Development Startup")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Check environment file
    if not check_environment_file():
        print("\n🔧 Please configure your .env file and run this script again")
        return
    
    # Install dependencies
    if not install_dependencies():
        print("\n🔧 Please install dependencies manually and run this script again")
        return
    
    # Initialize database
    if not await initialize_database():
        print("\n⚠️  Database initialization failed, but server will still start")
        print("🔧 Please check your Supabase configuration")
    
    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("=" * 50)
    
    # Start server
    start_server()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Startup cancelled by user")
    except Exception as e:
        print(f"\n❌ Startup error: {e}")
        sys.exit(1)
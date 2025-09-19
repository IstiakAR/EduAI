"""
Start the ultra-simple EduAI backend server
"""
import uvicorn
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def main():
    """Start the ultra-simple server."""
    print("🚀 Starting EduAI Ultra-Simple Backend...")
    print("📍 Server will run at: http://localhost:8000")
    print("🔗 API docs at: http://localhost:8000/docs")
    print("💬 Chat endpoint: http://localhost:8000/chat")
    print()
    
    # Check for Gemini API key
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        print("✅ Gemini API key found - Real AI responses enabled")
    else:
        print("⚠️  No Gemini API key - Demo responses will be used")
    print()
    
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down EduAI backend...")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
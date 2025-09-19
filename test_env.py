#!/usr/bin/env python3
"""
Environment Configuration Test Script
Tests that both frontend and backend can read from the unified .env file
"""
import os
import sys
from pathlib import Path

def test_env_loading():
    """Test environment variable loading."""
    print("🔧 EduAI Environment Configuration Test")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found in project root!")
        print("📋 Please copy .env.example to .env and configure it")
        return False
    
    print("✅ .env file found")
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment variables loaded")
    except ImportError:
        print("⚠️  python-dotenv not installed, using system env")
    
    # Test frontend variables
    print("\n🎨 Frontend Variables (VITE_ prefix):")
    frontend_vars = {
        "VITE_SUPABASE_URL": os.getenv("VITE_SUPABASE_URL"),
        "VITE_SUPABASE_ANON_KEY": os.getenv("VITE_SUPABASE_ANON_KEY")
    }
    
    for var, value in frontend_vars.items():
        if value:
            display_value = value[:50] + "..." if len(value) > 50 else value
            print(f"  ✅ {var}: {display_value}")
        else:
            print(f"  ❌ {var}: Not set")
    
    # Test backend variables
    print("\n🔧 Backend Variables:")
    backend_vars = {
        "SUPABASE_URL": os.getenv("SUPABASE_URL"),
        "SUPABASE_ANON_KEY": os.getenv("SUPABASE_ANON_KEY"),
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
        "GEMINI_MODEL": os.getenv("GEMINI_MODEL"),
        "SECRET_KEY": os.getenv("SECRET_KEY"),
        "APP_NAME": os.getenv("APP_NAME")
    }
    
    for var, value in backend_vars.items():
        if value:
            if "KEY" in var:
                display_value = value[:10] + "..." if len(value) > 10 else value
            else:
                display_value = value[:50] + "..." if len(value) > 50 else value
            print(f"  ✅ {var}: {display_value}")
        else:
            print(f"  ❌ {var}: Not set")
    
    # Test backend configuration loading
    print("\n🐍 Testing Backend Configuration:")
    try:
        sys.path.append("backend")
        from backend.app.core.config import get_settings
        settings = get_settings()
        print(f"  ✅ Backend config loaded successfully")
        print(f"  📊 App: {settings.APP_NAME} v{settings.VERSION}")
        print(f"  🤖 AI Model: {settings.GEMINI_MODEL}")
        print(f"  🌐 CORS Origins: {len(settings.cors_origins)} configured")
    except Exception as e:
        print(f"  ❌ Backend config error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Environment configuration test completed!")
    print("\n📝 Next steps:")
    print("  • Frontend: npm run dev (from project root)")
    print("  • Backend: cd backend && python -m uvicorn main:app --reload")
    print("  • API Docs: http://localhost:8000/docs")
    
    return True

if __name__ == "__main__":
    success = test_env_loading()
    sys.exit(0 if success else 1)
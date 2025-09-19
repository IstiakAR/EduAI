#!/usr/bin/env python3
"""
Test script to verify Gemini API integration
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../.env')

# Add the app directory to Python path
sys.path.append('.')

from app.services.gemini_service import GeminiService

async def test_gemini_basic():
    """Test basic Gemini API connectivity"""
    print("🔄 Testing basic Gemini API connectivity...")
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content('Hello, this is a test. Please respond with "API Test Successful".')
        print("✅ Basic Gemini API test passed!")
        print(f"Response: {response.text}")
        return True
    except Exception as e:
        print(f"❌ Basic Gemini API test failed: {e}")
        return False

async def test_gemini_service():
    """Test the GeminiService implementation"""
    print("\n🔄 Testing GeminiService question generation...")
    
    try:
        from app.schemas.question import QuestionType, Difficulty
        service = GeminiService()
        
        # Test question generation
        questions = await service.generate_questions(
            subject="Computer Science",
            topic="Python programming basics",
            difficulty=Difficulty.EASY,
            question_type=QuestionType.MCQ,
            num_questions=2
        )
        
        print("✅ Question generation test passed!")
        print(f"Generated {len(questions)} questions:")
        
        for i, question in enumerate(questions, 1):
            print(f"\n{i}. {question.question_text}")
            if hasattr(question, 'options') and question.options:
                for option in question.options:
                    mark = "✓" if option.is_correct else " "
                    print(f"   {option.option_id}. {option.text} {mark}")
            if hasattr(question, 'explanation'):
                print(f"   Explanation: {question.explanation}")
        
        return True
        
    except Exception as e:
        print(f"❌ GeminiService test failed: {e}")
        return False

async def test_answer_evaluation():
    """Test answer evaluation functionality"""
    print("\n🔄 Testing answer evaluation...")
    
    try:
        from app.schemas.question import QuestionType
        service = GeminiService()
        
        # Test answer evaluation
        evaluation = await service.evaluate_answer(
            question="What is a variable in Python?",
            correct_answer="A variable is a named storage location that holds data values.",
            user_answer="A variable stores data and can be used to hold different types of information.",
            question_type=QuestionType.SHORT
        )
        
        print("✅ Answer evaluation test passed!")
        print(f"Score: {evaluation.get('score', 'N/A')}")
        print(f"Feedback: {evaluation.get('feedback', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Answer evaluation test failed: {e}")
        return False

async def main():
    """Run all Gemini API tests"""
    print("🚀 Starting Gemini API Integration Tests")
    print("=" * 50)
    
    # Test basic connectivity
    basic_test = await test_gemini_basic()
    
    if basic_test:
        # Test service implementation
        service_test = await test_gemini_service()
        evaluation_test = await test_answer_evaluation()
        
        print("\n" + "=" * 50)
        print("📊 Test Results Summary:")
        print(f"Basic API: {'✅ PASS' if basic_test else '❌ FAIL'}")
        print(f"Question Gen: {'✅ PASS' if service_test else '❌ FAIL'}")
        print(f"Answer Eval: {'✅ PASS' if evaluation_test else '❌ FAIL'}")
        
        if all([basic_test, service_test, evaluation_test]):
            print("\n🎉 All Gemini API tests passed! Your integration is working correctly.")
        else:
            print("\n⚠️  Some tests failed. Check the error messages above.")
    else:
        print("\n❌ Basic API test failed. Please check your GEMINI_API_KEY in .env file.")

if __name__ == "__main__":
    asyncio.run(main())
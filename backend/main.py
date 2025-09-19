from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import os
from typing import Optional
from dotenv import load_dotenv

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

# Request/Response models
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
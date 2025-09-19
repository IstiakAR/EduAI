"""
EduAI - AI-Based Exam Preparation & Assessment Tool
Main application entry point.
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time
import logging
from contextlib import asynccontextmanager

# Import routers
from app.api.auth import router as auth_router
from app.api.questions import router as questions_router
from app.api.evaluation import router as evaluation_router
from app.api.assistant import router as assistant_router
from app.api.analytics import router as analytics_router

# Import configuration
from app.core.config import get_settings
from app.db.database import db_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting EduAI application...")
    
    # Check database connection
    try:
        if await db_manager.health_check():
            logger.info("Database connection successful")
        else:
            logger.warning("Database connection failed")
    except Exception as e:
        logger.error(f"Database health check error: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down EduAI application...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="""
    AI-Based Exam Preparation & Assessment Tool

    ## Features

    * **Question Generation**: Generate MCQ, short, and long questions using AI
    * **AI-Powered Evaluation**: Intelligent answer assessment with detailed feedback
    * **AI Assistant**: Academic question answering with research capabilities
    * **Analytics & Progress**: Comprehensive learning analytics and progress tracking
    * **Authentication**: Secure JWT-based user authentication
    * **Gamification**: Points, levels, and badges to motivate learning

    ## Authentication

    Most endpoints require authentication. Use the `/auth/login` endpoint to obtain a token,
    then include it in the Authorization header: `Bearer <token>`
    """,
    contact={
        "name": "EduAI Support",
        "email": "support@eduai.com",
    },
    license_info={
        "name": "MIT",
    },
    lifespan=lifespan
)

# Add security middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"]  # Configure appropriately for production
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add process time header to responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": "An unexpected error occurred. Please try again later."
        }
    )


# Rate limiting exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code
        }
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    try:
        db_healthy = await db_manager.health_check()
        
        return {
            "status": "healthy" if db_healthy else "unhealthy",
            "timestamp": time.time(),
            "database": "connected" if db_healthy else "disconnected",
            "version": settings.VERSION
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": time.time(),
                "error": str(e),
                "version": settings.VERSION
            }
        )


# Root endpoint
@app.get("/", tags=["Root"])
async def read_root():
    """Welcome endpoint."""
    return {
        "message": "Welcome to EduAI - AI-Based Exam Preparation & Assessment Tool",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health"
    }


# API version endpoint
@app.get("/api/v1", tags=["API Info"])
async def api_info():
    """API information endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "description": "AI-powered educational platform API",
        "endpoints": {
            "authentication": "/api/v1/auth",
            "questions": "/api/v1/questions", 
            "evaluation": "/api/v1/evaluate",
            "assistant": "/api/v1/assistant",
            "analytics": "/api/v1/analytics"
        },
        "features": [
            "AI Question Generation",
            "Intelligent Answer Evaluation", 
            "Academic AI Assistant",
            "Learning Analytics",
            "Progress Tracking",
            "Gamification"
        ]
    }


# Include API routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(questions_router, prefix="/api/v1")
app.include_router(evaluation_router, prefix="/api/v1")
app.include_router(assistant_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
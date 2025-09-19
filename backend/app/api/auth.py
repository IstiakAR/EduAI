"""
Authentication API endpoints.
"""
from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials
from app.schemas.user import (
    UserCreate, UserLogin, UserResponse, UserProfile, Token, 
    TokenRefresh, PasswordChange, PasswordReset
)
from app.core.security import (
    SecurityUtils, get_current_user_id, get_refresh_token_user_id,
    verify_password, create_access_token, create_refresh_token
)
from app.db.crud import user_crud
from app.core.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate):
    """Register a new user."""
    
    # Check if user already exists
    existing_email = await user_crud.get_user_by_email(user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    existing_username = await user_crud.get_user_by_username(user_data.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    try:
        user = await user_crud.create_user(
            email=user_data.email,
            username=user_data.username,
            password=user_data.password,
            full_name=user_data.full_name
        )
        
        return UserResponse(**user)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user account"
        )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """Authenticate user and return tokens."""
    
    # Try to find user by email or username
    user = None
    if "@" in credentials.username_or_email:
        user = await user_crud.get_user_by_email(credentials.username_or_email)
    else:
        user = await user_crud.get_user_by_username(credentials.username_or_email)
    
    # Verify user exists and password is correct
    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password"
        )
    
    # Check if user is active
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    # Create tokens
    access_token = create_access_token({"sub": user["id"]})
    refresh_token = create_refresh_token({"sub": user["id"]})
    
    # Update last login
    await user_crud.update_last_login(user["id"])
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(user_id: str = Depends(get_refresh_token_user_id)):
    """Refresh access token using refresh token."""
    
    # Verify user still exists and is active
    user = await user_crud.get_user_by_id(user_id)
    if not user or not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Create new tokens
    access_token = create_access_token({"sub": user_id})
    refresh_token = create_refresh_token({"sub": user_id})
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.get("/me", response_model=UserProfile)
async def get_current_user(user_id: str = Depends(get_current_user_id)):
    """Get current user profile."""
    
    user = await user_crud.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get additional profile statistics
    # This would typically come from other services/crud operations
    profile_data = {
        **user,
        "total_exams": 0,  # TODO: Get from exam_crud
        "total_questions_answered": 0,  # TODO: Get from answer_crud
        "average_score": 0.0,  # TODO: Calculate from results
        "current_streak": 0,  # TODO: Get from progress_crud
        "total_study_time_minutes": 0,  # TODO: Get from progress_crud
        "level": 1,  # TODO: Get from progress_crud
        "badges": []  # TODO: Get from progress_crud
    }
    
    return UserProfile(**profile_data)


@router.put("/me", response_model=UserResponse)
async def update_profile(
    update_data: dict,
    user_id: str = Depends(get_current_user_id)
):
    """Update current user profile."""
    
    # Validate that user exists
    user = await user_crud.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user
    try:
        updated_user = await user_crud.update_user(user_id, update_data)
        return UserResponse(**updated_user)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    user_id: str = Depends(get_current_user_id)
):
    """Change user password."""
    
    # Get current user
    user = await user_crud.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify current password
    if not verify_password(password_data.current_password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    try:
        hashed_new_password = SecurityUtils.hash_password(password_data.new_password)
        await user_crud.update_user(user_id, {"hashed_password": hashed_new_password})
        
        return {"message": "Password updated successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update password"
        )


@router.post("/logout")
async def logout(user_id: str = Depends(get_current_user_id)):
    """Logout user (invalidate token on client side)."""
    
    # Note: In a production system, you might want to maintain a blacklist of tokens
    # For now, we'll just return a success message and let the client handle token removal
    
    return {"message": "Logged out successfully"}


@router.post("/forgot-password")
async def forgot_password(request: PasswordReset):
    """Initiate password reset process."""
    
    # Check if user exists
    user = await user_crud.get_user_by_email(request.email)
    if not user:
        # Don't reveal if email exists or not for security
        return {"message": "If the email exists, a reset link has been sent"}
    
    # TODO: Implement password reset email sending
    # This would typically involve:
    # 1. Generate a secure reset token
    # 2. Store it in database with expiration
    # 3. Send email with reset link
    
    return {"message": "If the email exists, a reset link has been sent"}


@router.get("/verify-token")
async def verify_token(user_id: str = Depends(get_current_user_id)):
    """Verify if the current token is valid."""
    
    return {"valid": True, "user_id": user_id}
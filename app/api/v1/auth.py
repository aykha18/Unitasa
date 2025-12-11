"""
Enhanced Authentication API
Handles login, token refresh, password reset
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.user import User
from app.core.jwt_handler import JWTHandler, create_user_tokens, verify_password
from app.core.email_service import EmailService

router = APIRouter()
security = HTTPBearer()

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False

class LoginResponse(BaseModel):
    success: bool
    message: str
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: Dict[str, Any]

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
    confirm_password: str

class ProfileUpdateRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    company: Optional[str] = None
    avatar_url: Optional[str] = None

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
) -> LoginResponse:
    """User login with email and password"""
    try:
        # Find user by email
        result = await db.execute(select(User).where(User.email == request.email))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(request.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if account is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is disabled. Please contact support."
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        await db.commit()
        
        # Create tokens
        tokens = create_user_tokens(user)
        
        # Prepare user data
        user_data = {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "company": user.company,
            "is_co_creator": user.is_co_creator,
            "subscription_tier": user.subscription_tier,
            "is_verified": user.is_verified,
            "trial_end_date": user.trial_end_date.isoformat() if user.trial_end_date else None,
            "trial_days_remaining": user.trial_days_remaining,
            "is_trial_active": user.is_trial_active,
            "avatar_url": user.avatar_url,
            "last_login": user.last_login.isoformat() if user.last_login else None
        }
        
        return LoginResponse(
            success=True,
            message="Login successful",
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=tokens["expires_in"],
            user=user_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[LOGIN] Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again."
        )

@router.post("/refresh")
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Refresh access token using refresh token"""
    try:
        # Verify refresh token
        payload = JWTHandler.verify_token(request.refresh_token, "refresh")
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user from database
        result = await db.execute(select(User).where(User.id == int(user_id)))
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new tokens
        tokens = create_user_tokens(user)
        
        return {
            "success": True,
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "token_type": tokens["token_type"],
            "expires_in": tokens["expires_in"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[REFRESH_TOKEN] Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@router.post("/password-reset")
async def request_password_reset(
    request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Request password reset email"""
    try:
        # Find user by email
        result = await db.execute(select(User).where(User.email == request.email))
        user = result.scalar_one_or_none()
        
        if not user:
            # Don't reveal if email exists or not for security
            return {
                "success": True,
                "message": "If an account with this email exists, you will receive a password reset link."
            }
        
        # Generate password reset token (reuse email verification token field)
        reset_token = user.generate_email_verification_token()
        await db.commit()
        
        # Send password reset email
        email_service = EmailService()
        email_sent, email_message = email_service.send_password_reset_email(
            user=user,
            reset_token=reset_token
        )
        
        if not email_sent:
            print(f"[PASSWORD_RESET] Failed to send email: {email_message}")
        
        return {
            "success": True,
            "message": "If an account with this email exists, you will receive a password reset link."
        }
        
    except Exception as e:
        print(f"[PASSWORD_RESET] Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset request failed"
        )

@router.post("/password-reset/confirm")
async def confirm_password_reset(
    request: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Confirm password reset with token"""
    try:
        if request.new_password != request.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match"
            )
        
        if len(request.new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long"
            )
        
        # Find user by reset token
        result = await db.execute(
            select(User).where(User.email_verification_token == request.token)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Check if token is expired (24 hours)
        if user.email_verification_sent_at:
            if datetime.utcnow() - user.email_verification_sent_at > timedelta(hours=24):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Reset token has expired"
                )
        
        # Update password
        from app.core.jwt_handler import get_password_hash
        user.hashed_password = get_password_hash(request.new_password)
        user.email_verification_token = None  # Clear the token
        user.email_verification_sent_at = None
        
        await db.commit()
        
        return {
            "success": True,
            "message": "Password has been reset successfully. You can now log in with your new password."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[PASSWORD_RESET_CONFIRM] Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset confirmation failed"
        )

@router.get("/me")
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get current user information from token"""
    try:
        # Extract user info from token
        user_info = JWTHandler.get_user_from_token(credentials.credentials)
        
        # Get fresh user data from database
        result = await db.execute(select(User).where(User.id == user_info["user_id"]))
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "company": user.company,
            "is_co_creator": user.is_co_creator,
            "subscription_tier": user.subscription_tier,
            "is_verified": user.is_verified,
            "trial_end_date": user.trial_end_date.isoformat() if user.trial_end_date else None,
            "trial_days_remaining": user.trial_days_remaining,
            "is_trial_active": user.is_trial_active,
            "avatar_url": user.avatar_url,
            "last_login": user.last_login.isoformat() if user.last_login else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[GET_CURRENT_USER] Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )

@router.put("/profile")
async def update_user_profile(
    request: ProfileUpdateRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Update current user's profile information"""
    try:
        # Extract user info from token
        user_info = JWTHandler.get_user_from_token(credentials.credentials)
        user_id = user_info["user_id"]

        # Get user from database
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        # Update user fields if provided
        if request.first_name is not None:
            user.first_name = request.first_name
        if request.last_name is not None:
            user.last_name = request.last_name
        if request.full_name is not None:
            user.full_name = request.full_name
        if request.company is not None:
            user.company = request.company
        if request.avatar_url is not None:
            user.avatar_url = request.avatar_url

        # Commit changes
        await db.commit()

        # Return updated user data
        return {
            "success": True,
            "message": "Profile updated successfully",
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "company": user.company,
                "is_co_creator": user.is_co_creator,
                "subscription_tier": user.subscription_tier,
                "is_verified": user.is_verified,
                "trial_end_date": user.trial_end_date.isoformat() if user.trial_end_date else None,
                "trial_days_remaining": user.trial_days_remaining,
                "is_trial_active": user.is_trial_active,
                "avatar_url": user.avatar_url,
                "last_login": user.last_login.isoformat() if user.last_login else None
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[UPDATE_PROFILE] Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )

@router.put("/password")
async def change_password(
    request: PasswordChangeRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Change current user's password"""
    try:
        # Extract user info from token
        user_info = JWTHandler.get_user_from_token(credentials.credentials)
        user_id = user_info["user_id"]

        # Get user from database
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        # Verify current password
        if not verify_password(request.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        # Validate new password
        if request.new_password != request.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New passwords do not match"
            )

        if len(request.new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be at least 8 characters long"
            )

        # Update password
        from app.core.jwt_handler import get_password_hash
        user.hashed_password = get_password_hash(request.new_password)

        # Commit changes
        await db.commit()

        return {
            "success": True,
            "message": "Password changed successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[CHANGE_PASSWORD] Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )
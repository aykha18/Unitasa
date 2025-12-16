"""
User registration API endpoints
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext

from app.core.database import get_db
from app.models.user import User
from app.models.lead import Lead
from app.models.co_creator_program import CoCreator
from app.core.email_service import EmailService

router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

import bcrypt

class UserRegistrationRequest(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    company: str
    password: str
    confirmPassword: str
    agreeToTerms: bool
    pricingTier: Optional[str] = "pro"
    billingCycle: Optional[str] = "monthly"

class UserRegistrationResponse(BaseModel):
    success: bool
    message: str
    user_id: Optional[int] = None
    is_co_creator: bool = False

class GoogleOAuthRequest(BaseModel):
    credential: str  # Google ID token
    company: Optional[str] = None

class GoogleOAuthResponse(BaseModel):
    success: bool
    message: str
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: Dict[str, Any]

class FacebookOAuthRequest(BaseModel):
    access_token: str  # Facebook access token
    company: Optional[str] = None

class FacebookOAuthResponse(BaseModel):
    success: bool
    message: str
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: Dict[str, Any]

@router.post("/register", response_model=UserRegistrationResponse)
async def register_user(
    request: UserRegistrationRequest,
    db: AsyncSession = Depends(get_db)
) -> UserRegistrationResponse:
    """Register a new user account"""
    try:
        # Validate passwords match
        if request.password != request.confirmPassword:
            raise HTTPException(
                status_code=400,
                detail="Passwords do not match"
            )

        # Check if user already exists
        result = await db.execute(select(User).where(User.email == request.email))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="User with this email already exists"
            )

        # Hash password
        hashed_password = bcrypt.hashpw(request.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Determine subscription tier and trial settings
        subscription_tier = request.pricingTier or "free_trial"
        if request.pricingTier == "free":
            subscription_tier = "free_trial"  # Free trial for 15 days
            trial_end_date = datetime.utcnow() + timedelta(days=15)
        else:
            subscription_tier = request.pricingTier or "pro"
            trial_end_date = None  # Paid plans don't need trial

        # Create new user
        new_user = User(
            first_name=request.firstName,
            last_name=request.lastName,
            email=request.email,
            company=request.company,
            hashed_password=hashed_password,
            subscription_tier=subscription_tier,
            billing_cycle=request.billingCycle or "monthly",
            is_active=True,
            is_verified=False,
            trial_end_date=trial_end_date,
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        # Send welcome email
        email_service = EmailService()
        email_sent, email_message = email_service.send_welcome_email(new_user)

        if not email_sent:
            print(f"[REGISTRATION] Failed to send welcome email: {email_message}")

        return UserRegistrationResponse(
            success=True,
            message="Account created successfully! Please check your email for verification instructions.",
            user_id=new_user.id,
            is_co_creator=False
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"[REGISTRATION] Error: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Registration failed. Please try again."
        )
"""
User registration API endpoints
"""

from typing import Dict, Any, Optional
from datetime import datetime
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

class UserRegistrationResponse(BaseModel):
    success: bool
    message: str
    user_id: Optional[int] = None
    is_co_creator: bool = False

class GoogleOAuthRequest(BaseModel):
    credential: str  # Google ID token
    company: Optional[str] = None

def hash_password(password: str) -> str:
    """Hash a password using bcrypt directly"""
    # Use bcrypt directly to avoid passlib issues
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password using bcrypt directly"""
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)

@router.post("/register", response_model=UserRegistrationResponse)
async def register_user(
    request: UserRegistrationRequest,
    db: AsyncSession = Depends(get_db)
) -> UserRegistrationResponse:
    """Register a new user account"""
    try:
        print(f"[USER_REGISTRATION] Starting registration for: {request.email}")
        
        # Validate passwords match
        if request.password != request.confirmPassword:
            raise HTTPException(status_code=400, detail="Passwords do not match")
        
        # Validate password length (bcrypt has 72 byte limit)
        if len(request.password.encode('utf-8')) > 72:
            raise HTTPException(status_code=400, detail="Password is too long (max 72 characters)")
        
        # Validate password strength
        if len(request.password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
        
        # Validate terms agreement
        if not request.agreeToTerms:
            raise HTTPException(status_code=400, detail="You must agree to the terms of service")
        
        # Check if user already exists
        result = await db.execute(select(User).where(User.email == request.email))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        
        # Check if there's an existing lead for this email (from assessment)
        result = await db.execute(select(Lead).where(Lead.email == request.email))
        existing_lead = result.scalar_one_or_none()
        
        # Hash password
        from app.core.jwt_handler import get_password_hash
        hashed_password = get_password_hash(request.password)
        
        # Create new user with 15-day free trial
        from datetime import timedelta
        trial_end_date = datetime.utcnow() + timedelta(days=15)
        
        new_user = User(
            email=request.email,
            hashed_password=hashed_password,
            full_name=f"{request.firstName} {request.lastName}",
            first_name=request.firstName,
            last_name=request.lastName,
            company=request.company,
            is_active=True,
            is_verified=False,  # Email verification can be added later
            role="user",
            subscription_tier="free_trial",
            trial_end_date=trial_end_date
            # created_at will be set automatically by TimestampMixin
        )
        
        db.add(new_user)
        await db.flush()  # Get the user ID
        
        print(f"[USER_REGISTRATION] Created user with ID: {new_user.id}")
        
        # Check if user is a co-creator (has paid for co-creator program)
        is_co_creator = False
        if existing_lead:
            print(f"[USER_REGISTRATION] Found existing lead: {existing_lead.id}")
            
            # Update lead with user_id
            existing_lead.user_id = new_user.id
            
            # Check if this lead has a co-creator record
            result = await db.execute(
                select(CoCreator).where(CoCreator.lead_id == existing_lead.id)
            )
            co_creator = result.scalar_one_or_none()
            
            if co_creator:
                print(f"[USER_REGISTRATION] User is a co-creator: {co_creator.id}")
                # Update user to co-creator status
                new_user.is_co_creator = True
                new_user.co_creator_joined_at = datetime.utcnow()
                new_user.lifetime_access = True
                new_user.co_creator_seat_number = co_creator.seat_number
                new_user.subscription_tier = "co_creator"
                
                # Update co-creator record with user_id
                co_creator.user_id = new_user.id
                
                is_co_creator = True
        
        # Generate email verification token
        verification_token = new_user.generate_email_verification_token()
        
        await db.commit()
        
        print(f"[USER_REGISTRATION] Registration completed successfully")
        
        # Send welcome email with verification
        email_service = EmailService()
        
        if is_co_creator:
            # Co-creators get the existing co-creator welcome email
            # This would be handled by the co-creator payment flow
            pass
        else:
            # Free trial users get the new welcome email
            email_sent, email_message = email_service.send_free_trial_welcome_email(
                user=new_user,
                verification_token=verification_token
            )
            
            if not email_sent:
                print(f"[USER_REGISTRATION] Failed to send welcome email: {email_message}")
                # Don't fail registration if email fails
        
        return UserRegistrationResponse(
            success=True,
            message=f"Welcome to Unitasa! Your 15-day free trial has started. Please check your email to verify your account." + (" You're also a Co-Creator!" if is_co_creator else ""),
            user_id=new_user.id,
            is_co_creator=is_co_creator
        )
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        print(f"[USER_REGISTRATION] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.get("/check-email/{email}")
async def check_email_availability(
    email: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Check if email is available for registration"""
    try:
        result = await db.execute(select(User).where(User.email == email))
        existing_user = result.scalar_one_or_none()
        
        return {
            "available": existing_user is None,
            "message": "Email is available" if existing_user is None else "Email is already registered"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email check failed: {str(e)}")

@router.post("/verify-email")
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Verify user email with token"""
    try:
        result = await db.execute(
            select(User).where(User.email_verification_token == token)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=400, detail="Invalid or expired verification token")
        
        # Check if token is expired (24 hours)
        if user.email_verification_sent_at:
            from datetime import timedelta
            if datetime.utcnow() - user.email_verification_sent_at > timedelta(hours=24):
                raise HTTPException(status_code=400, detail="Verification token has expired")
        
        # Verify email
        if user.verify_email(token):
            await db.commit()
            return {
                "success": True,
                "message": "Email verified successfully! Your account is now fully activated."
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid verification token")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email verification failed: {str(e)}")

@router.post("/resend-verification")
async def resend_verification_email(
    email: EmailStr,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Resend email verification"""
    try:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.is_verified:
            return {
                "success": True,
                "message": "Email is already verified"
            }
        
        # Generate new verification token
        verification_token = user.generate_email_verification_token()
        await db.commit()
        
        # Send verification email
        email_service = EmailService()
        email_sent, email_message = email_service.send_email_verification(
            user=user,
            verification_token=verification_token
        )
        
        if email_sent:
            return {
                "success": True,
                "message": "Verification email sent successfully"
            }
        else:
            raise HTTPException(status_code=500, detail=f"Failed to send verification email: {email_message}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resend verification: {str(e)}")


@router.post("/google-oauth", response_model=UserRegistrationResponse)
async def google_oauth_signup(
    request: GoogleOAuthRequest,
    db: AsyncSession = Depends(get_db)
) -> UserRegistrationResponse:
    """Register/login user with Google OAuth"""
    try:
        # In a real implementation, you would verify the Google ID token
        # For now, we'll create a placeholder implementation
        
        # TODO: Implement Google ID token verification
        # from google.oauth2 import id_token
        # from google.auth.transport import requests
        # 
        # idinfo = id_token.verify_oauth2_token(
        #     request.credential, 
        #     requests.Request(), 
        #     "YOUR_GOOGLE_CLIENT_ID"
        # )
        
        # For demo purposes, we'll extract basic info from the credential
        # In production, properly verify the JWT token
        import json
        import base64
        
        # This is a simplified approach - DO NOT use in production
        # You must properly verify Google ID tokens
        try:
            # Decode the JWT payload (this is unsafe without verification)
            parts = request.credential.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid credential format")
            
            # Add padding if needed
            payload = parts[1]
            payload += '=' * (4 - len(payload) % 4)
            
            decoded = base64.urlsafe_b64decode(payload)
            user_info = json.loads(decoded)
            
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid Google credential")
        
        email = user_info.get('email')
        name = user_info.get('name', '')
        given_name = user_info.get('given_name', '')
        family_name = user_info.get('family_name', '')
        
        if not email:
            raise HTTPException(status_code=400, detail="Email not provided by Google")
        
        # Check if user already exists
        result = await db.execute(select(User).where(User.email == email))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            # User exists, log them in
            return UserRegistrationResponse(
                success=True,
                message="Welcome back! Logged in successfully with Google.",
                user_id=existing_user.id,
                is_co_creator=existing_user.is_co_creator
            )
        
        # Create new user
        from datetime import timedelta
        trial_end_date = datetime.utcnow() + timedelta(days=15)
        
        new_user = User(
            email=email,
            hashed_password="",  # No password for OAuth users
            full_name=name,
            first_name=given_name,
            last_name=family_name,
            company=request.company or "",
            is_active=True,
            is_verified=True,  # Google accounts are pre-verified
            role="user",
            subscription_tier="free_trial",
            trial_end_date=trial_end_date
        )
        
        db.add(new_user)
        await db.flush()
        
        # Check for existing lead/co-creator status
        result = await db.execute(select(Lead).where(Lead.email == email))
        existing_lead = result.scalar_one_or_none()
        
        is_co_creator = False
        if existing_lead:
            existing_lead.user_id = new_user.id
            
            # Check for co-creator status
            result = await db.execute(
                select(CoCreator).where(CoCreator.lead_id == existing_lead.id)
            )
            co_creator = result.scalar_one_or_none()
            
            if co_creator:
                new_user.is_co_creator = True
                new_user.co_creator_joined_at = datetime.utcnow()
                new_user.lifetime_access = True
                new_user.co_creator_seat_number = co_creator.seat_number
                new_user.subscription_tier = "co_creator"
                co_creator.user_id = new_user.id
                is_co_creator = True
        
        await db.commit()
        
        # Send welcome email (no verification needed for Google OAuth)
        email_service = EmailService()
        if not is_co_creator:
            email_service.send_free_trial_welcome_email(user=new_user)
        
        return UserRegistrationResponse(
            success=True,
            message=f"Welcome to Unitasa! Your account has been created with Google and your 15-day free trial has started." + (" You're also a Co-Creator!" if is_co_creator else ""),
            user_id=new_user.id,
            is_co_creator=is_co_creator
        )
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        print(f"[GOOGLE_OAUTH] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Google OAuth signup failed: {str(e)}")
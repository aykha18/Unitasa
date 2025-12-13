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
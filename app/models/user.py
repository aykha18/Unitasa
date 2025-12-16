"""
User model for authentication and user management
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """User model for the marketing platform"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    first_name = Column(String(100))
    last_name = Column(String(100))
    company = Column(String(255))
    role = Column(String(50), default="user")  # admin, user, agent
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # API key for authentication
    api_key = Column(String(255), unique=True, index=True)

    # Profile information
    avatar_url = Column(Text)
    bio = Column(Text)
    website = Column(String(255))

    # Subscription and limits
    subscription_tier = Column(String(50), default="free")  # free, free_trial, pro, enterprise, co_creator
    # billing_cycle = Column(String(20), default="monthly")  # monthly, quarterly, annual
    monthly_request_limit = Column(Integer, default=1000)
    requests_this_month = Column(Integer, default=0)
    trial_end_date = Column(DateTime)  # For free trial users

    # Co-creator program status
    is_co_creator = Column(Boolean, default=False, nullable=False, index=True)
    co_creator_joined_at = Column(DateTime)
    lifetime_access = Column(Boolean, default=False, nullable=False)
    co_creator_seat_number = Column(Integer)  # 1-25 for founding users
    co_creator_benefits = Column(Text)  # JSON string of benefits
    
    # Email verification
    email_verification_token = Column(String(255), unique=True, index=True)
    email_verification_sent_at = Column(DateTime)
    email_verified_at = Column(DateTime)
    
    # Timestamps (inherited from TimestampMixin)
    last_login = Column(DateTime)

    # Relationships
    events = relationship("Event", back_populates="user", cascade="all, delete-orphan")
    campaigns = relationship("Campaign", back_populates="user", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")

    # Social media relationships
    social_accounts = relationship("SocialAccount", back_populates="user", cascade="all, delete-orphan")
    social_posts = relationship("SocialPost", back_populates="user", cascade="all, delete-orphan")
    engagements = relationship("Engagement", back_populates="user", cascade="all, delete-orphan")
    content_templates = relationship("ContentTemplate", back_populates="user", cascade="all, delete-orphan")
    analytics_snapshots = relationship("AnalyticsSnapshot", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"

    def can_make_request(self) -> bool:
        """Check if user can make another API request this month"""
        return self.requests_this_month < self.monthly_request_limit

    def increment_request_count(self):
        """Increment the monthly request count"""
        self.requests_this_month += 1

    def reset_request_count(self):
        """Reset monthly request count (for billing cycle)"""
        self.requests_this_month = 0

    @property
    def is_admin(self) -> bool:
        """Check if user is an admin"""
        return self.role == "admin"

    @property
    def is_pro(self) -> bool:
        """Check if user has pro subscription"""
        return self.subscription_tier in ["pro", "enterprise"]

    @property
    def is_enterprise(self) -> bool:
        """Check if user has enterprise subscription"""
        return self.subscription_tier == "enterprise"

    @property
    def is_founding_user(self) -> bool:
        """Check if user is a founding co-creator"""
        return self.is_co_creator and self.co_creator_seat_number is not None

    def activate_co_creator_status(self, seat_number: int, benefits: str = None):
        """Activate co-creator status for user"""
        self.is_co_creator = True
        self.co_creator_joined_at = datetime.utcnow()
        self.lifetime_access = True
        self.co_creator_seat_number = seat_number
        self.co_creator_benefits = benefits
        self.updated_at = datetime.utcnow()

    def deactivate_co_creator_status(self):
        """Deactivate co-creator status"""
        self.is_co_creator = False
        self.lifetime_access = False
        self.co_creator_seat_number = None
        self.co_creator_benefits = None
        self.updated_at = datetime.utcnow()

    def generate_email_verification_token(self) -> str:
        """Generate email verification token"""
        import secrets
        token = secrets.token_urlsafe(32)
        self.email_verification_token = token
        self.email_verification_sent_at = datetime.utcnow()
        return token

    def verify_email(self, token: str) -> bool:
        """Verify email with token"""
        if self.email_verification_token == token:
            self.is_verified = True
            self.email_verified_at = datetime.utcnow()
            self.email_verification_token = None  # Clear token after use
            return True
        return False

    @property
    def is_trial_active(self) -> bool:
        """Check if free trial is still active"""
        if self.subscription_tier != "free_trial" or not self.trial_end_date:
            return False
        return datetime.utcnow() < self.trial_end_date

    @property
    def trial_days_remaining(self) -> int:
        """Get remaining trial days"""
        if not self.is_trial_active:
            return 0
        delta = self.trial_end_date - datetime.utcnow()
        return max(0, delta.days)

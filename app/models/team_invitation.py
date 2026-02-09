"""
Team Invitation model
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .base import Base

class TeamInvitation(Base):
    __tablename__ = "team_invitations"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, index=True)
    role = Column(String(50), default="member")
    status = Column(String(50), default="pending")  # pending, accepted, expired
    token = Column(String(255), unique=True, nullable=False)
    
    invited_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    accepted_at = Column(DateTime, nullable=True)

    invited_by = relationship("User", back_populates="sent_invitations")

"""
Team management API endpoints
"""

from typing import List, Optional
import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.user import User
from app.models.team_invitation import TeamInvitation
from app.api.v1.auth import get_current_active_user

router = APIRouter()

class InviteRequest(BaseModel):
    emails: List[EmailStr]
    role: str = "member"

class InviteResponse(BaseModel):
    success: bool
    message: str
    sent_count: int
    skipped_count: int
    skipped_emails: List[str]

@router.post("/invite", response_model=InviteResponse)
async def invite_team_members(
    request: InviteRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Invite team members to the organization.
    For now, this simply creates an invitation record.
    """
    try:
        sent_count = 0
        skipped_count = 0
        skipped_emails = []
        
        for email in request.emails:
            # Check if user already exists
            existing_user = await db.execute(select(User).where(User.email == email))
            if existing_user.scalar_one_or_none():
                # Skip existing users for now, or maybe handle differently
                skipped_count += 1
                skipped_emails.append(f"{email} (User already exists)")
                continue
                
            # Check if invitation already exists
            existing_invitation = await db.execute(
                select(TeamInvitation).where(
                    TeamInvitation.email == email,
                    TeamInvitation.status == "pending"
                )
            )
            if existing_invitation.scalar_one_or_none():
                skipped_count += 1
                skipped_emails.append(f"{email} (Invitation already pending)")
                continue

            # Create invitation
            token = secrets.token_urlsafe(32)
            invitation = TeamInvitation(
                email=email,
                role=request.role,
                status="pending",
                token=token,
                invited_by_id=current_user.id,
                expires_at=datetime.utcnow() + timedelta(days=7)
            )
            db.add(invitation)
            sent_count += 1
            
            # TODO: Send actual email using EmailService
        
        await db.commit()
        
        message = f"Successfully sent {sent_count} invitations"
        if skipped_count > 0:
            message += f". Skipped {skipped_count} emails (already exist or invited)."
        
        return {
            "success": True,
            "message": message,
            "sent_count": sent_count,
            "skipped_count": skipped_count,
            "skipped_emails": skipped_emails
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to invite team members: {str(e)}"
        )

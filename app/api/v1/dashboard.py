"""
Dashboard API endpoints
Provides analytics and onboarding data for the user dashboard
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.jwt_handler import JWTHandler
from app.models.user import User
from app.models.social_account import SocialAccount, SocialPost
from app.models.campaign import Campaign
from app.models.crm_integration import CRMConnection, ConnectionStatus
from app.models.team_invitation import TeamInvitation

router = APIRouter()
security = HTTPBearer()

@router.get("/analytics")
async def get_dashboard_analytics(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get dashboard analytics data for the current user"""
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

        # For now, return mock analytics data
        # TODO: Implement real analytics based on user campaigns, leads, etc.
        analytics_data = {
            "totalLeads": 0,  # Will be calculated from actual lead data
            "campaignsActive": 0,  # Will be calculated from active campaigns
            "engagementRate": 0,  # Will be calculated from engagement metrics
            "conversionRate": 0  # Will be calculated from conversion metrics
        }

        # Try to get some basic stats if tables exist
        try:
            # This is a placeholder - actual implementation would depend on your data models
            # For example, if you have Lead, Campaign, etc. models
            analytics_data["totalLeads"] = 0  # Replace with actual query
            analytics_data["campaignsActive"] = 0  # Replace with actual query
            analytics_data["engagementRate"] = 0  # Replace with actual calculation
            analytics_data["conversionRate"] = 0  # Replace with actual calculation
        except Exception as e:
            # If tables don't exist yet, keep mock data
            print(f"Analytics calculation failed, using mock data: {e}")
            pass

        return analytics_data

    except HTTPException:
        raise
    except Exception as e:
        print(f"[DASHBOARD_ANALYTICS] Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get analytics data"
        )

@router.get("/onboarding")
async def get_onboarding_progress(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get onboarding progress for the current user"""
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

        # Check CRM connection
        crm_result = await db.execute(
            select(CRMConnection).where(
                CRMConnection.user_id == user_id,
                CRMConnection.connection_status == ConnectionStatus.CONNECTED
            ).limit(1)
        )
        has_crm = crm_result.scalar_one_or_none() is not None

        # Check first campaign (Campaigns or Social Posts)
        campaign_result = await db.execute(
            select(Campaign).where(Campaign.user_id == user_id).limit(1)
        )
        has_campaign = campaign_result.scalar_one_or_none() is not None

        post_result = await db.execute(
            select(SocialPost).where(SocialPost.user_id == user_id).limit(1)
        )
        has_post = post_result.scalar_one_or_none() is not None

        # Check team invitations
        team_result = await db.execute(
            select(TeamInvitation).where(TeamInvitation.invited_by_id == user_id).limit(1)
        )
        has_team_invites = team_result.scalar_one_or_none() is not None

        # Calculate onboarding progress based on user data
        onboarding_progress = {
            "profileComplete": bool(
                user.full_name and
                user.first_name and
                user.last_name and
                user.company
            ),
            "crmConnected": has_crm,
            "firstCampaign": has_campaign or has_post,
            "teamInvited": has_team_invites
        }

        return onboarding_progress

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ONBOARDING_PROGRESS] Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get onboarding progress"
        )
"""
Admin Dashboard API endpoints for system status and observability
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.social_account import SocialPost, SocialAccount
from app.models.user import User
from app.models.schedule_rule import ScheduleRule
from app.api.v1.auth import get_current_user as get_current_active_user

router = APIRouter()

@router.get("/system-status")
async def get_system_status(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get system status metrics for the admin dashboard.
    Returns:
        - Active Agents (based on active schedule rules)
        - Tasks Completed (posted social posts)
        - Error Rates (failed posts vs total)
        - Recent Activity
    """
    # Only allow admins to see full system status (or for now, just authenticated users for demo)
    # if current_user.role != "admin":
    #     raise HTTPException(status_code=403, detail="Not authorized")

    try:
        # 1. Active Agents (Proxy: Count of active ScheduleRules)
        active_agents_result = await db.execute(
            select(func.count(ScheduleRule.id)).where(ScheduleRule.is_active == True)
        )
        active_agents_count = active_agents_result.scalar() or 0
        
        # If no rules, maybe use active users as a proxy for "potential agents"
        if active_agents_count == 0:
            active_users_result = await db.execute(
                select(func.count(User.id)).where(User.is_active == True)
            )
            active_agents_count = active_users_result.scalar() or 0

        # 2. Tasks Completed (SocialPost status = 'posted')
        # Total
        posts_posted_result = await db.execute(
            select(func.count(SocialPost.id)).where(SocialPost.status == 'posted')
        )
        total_posts_posted = posts_posted_result.scalar() or 0
        
        # Last 24 hours
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_posted_result = await db.execute(
            select(func.count(SocialPost.id)).where(
                SocialPost.status == 'posted',
                SocialPost.updated_at >= yesterday
            )
        )
        recent_posts_posted = recent_posted_result.scalar() or 0

        # 3. Error Rates
        # Total Failed
        posts_failed_result = await db.execute(
            select(func.count(SocialPost.id)).where(SocialPost.status == 'failed')
        )
        total_posts_failed = posts_failed_result.scalar() or 0
        
        # Total Attempts (posted + failed)
        total_attempts = total_posts_posted + total_posts_failed
        error_rate = 0.0
        if total_attempts > 0:
            error_rate = (total_posts_failed / total_attempts) * 100

        # 4. Recent Activity (Last 5 posts)
        recent_activity_result = await db.execute(
            select(SocialPost).order_by(SocialPost.updated_at.desc()).limit(5)
        )
        recent_posts = recent_activity_result.scalars().all()
        
        activity_log = []
        for post in recent_posts:
            activity_log.append({
                "id": post.id,
                "platform": post.platform,
                "status": post.status,
                "time": post.updated_at.isoformat(),
                "summary": f"Post to {post.platform}: {post.status}"
            })

        return {
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": {
                "active_agents": active_agents_count,
                "tasks_completed_total": total_posts_posted,
                "tasks_completed_24h": recent_posts_posted,
                "error_rate_percent": round(error_rate, 2),
                "total_errors": total_posts_failed
            },
            "recent_activity": activity_log
        }

    except Exception as e:
        print(f"Error fetching system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

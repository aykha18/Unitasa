"""
Simple scheduler service for automated social media posting
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
import structlog

from app.core.database import get_db_session
from app.core.logging import get_logger
from app.models.social_account import SocialPost
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)


class SimpleScheduler:
    """Simple scheduler for automated social media posting"""

    def __init__(self):
        self.is_running = False
        self.check_interval = 60  # Check every 60 seconds

    async def start(self):
        """Start the scheduler"""
        if self.is_running:
            return

        self.is_running = True
        logger.info("Starting social media scheduler")

        while self.is_running:
            try:
                await self.check_and_publish_posts()
            except Exception as e:
                logger.error(f"Scheduler error: {e}", exc_info=True)

            await asyncio.sleep(self.check_interval)

    def stop(self):
        """Stop the scheduler"""
        self.is_running = False
        logger.info("Stopping social media scheduler")

    async def check_and_publish_posts(self):
        """Check for posts that need to be published"""
        try:
            async with get_db_session() as db:
                # Find posts that are scheduled and due
                now = datetime.utcnow()
                result = await db.execute(
                    select(SocialPost).where(
                        SocialPost.status == "scheduled",
                        SocialPost.scheduled_at <= now
                    ).order_by(SocialPost.scheduled_at)
                )
                due_posts = result.scalars().all()

                if not due_posts:
                    return

                logger.info(f"Found {len(due_posts)} posts due for publishing")

                for post in due_posts:
                    try:
                        await self.publish_post(post, db)
                    except Exception as e:
                        logger.error(f"Failed to publish post {post.id}: {e}")
                        # Mark as failed
                        await db.execute(
                            update(SocialPost).where(SocialPost.id == post.id).values(
                                status="failed",
                                failed_at=datetime.utcnow(),
                                failure_reason=str(e)
                            )
                        )

                await db.commit()

        except Exception as e:
            logger.error(f"Error checking for due posts: {e}", exc_info=True)

    async def publish_post(self, post: SocialPost, db: AsyncSession):
        """Publish a single post"""
        try:
            # Import here to avoid circular imports
            from app.core.twitter_service import get_twitter_service
            from app.core.facebook_service import get_facebook_service
            from app.core.instagram_service import get_instagram_service

            # Get the social account
            account_result = await db.execute(
                select(SocialAccount).where(SocialAccount.id == post.social_account_id)
            )
            account = account_result.scalar_one_or_none()

            if not account or not account.is_active:
                raise Exception(f"Social account {post.social_account_id} not found or inactive")

            # Decrypt access token
            from app.api.v1.social import decrypt_data
            access_token = decrypt_data(account.access_token)

            # Publish based on platform
            result = None
            if post.platform == "twitter":
                service = get_twitter_service(access_token)
                result = service.post_content(post.content)
            elif post.platform == "facebook":
                service = get_facebook_service(access_token)
                result = service.post_content(post.content)
            elif post.platform == "instagram":
                service = get_instagram_service(access_token)
                result = service.post_content(post.content)
            else:
                raise Exception(f"Unsupported platform: {post.platform}")

            if result and result.get('success'):
                # Update post status
                await db.execute(
                    update(SocialPost).where(SocialPost.id == post.id).values(
                        status="posted",
                        posted_at=datetime.utcnow(),
                        platform_post_id=result.get('post_id', ''),
                        post_url=result.get('url', '')
                    )
                )
                logger.info(f"Successfully published post {post.id} to {post.platform}")
            else:
                raise Exception(f"Posting failed: {result.get('error', 'Unknown error')}")

        except Exception as e:
            logger.error(f"Error publishing post {post.id}: {e}")
            raise


# Global scheduler instance
scheduler = SimpleScheduler()


async def start_scheduler():
    """Start the global scheduler"""
    await scheduler.start()


def stop_scheduler():
    """Stop the global scheduler"""
    scheduler.stop()


# Import here to avoid circular imports
from app.models.social_account import SocialAccount
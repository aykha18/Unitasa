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
                await self._process_schedule_rules(db)
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

    async def _process_schedule_rules(self, db: AsyncSession):
        try:
            from zoneinfo import ZoneInfo
            from sqlalchemy import select, update
            from app.models.schedule_rule import ScheduleRule
            now_utc = datetime.utcnow()
            result = await db.execute(
                select(ScheduleRule).where(
                    ScheduleRule.is_active == True
                )
            )
            rules = result.scalars().all()
            for rule in rules:
                if rule.end_date and now_utc > rule.end_date:
                    continue
                if not rule.next_run_at or now_utc >= rule.next_run_at:
                    await self._materialize_rule(rule, db)
                    next_time = await self._compute_next_run(rule, now_utc)
                    await db.execute(
                        update(ScheduleRule).where(ScheduleRule.id == rule.id).values(
                            last_run_at=now_utc,
                            next_run_at=next_time
                        )
                    )
            await db.commit()
        except Exception as e:
            logger.error(f"Error processing schedule rules: {e}", exc_info=True)

    async def _compute_next_run(self, rule, now_utc: datetime) -> datetime:
        from zoneinfo import ZoneInfo
        tz = None
        try:
            tz = ZoneInfo(rule.timezone or "UTC")
        except Exception:
            tz = ZoneInfo("UTC")
        local_now = now_utc.astimezone(tz)
        parts = (rule.time_of_day or "00:00").split(":")
        hh = int(parts[0])
        mm = int(parts[1]) if len(parts) > 1 else 0
        target = local_now.replace(hour=hh, minute=mm, second=0, microsecond=0)
        if rule.frequency == "daily":
            if target <= local_now:
                target = target + timedelta(days=1)
        elif rule.frequency == "weekly":
            days = rule.days_of_week or [local_now.weekday()]
            dow = days[0]
            ahead = (dow - local_now.weekday()) % 7
            if ahead == 0 and target <= local_now:
                ahead = 7
            target = target + timedelta(days=ahead)
        elif rule.frequency == "monthly":
            month = local_now.month
            year = local_now.year
            day = local_now.day
            target = target.replace(day=day)
            if target <= local_now:
                month += 1
                if month > 12:
                    month = 1
                    year += 1
                target = target.replace(year=year, month=month)
        return target.astimezone(ZoneInfo("UTC"))

    async def _materialize_rule(self, rule, db: AsyncSession):
        try:
            from sqlalchemy import select
            accounts_result = await db.execute(
                select(SocialAccount).where(
                    SocialAccount.user_id == rule.user_id,
                    SocialAccount.platform.in_(rule.platforms),
                    SocialAccount.is_active == True
                )
            )
            accounts = accounts_result.scalars().all()
            content_text = rule.content_seed or ""
            if rule.generation_mode == "automatic":
                try:
                    from app.agents.social_content_knowledge_base import get_social_content_knowledge_base
                    kb = await get_social_content_knowledge_base()
                    for acc in accounts:
                        req = {
                            "platform": acc.platform,
                            "content_type": rule.content_type or "educational",
                            "topic": rule.topic
                        }
                        items = await kb.get_client_content(client_id=None, content_request=req)
                        text = ""
                        if items and isinstance(items, list):
                            text = items[0].get("content", "")
                        scheduled = SocialPost(
                            user_id=rule.user_id,
                            social_account_id=acc.id,
                            platform=acc.platform,
                            content=text or content_text,
                            status="scheduled" if rule.autopost else "draft",
                            scheduled_at=rule.next_run_at or datetime.utcnow(),
                            generated_by_ai=True
                        )
                        db.add(scheduled)
                except Exception:
                    for acc in accounts:
                        scheduled = SocialPost(
                            user_id=rule.user_id,
                            social_account_id=acc.id,
                            platform=acc.platform,
                            content=content_text,
                            status="scheduled" if rule.autopost else "draft",
                            scheduled_at=rule.next_run_at or datetime.utcnow(),
                            generated_by_ai=False
                        )
                        db.add(scheduled)
            else:
                for acc in accounts:
                    scheduled = SocialPost(
                        user_id=rule.user_id,
                        social_account_id=acc.id,
                        platform=acc.platform,
                        content=content_text,
                        status="scheduled" if rule.autopost else "draft",
                        scheduled_at=rule.next_run_at or datetime.utcnow(),
                        generated_by_ai=False
                    )
                    db.add(scheduled)
        except Exception as e:
            logger.error(f"Error materializing rule {rule.id}: {e}", exc_info=True)


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

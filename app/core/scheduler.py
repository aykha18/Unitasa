"""
Simple scheduler service for automated social media posting
"""

import asyncio
from datetime import datetime, timedelta, timezone
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
                # Use naive UTC for DB comparison if column is naive
                now = datetime.now(timezone.utc).replace(tzinfo=None)
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

            from app.api.v1.social import decrypt_data
            access_token = decrypt_data(account.access_token)
            refresh_token = decrypt_data(account.refresh_token) if account.refresh_token else None

            result = None
            if post.platform == "twitter":
                service = get_twitter_service(access_token)
                if refresh_token and account.token_expires_at:
                    service._refresh_token = refresh_token
                    service._token_expires_at = account.token_expires_at
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
                # Check for updated tokens and save them
                if result.get('updated_tokens'):
                    try:
                        from app.api.v1.social import encrypt_data
                        updated_tokens = result['updated_tokens']
                        
                        # Encrypt new tokens
                        new_access_token = encrypt_data(updated_tokens['access_token'])
                        new_refresh_token = None
                        if updated_tokens.get('refresh_token'):
                            new_refresh_token = encrypt_data(updated_tokens['refresh_token'])
                        
                        # Update account values
                        values = {
                            "access_token": new_access_token,
                            "token_expires_at": updated_tokens.get('expires_at'),
                            "last_synced_at": datetime.utcnow()
                        }
                        
                        if new_refresh_token:
                            values["refresh_token"] = new_refresh_token
                            
                        await db.execute(
                            update(SocialAccount).where(SocialAccount.id == account.id).values(**values)
                        )
                        logger.info(f"Updated tokens for account {account.id} after successful post")
                    except Exception as e:
                        logger.error(f"Failed to save updated tokens for account {account.id}: {e}")

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
            
            # Use aware datetime for logic, convert to naive for DB
            now_utc = datetime.now(timezone.utc)
            
            result = await db.execute(
                select(ScheduleRule).where(
                    ScheduleRule.is_active == True
                )
            )
            rules = result.scalars().all()
            for rule in rules:
                # Handle end_date (ensure it's aware if it's naive)
                if rule.end_date:
                    rule_end = rule.end_date
                    if rule_end.tzinfo is None:
                        rule_end = rule_end.replace(tzinfo=timezone.utc)
                    if now_utc > rule_end:
                        continue
                
                # Handle next_run_at comparison
                should_run = False
                if not rule.next_run_at:
                    should_run = True
                else:
                    rule_next = rule.next_run_at
                    if rule_next.tzinfo is None:
                        rule_next = rule_next.replace(tzinfo=timezone.utc)
                    if now_utc >= rule_next:
                        should_run = True
                
                if should_run:
                    await self._materialize_rule(rule, db)
                    next_time = await self._compute_next_run(rule, now_utc)
                    
                    # Convert to naive UTC for DB storage
                    next_run_naive = next_time.astimezone(timezone.utc).replace(tzinfo=None)
                    last_run_naive = now_utc.astimezone(timezone.utc).replace(tzinfo=None)
                    
                    await db.execute(
                        update(ScheduleRule).where(ScheduleRule.id == rule.id).values(
                            last_run_at=last_run_naive,
                            next_run_at=next_run_naive
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
            
        # Ensure now_utc is aware
        if now_utc.tzinfo is None:
            now_utc = now_utc.replace(tzinfo=timezone.utc)
            
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
            # Ensure days are integers
            days = [int(d) for d in days] if days else [local_now.weekday()]
            
            # Find the next day in the list that is today or future
            current_dow = local_now.weekday()
            sorted_days = sorted(days)
            
            found_next = False
            for d in sorted_days:
                if d > current_dow:
                    target = target + timedelta(days=(d - current_dow))
                    found_next = True
                    break
                elif d == current_dow:
                    if target > local_now:
                        found_next = True
                        break
            
            if not found_next:
                # Wrap around to the first day next week
                first_day = sorted_days[0]
                days_ahead = (first_day - current_dow + 7) % 7
                if days_ahead == 0:
                    days_ahead = 7
                target = target + timedelta(days=days_ahead)
                
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
                
        return target.astimezone(timezone.utc)

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
                        # Deduplication: Check posts from the last 24 hours
                        yesterday = datetime.utcnow() - timedelta(days=1)
                        existing_posts = await db.execute(
                            select(SocialPost.content).where(
                                SocialPost.social_account_id == acc.id,
                                SocialPost.created_at >= yesterday
                            )
                        )
                        # Normalize recent content for comparison (lower case, stripped)
                        recent_content_hashes = {
                            (row[0] or "").strip().lower() 
                            for row in existing_posts.all() 
                            if row[0]
                        }

                        text = ""
                        req = {
                            "platform": acc.platform,
                            "content_type": rule.content_type or "educational",
                            "topic": rule.topic
                        }

                        # Retry loop to find unique content (up to 3 attempts)
                        items = []
                        max_retries = 3
                        for attempt in range(max_retries):
                            items = await kb.get_client_content(client_id=None, content_request=req)
                            if items and isinstance(items, list):
                                candidate = items[0].get("content", "")
                                if candidate:
                                    # Check normalized candidate against normalized history
                                    normalized_candidate = candidate.strip().lower()
                                    if normalized_candidate not in recent_content_hashes:
                                        text = candidate
                                        break
                                    else:
                                        logger.info(f"Generated duplicate content for rule {rule.id} (attempt {attempt+1}/{max_retries}). Retrying.")
                            
                            # Small delay to prevent tight loops
                            await asyncio.sleep(0.05)
                        
                        # Fallback: if unique generation failed, use the last generated content
                        if not text and items and isinstance(items, list):
                            text = items[0].get("content", "")
                            logger.warning(f"Could not generate unique content for rule {rule.id} after {max_retries} attempts. Using duplicate content.")

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

"""
Background service for automatic token refresh
Runs periodically to keep social media tokens fresh
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.logging import get_logger
from app.core.twitter_service import TwitterOAuthService
from app.models.social_account import SocialAccount
from app.core.config import get_settings

settings = get_settings()
logger = get_logger(__name__)


class TokenRefreshService:
    """Service to automatically refresh expired social media tokens"""

    def __init__(self):
        self.twitter_oauth = TwitterOAuthService()

    async def refresh_expired_tokens(self) -> Dict[str, Any]:
        """
        Refresh all tokens that are close to expiration
        Returns summary of refresh operations
        """
        summary = {
            'total_accounts': 0,
            'refreshed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }

        try:
            async for db in get_db():
                # Find accounts that need token refresh
                # Refresh tokens that expire within the next 24 hours
                cutoff_time = datetime.utcnow() + timedelta(hours=24)

                result = await db.execute(
                    select(SocialAccount).where(
                        SocialAccount.is_active == True,
                        SocialAccount.token_expires_at <= cutoff_time,
                        SocialAccount.refresh_token.isnot(None)
                    )
                )

                accounts = result.scalars().all()
                summary['total_accounts'] = len(accounts)

                for account in accounts:
                    try:
                        success = await self._refresh_account_tokens(db, account)
                        if success:
                            summary['refreshed'] += 1
                            logger.info(f"Successfully refreshed tokens for {account.platform} account {account.id}")
                        else:
                            summary['failed'] += 1
                            logger.error(f"Failed to refresh tokens for {account.platform} account {account.id}")

                    except Exception as e:
                        summary['failed'] += 1
                        error_msg = f"Error refreshing {account.platform} account {account.id}: {str(e)}"
                        summary['errors'].append(error_msg)
                        logger.error(error_msg)

                # Check for accounts that haven't been refreshed recently but might need attention
                old_cutoff = datetime.utcnow() - timedelta(days=30)
                result = await db.execute(
                    select(SocialAccount).where(
                        SocialAccount.is_active == True,
                        SocialAccount.last_synced_at <= old_cutoff
                    )
                )

                stale_accounts = result.scalars().all()
                summary['stale_accounts'] = len(stale_accounts)

                await db.commit()

        except Exception as e:
            logger.error(f"Token refresh service error: {e}")
            summary['errors'].append(f"Service error: {str(e)}")

        return summary

    async def _refresh_account_tokens(self, db: AsyncSession, account: SocialAccount) -> bool:
        """Refresh tokens for a specific account"""
        try:
            if account.platform == 'twitter':
                return await self._refresh_twitter_tokens(db, account)
            elif account.platform == 'facebook':
                return await self._refresh_facebook_tokens(db, account)
            elif account.platform == 'instagram':
                return await self._refresh_instagram_tokens(db, account)
            elif account.platform == 'linkedin':
                return await self._refresh_linkedin_tokens(db, account)
            else:
                logger.warning(f"Token refresh not implemented for platform: {account.platform}")
                return False

        except Exception as e:
            logger.error(f"Error refreshing tokens for {account.platform} account {account.id}: {e}")
            return False

    async def _refresh_twitter_tokens(self, db: AsyncSession, account: SocialAccount) -> bool:
        """Refresh Twitter access tokens.

        If refresh fails, mark the account as needing reconnection so the UI
        doesn't continue to show it as fully connected with invalid tokens.
        """
        try:
            from app.core.encryption import decrypt_data, encrypt_data

            refresh_token = decrypt_data(account.refresh_token)

            token_data = self.twitter_oauth.refresh_access_token(refresh_token)

            new_access_token = encrypt_data(token_data['access_token'])
            new_refresh_token = encrypt_data(token_data.get('refresh_token', refresh_token))

            account.access_token = new_access_token
            account.refresh_token = new_refresh_token
            account.token_expires_at = token_data.get('expires_at')
            account.last_synced_at = datetime.utcnow()

            return True

        except Exception as e:
            logger.error(f"Twitter token refresh failed for account {account.id}: {e}")

            # Mark account as needing reconnection so the dashboard can prompt
            # the user to reconnect instead of silently keeping a broken link.
            account.is_active = False
            if account.platform_settings is None:
                account.platform_settings = {}
            account.platform_settings["needs_reconnection"] = True
            account.platform_settings["reconnection_reason"] = "twitter_token_refresh_failed"
            account.last_synced_at = datetime.utcnow()

            return False

    async def _refresh_facebook_tokens(self, db: AsyncSession, account: SocialAccount) -> bool:
        """Refresh Facebook access tokens"""
        # Facebook tokens can be refreshed by making API calls with the current token
        # Implementation would be similar to Twitter but with Facebook's API
        logger.info(f"Facebook token refresh not yet implemented for account {account.id}")
        return False

    async def _refresh_instagram_tokens(self, db: AsyncSession, account: SocialAccount) -> bool:
        """Refresh Instagram access tokens"""
        # Similar to Facebook
        logger.info(f"Instagram token refresh not yet implemented for account {account.id}")
        return False

    async def _refresh_linkedin_tokens(self, db: AsyncSession, account: SocialAccount) -> bool:
        """Refresh LinkedIn access tokens"""
        logger.info(f"LinkedIn token refresh not yet implemented for account {account.id}")
        return False

    async def check_token_health(self) -> Dict[str, Any]:
        """Check the health of all tokens and identify issues"""
        health_report = {
            'total_accounts': 0,
            'healthy': 0,
            'expiring_soon': 0,  # Within 24 hours
            'expired': 0,
            'no_refresh_token': 0,
            'accounts': []
        }

        try:
            async for db in get_db():
                result = await db.execute(
                    select(SocialAccount).where(SocialAccount.is_active == True)
                )

                accounts = result.scalars().all()
                health_report['total_accounts'] = len(accounts)

                now = datetime.utcnow()

                for account in accounts:
                    account_health = {
                        'id': account.id,
                        'platform': account.platform,
                        'username': account.account_username,
                        'expires_at': account.token_expires_at.isoformat() if account.token_expires_at else None,
                        'last_synced': account.last_synced_at.isoformat() if account.last_synced_at else None,
                        'has_refresh_token': account.refresh_token is not None,
                        'status': 'unknown'
                    }

                    if account.token_expires_at:
                        if account.token_expires_at <= now:
                            account_health['status'] = 'expired'
                            health_report['expired'] += 1
                        elif account.token_expires_at <= now + timedelta(hours=24):
                            account_health['status'] = 'expiring_soon'
                            health_report['expiring_soon'] += 1
                        else:
                            account_health['status'] = 'healthy'
                            health_report['healthy'] += 1
                    else:
                        account_health['status'] = 'no_expiration'
                        health_report['no_refresh_token'] += 1

                    health_report['accounts'].append(account_health)

        except Exception as e:
            logger.error(f"Token health check error: {e}")
            health_report['error'] = str(e)

        return health_report


# Global service instance
token_refresh_service = TokenRefreshService()


async def scheduled_token_refresh():
    """Scheduled task to refresh tokens - run this every 1 hour"""
    while True:
        try:
            logger.info("Starting scheduled token refresh...")
            summary = await token_refresh_service.refresh_expired_tokens()

            logger.info(f"Token refresh completed: {summary['refreshed']} refreshed, {summary['failed']} failed")

            if summary['errors']:
                logger.warning(f"Token refresh errors: {summary['errors']}")

        except Exception as e:
            logger.error(f"Scheduled token refresh failed: {e}")

        # Wait 1 hour before next refresh
        await asyncio.sleep(60 * 60)


if __name__ == "__main__":
    # For testing the service directly
    async def test_service():
        print("Testing Token Refresh Service...")

        # Check token health
        health = await token_refresh_service.check_token_health()
        print(f"Token Health: {health}")

        # Refresh expired tokens
        summary = await token_refresh_service.refresh_expired_tokens()
        print(f"Refresh Summary: {summary}")

    asyncio.run(test_service())

"""
Social media management API endpoints for client-facing platform
"""

import os
import secrets
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.twitter_service import TwitterOAuthService, get_twitter_service
from app.core.facebook_service import FacebookOAuthService, get_facebook_service
from app.core.instagram_service import InstagramOAuthService, get_instagram_service
from app.core.youtube_service import YouTubeOAuthService, get_youtube_service
from app.core.telegram_service import TelegramOAuthService, get_telegram_service
from app.core.reddit_service import RedditOAuthService, get_reddit_service
from app.core.mastodon_service import MastodonOAuthService, get_mastodon_service
from app.core.bluesky_service import BlueskyOAuthService, get_bluesky_service
from app.core.pinterest_service import PinterestOAuthService, get_pinterest_service
from app.models.social_account import SocialAccount, SocialPost, Engagement
from app.models.schedule_rule import ScheduleRule
from app.models.campaign import Campaign
from app.models.user import User
from app.agents.social_content_knowledge_base import get_social_content_knowledge_base
from app.core.jwt_handler import JWTHandler
import logging

settings = get_settings()
try:
    logger = get_logger(__name__)
except ImportError:
    # Fallback to standard logging if structlog is not available
    logger = logging.getLogger(__name__)

# Mock encryption functions for now - replace with actual implementation
def encrypt_data(data: str) -> str:
    return data  # TODO: Implement proper encryption

def decrypt_data(data: str) -> str:
    return data  # TODO: Implement proper decryption

router = APIRouter()
security = HTTPBearer()


# Pydantic models
class ConnectAccountRequest(BaseModel):
    platform: str = Field(..., description="Platform to connect (twitter, linkedin, etc.)")
    authorization_code: str = Field(..., description="OAuth authorization code")
    code_verifier: str = Field(..., description="PKCE code verifier")
    redirect_uri: Optional[str] = Field(None, description="OAuth redirect URI")


class AccountSettings(BaseModel):
    approval_required: Optional[bool] = Field(None, description="Whether posts require approval before publishing")



class CreateCampaignRequest(BaseModel):
    name: str = Field(..., description="Campaign name")
    description: Optional[str] = Field(None, description="Campaign description")
    platforms: List[str] = Field(default_factory=list, description="Platforms to use")
    schedule_config: Dict[str, Any] = Field(default_factory=dict, description="Scheduling configuration")
    content_templates: List[Dict[str, Any]] = Field(default_factory=list, description="Content templates")
    engagement_rules: Dict[str, Any] = Field(default_factory=dict, description="Engagement rules")


class PostContentRequest(BaseModel):
    content: str = Field(..., description="Content to post")
    platforms: List[str] = Field(default_factory=list, description="Platforms to post to")
    scheduled_at: Optional[datetime] = Field(None, description="When to post")
    campaign_id: Optional[int] = Field(None, description="Associated campaign")


class EngagementRequest(BaseModel):
    platform: str = Field(..., description="Platform for engagement")
    target_type: str = Field(..., description="Type of engagement target")
    target_id: str = Field(..., description="Target ID to engage with")
    engagement_type: str = Field(..., description="Type of engagement (like, comment, follow)")
    comment_text: Optional[str] = Field(None, description="Comment text if applicable")


class ContentGenerationRequest(BaseModel):
    feature_key: str = Field(..., description="Unitasa feature to generate content for")
    platform: str = Field(..., description="Target social media platform")
    content_type: str = Field("educational", description="Type of content (educational, benefit_focused, social_proof)")
    tone: str = Field("professional", description="Content tone")
    client_id: Optional[str] = Field(None, description="Client ID for knowledge base context")
    topic: Optional[str] = Field(None, description="Specific topic for content generation")


class SchedulePostRequest(BaseModel):
    content: str = Field(..., description="Content to post")
    platforms: List[str] = Field(..., description="Platforms to post to")
    scheduled_at: datetime = Field(..., description="When to post")
    campaign_id: Optional[int] = Field(None, description="Associated campaign")
    timezone_offset_minutes: Optional[int] = Field(None, description="Client timezone offset in minutes (UTC - local)")


class CreateScheduleRuleRequest(BaseModel):
    name: str = Field(..., description="Rule name")
    platforms: List[str] = Field(..., description="Target platforms")
    frequency: str = Field(..., description="Frequency (daily, weekly, monthly)")
    time_of_day: str = Field(..., description="Time of day (HH:MM)")
    timezone: str = Field("UTC", description="Timezone")
    days_of_week: List[str] = Field(default_factory=list, description="Days of week for weekly recurrence")
    recurrence_config: Dict[str, Any] = Field(default_factory=dict, description="Advanced recurrence config")
    content_variation: Dict[str, Any] = Field(default_factory=dict, description="Content variation settings")
    topic: Optional[str] = Field(None, description="Topic")
    tone: Optional[str] = Field(None, description="Tone")
    content_type: Optional[str] = Field(None, description="Content type")
    autopost: bool = Field(True, description="Whether to post automatically")
    start_date: Optional[datetime] = Field(None, description="Start date")
    end_date: Optional[datetime] = Field(None, description="End date")


# Dependencies
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    try:
        user_info = JWTHandler.get_user_from_token(credentials.credentials)
        result = await db.execute(select(User).where(User.id == user_info["user_id"]))
        user = result.scalar_one_or_none()
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="User not found or inactive")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to authenticate user: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")


@router.get("/auth/{platform}/url")
async def get_oauth_url(
    platform: str,
    current_user: User = Depends(get_current_user)
):
    """Get OAuth authorization URL for a platform"""
    try:
        user_id = current_user.id
        if platform == "twitter":
            logger.info(f"Generating Twitter OAuth URL for user_id={user_id}")
            # For development/demo purposes, return a mock OAuth URL if credentials are not configured
            try:
                oauth_service = TwitterOAuthService()
                # Generate state with user_id embedded to persist across callback
                state = f"{secrets.token_urlsafe(16)}.{user_id}"
                auth_url, code_verifier, state = oauth_service.get_authorization_url(state=state)
            except ValueError as e:
                logger.warning(f"Twitter credentials not configured: {e}")
                # Twitter credentials not configured - return demo URL
                code_verifier = secrets.token_urlsafe(32)[:43]
                state = f"{secrets.token_urlsafe(16)}.{user_id}"
                
                # Return a demo URL that shows the OAuth flow would work
                auth_url = f"https://twitter.com/i/oauth2/authorize?response_type=code&client_id=demo&redirect_uri=http://localhost:8001/api/v1/social/auth/twitter/callback&scope=tweet.read%20tweet.write%20users.read%20offline.access&state={state}&code_challenge=demo&code_challenge_method=S256"

                return {
                    "auth_url": auth_url,
                    "code_verifier": code_verifier,
                    "state": state,
                    "platform": platform,
                    "demo_mode": True,
                    "message": "Twitter API credentials not configured. This is a demo OAuth URL."
                }

            # Store code_verifier in a simple in-memory cache (in production, use Redis/database)
            # For demo purposes, we'll use a global dict
            if not hasattr(get_oauth_url, 'code_verifiers'):
                get_oauth_url.code_verifiers = {}
            get_oauth_url.code_verifiers[state] = code_verifier
            logger.info(f"Stored code_verifier for state {state}: length={len(code_verifier)}")

            return {
                "auth_url": auth_url,
                "code_verifier": code_verifier,  # Still return for frontend storage as backup
                "state": state,
                "platform": platform,
                "demo_mode": False
            }

        elif platform == "facebook":
            try:
                oauth_service = FacebookOAuthService()
                auth_url, state = oauth_service.get_authorization_url()
                return {
                    "auth_url": auth_url,
                    "state": state,
                    "platform": platform,
                    "demo_mode": False
                }
            except ValueError as e:
                return {
                    "auth_url": f"{settings.frontend_url}/facebook-setup?platform={platform}",
                    "state": secrets.token_urlsafe(16),
                    "platform": platform,
                    "demo_mode": True,
                    "message": "Facebook API credentials not configured."
                }

        elif platform == "instagram":
            try:
                oauth_service = InstagramOAuthService()
                auth_url, state = oauth_service.get_authorization_url()
                return {
                    "auth_url": auth_url,
                    "state": state,
                    "platform": platform,
                    "demo_mode": False
                }
            except ValueError as e:
                return {
                    "auth_url": f"{settings.frontend_url}/instagram-setup?platform={platform}",
                    "state": secrets.token_urlsafe(16),
                    "platform": platform,
                    "demo_mode": True,
                    "message": "Instagram API credentials not configured."
                }

        elif platform == "youtube":
            try:
                oauth_service = YouTubeOAuthService()
                auth_url, state = oauth_service.get_authorization_url()
                return {
                    "auth_url": auth_url,
                    "state": state,
                    "platform": platform,
                    "demo_mode": False
                }
            except ValueError as e:
                return {
                    "auth_url": f"{settings.frontend_url}/youtube-setup?platform={platform}",
                    "state": secrets.token_urlsafe(16),
                    "platform": platform,
                    "demo_mode": True,
                    "message": "YouTube API credentials not configured."
                }

        elif platform == "telegram":
            try:
                oauth_service = TelegramOAuthService()
                auth_url, state = oauth_service.get_authorization_url()
                return {
                    "auth_url": auth_url,
                    "state": state,
                    "platform": platform,
                    "demo_mode": False
                }
            except ValueError as e:
                return {
                    "auth_url": f"{settings.frontend_url}/telegram-setup?platform={platform}",
                    "state": secrets.token_urlsafe(16),
                    "platform": platform,
                    "demo_mode": True,
                    "message": "Telegram bot token not configured."
                }

        elif platform == "reddit":
            try:
                oauth_service = RedditOAuthService()
                auth_url, state = oauth_service.get_authorization_url()
                return {
                    "auth_url": auth_url,
                    "state": state,
                    "platform": platform,
                    "demo_mode": False
                }
            except ValueError as e:
                return {
                    "auth_url": f"{settings.frontend_url}/reddit-setup?platform={platform}",
                    "state": secrets.token_urlsafe(16),
                    "platform": platform,
                    "demo_mode": True,
                    "message": "Reddit API credentials not configured."
                }

        elif platform == "mastodon":
            try:
                oauth_service = MastodonOAuthService()
                auth_url, state = oauth_service.get_authorization_url()
                return {
                    "auth_url": auth_url,
                    "state": state,
                    "platform": platform,
                    "demo_mode": False
                }
            except ValueError as e:
                return {
                    "auth_url": f"{settings.frontend_url}/mastodon-setup?platform={platform}",
                    "state": secrets.token_urlsafe(16),
                    "platform": platform,
                    "demo_mode": True,
                    "message": "Mastodon API credentials not configured."
                }

        elif platform == "bluesky":
            try:
                oauth_service = BlueskyOAuthService()
                auth_url, state = oauth_service.get_authorization_url()
                return {
                    "auth_url": auth_url,
                    "state": state,
                    "platform": platform,
                    "demo_mode": False
                }
            except ValueError as e:
                return {
                    "auth_url": f"{settings.frontend_url}/bluesky-setup?platform={platform}",
                    "state": secrets.token_urlsafe(16),
                    "platform": platform,
                    "demo_mode": True,
                    "message": "Bluesky API credentials not configured."
                }

        elif platform == "pinterest":
            try:
                oauth_service = PinterestOAuthService()
                auth_url, state = oauth_service.get_authorization_url()
                return {
                    "auth_url": auth_url,
                    "state": state,
                    "platform": platform,
                    "demo_mode": False
                }
            except ValueError as e:
                return {
                    "auth_url": f"{settings.frontend_url}/pinterest-setup?platform={platform}",
                    "state": secrets.token_urlsafe(16),
                    "platform": platform,
                    "demo_mode": True,
                    "message": "Pinterest API credentials not configured."
                }

        elif platform == "linkedin":
            # LinkedIn is not implemented yet - return demo mode
            return {
                "auth_url": f"{settings.frontend_url}/linkedin-setup?platform={platform}",
                "state": secrets.token_urlsafe(16),
                "platform": platform,
                "demo_mode": True,
                "message": "LinkedIn integration not yet implemented."
            }

        elif platform == "medium":
            # Medium is not implemented yet - return demo mode
            return {
                "auth_url": f"{settings.frontend_url}/medium-setup?platform={platform}",
                "state": secrets.token_urlsafe(16),
                "platform": platform,
                "demo_mode": True,
                "message": "Medium integration not yet implemented."
            }

        else:
            raise HTTPException(status_code=400, detail=f"Platform '{platform}' not supported")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate auth URL: {str(e)}")


@router.get("/auth/{platform}/callback")
async def oauth_callback(
    platform: str,
    code: str = Query(..., description="Authorization code from OAuth provider"),
    state: str = Query(..., description="State parameter for security"),
    code_verifier: Optional[str] = Query(None, description="PKCE code verifier (optional, retrieved from server storage)"),
    error: Optional[str] = Query(None, description="Error from OAuth provider")
):
    """Handle OAuth callback from social media platforms and automatically connect account"""
    user_id = None
    try:
        parts = state.split('.')
        if len(parts) > 1 and parts[-1].isdigit():
            user_id = int(parts[-1])
            logger.info(f"Extracted user_id={user_id} from state")
    except Exception as e:
        logger.error(f"Failed to extract user_id from state: {e}")

    if user_id is None:
        logger.error("Could not determine user_id from OAuth state")
        content = f"""
        <html>
        <head><title>Authentication Error</title></head>
        <body>
        <h1>Authentication Error</h1>
        <p>We could not verify your account for this connection. Please go back to your dashboard and try connecting again.</p>
        <a href="{settings.frontend_url}/dashboard">Back to Dashboard</a>
        </body>
        </html>
        """
        return HTMLResponse(content=content)

    logger.info(f"OAuth callback triggered: platform={platform}, has_code={code is not None}, has_state={state is not None}, has_error={error is not None}, user_id={user_id}")

    if error:
        logger.error(f"OAuth callback error: platform={platform}, error={error}")
        # Redirect back to dashboard with error
        content = f"""
        <html>
        <head><title>OAuth Error</title></head>
        <body>
        <h1>OAuth Error</h1>
        <p>Error: {error}</p>
        <p>Platform: {platform}</p>
        <a href="{settings.frontend_url}/dashboard">Back to Dashboard</a>
        <script>
        setTimeout(function() {{
            window.location.href = '{settings.frontend_url}/dashboard';
        }}, 3000);
        </script>
        </body>
        </html>
        """
        return HTMLResponse(content=content)

    try:
        # Try to get code_verifier from server-side storage first, then from query param
        stored_code_verifier = None
        if hasattr(get_oauth_url, 'code_verifiers') and state in get_oauth_url.code_verifiers:
            stored_code_verifier = get_oauth_url.code_verifiers.pop(state, None)  # Remove after use

        final_code_verifier = stored_code_verifier or code_verifier
        logger.info(f"OAuth callback received: platform={platform}, state={state}")
        logger.info(f"Code verifier details: stored_length={len(stored_code_verifier) if stored_code_verifier else 0}, query_length={len(code_verifier) if code_verifier else 0}, final_length={len(final_code_verifier) if final_code_verifier else 0}")
        logger.info(f"Available states in storage: {list(getattr(get_oauth_url, 'code_verifiers', {}).keys())}")

        if not final_code_verifier:
            logger.error(f"No code verifier found for platform={platform}, state={state}")
            content = f"""
            <html>
            <head><title>Code Verifier Missing</title></head>
            <body>
            <h1>Authentication Error</h1>
            <p>Code verifier not found. Please try connecting again.</p>
            <a href="{settings.frontend_url}/dashboard">Back to Dashboard</a>
            </body>
            </html>
            """
            return HTMLResponse(content=content)

        # Automatically connect the account
        from app.core.database import init_database
        from app.models.user import User

        engine, AsyncSessionLocal = init_database()
        async with AsyncSessionLocal() as db:
            # Get user (mock for now)
            user_result = await db.execute(select(User).where(User.id == user_id))
            user = user_result.scalar_one_or_none()

            if not user:
                content = f"""
                <html>
                <head><title>OAuth Error</title></head>
                <body>
                <h1>User Not Found</h1>
                <p>User ID {user_id} not found.</p>
                <a href="/dashboard">Back to Dashboard</a>
                </body>
                </html>
                """
                return HTMLResponse(content=content)

            # Connect the account using the same logic as the connect endpoint
            account_info = None
            token_data = None

            if platform == "twitter":
                logger.info(f"Processing Twitter OAuth: code_length={len(code)}, verifier_length={len(final_code_verifier) if final_code_verifier else 0}")
                oauth_service = TwitterOAuthService()
                logger.info(f"Twitter OAuth service redirect_uri: {oauth_service.redirect_uri}")
                token_data = oauth_service.exchange_code_for_tokens(code, final_code_verifier)
                logger.info(f"Token exchange successful: has_access_token={token_data.get('access_token') is not None}")
                twitter_service = get_twitter_service(token_data['access_token'])
                account_info = twitter_service.get_account_info()
                logger.info(f"Account info retrieved: username={account_info.get('username')}")

            elif platform == "facebook":
                oauth_service = FacebookOAuthService()
                token_data = oauth_service.exchange_code_for_tokens(code)
                facebook_service = get_facebook_service(token_data['access_token'])
                account_info = facebook_service.get_account_info()

            elif platform == "instagram":
                oauth_service = InstagramOAuthService()
                token_data = oauth_service.exchange_code_for_tokens(code)
                instagram_service = get_instagram_service(token_data['access_token'])
                account_info = instagram_service.get_account_info()

            elif platform == "youtube":
                oauth_service = YouTubeOAuthService()
                token_data = oauth_service.exchange_code_for_tokens(code)
                youtube_service = get_youtube_service(token_data['access_token'])
                account_info = youtube_service.get_account_info()

            else:
                content = f"""
                <html>
                <head><title>Platform Not Supported</title></head>
                <body>
                <h1>Platform Not Supported</h1>
                <p>Platform '{platform}' is not supported for automatic connection.</p>
                <a href="/dashboard">Back to Dashboard</a>
                </body>
                </html>
                """
                return HTMLResponse(content=content)

            if not account_info or not token_data:
                content = f"""
                <html>
                <head><title>Connection Failed</title></head>
                <body>
                <h1>Connection Failed</h1>
                <p>Failed to retrieve account information from {platform}.</p>
                <a href="/dashboard">Back to Dashboard</a>
                </body>
                </html>
                """
                return HTMLResponse(content=content)

            # Encrypt tokens
            encrypted_access_token = encrypt_data(token_data['access_token'])
            encrypted_refresh_token = encrypt_data(token_data.get('refresh_token', ''))

            # Create or update social account
            existing_account = await db.execute(
                select(SocialAccount).where(
                    SocialAccount.user_id == user.id,
                    SocialAccount.platform == platform,
                    SocialAccount.account_id == account_info['account_id']
                )
            )
            existing_account = existing_account.scalar_one_or_none()

            if existing_account:
                existing_account.access_token = encrypted_access_token
                existing_account.refresh_token = encrypted_refresh_token
                existing_account.token_expires_at = token_data.get('expires_at')
                existing_account.account_username = account_info['username']
                existing_account.account_name = account_info['name']
                existing_account.profile_url = account_info['profile_url']
                existing_account.avatar_url = account_info['avatar_url']
                existing_account.follower_count = account_info.get('follower_count', 0)
                existing_account.following_count = account_info.get('following_count', 0)
                existing_account.is_active = True
                existing_account.last_synced_at = datetime.utcnow()
                account = existing_account
            else:
                account = SocialAccount(
                    user_id=user.id,
                    platform=platform,
                    account_id=account_info['account_id'],
                    account_username=account_info['username'],
                    account_name=account_info['name'],
                    profile_url=account_info['profile_url'],
                    avatar_url=account_info['avatar_url'],
                    access_token=encrypted_access_token,
                    refresh_token=encrypted_refresh_token,
                    token_expires_at=token_data.get('expires_at'),
                    follower_count=account_info.get('follower_count', 0),
                    following_count=account_info.get('following_count', 0),
                    is_active=True,
                    last_synced_at=datetime.utcnow()
                )
                db.add(account)

            await db.commit()
            await db.refresh(account)

            # Success page with redirect
            content = f"""
            <html>
            <head><title>Account Connected</title></head>
            <body>
            <h1>Success!</h1>
            <p>Successfully connected your {platform} account: @{account_info['username']}</p>
            <p>Redirecting to Dashboard...</p>
            <a href="{settings.frontend_url}/dashboard">Go to Dashboard</a>
            <script>
            setTimeout(function() {{
                window.location.href = '{settings.frontend_url}/dashboard';
            }}, 2000);
            </script>
            </body>
            </html>
            """
            return HTMLResponse(content=content)

    except Exception as e:
        logger.error(f"OAuth callback error for {platform}: {str(e)}", exc_info=True)
        content = f"""
        <html>
        <head><title>Connection Error</title></head>
        <body>
        <h1>Connection Error</h1>
        <p>An error occurred while connecting your {platform} account.</p>
        <p>Error: {str(e)}</p>
        <a href="/dashboard">Back to Dashboard</a>
        </body>
        </html>
        """
        return HTMLResponse(content=content)


@router.post("/accounts/connect")
async def connect_account(
    request: ConnectAccountRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Connect a social media account using OAuth code"""
    logger.info(f"🔗 Connecting account: platform={request.platform}, user_id={user.id}, has_code={bool(request.authorization_code)}, has_verifier={bool(request.code_verifier)}")
    try:
        account_info = None
        token_data = None

        if request.platform == "twitter":
            # Exchange code for tokens
            oauth_service = TwitterOAuthService()
            token_data = oauth_service.exchange_code_for_tokens(
                request.authorization_code,
                request.code_verifier
            )

            # Get account info using access token
            twitter_service = get_twitter_service(token_data['access_token'])
            account_info = twitter_service.get_account_info()

        elif request.platform == "facebook":
            oauth_service = FacebookOAuthService()
            token_data = oauth_service.exchange_code_for_tokens(request.authorization_code)

            facebook_service = get_facebook_service(token_data['access_token'])
            account_info = facebook_service.get_account_info()

        elif request.platform == "instagram":
            oauth_service = InstagramOAuthService()
            token_data = oauth_service.exchange_code_for_tokens(request.authorization_code)

            instagram_service = get_instagram_service(token_data['access_token'])
            account_info = instagram_service.get_account_info()

        elif request.platform == "youtube":
            oauth_service = YouTubeOAuthService()
            token_data = oauth_service.exchange_code_for_tokens(request.authorization_code)

            youtube_service = get_youtube_service(token_data['access_token'])
            account_info = youtube_service.get_account_info()

        elif request.platform == "telegram":
            oauth_service = TelegramOAuthService()
            token_data = oauth_service.exchange_code_for_tokens({})

            telegram_service = get_telegram_service(token_data['access_token'])
            account_info = telegram_service.get_account_info()

        elif request.platform == "reddit":
            oauth_service = RedditOAuthService()
            token_data = oauth_service.exchange_code_for_tokens(request.authorization_code)

            reddit_service = get_reddit_service(token_data['access_token'])
            account_info = reddit_service.get_account_info()

        elif request.platform == "mastodon":
            oauth_service = MastodonOAuthService()
            token_data = oauth_service.exchange_code_for_tokens(request.authorization_code)

            mastodon_service = get_mastodon_service(token_data['access_token'])
            account_info = mastodon_service.get_account_info()

        elif request.platform == "bluesky":
            oauth_service = BlueskyOAuthService()
            token_data = oauth_service.exchange_code_for_tokens({})

            bluesky_service = get_bluesky_service(token_data['access_token'])
            account_info = bluesky_service.get_account_info()

        elif request.platform == "pinterest":
            oauth_service = PinterestOAuthService()
            token_data = oauth_service.exchange_code_for_tokens(request.authorization_code)

            pinterest_service = get_pinterest_service(token_data['access_token'])
            account_info = pinterest_service.get_account_info()

        else:
            raise HTTPException(status_code=400, detail=f"Platform '{request.platform}' not supported")

        if not account_info or not token_data:
            raise HTTPException(status_code=500, detail="Failed to retrieve account information")

        # Encrypt sensitive tokens
        encrypted_access_token = encrypt_data(token_data['access_token'])
        encrypted_refresh_token = encrypt_data(token_data.get('refresh_token', ''))

        # Create or update social account
        existing_account = await db.execute(
            select(SocialAccount).where(
                SocialAccount.user_id == user.id,
                SocialAccount.platform == request.platform,
                SocialAccount.account_id == account_info['account_id']
            )
        )
        existing_account = existing_account.scalar_one_or_none()

        if existing_account:
            # Update existing account
            existing_account.access_token = encrypted_access_token
            existing_account.refresh_token = encrypted_refresh_token
            existing_account.token_expires_at = token_data.get('expires_at')
            existing_account.account_username = account_info['username']
            existing_account.account_name = account_info['name']
            existing_account.profile_url = account_info['profile_url']
            existing_account.avatar_url = account_info['avatar_url']
            existing_account.follower_count = account_info.get('follower_count', 0)
            existing_account.following_count = account_info.get('following_count', 0)
            existing_account.is_active = True
            existing_account.last_synced_at = datetime.utcnow()
            account = existing_account
        else:
            # Create new account
            account = SocialAccount(
                user_id=user.id,
                platform=request.platform,
                account_id=account_info['account_id'],
                account_username=account_info['username'],
                account_name=account_info['name'],
                profile_url=account_info['profile_url'],
                avatar_url=account_info['avatar_url'],
                access_token=encrypted_access_token,
                refresh_token=encrypted_refresh_token,
                token_expires_at=token_data.get('expires_at'),
                follower_count=account_info.get('follower_count', 0),
                following_count=account_info.get('following_count', 0),
                is_active=True,
                last_synced_at=datetime.utcnow()
            )
            db.add(account)

        await db.commit()
        await db.refresh(account)

        return {
            "success": True,
            "account": {
                "id": account.id,
                "platform": account.platform,
                "username": account.account_username,
                "name": account.account_name,
                "profile_url": account.profile_url,
                "avatar_url": account.avatar_url,
                "follower_count": account.follower_count,
                "is_active": account.is_active
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to connect account: {str(e)}")


@router.get("/accounts")
async def get_connected_accounts(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all connected social accounts for the user"""
    try:
        # Query database for accounts
        result = await db.execute(
            select(SocialAccount).where(
                SocialAccount.user_id == user.id,
                SocialAccount.is_active == True
            )
        )
        accounts = result.scalars().all()
        
        if accounts:
            return {
                "accounts": [
                    {
                        "id": acc.id,
                        "platform": acc.platform,
                        "username": acc.account_username,
                        "name": acc.account_name,
                        "profile_url": acc.profile_url,
                        "avatar_url": acc.avatar_url,
                        "follower_count": acc.follower_count,
                        "is_active": acc.is_active,
                        "last_synced_at": acc.last_synced_at.isoformat() if acc.last_synced_at else None,
                        "settings": acc.platform_settings or {}
                    }
                    for acc in accounts
                ]
            }
            
        # For development, return empty accounts to allow real OAuth setup
        # Comment out mock data to enable real account connections
        # if settings.environment == "development":
        #     return {
        #         "accounts": [
        #             {
        #                 "id": 1,
        #                 "platform": "twitter",
        #                 "username": "@unitasaAI",
        #                 "name": "Unitasa AI",
        #                 "profile_url": "https://twitter.com/unitasaAI",
        #                 "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=unitasa",
        #                 "follower_count": 1250,
        #                 "is_active": True,
        #                 "last_synced_at": datetime.utcnow().isoformat()
        #             }
        #         ]
        #     }
            
        return {"accounts": []}
        
    except Exception as e:
        # In case of DB error, return empty accounts for real OAuth setup
        # if settings.environment == "development":
        #       return {
        #         "accounts": [
        #             {
        #                 "id": 1,
        #                 "platform": "twitter",
        #                 "username": "@unitasaAI",
        #                 "name": "Unitasa AI",
        #                 "profile_url": "https://twitter.com/unitasaAI",
        #                 "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=unitasa",
        #                 "follower_count": 1250,
        #                 "is_active": True,
        #                 "last_synced_at": datetime.utcnow().isoformat()
        #             }
        #         ]
        #     }
        raise HTTPException(status_code=500, detail=f"Failed to fetch accounts: {str(e)}")


@router.delete("/accounts/{account_id}")
async def disconnect_account(
    account_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Disconnect a social account"""
    try:
        account = await db.get(SocialAccount, account_id)
        if not account or account.user_id != user.id:
            raise HTTPException(status_code=404, detail="Account not found")

        await db.delete(account)
        await db.commit()

        return {"success": True, "message": "Account disconnected"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to disconnect account: {str(e)}")


@router.patch("/accounts/{account_id}/settings")
async def update_account_settings(
    account_id: int,
    settings_update: AccountSettings,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update social account settings"""
    logger.info(f"Updating settings for account {account_id}")
    try:
        account = await db.get(SocialAccount, account_id)
        if not account or account.user_id != user.id:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Initialize platform_settings if None
        if account.platform_settings is None:
            account.platform_settings = {}
        
        # Create a mutable copy of the dictionary
        current_settings = dict(account.platform_settings)
        
        if settings_update.approval_required is not None:
            current_settings['approval_required'] = settings_update.approval_required
            
        account.platform_settings = current_settings
        
        await db.commit()
        await db.refresh(account)
        
        return {"success": True, "settings": account.platform_settings}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {str(e)}")



@router.post("/campaigns")
async def create_campaign(
    request: CreateCampaignRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new social media campaign"""
    try:
        # For now, create a basic campaign - this would be expanded
        campaign = Campaign(
            user_id=user.id,
            name=request.name,
            description=request.description,
            platforms=request.platforms,
            schedule_config=request.schedule_config,
            content_templates=request.content_templates,
            engagement_rules=request.engagement_rules,
            status="draft"
        )

        db.add(campaign)
        await db.commit()
        await db.refresh(campaign)

        return {
            "success": True,
            "campaign": {
                "id": campaign.id,
                "name": campaign.name,
                "status": campaign.status,
                "platforms": campaign.platforms,
                "created_at": campaign.created_at.isoformat()
            }
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create campaign: {str(e)}")


@router.get("/campaigns")
async def get_campaigns():
    """Get all campaigns for the user"""
    # Mock data for now (removed auth for development)
    return {
        "campaigns": [
            {
                "id": 1,
                "name": "B2B Marketing Automation",
                "status": "active",
                "platforms": ["twitter"],
                "total_posts": 45,
                "total_engagements": 234,
                "created_at": datetime.utcnow().isoformat()
            }
        ]
    }


@router.post("/posts")
async def create_post(
    request: PostContentRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create and schedule a social media post"""
    logger.info(f"Starting create_post: user_id={user.id}, platforms={request.platforms}, content_length={len(request.content)}")
    try:
        results = []

        for platform in request.platforms:
            logger.info(f"Processing platform: {platform}, user_id={user.id}")
            try:
                # Get user's account for this platform
                logger.debug(f"Querying social account: platform={platform}, user_id={user.id}")
                account = await db.execute(
                    select(SocialAccount).where(
                        SocialAccount.user_id == user.id,
                        SocialAccount.platform == platform,
                        SocialAccount.is_active == True
                    )
                )
                account = account.scalar_one_or_none()
                logger.info(f"Account query result: platform={platform}, account_found={account is not None}")

                # Demo mode fallback
                if not account and settings.environment == "development":
                    # Simulate success for demo/dev environment
                    results.append({
                        "platform": platform,
                        "success": True,
                        "post_id": f"demo-{secrets.token_hex(8)}",
                        "url": f"https://{platform}.com/demo/status/{secrets.token_hex(8)}",
                        "posted_at": datetime.utcnow().isoformat(),
                        "note": "Demo mode: Post simulated"
                    })
                    continue

                if not account:
                    results.append({
                        "platform": platform,
                        "success": False,
                        "error": f"No active {platform} account connected"
                    })
                    continue

                # Decrypt tokens
                logger.debug(f"Decrypting tokens for platform: {platform}")
                access_token = decrypt_data(account.access_token)
                refresh_token = decrypt_data(account.refresh_token) if account.refresh_token else None

                # Post to platform
                logger.info(f"Getting service for platform: {platform}")
                if platform == "twitter":
                    service = get_twitter_service(access_token)
                    # Set refresh token and expiration info for automatic token refresh
                    logger.info(f"Setting refresh token data: refresh_token_exists={refresh_token is not None}, expires_at={account.token_expires_at}")
                    if refresh_token and account.token_expires_at:
                        service._refresh_token = refresh_token
                        service._token_expires_at = account.token_expires_at
                        logger.info(f"Refresh token data set successfully")
                    else:
                        logger.warning(f"Missing refresh token or expiration data")
                elif platform == "facebook":
                    service = get_facebook_service(access_token)
                elif platform == "instagram":
                    service = get_instagram_service(access_token)
                elif platform == "mastodon":
                    service = get_mastodon_service(access_token)
                elif platform == "bluesky":
                    service = get_bluesky_service(access_token)
                else:
                    logger.warning(f"Posting not implemented for platform: {platform}")
                    results.append({
                        "platform": platform,
                        "success": False,
                        "error": f"Posting not implemented for {platform}"
                    })
                    continue

                logger.info(f"Calling service.post_content for platform: {platform}")
                result = service.post_content(request.content)
                logger.info(f"Service post_content result: platform={platform}, success={result.get('success')}, error={result.get('error')}")

                if result['success']:
                    # Save post record
                    logger.info(f"Saving post to database: platform={platform}, account_id={account.id}")
                    post = SocialPost(
                        user_id=user.id,
                        social_account_id=account.id,
                        campaign_id=request.campaign_id,
                        platform=platform,
                        platform_post_id=result.get('post_id', ''),
                        post_url=result.get('url', ''),
                        content=request.content,
                        status="posted",
                        posted_at=datetime.utcnow()
                    )
                    db.add(post)
                    logger.info(f"Post saved successfully: platform={platform}, post_id={post.id}")

                    results.append({
                        "platform": platform,
                        "success": True,
                        "post_id": post.id,
                        "url": result.get('url', ''),
                        "posted_at": post.posted_at.isoformat()
                    })
                else:
                    # Check if account needs reconnection
                    if result.get('needs_reconnection'):
                        logger.warning(f"Account needs reconnection: platform={platform}, account_id={account.id}")
                        # Mark account as inactive and requiring reconnection
                        account.is_active = False
                        account.last_synced_at = datetime.utcnow()
                        # Could also send notification here

                    results.append({
                        "platform": platform,
                        "success": False,
                        "error": result.get('error', 'Unknown error'),
                        "needs_reconnection": result.get('needs_reconnection', False)
                    })

            except Exception as e:
                logger.error(f"Error processing platform: {platform}, error={str(e)}", exc_info=True)
                results.append({
                    "platform": platform,
                    "success": False,
                    "error": str(e)
                })

        logger.info(f"Committing database transaction: user_id={user.id}")
        await db.commit()
        logger.info("Database commit successful")

        # Check if any posts succeeded
        success_count = sum(1 for r in results if r['success'])
        logger.info(f"Post creation summary: success_count={success_count}, total_platforms={len(request.platforms)}")
        
        # Always return results, even if all failed
        # The frontend expects a 200 OK with results array to handle per-item status
        return {
            "success": success_count > 0,
            "message": f"Posted to {success_count} of {len(request.platforms)} platforms",
            "results": results
        }

    except Exception as e:
        logger.error(f"Failed to create post: error={str(e)}", exc_info=True)
        await db.rollback()
        # Still return 500 for unexpected system errors
        raise HTTPException(status_code=500, detail=f"Failed to create post: {str(e)}")


@router.post("/engagement")
async def perform_engagement(
    request: EngagementRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Perform engagement action on social media"""
    try:
        # Get the social account
        account = await db.execute(
            select(SocialAccount).where(
                SocialAccount.user_id == user.id,
                SocialAccount.platform == request.platform,
                SocialAccount.is_active == True
            )
        )
        account = account.scalar_one_or_none()

        if not account:
            raise HTTPException(status_code=400, detail=f"No active {request.platform} account connected")

        # For Twitter engagement
        if request.platform == "twitter":
            access_token = decrypt_data(account.access_token)
            twitter_service = get_twitter_service(access_token)

            # Perform the engagement
            result = twitter_service.perform_engagement(
                target={'tweet_id': request.target_id, 'author_id': 'target_author'},
                engagement_type=request.engagement_type,
                custom_comment=request.comment_text
            )

            if result['success']:
                # Save engagement record
                engagement = Engagement(
                    user_id=user.id,
                    social_account_id=account.id,
                    platform=request.platform,
                    engagement_type=request.engagement_type,
                    target_post_id=request.target_id,
                    comment_text=request.comment_text,
                    status="completed"
                )
                db.add(engagement)
                await db.commit()

                return {"success": True, "engagement": result}
            else:
                raise HTTPException(status_code=500, detail=f"Engagement failed: {result.get('error')}")

        else:
            raise HTTPException(status_code=400, detail="Platform not supported for engagement")

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Engagement failed: {str(e)}")


@router.get("/analytics")
async def get_analytics(
    platform: Optional[str] = None,
    days: int = 7
):
    """Get social media analytics"""
    # Mock analytics data for now (removed auth for development)
    return {
        "summary": {
            "total_posts": 45,
            "total_engagements": 234,
            "total_followers_gained": 89,
            "engagement_rate": 5.2
        },
        "platform_breakdown": {
            "twitter": {
                "posts": 45,
                "engagements": 234,
                "followers_gained": 89,
                "engagement_rate": 5.2
            }
        },
        "performance_trend": [
            {"date": "2024-01-01", "posts": 5, "engagements": 25},
            {"date": "2024-01-02", "posts": 7, "engagements": 35},
            # ... more data points
        ]
    }


@router.post("/content/generate")
async def generate_content(
    request: ContentGenerationRequest,
    user: User = Depends(get_current_user)
):
    """Generate AI-powered social media content"""
    try:
        logger.info(f"Received content generation request. Client ID: {request.client_id}")
        
        # Try to use Knowledge Base if client_id is available
        if request.client_id:
            try:
                kb = await get_social_content_knowledge_base()
                logger.info(f"Knowledge Base instance retrieved. Attempting to get content for {request.client_id}")
                
                # Get client content from KB
                # Pack request parameters into a dictionary as expected by get_client_content
                content_req = {
                    "platform": request.platform,
                    "content_type": request.content_type,
                    "topic": request.topic
                }
                
                client_content = await kb.get_client_content(
                    client_id=request.client_id,
                    content_request=content_req
                )
                
                logger.info(f"Client content generated: {len(client_content) if client_content else 0} items")
                
                if client_content:
                    return {
                        "success": True,
                        "content": client_content,
                        "message": "Content generated using client knowledge base"
                    }
            except Exception as kb_error:
                logger.warning(f"Failed to generate content from KB: {kb_error}", exc_info=True)
                # Fallback to mock content if KB fails

        # Fallback to Mock content (Generic Business)
        mock_templates = {
            "automated_social_posting": {
                "twitter": "🚀 Ready to grow your business? Discover how our solutions can help you save time and boost results. #BusinessGrowth #Efficiency",
                "facebook": "Take your business to the next level! Our proven strategies help you save time and increase revenue. Learn more today.",
                "instagram": "🚀 Unlock your business potential! Save time and grow faster with our expert solutions. #Business #Growth #Success"
            },
            "crm_follow_ups": {
                "twitter": "💡 maximize your opportunities! efficiently manage your leads and close more deals. #Sales #BusinessTips",
                "facebook": "Stop losing opportunities! Our system helps you nurture prospects effectively and close more sales.",
                "instagram": "🎯 Smart business growth! Better management means better results. #Business #Sales #Success"
            }
        }

        feature_templates = mock_templates.get(request.feature_key, mock_templates["automated_social_posting"])
        content = feature_templates.get(request.platform, feature_templates["twitter"])

        # Extract hashtags from content
        hashtags = []
        words = content.split()
        for word in words:
            if word.startswith('#'):
                hashtags.append(word)

        mock_content = {
            "success": True,
            "content": [
                {
                    "id": f"mock_{request.feature_key}_{request.platform}_{int(datetime.utcnow().timestamp())}",
                    "feature": request.feature_key,
                    "platform": request.platform,
                    "type": request.content_type,
                    "content": content,
                    "hashtags": hashtags,
                    "call_to_action": "Learn more!",
                    "character_count": len(content),
                    "generated_at": datetime.utcnow().isoformat(),
                    "source": "mock"
                }
            ],
            "message": "Content generated successfully (using simplified mock data)"
        }

        return mock_content

    except Exception as e:
        logger.error(f"Content generation failed: {str(e)}", exc_info=True)
        # Return fallback content even on error (Generic)
        return {
            "success": True,
            "content": [
                {
                    "id": f"fallback_{request.feature_key}_{request.platform}",
                    "feature": request.feature_key,
                    "platform": request.platform,
                    "type": request.content_type,
                    "content": f"🚀 Ready to upgrade your business? Experience the difference with our {request.feature_key.replace('_', ' ')} solutions. #BusinessGrowth",
                    "hashtags": ["#BusinessGrowth", "#Success"],
                    "call_to_action": "Get started today!",
                    "character_count": 120,
                    "generated_at": datetime.utcnow().isoformat(),
                    "source": "fallback"
                }
            ],
            "message": "Content generated successfully (fallback mode)"
        }


@router.post("/schedule")
async def schedule_post(
    request: SchedulePostRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Schedule a social media post for future publishing"""
    try:
        from app.models.social_account import SocialPost

        scheduled_posts = []

        scheduled_at = request.scheduled_at
        if request.timezone_offset_minutes is not None:
            scheduled_at = scheduled_at + timedelta(minutes=request.timezone_offset_minutes)

        if scheduled_at <= datetime.utcnow():
            raise HTTPException(status_code=400, detail="Scheduled time must be in the future")

        # Create scheduled posts for each platform
        for platform in request.platforms:
            # Get user's account for this platform
            account = await db.execute(
                select(SocialAccount).where(
                    SocialAccount.user_id == user.id,
                    SocialAccount.platform == platform,
                    SocialAccount.is_active == True
                )
            )
            account = account.scalar_one_or_none()

            if not account:
                continue  # Skip platforms where user doesn't have an account

            # Check if approval is required
            settings = account.platform_settings or {}
            requires_approval = settings.get("approval_required", False)
            initial_status = "draft" if requires_approval else "scheduled"

            # Create scheduled post
            scheduled_post = SocialPost(
                user_id=user.id,
                social_account_id=account.id,
                campaign_id=request.campaign_id,
                platform=platform,
                content=request.content,
                status=initial_status,
                scheduled_at=scheduled_at,
                generated_by_ai=False
            )

            db.add(scheduled_post)
            await db.flush()
            scheduled_posts.append({
                "id": scheduled_post.id,
                "platform": platform,
                "scheduled_at": scheduled_at.isoformat(),
                "status": initial_status
            })

        await db.commit()

        if not scheduled_posts:
            raise HTTPException(status_code=400, detail="No posts were scheduled. Please ensure you have connected accounts for the selected platforms.")

        return {
            "success": True,
            "message": f"Scheduled post for {len(scheduled_posts)} platforms",
            "scheduled_posts": scheduled_posts
        }

    except Exception as e:
        await db.rollback()
        logger.error(f"Post scheduling failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Post scheduling failed: {str(e)}")


@router.get("/scheduled")
async def get_scheduled_posts(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all scheduled posts for the user"""
    try:
        from app.models.social_account import SocialPost

        result = await db.execute(
            select(SocialPost).where(
                SocialPost.user_id == user.id,
                SocialPost.status == "scheduled",
                SocialPost.scheduled_at > datetime.utcnow()
            ).order_by(SocialPost.scheduled_at)
        )
        posts = result.scalars().all()

        return {
            "scheduled_posts": [
                {
                    "id": post.id,
                    "platform": post.platform,
                    "content": post.content,
                    "scheduled_at": post.scheduled_at.isoformat(),
                    "campaign_id": post.campaign_id,
                    "created_at": post.created_at.isoformat()
                }
                for post in posts
            ]
        }

    except Exception as e:
        logger.error(f"Failed to fetch scheduled posts: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch scheduled posts: {str(e)}")


@router.get("/scheduled/drafts")
async def get_draft_posts(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all draft posts (awaiting approval) for the user"""
    try:
        from app.models.social_account import SocialPost

        result = await db.execute(
            select(SocialPost).where(
                SocialPost.user_id == user.id,
                SocialPost.status == "draft"
            ).order_by(SocialPost.scheduled_at)
        )
        posts = result.scalars().all()

        return {
            "draft_posts": [
                {
                    "id": post.id,
                    "platform": post.platform,
                    "content": post.content,
                    "scheduled_at": post.scheduled_at.isoformat() if post.scheduled_at else None,
                    "campaign_id": post.campaign_id,
                    "created_at": post.created_at.isoformat()
                }
                for post in posts
            ]
        }

    except Exception as e:
        logger.error(f"Failed to fetch draft posts: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch draft posts: {str(e)}")


@router.get("/history")
async def get_post_history(
    status: Optional[str] = None,
    limit: int = 5,
    offset: int = 0,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get history of posted and failed posts"""
    try:
        from app.models.social_account import SocialPost
        from sqlalchemy import or_

        query = select(SocialPost).where(SocialPost.user_id == user.id)
        if status in ("posted", "failed"):
            query = query.where(SocialPost.status == status)
        else:
            query = query.where(
                or_(
                    SocialPost.status == "posted",
                    SocialPost.status == "failed"
                )
            )

        result = await db.execute(
            query.order_by(SocialPost.scheduled_at.desc())
                 .offset(offset)
                 .limit(limit)
        )
        posts = result.scalars().all()

        return {
            "history_posts": [
                {
                    "id": post.id,
                    "platform": post.platform,
                    "content": post.content,
                    "scheduled_at": post.scheduled_at.isoformat() if post.scheduled_at else None,
                    "posted_at": post.posted_at.isoformat() if post.posted_at else None,
                    "failed_at": post.failed_at.isoformat() if post.failed_at else None,
                    "status": post.status,
                    "failure_reason": post.failure_reason,
                    "post_url": post.post_url,
                    "campaign_id": post.campaign_id,
                    "created_at": post.created_at.isoformat()
                }
                for post in posts
            ]
        }

    except Exception as e:
        logger.error(f"Failed to fetch post history: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch post history: {str(e)}")


@router.post("/scheduled/{post_id}/approve")
async def approve_scheduled_post(
    post_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Approve a draft post"""
    try:
        from app.models.social_account import SocialPost
        
        result = await db.execute(
            select(SocialPost).where(
                SocialPost.id == post_id,
                SocialPost.user_id == user.id
            )
        )
        post = result.scalar_one_or_none()
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
            
        post.status = "scheduled"
        await db.commit()
        
        return {"success": True, "message": "Post approved successfully"}
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to approve post: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to approve post: {str(e)}")


@router.delete("/scheduled/{post_id}")
async def delete_scheduled_post(
    post_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a scheduled post"""
    try:
        from app.models.social_account import SocialPost
        
        result = await db.execute(
            select(SocialPost).where(
                SocialPost.id == post_id,
                SocialPost.user_id == user.id
            )
        )
        post = result.scalar_one_or_none()
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
            
        await db.delete(post)
        await db.commit()
        
        return {"success": True, "message": "Post deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to delete post: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to delete post: {str(e)}")


@router.post("/schedule/rules")
async def create_schedule_rule(
    request: CreateScheduleRuleRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new recurring schedule rule"""
    try:
        # Check for duplicate rules (same timing and overlapping platforms)
        existing_rule_result = await db.execute(
            select(ScheduleRule).where(
                ScheduleRule.user_id == user.id,
                ScheduleRule.frequency == request.frequency,
                ScheduleRule.time_of_day == request.time_of_day,
                ScheduleRule.is_active == True
            )
        )
        existing_rules = existing_rule_result.scalars().all()
        
        for existing_rule in existing_rules:
            # Check if platforms overlap
            common_platforms = set(existing_rule.platforms) & set(request.platforms)
            if common_platforms:
                raise HTTPException(
                    status_code=400, 
                    detail=f"A rule '{existing_rule.name}' already exists for {request.frequency} at {request.time_of_day} on overlapping platforms ({', '.join(common_platforms)})"
                )

        # Validate connected accounts
        active_accounts_result = await db.execute(
            select(SocialAccount).where(
                SocialAccount.user_id == user.id,
                SocialAccount.platform.in_(request.platforms),
                SocialAccount.is_active == True
            )
        )
        active_accounts = active_accounts_result.scalars().all()
        active_platforms = {acc.platform for acc in active_accounts}
        
        missing_platforms = set(request.platforms) - active_platforms
        if missing_platforms:
            raise HTTPException(
                status_code=400,
                detail=f"No active accounts found for: {', '.join(missing_platforms)}. Please connect them first."
            )

        rule = ScheduleRule(
            user_id=user.id,
            name=request.name,
            platforms=request.platforms,
            frequency=request.frequency,
            time_of_day=request.time_of_day,
            timezone=request.timezone,
            days_of_week=request.days_of_week,
            recurrence_config=request.recurrence_config,
            content_variation=request.content_variation,
            topic=request.topic,
            tone=request.tone,
            content_type=request.content_type,
            autopost=request.autopost,
            start_date=request.start_date,
            end_date=request.end_date,
            is_active=True
        )
        
        db.add(rule)
        await db.commit()
        await db.refresh(rule)
        
        return {
            "success": True,
            "rule": {
                "id": rule.id,
                "name": rule.name,
                "frequency": rule.frequency,
                "time_of_day": rule.time_of_day,
                "platforms": rule.platforms,
                "is_active": rule.is_active
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create schedule rule: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create schedule rule: {str(e)}")


@router.delete("/schedule/rules/{rule_id}")
async def delete_schedule_rule(
    rule_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a recurring schedule rule"""
    try:
        result = await db.execute(
            select(ScheduleRule).where(
                ScheduleRule.id == rule_id,
                ScheduleRule.user_id == user.id
            )
        )
        rule = result.scalar_one_or_none()
        
        if not rule:
            raise HTTPException(status_code=404, detail="Rule not found")
            
        # Hard delete or soft delete? Let's use soft delete
        rule.is_active = False
        await db.commit()
        
        return {"success": True, "message": "Rule deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to delete schedule rule: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to delete schedule rule: {str(e)}")


@router.get("/schedule/rules")
async def get_schedule_rules(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all recurring schedule rules for the user"""
    try:
        result = await db.execute(
            select(ScheduleRule).where(
                ScheduleRule.user_id == user.id,
                ScheduleRule.is_active == True
            ).order_by(ScheduleRule.created_at.desc())
        )
        rules = result.scalars().all()
        
        return {
            "rules": [
                {
                    "id": rule.id,
                    "name": rule.name,
                    "frequency": rule.frequency,
                    "time_of_day": rule.time_of_day,
                    "platforms": rule.platforms,
                    "is_active": rule.is_active,
                    "days_of_week": rule.days_of_week,
                    "next_run_at": rule.next_run_at.isoformat() if rule.next_run_at else None
                }
                for rule in rules
            ]
        }
    except Exception as e:
        logger.error(f"Failed to fetch schedule rules: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch schedule rules: {str(e)}")


# AI Content Hub API Endpoints
class HashtagGenerationRequest(BaseModel):
    topic: str = Field(..., description="Topic or keyword to generate hashtags for")
    platform: str = Field("twitter", description="Target social media platform")
    count: int = Field(10, description="Number of hashtags to generate", ge=5, le=30)


class ImageGenerationRequest(BaseModel):
    query: str = Field(..., description="Image search query or description")
    count: int = Field(6, description="Number of images to generate", ge=1, le=12)


class ChatAssistantRequest(BaseModel):
    message: str = Field(..., description="User message to the AI assistant")
    context: Optional[str] = Field(None, description="Optional context about the conversation")


@router.post("/content/generate-hashtags")
async def generate_hashtags(request: HashtagGenerationRequest):
    """Generate relevant hashtags for a given topic and platform"""
    try:
        # Mock hashtag generation based on topic and platform
        base_hashtags = {
            "marketing": ["#Marketing", "#DigitalMarketing", "#MarketingTips", "#MarketingStrategy", "#MarketingAutomation"],
            "business": ["#Business", "#Entrepreneurship", "#BusinessTips", "#BusinessGrowth", "#BusinessStrategy"],
            "technology": ["#Technology", "#Tech", "#Innovation", "#TechTrends", "#DigitalTransformation"],
            "social media": ["#SocialMedia", "#SocialMediaMarketing", "#SocialMediaTips", "#SocialMediaStrategy", "#ContentMarketing"],
            "ai": ["#AI", "#ArtificialIntelligence", "#MachineLearning", "#AI", "#TechInnovation"],
            "sales": ["#Sales", "#SalesTips", "#SalesStrategy", "#BusinessDevelopment", "#LeadGeneration"],
            "startup": ["#Startup", "#Entrepreneur", "#StartupLife", "#BusinessGrowth", "#Innovation"],
            "finance": ["#Finance", "#FinancialPlanning", "#Investment", "#MoneyManagement", "#FinancialFreedom"],
            "health": ["#Health", "#Wellness", "#HealthyLiving", "#Fitness", "#Nutrition"],
            "education": ["#Education", "#Learning", "#OnlineLearning", "#Knowledge", "#PersonalDevelopment"]
        }

        # Platform-specific hashtag variations
        platform_modifiers = {
            "twitter": ["#Twitter", "#TwitterMarketing", "#Tweet"],
            "instagram": ["#Instagram", "#InstaDaily", "#PhotoOfTheDay"],
            "facebook": ["#Facebook", "#FacebookMarketing", "#SocialMedia"],
            "linkedin": ["#LinkedIn", "#ProfessionalDevelopment", "#BusinessNetworking"],
            "tiktok": ["#TikTok", "#Viral", "#Trending"]
        }

        # Get base hashtags for the topic
        topic_lower = request.topic.lower()
        hashtags = []

        # Find matching topic categories
        for category, category_hashtags in base_hashtags.items():
            if category in topic_lower or any(word in topic_lower for word in category.split()):
                hashtags.extend(category_hashtags)
                break

        # If no specific category found, use general marketing/business hashtags
        if not hashtags:
            hashtags = base_hashtags["marketing"] + base_hashtags["business"]

        # Add platform-specific hashtags
        platform_hashtags = platform_modifiers.get(request.platform, platform_modifiers["twitter"])
        hashtags.extend(platform_hashtags)

        # Add some trending/popular hashtags
        trending_hashtags = ["#Viral", "#Trending", "#ContentMarketing", "#DigitalMarketing", "#BusinessGrowth"]
        hashtags.extend(trending_hashtags)

        # Remove duplicates and limit to requested count
        unique_hashtags = list(set(hashtags))[:request.count]

        # Create response with metadata
        hashtag_objects = []
        for i, hashtag in enumerate(unique_hashtags):
            hashtag_objects.append({
                "id": f"hashtag_{i+1}",
                "text": hashtag,
                "category": "topic" if i < len(unique_hashtags) - len(trending_hashtags) - len(platform_hashtags) else "trending",
                "popularity_score": 0.5 + (i * 0.1) % 0.5,  # Mock popularity score
                "usage_count": 1000 + (i * 500)  # Mock usage count
            })

        return {
            "success": True,
            "topic": request.topic,
            "platform": request.platform,
            "hashtags": hashtag_objects,
            "total_count": len(hashtag_objects),
            "generated_at": datetime.utcnow().isoformat(),
            "source": "mock_ai"
        }

    except Exception as e:
        logger.error(f"Hashtag generation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Hashtag generation failed: {str(e)}")


@router.post("/content/generate-images")
async def generate_images(request: ImageGenerationRequest):
    """Generate image suggestions based on search query"""
    try:
        # Mock image generation - in production this would call an AI image service
        mock_images = []

        # Generate mock image data based on query
        for i in range(request.count):
            image_id = f"img_{int(datetime.utcnow().timestamp())}_{i+1}"
            mock_images.append({
                "id": image_id,
                "url": f"https://picsum.photos/400/300?random={i+1}",  # Using Lorem Picsum for demo
                "thumbnail_url": f"https://picsum.photos/200/150?random={i+1}",
                "title": f"Image suggestion {i+1} for '{request.query}'",
                "description": f"AI-generated image related to {request.query}",
                "width": 400,
                "height": 300,
                "format": "jpg",
                "source": "mock_ai",
                "tags": [request.query, "ai_generated", f"suggestion_{i+1}"],
                "generated_at": datetime.utcnow().isoformat(),
                "download_url": f"https://picsum.photos/800/600?random={i+1}"
            })

        return {
            "success": True,
            "query": request.query,
            "images": mock_images,
            "total_count": len(mock_images),
            "generated_at": datetime.utcnow().isoformat(),
            "source": "mock_ai",
            "note": "Using mock image data. In production, this would connect to an AI image generation service."
        }

    except Exception as e:
        logger.error(f"Image generation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")


@router.post("/content/chat-assistant")
async def chat_assistant(request: ChatAssistantRequest):
    """AI-powered chat assistant for content strategy advice"""
    try:
        # Mock AI responses based on user message content
        responses = {
            "hashtag": [
                "For optimal hashtag performance, use a mix of popular (#Viral with 10M+ posts) and niche hashtags specific to your audience. Aim for 5-10 hashtags per post, and track which combinations drive the most engagement.",
                "Hashtag strategy tip: Research trending hashtags in your niche using tools like Instagram's search, then combine them with branded hashtags to increase discoverability."
            ],
            "content": [
                "Great content strategy involves understanding your audience's pain points and providing value. Focus on educational content that positions your brand as an expert in your field.",
                "Content calendar tip: Plan your posts around key themes and events. Consistency matters, but quality always trumps quantity."
            ],
            "engagement": [
                "Boost engagement by asking questions in your captions, responding to comments within 24 hours, and creating content that encourages shares and saves.",
                "Engagement strategy: Use Stories for quick polls and questions, and leverage user-generated content to build community around your brand."
            ],
            "time": [
                "Best posting times vary by platform and audience. Generally: Instagram & TikTok work well 7-9 PM weekdays, Facebook 1-3 PM weekdays, Twitter anytime but especially 8-10 AM and 5-7 PM.",
                "Posting time tip: Test different times with your specific audience and use analytics to determine what works best for your content."
            ],
            "analytics": [
                "Track engagement rate, reach, and click-through rates. Focus on content that drives meaningful actions, not just vanity metrics like likes.",
                "Analytics insight: Look at which content types perform best and double down on those formats while experimenting with new approaches."
            ]
        }

        # Default response
        default_responses = [
            "I'd be happy to help with your content strategy! Could you tell me more about what specific aspect you'd like advice on - hashtags, posting times, content creation, or analytics?",
            "That's an interesting question about social media marketing. Based on current best practices, here are some key insights...",
            "Great question! Let me share some proven strategies that have helped businesses like yours succeed on social media."
        ]

        # Find relevant response based on message content
        message_lower = request.message.lower()
        response_text = default_responses[0]  # Default fallback

        for keyword, keyword_responses in responses.items():
            if keyword in message_lower:
                response_text = keyword_responses[0]  # Use first response for that keyword
                break

        # If no specific keyword match, use a general response
        if response_text == default_responses[0]:
            response_text = default_responses[1]

        return {
            "success": True,
            "response": {
                "id": f"chat_{int(datetime.utcnow().timestamp())}",
                "message": response_text,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "mock_ai",
                "confidence": 0.85,  # Mock confidence score
                "suggestions": [
                    "Would you like me to elaborate on this topic?",
                    "I can also help with hashtag research or content ideas.",
                    "Let me know if you need platform-specific advice."
                ]
            },
            "conversation_context": request.context,
            "processing_time_ms": 150 + (datetime.utcnow().microsecond % 500)  # Mock processing time
        }

    except Exception as e:
        logger.error(f"Chat assistant failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Chat assistant failed: {str(e)}")


@router.get("/performance")
async def get_performance_metrics(
    period: str = Query("30d", description="Time period for metrics"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get performance metrics for social accounts"""
    # Stub implementation to fix 404 error
    # In a real implementation, this would aggregate stats from SocialAccount and SocialPost tables
    return {
        "overview": {
            "total_followers": 0,
            "total_engagement": 0,
            "total_posts": 0,
            "engagement_rate": 0
        },
        "platforms": [],
        "recent_posts": []
    }

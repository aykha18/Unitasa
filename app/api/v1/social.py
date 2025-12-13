"""
Social media management API endpoints for client-facing platform
"""

import secrets
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Request, Query
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
from app.models.campaign import Campaign
from app.models.user import User
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


# Pydantic models
class ConnectAccountRequest(BaseModel):
    platform: str = Field(..., description="Platform to connect (twitter, linkedin, etc.)")
    authorization_code: str = Field(..., description="OAuth authorization code")
    code_verifier: str = Field(..., description="PKCE code verifier")
    redirect_uri: Optional[str] = Field(None, description="OAuth redirect URI")


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


class SchedulePostRequest(BaseModel):
    content: str = Field(..., description="Content to post")
    platforms: List[str] = Field(..., description="Platforms to post to")
    scheduled_at: datetime = Field(..., description="When to post")
    campaign_id: Optional[int] = Field(None, description="Associated campaign")


# Dependencies
async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)) -> User:
    """Get current authenticated user"""
    # For now, return a mock user - in production this would validate JWT tokens
    # TODO: Implement proper JWT authentication
    user_id = getattr(request.state, 'user_id', 1)  # Default to user ID 1 for development

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


@router.get("/auth/{platform}/url")
async def get_oauth_url(platform: str, user_id: int = Query(1, description="User ID")):
    """Get OAuth authorization URL for a platform"""
    try:
        if platform == "twitter":
            # For development/demo purposes, return a mock OAuth URL if credentials are not configured
            try:
                oauth_service = TwitterOAuthService()
                auth_url, code_verifier, state = oauth_service.get_authorization_url()
            except ValueError as e:
                # Twitter credentials not configured - return demo URL
                code_verifier = secrets.token_urlsafe(32)[:43]
                state = secrets.token_urlsafe(16)

                # Return a demo URL that shows the OAuth flow would work
                auth_url = f"https://twitter.com/i/oauth2/authorize?response_type=code&client_id=demo&redirect_uri=http://localhost:3000/social/callback&scope=tweet.read%20tweet.write%20users.read%20offline.access&state={state}&code_challenge=demo&code_challenge_method=S256"

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

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate auth URL: {str(e)}")


@router.get("/auth/{platform}/callback")
async def oauth_callback(
    platform: str,
    code: str = Query(..., description="Authorization code from OAuth provider"),
    state: str = Query(..., description="State parameter for security"),
    code_verifier: Optional[str] = Query(None, description="PKCE code verifier (optional, retrieved from server storage)"),
    error: Optional[str] = Query(None, description="Error from OAuth provider"),
    user_id: int = Query(1, description="User ID")
):
    """Handle OAuth callback from social media platforms and automatically connect account"""
    if error:
        # Redirect back to social dashboard with error
        return f"""
        <html>
        <head><title>OAuth Error</title></head>
        <body>
        <h1>OAuth Error</h1>
        <p>Error: {error}</p>
        <p>Platform: {platform}</p>
        <a href="/social">Back to Social Dashboard</a>
        <script>
        setTimeout(function() {{
            window.location.href = '/social';
        }}, 3000);
        </script>
        </body>
        </html>
        """

    try:
        # Try to get code_verifier from server-side storage first, then from query param
        stored_code_verifier = None
        if hasattr(get_oauth_url, 'code_verifiers') and state in get_oauth_url.code_verifiers:
            stored_code_verifier = get_oauth_url.code_verifiers.pop(state, None)  # Remove after use

        final_code_verifier = stored_code_verifier or code_verifier
        logger.info(f"OAuth callback received: platform={platform}, state={state}")
        logger.info(f"Code verifier details: stored_length={len(stored_code_verifier) if stored_code_verifier else 0}, query_length={len(code_verifier) if code_verifier else 0}, final_length={len(final_code_verifier) if final_code_verifier else 0}")
        logger.info(f"Available states in storage: {list(getattr(get_oauth_url, 'code_verifiers', {}).keys())}")

        # Automatically connect the account
        from app.core.database import init_database
        from app.models.user import User

        engine, AsyncSessionLocal = init_database()
        async with AsyncSessionLocal() as db:
            # Get user (mock for now)
            user_result = await db.execute(select(User).where(User.id == user_id))
            user = user_result.scalar_one_or_none()

            if not user:
                return f"""
                <html>
                <head><title>OAuth Error</title></head>
                <body>
                <h1>User Not Found</h1>
                <p>User ID {user_id} not found.</p>
                <a href="/social">Back to Social Dashboard</a>
                </body>
                </html>
                """

            # Connect the account using the same logic as the connect endpoint
            account_info = None
            token_data = None

            if platform == "twitter":
                oauth_service = TwitterOAuthService()
                token_data = oauth_service.exchange_code_for_tokens(code, final_code_verifier)
                twitter_service = get_twitter_service(token_data['access_token'])
                account_info = twitter_service.get_account_info()

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
                return f"""
                <html>
                <head><title>Platform Not Supported</title></head>
                <body>
                <h1>Platform Not Supported</h1>
                <p>Platform '{platform}' is not supported for automatic connection.</p>
                <a href="/social">Back to Social Dashboard</a>
                </body>
                </html>
                """

            if not account_info or not token_data:
                return f"""
                <html>
                <head><title>Connection Failed</title></head>
                <body>
                <h1>Connection Failed</h1>
                <p>Failed to retrieve account information from {platform}.</p>
                <a href="/social">Back to Social Dashboard</a>
                </body>
                </html>
                """

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
            return f"""
            <html>
            <head><title>Account Connected</title></head>
            <body>
            <h1>Success!</h1>
            <p>Successfully connected your {platform} account: @{account_info['username']}</p>
            <p>Redirecting to Social Dashboard...</p>
            <a href="/social">Go to Social Dashboard</a>
            <script>
            setTimeout(function() {{
                window.location.href = '/social';
            }}, 2000);
            </script>
            </body>
            </html>
            """

    except Exception as e:
        logger.error(f"OAuth callback error for {platform}: {str(e)}", exc_info=True)
        return f"""
        <html>
        <head><title>Connection Error</title></head>
        <body>
        <h1>Connection Error</h1>
        <p>An error occurred while connecting your {platform} account.</p>
        <p>Error: {str(e)}</p>
        <a href="/social">Back to Social Dashboard</a>
        </body>
        </html>
        """


@router.post("/accounts/connect")
async def connect_account(
    request: ConnectAccountRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Connect a social media account using OAuth code"""
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
                        "last_synced_at": acc.last_synced_at.isoformat() if acc.last_synced_at else None
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
        # Check if it's the mock account
        if account_id == 1 and settings.environment == "development":
             return {"success": True, "message": "Mock account disconnected"}

        account = await db.get(SocialAccount, account_id)
        if not account or account.user_id != user.id:
            raise HTTPException(status_code=404, detail="Account not found")
            
        await db.delete(account)
        await db.commit()
        
        return {"success": True, "message": "Account disconnected"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to disconnect account: {str(e)}")


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
        if success_count > 0:
            return {
                "success": True,
                "message": f"Posted to {success_count} of {len(request.platforms)} platforms",
                "results": results
            }
        else:
            logger.error(f"No posts succeeded: results={results}")
            raise HTTPException(status_code=500, detail="Failed to post to any platforms")

    except Exception as e:
        logger.error(f"Failed to create post: error={str(e)}", exc_info=True)
        await db.rollback()
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
        # For now, return mock content to avoid complex dependencies
        # TODO: Re-enable full AI content generation when dependencies are stable

        # Mock content based on feature and platform
        mock_templates = {
            "automated_social_posting": {
                "twitter": "🚀 Transform your marketing with Unitasa's AI agents! Save 15+ hours/week with automated social posting. #MarketingAutomation",
                "facebook": "Transform your marketing with Unitasa's AI agents! Save 15+ hours/week with automated social posting across all platforms. Book a free demo today!",
                "instagram": "🚀 AI agents that run your marketing for you! Save 15+ hours/week with automated posting. #MarketingAutomation #AI #SaaS #Business"
            },
            "crm_follow_ups": {
                "twitter": "💡 Never miss a lead again! Unitasa's AI agents send personalized follow-ups based on behavior. #CRM #LeadGeneration",
                "facebook": "Stop losing leads to competitors! Our AI agents nurture prospects automatically based on their behavior and pipeline stage.",
                "instagram": "🎯 Smart lead nurturing with AI! Personalized follow-ups based on behavior. #CRM #LeadGeneration #Sales"
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
                    "call_to_action": "Book a demo today!" if "demo" in content.lower() else "Learn more!",
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
        # Return fallback content even on error
        return {
            "success": True,
            "content": [
                {
                    "id": f"fallback_{request.feature_key}_{request.platform}",
                    "feature": request.feature_key,
                    "platform": request.platform,
                    "type": request.content_type,
                    "content": f"🚀 Transform your marketing with Unitasa's AI agents! Save time and boost results with our {request.feature_key.replace('_', ' ')} feature. #MarketingAutomation",
                    "hashtags": ["#MarketingAutomation", "#AI", "#SaaS"],
                    "call_to_action": "Book a demo today!",
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

        # Validate scheduled time is in the future
        if request.scheduled_at <= datetime.utcnow():
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

            # Create scheduled post
            scheduled_post = SocialPost(
                user_id=user.id,
                social_account_id=account.id,
                campaign_id=request.campaign_id,
                platform=platform,
                content=request.content,
                status="scheduled",
                scheduled_at=request.scheduled_at,
                generated_by_ai=False
            )

            db.add(scheduled_post)
            scheduled_posts.append({
                "id": scheduled_post.id,
                "platform": platform,
                "scheduled_at": request.scheduled_at.isoformat(),
                "status": "scheduled"
            })

        await db.commit()

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
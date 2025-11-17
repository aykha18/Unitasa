"""
Instagram Basic Display API integration service for social media automation
"""

import os
import json
import secrets
import requests
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from urllib.parse import urlencode

from app.core.config import get_settings

settings = get_settings()


class InstagramOAuthService:
    """Handles Instagram Basic Display OAuth flow"""

    def __init__(self):
        self.app_id = os.getenv("INSTAGRAM_APP_ID", "")
        self.app_secret = os.getenv("INSTAGRAM_APP_SECRET", "")
        self.redirect_uri = os.getenv("INSTAGRAM_REDIRECT_URI", f"{settings.frontend_url}/auth/instagram/callback")

        if not self.app_id:
            raise ValueError("INSTAGRAM_APP_ID environment variable is required")

    def get_authorization_url(self, state: str = None) -> Tuple[str, str]:
        """
        Generate Instagram OAuth authorization URL

        Returns:
            Tuple of (auth_url, state)
        """
        if not state:
            state = secrets.token_urlsafe(16)

        params = {
            'client_id': self.app_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'user_profile,user_media',
            'response_type': 'code',
            'state': state
        }

        auth_url = f"https://api.instagram.com/oauth/authorize?{urlencode(params)}"
        return auth_url, state

    def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token
        """
        token_url = "https://api.instagram.com/oauth/access_token"

        data = {
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri,
            'code': code
        }

        response = requests.post(token_url, data=data)

        if response.status_code != 200:
            raise Exception(f"Token exchange failed: {response.text}")

        token_data = response.json()

        # Calculate token expiration (60 days for Instagram Basic Display)
        expires_in = token_data.get('expires_in', 5184000)  # Default 60 days
        token_data['expires_at'] = datetime.utcnow() + timedelta(seconds=expires_in)

        return token_data

    def refresh_access_token(self, access_token: str) -> Dict[str, Any]:
        """
        Refresh access token (Instagram Basic Display tokens don't expire)
        """
        return {
            'access_token': access_token,
            'expires_at': datetime.utcnow() + timedelta(days=60),
            'token_type': 'bearer'
        }


class InstagramAPIService:
    """Handles Instagram Basic Display API interactions"""

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://graph.instagram.com"
        self.headers = {
            'Content-Type': 'application/json'
        }

    def get_user_info(self) -> Dict[str, Any]:
        """Get user profile information"""
        url = f"{self.base_url}/me"
        params = {
            'fields': 'id,username,account_type,media_count',
            'access_token': self.access_token
        }

        response = requests.get(url, params=params, headers=self.headers)

        if response.status_code != 200:
            raise Exception(f"Failed to get user info: {response.text}")

        return response.json()

    def get_user_media(self, limit: int = 10) -> Dict[str, Any]:
        """Get user's media"""
        url = f"{self.base_url}/me/media"
        params = {
            'fields': 'id,media_type,media_url,permalink,caption,timestamp,like_count,comments_count',
            'limit': limit,
            'access_token': self.access_token
        }

        response = requests.get(url, params=params, headers=self.headers)

        if response.status_code != 200:
            raise Exception(f"Failed to get media: {response.text}")

        return response.json()

    def create_post(self, image_url: str, caption: str) -> Dict[str, Any]:
        """Create a new post (Instagram Basic Display API has limited posting capabilities)"""
        # Note: Instagram Basic Display API doesn't support posting
        # This would require Instagram Graph API with Business account
        raise NotImplementedError("Instagram Basic Display API doesn't support posting. Use Instagram Graph API for business accounts.")


class InstagramAutomationService:
    """High-level service for Instagram automation"""

    def __init__(self, access_token: str):
        self.api = InstagramAPIService(access_token)
        self.oauth = InstagramOAuthService()

    def get_account_info(self) -> Dict[str, Any]:
        """Get connected account information"""
        user_info = self.api.get_user_info()

        return {
            'account_id': user_info['id'],
            'username': user_info['username'],
            'name': user_info['username'],  # Instagram doesn't provide display name in Basic API
            'profile_url': f"https://www.instagram.com/{user_info['username']}",
            'avatar_url': '',  # Not available in Basic API
            'follower_count': 0,  # Not available in Basic API
            'following_count': 0,
            'account_type': user_info.get('account_type', 'personal'),
            'media_count': user_info.get('media_count', 0)
        }

    def post_content(self, content: str, campaign_data: Dict = None) -> Dict[str, Any]:
        """Post content to Instagram (limited by Basic Display API)"""
        return {
            'success': False,
            'error': 'Instagram Basic Display API does not support posting. Use Instagram Graph API for business accounts.',
            'platform': 'instagram'
        }


def get_instagram_service(access_token: str = None) -> InstagramAutomationService:
    """Factory function to get Instagram service"""
    if not access_token:
        raise ValueError("Access token is required for Instagram API")

    return InstagramAutomationService(access_token)
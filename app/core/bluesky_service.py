"""
Bluesky API integration service for social media automation
"""

import os
import json
import secrets
import requests
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

from app.core.config import get_settings

settings = get_settings()


class BlueskyOAuthService:
    """Handles Bluesky authentication (simplified - Bluesky uses custom auth)"""

    def __init__(self):
        self.service_url = "https://bsky.social"
        self.client_id = os.getenv("BLUESKY_CLIENT_ID", "")
        self.client_secret = os.getenv("BLUESKY_CLIENT_SECRET", "")
        self.redirect_uri = os.getenv("BLUESKY_REDIRECT_URI", f"{settings.frontend_url}/auth/bluesky/callback")

    def get_authorization_url(self, state: str = None) -> Tuple[str, str]:
        """
        Generate Bluesky authorization URL

        Returns:
            Tuple of (auth_url, state)
        """
        if not state:
            state = secrets.token_urlsafe(16)

        # Bluesky doesn't have traditional OAuth, so we redirect to a setup page
        auth_url = f"{settings.frontend_url}/bluesky-setup?state={state}"

        return auth_url, state

    def exchange_code_for_tokens(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exchange credentials for session tokens
        """
        # Bluesky uses username/password or app passwords
        # This is a simplified implementation
        return {
            'access_token': credentials.get('access_token', ''),
            'refresh_token': credentials.get('refresh_token', ''),
            'expires_at': datetime.utcnow() + timedelta(hours=2),  # Bluesky sessions are short-lived
            'token_type': 'bearer',
            'handle': credentials.get('handle', '')
        }


class BlueskyAPIService:
    """Handles Bluesky API interactions"""

    def __init__(self, access_token: str, handle: str = None):
        self.access_token = access_token
        self.handle = handle
        self.service_url = "https://bsky.social"
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

    def get_profile(self) -> Dict[str, Any]:
        """Get user profile"""
        url = f"{self.service_url}/xrpc/app.bsky.actor.getProfile"

        params = {'actor': self.handle} if self.handle else {}

        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code != 200:
            raise Exception(f"Failed to get profile: {response.text}")

        return response.json()

    def create_post(self, text: str) -> Dict[str, Any]:
        """Create a post on Bluesky"""
        url = f"{self.service_url}/xrpc/com.atproto.repo.createRecord"

        data = {
            "repo": self.handle,
            "collection": "app.bsky.feed.post",
            "record": {
                "text": text,
                "createdAt": datetime.utcnow().isoformat() + "Z",
                "$type": "app.bsky.feed.post"
            }
        }

        response = requests.post(url, headers=self.headers, json=data)

        if response.status_code != 200:
            raise Exception(f"Failed to create post: {response.text}")

        return response.json()


class BlueskyAutomationService:
    """High-level service for Bluesky automation"""

    def __init__(self, access_token: str, handle: str = None):
        self.api = BlueskyAPIService(access_token, handle)
        self.oauth = BlueskyOAuthService()

    def get_account_info(self) -> Dict[str, Any]:
        """Get connected account information"""
        profile = self.api.get_profile()

        return {
            'account_id': profile.get('did', ''),
            'username': profile.get('handle', ''),
            'name': profile.get('displayName', ''),
            'profile_url': f"https://bsky.app/profile/{profile.get('handle', '')}",
            'avatar_url': profile.get('avatar', ''),
            'follower_count': profile.get('followersCount', 0),
            'following_count': profile.get('followsCount', 0),
            'description': profile.get('description', '')
        }

    def post_content(self, content: str, campaign_data: Dict = None) -> Dict[str, Any]:
        """Post content to Bluesky"""
        try:
            post = self.api.create_post(content)

            return {
                'success': True,
                'post_id': post['uri'],
                'url': f"https://bsky.app/profile/{self.api.handle}/post/{post['uri'].split('/')[-1]}",
                'posted_at': datetime.utcnow().isoformat(),
                'platform': 'bluesky'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'platform': 'bluesky'
            }


def get_bluesky_service(access_token: str = None, handle: str = None) -> BlueskyAutomationService:
    """Factory function to get Bluesky service"""
    if not access_token:
        raise ValueError("Access token is required for Bluesky API")

    return BlueskyAutomationService(access_token, handle)
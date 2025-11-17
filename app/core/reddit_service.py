"""
Reddit API integration service for social media automation
"""

import os
import json
import secrets
import base64
import requests
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from urllib.parse import urlencode

from app.core.config import get_settings

settings = get_settings()


class RedditOAuthService:
    """Handles Reddit OAuth 2.0 flow"""

    def __init__(self):
        self.client_id = os.getenv("REDDIT_CLIENT_ID", "")
        self.client_secret = os.getenv("REDDIT_CLIENT_SECRET", "")
        self.redirect_uri = os.getenv("REDDIT_REDIRECT_URI", f"{settings.frontend_url}/auth/reddit/callback")

        if not self.client_id:
            raise ValueError("REDDIT_CLIENT_ID environment variable is required")

    def get_authorization_url(self, state: str = None) -> Tuple[str, str]:
        """
        Generate Reddit OAuth authorization URL

        Returns:
            Tuple of (auth_url, state)
        """
        if not state:
            state = secrets.token_urlsafe(16)

        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'state': state,
            'redirect_uri': self.redirect_uri,
            'duration': 'permanent',
            'scope': 'identity submit read'
        }

        auth_url = f"https://www.reddit.com/api/v1/authorize?{urlencode(params)}"
        return auth_url, state

    def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access tokens
        """
        token_url = "https://www.reddit.com/api/v1/access_token"

        auth = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        headers = {
            'Authorization': f'Basic {auth}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri
        }

        response = requests.post(token_url, headers=headers, data=data)

        if response.status_code != 200:
            raise Exception(f"Token exchange failed: {response.text}")

        token_data = response.json()

        # Calculate token expiration
        expires_in = token_data.get('expires_in', 3600)  # Default 1 hour
        token_data['expires_at'] = datetime.utcnow() + timedelta(seconds=expires_in)

        return token_data

    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh an expired access token
        """
        token_url = "https://www.reddit.com/api/v1/access_token"

        auth = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        headers = {
            'Authorization': f'Basic {auth}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }

        response = requests.post(token_url, headers=headers, data=data)

        if response.status_code != 200:
            raise Exception(f"Token refresh failed: {response.text}")

        token_data = response.json()

        # Calculate new token expiration
        expires_in = token_data.get('expires_in', 3600)
        token_data['expires_at'] = datetime.utcnow() + timedelta(seconds=expires_in)

        return token_data


class RedditAPIService:
    """Handles Reddit API interactions"""

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://oauth.reddit.com"
        self.headers = {
            'Authorization': f'bearer {access_token}',
            'User-Agent': 'AI Marketing Agent/1.0'
        }

    def get_user_info(self) -> Dict[str, Any]:
        """Get authenticated user information"""
        url = f"{self.base_url}/api/v1/me"

        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            raise Exception(f"Failed to get user info: {response.text}")

        return response.json()

    def submit_post(self, subreddit: str, title: str, text: str = None, url: str = None) -> Dict[str, Any]:
        """Submit a post to a subreddit"""
        url_endpoint = f"{self.base_url}/api/submit"

        data = {
            'sr': subreddit,
            'title': title,
            'kind': 'self' if text else 'link'
        }

        if text:
            data['text'] = text
        if url:
            data['url'] = url
            data['kind'] = 'link'

        response = requests.post(url_endpoint, headers=self.headers, data=data)

        if response.status_code != 200:
            raise Exception(f"Failed to submit post: {response.text}")

        return response.json()

    def get_subreddits(self) -> Dict[str, Any]:
        """Get user's subscribed subreddits"""
        url = f"{self.base_url}/subreddits/mine/subscriber"

        params = {'limit': 100}

        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code != 200:
            raise Exception(f"Failed to get subreddits: {response.text}")

        return response.json()


class RedditAutomationService:
    """High-level service for Reddit automation"""

    def __init__(self, access_token: str):
        self.api = RedditAPIService(access_token)
        self.oauth = RedditOAuthService()

    def get_account_info(self) -> Dict[str, Any]:
        """Get connected account information"""
        user_info = self.api.get_user_info()

        return {
            'account_id': user_info['id'],
            'username': user_info['name'],
            'name': user_info['name'],
            'profile_url': f"https://www.reddit.com/user/{user_info['name']}",
            'avatar_url': '',  # Reddit avatars require additional API calls
            'follower_count': 0,  # Not directly available
            'following_count': 0,
            'karma': user_info.get('total_karma', 0),
            'has_verified_email': user_info.get('has_verified_email', False)
        }

    def post_content(self, content: str, campaign_data: Dict = None) -> Dict[str, Any]:
        """Post content to Reddit"""
        try:
            # This would need subreddit configuration
            return {
                'success': False,
                'error': 'Reddit subreddit must be configured for posting',
                'platform': 'reddit'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'platform': 'reddit'
            }


def get_reddit_service(access_token: str = None) -> RedditAutomationService:
    """Factory function to get Reddit service"""
    if not access_token:
        raise ValueError("Access token is required for Reddit API")

    return RedditAutomationService(access_token)
"""
Mastodon API integration service for social media automation
"""

import os
import json
import secrets
import requests
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

from app.core.config import get_settings

settings = get_settings()


class MastodonOAuthService:
    """Handles Mastodon OAuth 2.0 flow"""

    def __init__(self, instance_url: str = "https://mastodon.social"):
        self.instance_url = instance_url
        self.client_id = os.getenv("MASTODON_CLIENT_ID", "")
        self.client_secret = os.getenv("MASTODON_CLIENT_SECRET", "")
        self.redirect_uri = os.getenv("MASTODON_REDIRECT_URI", f"{settings.frontend_url}/auth/mastodon/callback")

        if not self.client_id:
            raise ValueError("MASTODON_CLIENT_ID environment variable is required")

    def get_authorization_url(self, state: str = None) -> Tuple[str, str]:
        """
        Generate Mastodon OAuth authorization URL

        Returns:
            Tuple of (auth_url, state)
        """
        if not state:
            state = secrets.token_urlsafe(16)

        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'scope': 'read write follow',
            'state': state
        }

        auth_url = f"{self.instance_url}/oauth/authorize?{('&'.join(f'{k}={v}' for k, v in params.items()))}"
        return auth_url, state

    def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access tokens
        """
        token_url = f"{self.instance_url}/oauth/token"

        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code',
            'code': code,
            'scope': 'read write follow'
        }

        response = requests.post(token_url, data=data)

        if response.status_code != 200:
            raise Exception(f"Token exchange failed: {response.text}")

        token_data = response.json()

        # Calculate token expiration (Mastodon tokens may not expire)
        expires_in = token_data.get('expires_in')
        if expires_in:
            token_data['expires_at'] = datetime.utcnow() + timedelta(seconds=expires_in)
        else:
            token_data['expires_at'] = datetime.utcnow() + timedelta(days=365)  # Assume 1 year

        return token_data


class MastodonAPIService:
    """Handles Mastodon API interactions"""

    def __init__(self, access_token: str, instance_url: str = "https://mastodon.social"):
        self.access_token = access_token
        self.instance_url = instance_url
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

    def get_account_info(self) -> Dict[str, Any]:
        """Get authenticated account information"""
        url = f"{self.instance_url}/api/v1/accounts/verify_credentials"

        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            raise Exception(f"Failed to get account info: {response.text}")

        return response.json()

    def post_status(self, status: str, visibility: str = 'public') -> Dict[str, Any]:
        """Post a status to Mastodon"""
        url = f"{self.instance_url}/api/v1/statuses"

        data = {
            'status': status,
            'visibility': visibility
        }

        response = requests.post(url, headers=self.headers, json=data)

        if response.status_code != 200:
            raise Exception(f"Failed to post status: {response.text}")

        return response.json()


class MastodonAutomationService:
    """High-level service for Mastodon automation"""

    def __init__(self, access_token: str, instance_url: str = "https://mastodon.social"):
        self.api = MastodonAPIService(access_token, instance_url)
        self.oauth = MastodonOAuthService(instance_url)

    def get_account_info(self) -> Dict[str, Any]:
        """Get connected account information"""
        account = self.api.get_account_info()

        return {
            'account_id': account['id'],
            'username': account['username'],
            'name': account['display_name'] or account['username'],
            'profile_url': account['url'],
            'avatar_url': account['avatar'],
            'follower_count': account['followers_count'],
            'following_count': account['following_count'],
            'instance': self.oauth.instance_url
        }

    def post_content(self, content: str, campaign_data: Dict = None) -> Dict[str, Any]:
        """Post content to Mastodon"""
        try:
            status = self.api.post_status(content)

            return {
                'success': True,
                'post_id': status['id'],
                'url': status['url'],
                'posted_at': status['created_at'],
                'platform': 'mastodon'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'platform': 'mastodon'
            }


def get_mastodon_service(access_token: str = None, instance_url: str = "https://mastodon.social") -> MastodonAutomationService:
    """Factory function to get Mastodon service"""
    if not access_token:
        raise ValueError("Access token is required for Mastodon API")

    return MastodonAutomationService(access_token, instance_url)
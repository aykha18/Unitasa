"""
Pinterest API integration service for social media automation
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


class PinterestOAuthService:
    """Handles Pinterest OAuth 2.0 flow"""

    def __init__(self):
        self.app_id = os.getenv("PINTEREST_APP_ID", "")
        self.app_secret = os.getenv("PINTEREST_APP_SECRET", "")
        self.redirect_uri = os.getenv("PINTEREST_REDIRECT_URI", f"{settings.frontend_url}/auth/pinterest/callback")

        if not self.app_id:
            raise ValueError("PINTEREST_APP_ID environment variable is required")

    def get_authorization_url(self, state: str = None) -> Tuple[str, str]:
        """
        Generate Pinterest OAuth authorization URL

        Returns:
            Tuple of (auth_url, state)
        """
        if not state:
            state = secrets.token_urlsafe(16)

        params = {
            'client_id': self.app_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': 'read_public,write_public',
            'state': state
        }

        auth_url = f"https://www.pinterest.com/oauth/?{urlencode(params)}"
        return auth_url, state

    def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access tokens
        """
        token_url = "https://api.pinterest.com/v5/oauth/token"

        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri
        }

        headers = {
            'Authorization': f'Basic {os.getenv("PINTEREST_APP_ID")}:{os.getenv("PINTEREST_APP_SECRET")}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.post(token_url, headers=headers, data=data)

        if response.status_code != 200:
            raise Exception(f"Token exchange failed: {response.text}")

        token_data = response.json()

        # Calculate token expiration
        expires_in = token_data.get('expires_in', 2592000)  # Default 30 days
        token_data['expires_at'] = datetime.utcnow() + timedelta(seconds=expires_in)

        return token_data

    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh an expired access token
        """
        token_url = "https://api.pinterest.com/v5/oauth/token"

        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }

        headers = {
            'Authorization': f'Basic {os.getenv("PINTEREST_APP_ID")}:{os.getenv("PINTEREST_APP_SECRET")}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.post(token_url, headers=headers, data=data)

        if response.status_code != 200:
            raise Exception(f"Token refresh failed: {response.text}")

        token_data = response.json()

        # Calculate new token expiration
        expires_in = token_data.get('expires_in', 2592000)
        token_data['expires_at'] = datetime.utcnow() + timedelta(seconds=expires_in)

        return token_data


class PinterestAPIService:
    """Handles Pinterest API interactions"""

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://api.pinterest.com/v5"
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

    def get_user_info(self) -> Dict[str, Any]:
        """Get authenticated user information"""
        url = f"{self.base_url}/user_account"

        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            raise Exception(f"Failed to get user info: {response.text}")

        return response.json()

    def create_pin(self, board_id: str, title: str, description: str, image_url: str, link: str = None) -> Dict[str, Any]:
        """Create a pin"""
        url = f"{self.base_url}/pins"

        data = {
            'board_id': board_id,
            'title': title,
            'description': description,
            'media_source': {
                'source_type': 'image_url',
                'url': image_url
            }
        }

        if link:
            data['link'] = link

        response = requests.post(url, headers=self.headers, json=data)

        if response.status_code != 201:
            raise Exception(f"Failed to create pin: {response.text}")

        return response.json()

    def get_boards(self) -> Dict[str, Any]:
        """Get user's boards"""
        url = f"{self.base_url}/boards"

        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            raise Exception(f"Failed to get boards: {response.text}")

        return response.json()


class PinterestAutomationService:
    """High-level service for Pinterest automation"""

    def __init__(self, access_token: str):
        self.api = PinterestAPIService(access_token)
        self.oauth = PinterestOAuthService()

    def get_account_info(self) -> Dict[str, Any]:
        """Get connected account information"""
        user_info = self.api.get_user_info()

        return {
            'account_id': user_info['username'],
            'username': user_info['username'],
            'name': user_info.get('full_name', user_info['username']),
            'profile_url': f"https://www.pinterest.com/{user_info['username']}",
            'avatar_url': '',  # Not available in basic API
            'follower_count': user_info.get('follower_count', 0),
            'following_count': user_info.get('following_count', 0),
            'board_count': user_info.get('board_count', 0)
        }

    def post_content(self, content: str, campaign_data: Dict = None) -> Dict[str, Any]:
        """Post content to Pinterest (requires image)"""
        return {
            'success': False,
            'error': 'Pinterest requires image uploads, not text posts',
            'platform': 'pinterest'
        }


def get_pinterest_service(access_token: str = None) -> PinterestAutomationService:
    """Factory function to get Pinterest service"""
    if not access_token:
        raise ValueError("Access token is required for Pinterest API")

    return PinterestAutomationService(access_token)
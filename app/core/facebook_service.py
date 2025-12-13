"""
Facebook Page API integration service for social media automation
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


class FacebookOAuthService:
    """Handles Facebook OAuth 2.0 flow for Page access"""

    def __init__(self):
        self.app_id = os.getenv("FACEBOOK_APP_ID", "")
        self.app_secret = os.getenv("FACEBOOK_APP_SECRET", "")
        self.redirect_uri = os.getenv("FACEBOOK_REDIRECT_URI", f"{settings.frontend_url}/auth/facebook/callback")

        if not self.app_id:
            raise ValueError("FACEBOOK_APP_ID environment variable is required")

    def get_authorization_url(self, state: str = None) -> Tuple[str, str]:
        """
        Generate Facebook OAuth authorization URL for Page access

        Returns:
            Tuple of (auth_url, state)
        """
        if not state:
            state = secrets.token_urlsafe(16)

        params = {
            'client_id': self.app_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'pages_show_list,email,public_profile',
            'response_type': 'code',
            'state': state
        }

        auth_url = f"https://www.facebook.com/v18.0/dialog/oauth?{urlencode(params)}"
        return auth_url, state

    def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access tokens
        """
        token_url = f"https://graph.facebook.com/v18.0/oauth/access_token"

        params = {
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'redirect_uri': self.redirect_uri,
            'code': code
        }

        response = requests.get(token_url, params=params)

        if response.status_code != 200:
            raise Exception(f"Token exchange failed: {response.text}")

        token_data = response.json()

        # Get long-lived token
        long_lived_url = f"https://graph.facebook.com/v18.0/oauth/access_token"
        long_lived_params = {
            'grant_type': 'fb_exchange_token',
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'fb_exchange_token': token_data['access_token']
        }

        long_lived_response = requests.get(long_lived_url, params=long_lived_params)

        if long_lived_response.status_code == 200:
            token_data = long_lived_response.json()

        # Calculate token expiration (60 days for long-lived tokens)
        expires_in = token_data.get('expires_in', 5184000)  # Default 60 days
        token_data['expires_at'] = datetime.utcnow() + timedelta(seconds=expires_in)

        return token_data

    def refresh_access_token(self, access_token: str) -> Dict[str, Any]:
        """
        Refresh a long-lived access token
        Note: Facebook doesn't have traditional refresh tokens, tokens are long-lived
        """
        # For Facebook, we just return the same token with extended expiry
        # In practice, you'd need to re-authenticate when tokens expire
        return {
            'access_token': access_token,
            'expires_at': datetime.utcnow() + timedelta(days=60),
            'token_type': 'bearer'
        }


class FacebookAPIService:
    """Handles Facebook Graph API interactions"""

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v18.0"
        self.headers = {
            'Content-Type': 'application/json'
        }

    def get_user_pages(self) -> Dict[str, Any]:
        """Get user's Facebook Pages"""
        url = f"{self.base_url}/me/accounts"
        params = {
            'access_token': self.access_token,
            'fields': 'id,name,category,access_token,tasks'
        }

        response = requests.get(url, params=params, headers=self.headers)

        if response.status_code != 200:
            raise Exception(f"Failed to get pages: {response.text}")

        return response.json()

    def get_page_info(self, page_id: str) -> Dict[str, Any]:
        """Get page information"""
        url = f"{self.base_url}/{page_id}"
        params = {
            'access_token': self.access_token,
            'fields': 'id,name,category,about,website,fan_count,followers_count,posts'
        }

        response = requests.get(url, params=params, headers=self.headers)

        if response.status_code != 200:
            raise Exception(f"Failed to get page info: {response.text}")

        return response.json()['data'] if 'data' in response.json() else response.json()

    def post_to_page(self, page_id: str, page_access_token: str, message: str, link: str = None) -> Dict[str, Any]:
        """Post to a Facebook Page"""
        url = f"{self.base_url}/{page_id}/feed"

        data = {'message': message, 'access_token': page_access_token}
        if link:
            data['link'] = link

        response = requests.post(url, data=data, headers=self.headers)

        if response.status_code != 200:
            raise Exception(f"Failed to post to page: {response.text}")

        return response.json()

    def get_page_posts(self, page_id: str, limit: int = 10) -> Dict[str, Any]:
        """Get page posts"""
        url = f"{self.base_url}/{page_id}/posts"
        params = {
            'access_token': self.access_token,
            'fields': 'id,message,created_time,permalink_url,insights.metric(post_impressions,post_engaged_users)',
            'limit': limit
        }

        response = requests.get(url, params=params, headers=self.headers)

        if response.status_code != 200:
            raise Exception(f"Failed to get posts: {response.text}")

        return response.json()


class FacebookAutomationService:
    """High-level service for Facebook Page automation"""

    def __init__(self, access_token: str):
        self.api = FacebookAPIService(access_token)
        self.oauth = FacebookOAuthService()

    def get_account_info(self) -> Dict[str, Any]:
        """Get connected account information"""
        pages = self.api.get_user_pages()

        if not pages.get('data'):
            raise Exception("No Facebook Pages found for this account")

        # Use the first page for now (in production, user should select)
        page = pages['data'][0]

        return {
            'account_id': page['id'],
            'username': page['id'],  # Facebook Pages use ID as username
            'name': page['name'],
            'profile_url': f"https://www.facebook.com/{page['id']}",
            'avatar_url': f"https://graph.facebook.com/{page['id']}/picture?type=large",
            'follower_count': 0,  # Would need additional API call
            'following_count': 0,
            'page_access_token': page.get('access_token'),
            'category': page.get('category', '')
        }

    def post_content(self, content: str, campaign_data: Dict = None) -> Dict[str, Any]:
        """Post content to Facebook Page"""
        try:
            pages = self.api.get_user_pages()
            if not pages.get('data'):
                raise Exception("No Facebook Pages available")

            page = pages['data'][0]  # Use first page
            page_access_token = page.get('access_token')

            if not page_access_token:
                raise Exception("No page access token available")

            post_data = self.api.post_to_page(page['id'], page_access_token, content)

            return {
                'success': True,
                'post_id': post_data['id'],
                'url': f"https://www.facebook.com/{post_data['id']}",
                'posted_at': datetime.utcnow().isoformat(),
                'platform': 'facebook'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'platform': 'facebook'
            }


def get_facebook_service(access_token: str = None) -> FacebookAutomationService:
    """Factory function to get Facebook service"""
    if not access_token:
        raise ValueError("Access token is required for Facebook API")

    return FacebookAutomationService(access_token)
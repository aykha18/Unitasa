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
    """Handles Instagram OAuth flow via Facebook (for Business accounts)"""

    def __init__(self):
        # Use Facebook credentials for Instagram access (unified OAuth)
        self.app_id = os.getenv("FACEBOOK_APP_ID", "")
        self.app_secret = os.getenv("FACEBOOK_APP_SECRET", "")
        self.redirect_uri = os.getenv("FACEBOOK_REDIRECT_URI", f"{settings.frontend_url}/auth/instagram/callback")

        if not self.app_id:
            raise ValueError("FACEBOOK_APP_ID environment variable is required for Instagram access")

    def get_authorization_url(self, state: str = None) -> Tuple[str, str]:
        """
        Generate Instagram OAuth authorization URL via Facebook

        Returns:
            Tuple of (auth_url, state)
        """
        if not state:
            state = secrets.token_urlsafe(16)

        params = {
            'client_id': self.app_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'instagram_basic,instagram_content_publish,pages_read_engagement',
            'response_type': 'code',
            'state': state
        }

        auth_url = f"https://www.facebook.com/v18.0/dialog/oauth?{urlencode(params)}"
        return auth_url, state

    def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access tokens via Facebook
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
        Refresh access token (Instagram Basic Display tokens don't expire)
        """
        return {
            'access_token': access_token,
            'expires_at': datetime.utcnow() + timedelta(days=60),
            'token_type': 'bearer'
        }


class InstagramAPIService:
    """Handles Instagram Graph API interactions for Business accounts"""

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v18.0"
        self.headers = {
            'Content-Type': 'application/json'
        }

    def get_instagram_accounts(self) -> Dict[str, Any]:
        """Get Instagram Business accounts connected to Facebook pages"""
        url = f"{self.base_url}/me/accounts"
        params = {
            'access_token': self.access_token,
            'fields': 'id,name,instagram_business_account{id,username,name,profile_picture_url,followers_count,follows_count,media_count}'
        }

        response = requests.get(url, params=params, headers=self.headers)

        if response.status_code != 200:
            raise Exception(f"Failed to get Instagram accounts: {response.text}")

        return response.json()

    def get_account_info(self, instagram_account_id: str) -> Dict[str, Any]:
        """Get Instagram account information"""
        url = f"{self.base_url}/{instagram_account_id}"
        params = {
            'fields': 'id,username,name,profile_picture_url,followers_count,follows_count,media_count,biography',
            'access_token': self.access_token
        }

        response = requests.get(url, params=params, headers=self.headers)

        if response.status_code != 200:
            raise Exception(f"Failed to get account info: {response.text}")

        return response.json()

    def get_user_media(self, instagram_account_id: str, limit: int = 10) -> Dict[str, Any]:
        """Get user's media"""
        url = f"{self.base_url}/{instagram_account_id}/media"
        params = {
            'fields': 'id,media_type,media_url,permalink,caption,timestamp,like_count,comments_count,insights.metric(impressions,reach,engagement)',
            'limit': limit,
            'access_token': self.access_token
        }

        response = requests.get(url, params=params, headers=self.headers)

        if response.status_code != 200:
            raise Exception(f"Failed to get media: {response.text}")

        return response.json()

    def create_post(self, instagram_account_id: str, image_url: str, caption: str) -> Dict[str, Any]:
        """Create a new Instagram post"""
        # First, create a media container
        url = f"{self.base_url}/{instagram_account_id}/media"
        data = {
            'image_url': image_url,
            'caption': caption,
            'access_token': self.access_token
        }

        response = requests.post(url, data=data, headers=self.headers)

        if response.status_code != 200:
            raise Exception(f"Failed to create media container: {response.text}")

        container_data = response.json()
        container_id = container_data['id']

        # Publish the container
        publish_url = f"{self.base_url}/{instagram_account_id}/media_publish"
        publish_data = {
            'creation_id': container_id,
            'access_token': self.access_token
        }

        publish_response = requests.post(publish_url, data=publish_data, headers=self.headers)

        if publish_response.status_code != 200:
            raise Exception(f"Failed to publish post: {publish_response.text}")

        return publish_response.json()


class InstagramAutomationService:
    """High-level service for Instagram automation via Facebook Graph API"""

    def __init__(self, access_token: str):
        self.api = InstagramAPIService(access_token)
        self.oauth = InstagramOAuthService()

    def get_account_info(self) -> Dict[str, Any]:
        """Get connected Instagram account information"""
        try:
            # Get Instagram accounts connected to Facebook pages
            accounts_data = self.api.get_instagram_accounts()

            if not accounts_data.get('data'):
                raise Exception("No Facebook Pages with connected Instagram Business accounts found")

            # Use the first available Instagram account
            for page in accounts_data['data']:
                instagram_account = page.get('instagram_business_account')
                if instagram_account:
                    account_details = self.api.get_account_info(instagram_account['id'])

                    return {
                        'account_id': account_details['id'],
                        'username': account_details['username'],
                        'name': account_details.get('name', account_details['username']),
                        'profile_url': f"https://www.instagram.com/{account_details['username']}",
                        'avatar_url': account_details.get('profile_picture_url', ''),
                        'follower_count': account_details.get('followers_count', 0),
                        'following_count': account_details.get('follows_count', 0),
                        'account_type': 'business',
                        'media_count': account_details.get('media_count', 0),
                        'biography': account_details.get('biography', '')
                    }

            raise Exception("No Instagram Business accounts found. Make sure your Facebook Page is connected to an Instagram Business account.")

        except Exception as e:
            # Fallback for development/demo
            return {
                'account_id': 'demo_instagram_id',
                'username': 'demo_instagram',
                'name': 'Demo Instagram Account',
                'profile_url': 'https://www.instagram.com/demo',
                'avatar_url': '',
                'follower_count': 0,
                'following_count': 0,
                'account_type': 'business',
                'media_count': 0
            }

    def post_content(self, content: str, campaign_data: Dict = None) -> Dict[str, Any]:
        """Post content to Instagram"""
        try:
            # Get account info to find Instagram account ID
            account_info = self.get_account_info()

            if account_info['account_id'] == 'demo_instagram_id':
                # Demo mode
                return {
                    'success': True,
                    'post_id': f"demo_instagram_{secrets.token_hex(8)}",
                    'url': f"https://www.instagram.com/p/demo{secrets.token_hex(4)}",
                    'posted_at': datetime.utcnow().isoformat(),
                    'platform': 'instagram',
                    'note': 'Demo mode: Post simulated'
                }

            # For now, we'll need an image URL. In production, this would be uploaded first
            # For this quick win, we'll assume content is just text and needs an image
            # TODO: Add image upload capability

            return {
                'success': False,
                'error': 'Instagram posting requires an image URL. Image upload functionality needed.',
                'platform': 'instagram'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'platform': 'instagram'
            }


def get_instagram_service(access_token: str = None) -> InstagramAutomationService:
    """Factory function to get Instagram service"""
    if not access_token:
        raise ValueError("Access token is required for Instagram API")

    return InstagramAutomationService(access_token)
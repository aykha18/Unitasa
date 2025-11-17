"""
YouTube Data API integration service for social media automation
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


class YouTubeOAuthService:
    """Handles YouTube OAuth 2.0 flow using Google OAuth"""

    def __init__(self):
        self.client_id = os.getenv("YOUTUBE_CLIENT_ID", "")
        self.client_secret = os.getenv("YOUTUBE_CLIENT_SECRET", "")
        self.redirect_uri = os.getenv("YOUTUBE_REDIRECT_URI", f"{settings.frontend_url}/auth/youtube/callback")

        if not self.client_id:
            raise ValueError("YOUTUBE_CLIENT_ID environment variable is required")

    def get_authorization_url(self, state: str = None) -> Tuple[str, str]:
        """
        Generate YouTube OAuth authorization URL

        Returns:
            Tuple of (auth_url, state)
        """
        if not state:
            state = secrets.token_urlsafe(16)

        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly https://www.googleapis.com/auth/youtube.force-ssl',
            'response_type': 'code',
            'access_type': 'offline',
            'include_granted_scopes': 'true',
            'state': state,
            'prompt': 'consent'
        }

        auth_url = f"https://accounts.google.com/o/oauth2/auth?{urlencode(params)}"
        return auth_url, state

    def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access tokens
        """
        token_url = "https://oauth2.googleapis.com/token"

        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri
        }

        response = requests.post(token_url, data=data)

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
        token_url = "https://oauth2.googleapis.com/token"

        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }

        response = requests.post(token_url, data=data)

        if response.status_code != 200:
            raise Exception(f"Token refresh failed: {response.text}")

        token_data = response.json()

        # Calculate new token expiration
        expires_in = token_data.get('expires_in', 3600)
        token_data['expires_at'] = datetime.utcnow() + timedelta(seconds=expires_in)

        return token_data


class YouTubeAPIService:
    """Handles YouTube Data API interactions"""

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

    def get_channel_info(self) -> Dict[str, Any]:
        """Get authenticated user's channel information"""
        url = f"{self.base_url}/channels"
        params = {
            'part': 'snippet,statistics',
            'mine': 'true'
        }

        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code != 200:
            raise Exception(f"Failed to get channel info: {response.text}")

        data = response.json()
        if not data.get('items'):
            raise Exception("No channel found")

        channel = data['items'][0]
        return channel

    def upload_video(self, title: str, description: str, video_path: str, privacy: str = 'private') -> Dict[str, Any]:
        """Upload a video to YouTube"""
        # This is a simplified version. Real implementation would need multipart upload
        # and proper video file handling
        raise NotImplementedError("Video upload requires complex multipart handling")

    def get_channel_videos(self, max_results: int = 10) -> Dict[str, Any]:
        """Get channel videos"""
        # First get channel ID
        channel_info = self.get_channel_info()
        channel_id = channel_info['id']

        url = f"{self.base_url}/search"
        params = {
            'part': 'snippet',
            'channelId': channel_id,
            'order': 'date',
            'type': 'video',
            'maxResults': max_results
        }

        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code != 200:
            raise Exception(f"Failed to get videos: {response.text}")

        return response.json()


class YouTubeAutomationService:
    """High-level service for YouTube automation"""

    def __init__(self, access_token: str):
        self.api = YouTubeAPIService(access_token)
        self.oauth = YouTubeOAuthService()

    def get_account_info(self) -> Dict[str, Any]:
        """Get connected account information"""
        channel = self.api.get_channel_info()
        snippet = channel['snippet']
        statistics = channel['statistics']

        return {
            'account_id': channel['id'],
            'username': snippet['title'],
            'name': snippet['title'],
            'profile_url': f"https://www.youtube.com/channel/{channel['id']}",
            'avatar_url': snippet['thumbnails'].get('default', {}).get('url', ''),
            'follower_count': int(statistics.get('subscriberCount', 0)),
            'following_count': 0,  # YouTube doesn't have following count
            'video_count': int(statistics.get('videoCount', 0)),
            'view_count': int(statistics.get('viewCount', 0))
        }

    def post_content(self, content: str, campaign_data: Dict = None) -> Dict[str, Any]:
        """Post content to YouTube (video upload)"""
        # YouTube requires video files, not just text
        return {
            'success': False,
            'error': 'YouTube requires video file uploads, not text posts',
            'platform': 'youtube'
        }


def get_youtube_service(access_token: str = None) -> YouTubeAutomationService:
    """Factory function to get YouTube service"""
    if not access_token:
        raise ValueError("Access token is required for YouTube API")

    return YouTubeAutomationService(access_token)
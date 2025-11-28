"""
Twitter/X API integration service for social media automation
"""

import os
import json
import base64
import secrets
import hashlib
import requests
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from urllib.parse import urlencode

from app.core.config import get_settings

settings = get_settings()


class TwitterOAuthService:
    """Handles Twitter OAuth 2.0 PKCE flow"""

    def __init__(self):
        self.client_id = os.getenv("TWITTER_CLIENT_ID", "")
        self.client_secret = os.getenv("TWITTER_CLIENT_SECRET", "")
        self.redirect_uri = os.getenv("TWITTER_REDIRECT_URI", f"{settings.frontend_url}/api/v1/social/auth/twitter/callback")

        if not self.client_id:
            raise ValueError("TWITTER_CLIENT_ID environment variable is required")

    def generate_code_verifier(self) -> str:
        """Generate a cryptographically secure code verifier"""
        return secrets.token_urlsafe(32)[:43]  # Max 43 characters

    def generate_code_challenge(self, code_verifier: str) -> str:
        """Generate code challenge from verifier using SHA256"""
        sha256 = hashlib.sha256(code_verifier.encode()).digest()
        return base64.urlsafe_b64encode(sha256).decode().rstrip('=')

    def get_authorization_url(self, state: str = None) -> Tuple[str, str, str]:
        """
        Generate Twitter OAuth authorization URL

        Returns:
            Tuple of (auth_url, code_verifier, state)
        """
        code_verifier = self.generate_code_verifier()
        code_challenge = self.generate_code_challenge(code_verifier)

        if not state:
            state = secrets.token_urlsafe(16)

        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'tweet.read tweet.write users.read offline.access',
            'state': state,
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256'
        }

        auth_url = f"https://twitter.com/i/oauth2/authorize?{urlencode(params)}"
        return auth_url, code_verifier, state

    def exchange_code_for_tokens(self, code: str, code_verifier: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access tokens
        """
        token_url = "https://api.twitter.com/2/oauth2/token"

        # Create Basic Auth header - Twitter requires this format
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_string.encode('utf-8')
        auth_b64 = base64.b64encode(auth_bytes).decode('utf-8')

        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri,
            'code_verifier': code_verifier
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {auth_b64}'
        }

        response = requests.post(token_url, data=data, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Token exchange failed: {response.text}")

        token_data = response.json()

        # Calculate token expiration
        expires_in = token_data.get('expires_in', 7200)  # Default 2 hours
        token_data['expires_at'] = datetime.utcnow() + timedelta(seconds=expires_in)

        return token_data

    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh an expired access token
        """
        token_url = "https://api.twitter.com/2/oauth2/token"

        # Create Basic Auth header
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_string.encode('utf-8')
        auth_b64 = base64.b64encode(auth_bytes).decode('utf-8')

        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {auth_b64}'
        }

        response = requests.post(token_url, data=data, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Token refresh failed: {response.text}")

        token_data = response.json()

        # Calculate new token expiration
        expires_in = token_data.get('expires_in', 7200)
        token_data['expires_at'] = datetime.utcnow() + timedelta(seconds=expires_in)

        return token_data

    def revoke_token(self, token: str, token_type_hint: str = "access_token") -> bool:
        """
        Revoke an access or refresh token
        """
        revoke_url = "https://api.twitter.com/2/oauth2/revoke"

        # Create Basic Auth header
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_string.encode('utf-8')
        auth_b64 = base64.b64encode(auth_bytes).decode('utf-8')

        data = {
            'token': token,
            'token_type_hint': token_type_hint
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {auth_b64}'
        }

        response = requests.post(revoke_url, data=data, headers=headers)
        return response.status_code == 200


class TwitterAPIService:
    """Handles Twitter API interactions"""

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://api.twitter.com/2"
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

    def get_user_info(self) -> Dict[str, Any]:
        """Get authenticated user information"""
        url = f"{self.base_url}/users/me"
        params = {
            'user.fields': 'id,name,username,profile_image_url,public_metrics,verified'
        }

        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code != 200:
            raise Exception(f"Failed to get user info: {response.text}")

        return response.json()['data']

    def post_tweet(self, text: str, reply_to: str = None) -> Dict[str, Any]:
        """Post a tweet"""
        url = f"{self.base_url}/tweets"

        data = {'text': text}
        if reply_to:
            data['reply'] = {'in_reply_to_tweet_id': reply_to}

        response = requests.post(url, headers=self.headers, json=data)

        if response.status_code != 201:
            raise Exception(f"Failed to post tweet: {response.text}")

        return response.json()['data']

    def search_tweets(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Search for tweets"""
        url = f"{self.base_url}/tweets/search/recent"

        params = {
            'query': query,
            'max_results': min(max_results, 100),
            'tweet.fields': 'id,text,author_id,created_at,public_metrics,context_annotations',
            'user.fields': 'id,name,username,verified',
            'expansions': 'author_id'
        }

        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code != 200:
            raise Exception(f"Failed to search tweets: {response.text}")

        return response.json()

    def like_tweet(self, tweet_id: str) -> Dict[str, Any]:
        """Like a tweet"""
        url = f"{self.base_url}/users/me/likes"

        data = {'tweet_id': tweet_id}

        response = requests.post(url, headers=self.headers, json=data)

        if response.status_code != 200:
            raise Exception(f"Failed to like tweet: {response.text}")

        return response.json()

    def retweet(self, tweet_id: str) -> Dict[str, Any]:
        """Retweet a tweet"""
        url = f"{self.base_url}/users/me/retweets"

        data = {'tweet_id': tweet_id}

        response = requests.post(url, headers=self.headers, json=data)

        if response.status_code != 200:
            raise Exception(f"Failed to retweet: {response.text}")

        return response.json()

    def follow_user(self, user_id: str) -> Dict[str, Any]:
        """Follow a user"""
        url = f"{self.base_url}/users/me/following"

        data = {'target_user_id': user_id}

        response = requests.post(url, headers=self.headers, json=data)

        if response.status_code != 200:
            raise Exception(f"Failed to follow user: {response.text}")

        return response.json()

    def get_tweet_metrics(self, tweet_id: str) -> Dict[str, Any]:
        """Get tweet metrics"""
        url = f"{self.base_url}/tweets/{tweet_id}"

        params = {
            'tweet.fields': 'public_metrics,non_public_metrics'
        }

        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code != 200:
            raise Exception(f"Failed to get tweet metrics: {response.text}")

        return response.json()['data']


class TwitterAutomationService:
    """High-level service for Twitter automation"""

    def __init__(self, access_token: str):
        self.api = TwitterAPIService(access_token)
        self.oauth = TwitterOAuthService()

    def get_account_info(self) -> Dict[str, Any]:
        """Get connected account information"""
        user_info = self.api.get_user_info()

        return {
            'account_id': user_info['id'],
            'username': user_info['username'],
            'name': user_info['name'],
            'profile_url': f"https://twitter.com/{user_info['username']}",
            'avatar_url': user_info.get('profile_image_url', ''),
            'follower_count': user_info['public_metrics']['followers_count'],
            'following_count': user_info['public_metrics']['following_count'],
            'verified': user_info.get('verified', False)
        }

    def post_content(self, content: str, campaign_data: Dict = None) -> Dict[str, Any]:
        """Post content to Twitter"""
        try:
            tweet_data = self.api.post_tweet(content)

            return {
                'success': True,
                'post_id': tweet_data['id'],
                'url': f"https://twitter.com/i/status/{tweet_data['id']}",
                'posted_at': tweet_data.get('created_at'),
                'platform': 'twitter'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'platform': 'twitter'
            }

    def find_engagement_targets(self, keywords: list, max_results: int = 20) -> list:
        """Find tweets to engage with based on keywords"""
        targets = []

        for keyword in keywords:
            try:
                search_results = self.api.search_tweets(keyword, max_results=max_results//len(keywords))

                for tweet in search_results.get('data', []):
                    if self._should_engage_with_tweet(tweet):
                        targets.append({
                            'tweet_id': tweet['id'],
                            'text': tweet['text'],
                            'author_id': tweet['author_id'],
                            'url': f"https://twitter.com/i/status/{tweet['id']}",
                            'keyword': keyword,
                            'engagement_potential': self._calculate_engagement_potential(tweet)
                        })

            except Exception as e:
                print(f"Error searching for keyword '{keyword}': {e}")
                continue

        # Sort by engagement potential and return top results
        targets.sort(key=lambda x: x['engagement_potential'], reverse=True)
        return targets[:max_results]

    def perform_engagement(self, target: Dict, engagement_type: str, custom_comment: str = None) -> Dict[str, Any]:
        """Perform engagement action on a tweet"""
        try:
            if engagement_type == 'like':
                result = self.api.like_tweet(target['tweet_id'])
                return {'success': True, 'type': 'like', 'target': target['tweet_id']}

            elif engagement_type == 'retweet':
                result = self.api.retweet(target['tweet_id'])
                return {'success': True, 'type': 'retweet', 'target': target['tweet_id']}

            elif engagement_type == 'comment' and custom_comment:
                result = self.api.post_tweet(custom_comment, reply_to=target['tweet_id'])
                return {
                    'success': True,
                    'type': 'comment',
                    'target': target['tweet_id'],
                    'comment_id': result['id']
                }

            elif engagement_type == 'follow':
                result = self.api.follow_user(target['author_id'])
                return {'success': True, 'type': 'follow', 'target': target['author_id']}

        except Exception as e:
            return {'success': False, 'error': str(e), 'type': engagement_type}

    def _should_engage_with_tweet(self, tweet: Dict) -> bool:
        """Determine if we should engage with a tweet"""
        # Skip tweets that are too old
        created_at = datetime.fromisoformat(tweet['created_at'].replace('Z', '+00:00'))
        if (datetime.utcnow() - created_at).days > 7:
            return False

        # Skip tweets with low engagement potential
        metrics = tweet.get('public_metrics', {})
        total_engagement = (metrics.get('like_count', 0) +
                          metrics.get('retweet_count', 0) +
                          metrics.get('reply_count', 0))

        if total_engagement < 5:  # Too low engagement
            return False

        if total_engagement > 1000:  # Too high, probably viral
            return False

        return True

    def _calculate_engagement_potential(self, tweet: Dict) -> float:
        """Calculate engagement potential score (0-1)"""
        metrics = tweet.get('public_metrics', {})
        likes = metrics.get('like_count', 0)
        retweets = metrics.get('retweet_count', 0)
        replies = metrics.get('reply_count', 0)

        # Simple scoring algorithm
        score = min((likes + retweets * 2 + replies * 3) / 100, 1.0)

        # Boost score for recent tweets
        created_at = datetime.fromisoformat(tweet['created_at'].replace('Z', '+00:00'))
        hours_old = (datetime.utcnow() - created_at).total_seconds() / 3600
        recency_boost = max(0, 1 - (hours_old / 24))  # Decay over 24 hours

        return score * (0.7 + 0.3 * recency_boost)


def get_twitter_service(access_token: str = None) -> TwitterAutomationService:
    """Factory function to get Twitter service"""
    if not access_token:
        raise ValueError("Access token is required for Twitter API")

    return TwitterAutomationService(access_token)
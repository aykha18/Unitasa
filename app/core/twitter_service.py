"""
Twitter/X API integration service for social media automation
"""

import os
import json
import base64
import secrets
import hashlib
import requests
import time
import random
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
try:
    logger = get_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)


class TwitterOAuthService:
    """Handles Twitter OAuth 2.0 PKCE flow"""

    def __init__(self):
        self.client_id = os.getenv("TWITTER_CLIENT_ID", "")
        self.client_secret = os.getenv("TWITTER_CLIENT_SECRET", "")
        self.redirect_uri = os.getenv("TWITTER_REDIRECT_URI", "http://localhost:8001/api/v1/social/auth/twitter/callback")

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
        """Post content to Twitter with automatic token management, verification, and backoff"""
        max_retries = 3
        base_delay = 2  # seconds

        updated_tokens = None

        for attempt in range(max_retries):
            try:
                # Check if token needs refresh (tokens expire after 2 hours)
                if self._should_refresh_token():
                    logger.info(f"Token needs refresh (attempt {attempt + 1})")
                    try:
                        updated_tokens = self.perform_token_refresh()
                        logger.info("Token refresh successful")
                    except Exception as refresh_error:
                        logger.error(f"Token refresh failed: {refresh_error}")
                        if attempt == max_retries - 1:
                            # Final attempt failed, mark account as needing reconnection
                            return {
                                'success': False,
                                'error': f'Token refresh failed: {refresh_error}. Account needs reconnection.',
                                'needs_reconnection': True,
                                'platform': 'twitter'
                            }
                        
                        # Exponential backoff before retry
                        sleep_time = base_delay * (2 ** attempt) + random.uniform(0, 1)
                        logger.info(f"Retrying after {sleep_time:.2f}s due to refresh failure")
                        time.sleep(sleep_time)
                        continue

                # Attempt to post
                logger.info(f"Attempting to post tweet (attempt {attempt + 1}): {content[:50]}...")
                tweet_data = self.api.post_tweet(content)
                post_id = tweet_data['id']
                
                # Verification step
                logger.info(f"Post successful, verifying post_id: {post_id}")
                verification = self._verify_post(post_id)
                
                if verification['success']:
                    logger.info(f"Post verification successful: {post_id}")
                    result = {
                        'success': True,
                        'post_id': post_id,
                        'url': f"https://twitter.com/i/status/{post_id}",
                        'posted_at': tweet_data.get('created_at'),
                        'platform': 'twitter',
                        'verification': verification
                    }
                    if updated_tokens:
                        result['updated_tokens'] = updated_tokens
                    return result
                else:
                    logger.warning(f"Post verification failed: {verification.get('error')}")
                    # Return success but note the verification failure
                    result = {
                        'success': True,
                        'post_id': post_id,
                        'url': f"https://twitter.com/i/status/{post_id}",
                        'posted_at': tweet_data.get('created_at'),
                        'platform': 'twitter',
                        'verification_failed': True,
                        'verification_error': verification.get('error')
                    }
                    if updated_tokens:
                        result['updated_tokens'] = updated_tokens
                    return result

            except Exception as e:
                error_str = str(e).lower()
                logger.error(f"Error during posting attempt {attempt + 1}: {e}")
                
                # Check for specific 403 permission error
                if 'forbidden' in error_str or '403' in error_str:
                    if 'permitted' in error_str:
                         result = {
                             'success': False,
                             'error': "Twitter Permission Error: Please go to the Twitter Developer Portal -> User authentication settings, and ensure 'App permissions' is set to 'Read and write'. Then reconnect your account.",
                             'platform': 'twitter',
                             'needs_reconnection': True
                         }
                         if updated_tokens:
                             result['updated_tokens'] = updated_tokens
                         return result

                    if 'duplicate' in error_str:
                         result = {
                             'success': False,
                             'error': "Twitter Error: Duplicate content. You cannot post the same tweet twice.",
                             'platform': 'twitter'
                         }
                         if updated_tokens:
                             result['updated_tokens'] = updated_tokens
                         return result

                if 'unauthorized' in error_str or '401' in error_str:
                    if attempt < max_retries - 1:
                        logger.info(f"Post failed with auth error, trying refresh and retry after backoff")
                        # Force refresh on next attempt
                        try:
                            updated_tokens = self.perform_token_refresh()
                        except:
                            pass
                            
                        sleep_time = base_delay * (2 ** attempt) + random.uniform(0, 1)
                        time.sleep(sleep_time)
                        continue
                    else:
                        # All attempts failed
                        result = {
                            'success': False,
                            'error': f'Authentication failed after {max_retries} attempts. Account needs reconnection.',
                            'needs_reconnection': True,
                            'platform': 'twitter'
                        }
                        if updated_tokens:
                            result['updated_tokens'] = updated_tokens
                        return result
                else:
                    # Non-auth error, still retry with backoff if not last attempt
                    if attempt < max_retries - 1:
                        sleep_time = base_delay * (2 ** attempt) + random.uniform(0, 1)
                        logger.info(f"Post failed with error, retrying in {sleep_time:.2f}s: {e}")
                        time.sleep(sleep_time)
                        continue
                        
                    result = {
                        'success': False,
                        'error': str(e),
                        'platform': 'twitter'
                    }
                    if updated_tokens:
                        result['updated_tokens'] = updated_tokens
                    return result

        # Should not reach here, but fallback
        return {
            'success': False,
            'error': 'Unknown posting error after retries',
            'platform': 'twitter'
        }

    def _verify_post(self, post_id: str) -> Dict[str, Any]:
        """Verify that a post actually exists and is accessible"""
        try:
            # Wait a brief moment for API propagation
            time.sleep(2)
            
            metrics = self.api.get_tweet_metrics(post_id)
            # If we get metrics, the tweet exists
            return {
                'success': True,
                'metrics': metrics
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
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
                logger.error(f"Error searching for keyword '{keyword}': {e}")
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
        try:
            created_at = datetime.fromisoformat(tweet['created_at'].replace('Z', '+00:00'))
            current_time = datetime.now(timezone.utc)
            if (current_time - created_at).days > 7:
                return False
        except (ValueError, TypeError):
            # Fallback if date parsing fails
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
        try:
            created_at = datetime.fromisoformat(tweet['created_at'].replace('Z', '+00:00'))
            current_time = datetime.now(timezone.utc)
            hours_old = (current_time - created_at).total_seconds() / 3600
            recency_boost = max(0, 1 - (hours_old / 24))  # Decay over 24 hours
        except (ValueError, TypeError):
            recency_boost = 0

        return score * (0.7 + 0.3 * recency_boost)

    def _should_refresh_token(self) -> bool:
        """Check if the access token needs to be refreshed"""
        # Twitter access tokens expire after 2 hours
        # We'll refresh if it's been more than 1.5 hours to be safe
        if not hasattr(self, '_token_expires_at') or self._token_expires_at is None:
            logger.info("No token expiration info, will refresh")
            return True  # No expiration info, refresh to be safe

        expires_at = self._token_expires_at
        if expires_at.tzinfo is None:
            # Assume UTC if no timezone info
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        current_time = datetime.now(timezone.utc)

        # Add 30-minute buffer before expiration
        buffer_time = timedelta(minutes=30)
        should_refresh = current_time + buffer_time >= expires_at

        logger.info(f"Token expires at: {expires_at}, current time: {current_time}, should refresh: {should_refresh}")
        return should_refresh

    def perform_token_refresh(self) -> Dict[str, Any]:
        """Refresh the access token using the refresh token"""
        try:
            if not hasattr(self, '_refresh_token') or not self._refresh_token:
                raise Exception("No refresh token available")

            # Use the OAuth service to refresh
            token_data = self.oauth.refresh_access_token(self._refresh_token)

            # Update the API service with new token
            self.api = TwitterAPIService(token_data['access_token'])

            # Store new token data
            self._access_token = token_data['access_token']
            self._refresh_token = token_data.get('refresh_token')
            self._token_expires_at = token_data.get('expires_at')

            logger.info(f"Successfully refreshed Twitter access token")
            return token_data

        except Exception as e:
            logger.error(f"Failed to refresh Twitter token: {e}")
            raise


def get_twitter_service(access_token: str = None) -> TwitterAutomationService:
    """Factory function to get Twitter service"""
    if not access_token:
        raise ValueError("Access token is required for Twitter API")

    return TwitterAutomationService(access_token)
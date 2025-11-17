"""
Telegram Bot API integration service for social media automation
"""

import os
import json
import secrets
import requests
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

from app.core.config import get_settings

settings = get_settings()


class TelegramOAuthService:
    """Handles Telegram Bot authentication"""

    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.redirect_uri = os.getenv("TELEGRAM_REDIRECT_URI", f"{settings.frontend_url}/auth/telegram/callback")

        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

    def get_authorization_url(self, state: str = None) -> Tuple[str, str]:
        """
        Generate Telegram authorization URL

        Returns:
            Tuple of (auth_url, state)
        """
        if not state:
            state = secrets.token_urlsafe(16)

        # For Telegram, we redirect to a page that explains how to set up the bot
        auth_url = f"{settings.frontend_url}/telegram-setup?state={state}&bot_token={self.bot_token[:10]}..."

        return auth_url, state

    def exchange_code_for_tokens(self, auth_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exchange authorization data for bot tokens
        For Telegram, this is more about validating the bot setup
        """
        # Validate bot token
        bot_info = self.get_bot_info()

        return {
            'access_token': self.bot_token,
            'expires_at': datetime.utcnow() + timedelta(days=365*10),  # Bot tokens don't expire
            'token_type': 'bot',
            'bot_info': bot_info
        }

    def get_bot_info(self) -> Dict[str, Any]:
        """Get bot information"""
        url = f"https://api.telegram.org/bot{self.bot_token}/getMe"

        response = requests.get(url)

        if response.status_code != 200:
            raise Exception(f"Failed to get bot info: {response.text}")

        return response.json()['result']


class TelegramAPIService:
    """Handles Telegram Bot API interactions"""

    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{bot_token}"

    def send_message(self, chat_id: str, text: str) -> Dict[str, Any]:
        """Send a message to a channel/chat"""
        url = f"{self.base_url}/sendMessage"

        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }

        response = requests.post(url, data=data)

        if response.status_code != 200:
            raise Exception(f"Failed to send message: {response.text}")

        return response.json()['result']

    def get_chat_info(self, chat_id: str) -> Dict[str, Any]:
        """Get chat/channel information"""
        url = f"{self.base_url}/getChat"

        params = {'chat_id': chat_id}

        response = requests.get(url, params=params)

        if response.status_code != 200:
            raise Exception(f"Failed to get chat info: {response.text}")

        return response.json()['result']

    def get_chat_members_count(self, chat_id: str) -> int:
        """Get chat members count"""
        url = f"{self.base_url}/getChatMembersCount"

        params = {'chat_id': chat_id}

        response = requests.get(url, params=params)

        if response.status_code != 200:
            raise Exception(f"Failed to get members count: {response.text}")

        return response.json()['result']


class TelegramAutomationService:
    """High-level service for Telegram automation"""

    def __init__(self, bot_token: str):
        self.api = TelegramAPIService(bot_token)
        self.oauth = TelegramOAuthService()

    def get_account_info(self) -> Dict[str, Any]:
        """Get connected bot information"""
        bot_info = self.oauth.get_bot_info()

        return {
            'account_id': str(bot_info['id']),
            'username': bot_info['username'],
            'name': bot_info['first_name'],
            'profile_url': f"https://t.me/{bot_info['username']}",
            'avatar_url': '',  # Bot avatars not easily accessible
            'follower_count': 0,  # Would need channel/chat info
            'following_count': 0,
            'is_bot': True,
            'can_join_groups': bot_info.get('can_join_groups', False),
            'can_read_all_group_messages': bot_info.get('can_read_all_group_messages', False)
        }

    def post_content(self, content: str, campaign_data: Dict = None) -> Dict[str, Any]:
        """Post content to Telegram channel/chat"""
        try:
            # This would need the channel/chat ID to be configured
            # For now, return an error indicating setup needed
            return {
                'success': False,
                'error': 'Telegram channel/chat ID must be configured for posting',
                'platform': 'telegram'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'platform': 'telegram'
            }


def get_telegram_service(bot_token: str = None) -> TelegramAutomationService:
    """Factory function to get Telegram service"""
    if not bot_token:
        raise ValueError("Bot token is required for Telegram API")

    return TelegramAutomationService(bot_token)
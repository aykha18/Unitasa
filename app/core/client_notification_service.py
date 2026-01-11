"""
Client notification service for token and account issues
Sends alerts when social media accounts need attention
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.logging import get_logger
from app.core.email_service import EmailService
from app.models.social_account import SocialAccount
from app.models.user import User

logger = get_logger(__name__)


class ClientNotificationService:
    """Service to notify clients about account issues and token expirations"""

    def __init__(self):
        self.email_service = EmailService()

    async def check_and_notify_clients(self) -> Dict[str, Any]:
        """
        Check for accounts needing attention and notify clients
        Returns summary of notifications sent
        """
        summary = {
            'accounts_checked': 0,
            'notifications_sent': 0,
            'errors': []
        }

        try:
            async for db in get_db():
                # Find accounts that need attention
                accounts_needing_attention = await self._find_accounts_needing_attention(db)
                summary['accounts_checked'] = len(accounts_needing_attention)

                # Group by user to send consolidated notifications
                notifications_by_user = self._group_notifications_by_user(accounts_needing_attention)

                for user_id, notifications in notifications_by_user.items():
                    try:
                        await self._send_user_notification(db, user_id, notifications)
                        summary['notifications_sent'] += 1
                        logger.info(f"Sent notification to user {user_id} about {len(notifications)} accounts")
                    except Exception as e:
                        error_msg = f"Failed to notify user {user_id}: {str(e)}"
                        summary['errors'].append(error_msg)
                        logger.error(error_msg)

        except Exception as e:
            logger.error(f"Client notification service error: {e}")
            summary['errors'].append(f"Service error: {str(e)}")

        return summary

    async def _find_accounts_needing_attention(self, db: AsyncSession) -> List[Dict[str, Any]]:
        """Find social accounts that need client attention"""
        accounts_needing_attention = []

        # Accounts that are inactive (need reconnection)
        result = await db.execute(
            select(SocialAccount, User).join(User).where(
                SocialAccount.is_active == False,
                SocialAccount.last_synced_at >= datetime.utcnow() - timedelta(days=7)  # Recently became inactive
            )
        )

        for account, user in result:
            accounts_needing_attention.append({
                'account': account,
                'user': user,
                'issue_type': 'reconnection_needed',
                'severity': 'high',
                'message': f"Your {account.platform} account (@{account.account_username}) needs to be reconnected."
            })

        # Accounts with refresh tokens that will expire soon (within 7 days)
        warning_time = datetime.utcnow() + timedelta(days=7)
        result = await db.execute(
            select(SocialAccount, User).join(User).where(
                SocialAccount.is_active == True,
                SocialAccount.refresh_token.isnot(None),
                SocialAccount.token_expires_at <= warning_time,
                SocialAccount.token_expires_at > datetime.utcnow()
            )
        )

        for account, user in result:
            days_until_expiry = (account.token_expires_at - datetime.utcnow()).days
            accounts_needing_attention.append({
                'account': account,
                'user': user,
                'issue_type': 'refresh_token_expiring',
                'severity': 'medium',
                'message': f"Your {account.platform} refresh token expires in {days_until_expiry} days. Reconnect soon to avoid interruptions."
            })

        # Accounts with no refresh token (long-term tokens)
        result = await db.execute(
            select(SocialAccount, User).join(User).where(
                SocialAccount.is_active == True,
                SocialAccount.refresh_token.is_(None),
                SocialAccount.token_expires_at <= datetime.utcnow() + timedelta(days=30)
            )
        )

        for account, user in result:
            days_until_expiry = (account.token_expires_at - datetime.utcnow()).days
            accounts_needing_attention.append({
                'account': account,
                'user': user,
                'issue_type': 'token_expiring_no_refresh',
                'severity': 'high',
                'message': f"Your {account.platform} access token expires in {days_until_expiry} days and cannot be automatically renewed."
            })

        return accounts_needing_attention

    def _group_notifications_by_user(self, notifications: List[Dict[str, Any]]) -> Dict[int, List[Dict[str, Any]]]:
        """Group notifications by user ID"""
        grouped = {}

        for notification in notifications:
            user_id = notification['user'].id
            if user_id not in grouped:
                grouped[user_id] = []
            grouped[user_id].append(notification)

        return grouped

    async def _send_user_notification(self, db: AsyncSession, user_id: int, notifications: List[Dict[str, Any]]):
        """Send notification to a specific user"""
        # Get user details
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise Exception(f"User {user_id} not found")

        # Prepare notification content
        subject, html_content, text_content = self._prepare_notification_content(user, notifications)

        # Send email notification
        success, message = self.email_service.send_email(
            to_email=user.email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
        
        if not success:
            logger.error(f"Failed to send email to {user.email}: {message}")
            raise Exception(f"Email delivery failed: {message}")

        # Could also send in-app notifications, SMS, etc.

    def _prepare_notification_content(self, user: User, notifications: List[Dict[str, Any]]) -> tuple[str, str, str]:
        """Prepare notification email content"""
        high_priority = [n for n in notifications if n['severity'] == 'high']
        medium_priority = [n for n in notifications if n['severity'] == 'medium']

        subject = f"Unitasa: {len(high_priority)} account(s) need attention"

        if not high_priority:
            subject = f"Unitasa: Account maintenance reminder"

        # HTML content
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }}
                .content {{ padding: 20px; }}
                .account-issue {{ background: #f8f9fa; border-left: 4px solid #dc3545; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .account-warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .cta-button {{ display: inline-block; background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Unitasa Account Alert</h1>
                    <p>Action needed for your social media accounts</p>
                </div>

                <div class="content">
                    <p>Hello {user.first_name or 'there'},</p>

                    <p>We detected some issues with your connected social media accounts that need your attention:</p>
        """

        # Add high priority issues
        for notification in high_priority:
            html_content += f"""
                    <div class="account-issue">
                        <strong>{notification['account'].platform.title()} Account</strong><br>
                        {notification['message']}
                    </div>
            """

        # Add medium priority issues
        for notification in medium_priority:
            html_content += f"""
                    <div class="account-warning">
                        <strong>{notification['account'].platform.title()} Account</strong><br>
                        {notification['message']}
                    </div>
            """

        html_content += """
                    <p style="margin: 30px 0;">
                        <a href="http://localhost:3001/social" class="cta-button">Manage Your Accounts</a>
                    </p>

                    <p><strong>What happens if I don't take action?</strong></p>
                    <ul>
                        <li>Automated posting will be paused for affected accounts</li>
                        <li>Content will be queued until accounts are reconnected</li>
                        <li>You won't lose any scheduled content</li>
                    </ul>

                    <p>If you have any questions, please don't hesitate to contact our support team.</p>

                    <p>Best regards,<br>The Unitasa Team</p>
                </div>

                <div class="footer">
                    <p>This is an automated message from Unitasa. Please do not reply to this email.</p>
                    <p>© 2025 Unitasa. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Text content for email clients that don't support HTML
        text_content = f"""
        Unitasa Account Alert

        Hello {user.first_name or 'there'},

        We detected some issues with your connected social media accounts:

        """

        for notification in notifications:
            text_content += f"- {notification['message']}\n"

        text_content += """

        Please visit: http://localhost:3001/social to manage your accounts.

        What happens if I don't take action?
        - Automated posting will be paused for affected accounts
        - Content will be queued until accounts are reconnected
        - You won't lose any scheduled content

        Best regards,
        The Unitasa Team
        """

        return subject, html_content, text_content


# Global service instance
client_notification_service = ClientNotificationService()


async def scheduled_client_notifications():
    """Scheduled task to check and notify clients - run daily"""
    while True:
        try:
            logger.info("Starting scheduled client notifications...")
            summary = await client_notification_service.check_and_notify_clients()

            logger.info(f"Client notifications completed: {summary['notifications_sent']} sent, {len(summary['errors'])} errors")

            if summary['errors']:
                logger.warning(f"Notification errors: {summary['errors']}")

        except Exception as e:
            logger.error(f"Scheduled client notifications failed: {e}")

        # Wait 24 hours before next check
        await asyncio.sleep(24 * 60 * 60)


if __name__ == "__main__":
    # For testing the service directly
    async def test_service():
        print("Testing Client Notification Service...")

        # Check and send notifications
        summary = await client_notification_service.check_and_notify_clients()
        print(f"Notification Summary: {summary}")

    asyncio.run(test_service())
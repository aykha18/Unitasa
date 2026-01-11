"""
Payment support service for handling payment-related communications
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime
from app.core.config import get_settings
from app.core.email_service import EmailService

settings = get_settings()


class PaymentSupportService:
    """Service for handling payment support and communications"""
    
    def __init__(self):
        self.support_email = settings.email.support_email
        self.from_email = settings.email.from_email
        self.email_service = EmailService()
    
    async def send_payment_confirmation(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send payment confirmation email to customer"""
        try:
            customer_email = payment_data.get("customer_email")
            customer_name = payment_data.get("customer_name", "Valued Customer")
            amount = payment_data.get("amount")
            currency = payment_data.get("currency", "USD")
            order_id = payment_data.get("order_id")
            
            subject = "Payment Confirmation - Unitasa Co-Creator Program"
            
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #2563eb;">Unitasa</h1>
                        <h2 style="color: #059669;">Payment Confirmed! 🎉</h2>
                    </div>
                    
                    <div style="background: #f8fafc; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                        <h3>Dear {customer_name},</h3>
                        <p>Thank you for joining the Unitasa Co-Creator Program! Your payment has been successfully processed.</p>
                    </div>
                    
                    <div style="background: #fff; border: 1px solid #e5e7eb; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                        <h3 style="margin-top: 0;">Payment Details</h3>
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 8px 0; border-bottom: 1px solid #f3f4f6;"><strong>Order ID:</strong></td>
                                <td style="padding: 8px 0; border-bottom: 1px solid #f3f4f6;">{order_id}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; border-bottom: 1px solid #f3f4f6;"><strong>Amount:</strong></td>
                                <td style="padding: 8px 0; border-bottom: 1px solid #f3f4f6;">{currency} {amount:,.2f}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; border-bottom: 1px solid #f3f4f6;"><strong>Program:</strong></td>
                                <td style="padding: 8px 0; border-bottom: 1px solid #f3f4f6;">Co-Creator Program</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0;"><strong>Date:</strong></td>
                                <td style="padding: 8px 0;">{datetime.now().strftime('%B %d, %Y at %I:%M %p')}</td>
                            </tr>
                        </table>
                    </div>
                    
                    <div style="background: #ecfdf5; border: 1px solid #10b981; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                        <h3 style="color: #059669; margin-top: 0;">What's Next?</h3>
                        <ul style="margin: 0; padding-left: 20px;">
                            <li>Your Co-Creator account is now active</li>
                            <li>You'll receive onboarding instructions shortly</li>
                            <li>Access to exclusive resources and community</li>
                            <li>Direct collaboration opportunities</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px;">
                        <p>Need help? Contact our support team:</p>
                        <p><strong>Email:</strong> <a href="mailto:{self.support_email}">{self.support_email}</a></p>
                        <p style="color: #6b7280; font-size: 14px;">
                            This is an automated confirmation. Please keep this email for your records.
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            result = self.email_service.send_email(
                to_email=customer_email,
                subject=subject,
                html_content=html_content,
                text_content=None
            )
            
            # Unpack tuple if needed, but the original code assigns it to result which is returned.
            # However, the original code returns a dict structure later.
            # Let's check line 98: return { "success": True, ... }
            # Wait, result variable is overwritten or unused?
            # Original code:
            # result = await self.email_service.send_email(...)
            # return { "success": True, ... }
            # The result variable is not used in the return statement shown in the tool output.
            # But line 98 starts `return {`.
            # So I should just call it.
            
            success, message = self.email_service.send_email(
                to_email=customer_email,
                subject=subject,
                html_content=html_content,
                text_content=None
            )
            
            if not success:
                 return {
                     "success": False,
                     "message": f"Payment processed but email failed: {message}"
                 }
            
            return {
                "success": True,
                "message": "Payment confirmation sent successfully",
                "email_sent": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to send payment confirmation: {str(e)}"
            }
    
    async def send_payment_failure_notification(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send payment failure notification to customer"""
        try:
            customer_email = payment_data.get("customer_email")
            customer_name = payment_data.get("customer_name", "Valued Customer")
            order_id = payment_data.get("order_id")
            error_reason = payment_data.get("error_reason", "Payment processing failed")
            
            subject = "Payment Issue - Unitasa Co-Creator Program"
            
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #2563eb;">Unitasa</h1>
                        <h2 style="color: #dc2626;">Payment Issue Detected</h2>
                    </div>
                    
                    <div style="background: #fef2f2; border: 1px solid #fca5a5; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                        <h3 style="color: #dc2626; margin-top: 0;">Dear {customer_name},</h3>
                        <p>We encountered an issue processing your payment for the Unitasa Co-Creator Program.</p>
                        <p><strong>Order ID:</strong> {order_id}</p>
                        <p><strong>Issue:</strong> {error_reason}</p>
                    </div>
                    
                    <div style="background: #f8fafc; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                        <h3>What You Can Do:</h3>
                        <ul>
                            <li>Try the payment again with a different card</li>
                            <li>Check if your card has sufficient funds</li>
                            <li>Ensure your card is enabled for online transactions</li>
                            <li>Contact your bank if the issue persists</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px;">
                        <p><strong>Need immediate assistance?</strong></p>
                        <p>Our support team is here to help:</p>
                        <p><strong>Email:</strong> <a href="mailto:{self.support_email}">{self.support_email}</a></p>
                        <p style="color: #6b7280; font-size: 14px;">
                            We're committed to resolving this quickly for you.
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            result = await self.email_service.send_email(
                to_email=customer_email,
                subject=subject,
                html_content=html_content,
                from_email=self.from_email
            )
            
            return {
                "success": True,
                "message": "Payment failure notification sent successfully",
                "email_sent": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to send payment failure notification: {str(e)}"
            }
    
    async def notify_support_team(self, payment_data: Dict[str, Any], issue_type: str = "payment_issue") -> Dict[str, Any]:
        """Notify support team about payment issues"""
        try:
            customer_email = payment_data.get("customer_email")
            customer_name = payment_data.get("customer_name")
            order_id = payment_data.get("order_id")
            amount = payment_data.get("amount")
            currency = payment_data.get("currency", "USD")
            
            subject = f"Payment Alert: {issue_type.replace('_', ' ').title()} - Order {order_id}"
            
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #dc2626;">Payment Alert - Support Required</h2>
                    
                    <div style="background: #f8fafc; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                        <h3>Issue Details:</h3>
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 8px 0; border-bottom: 1px solid #f3f4f6;"><strong>Issue Type:</strong></td>
                                <td style="padding: 8px 0; border-bottom: 1px solid #f3f4f6;">{issue_type.replace('_', ' ').title()}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; border-bottom: 1px solid #f3f4f6;"><strong>Order ID:</strong></td>
                                <td style="padding: 8px 0; border-bottom: 1px solid #f3f4f6;">{order_id}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; border-bottom: 1px solid #f3f4f6;"><strong>Customer:</strong></td>
                                <td style="padding: 8px 0; border-bottom: 1px solid #f3f4f6;">{customer_name} ({customer_email})</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; border-bottom: 1px solid #f3f4f6;"><strong>Amount:</strong></td>
                                <td style="padding: 8px 0; border-bottom: 1px solid #f3f4f6;">{currency} {amount:,.2f}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0;"><strong>Timestamp:</strong></td>
                                <td style="padding: 8px 0;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</td>
                            </tr>
                        </table>
                    </div>
                    
                    <div style="background: #fef2f2; border: 1px solid #fca5a5; padding: 15px; border-radius: 8px;">
                        <p><strong>Action Required:</strong> Please review this payment issue and contact the customer if necessary.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            result = await self.email_service.send_email(
                to_email=self.support_email,
                subject=subject,
                html_content=html_content,
                from_email=self.from_email
            )
            
            return {
                "success": True,
                "message": "Support team notified successfully",
                "email_sent": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to notify support team: {str(e)}"
            }
    
    async def send_co_creator_welcome_email(self, co_creator_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send welcome email to new co-creator"""
        try:
            customer_email = co_creator_data.get("email")
            customer_name = co_creator_data.get("name", "New Co-Creator")
            
            subject = "Welcome to the Unitasa Co-Creator Program! 🚀"
            
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #2563eb;">Unitasa</h1>
                        <h2 style="color: #059669;">Welcome to the Co-Creator Program! 🎉</h2>
                    </div>
                    
                    <div style="background: #ecfdf5; border: 1px solid #10b981; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                        <h3 style="color: #059669; margin-top: 0;">Dear {customer_name},</h3>
                        <p>Congratulations! You're now officially part of the Unitasa Co-Creator Program. We're excited to have you on this journey with us!</p>
                    </div>
                    
                    <div style="background: #f8fafc; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                        <h3>What's Included in Your Membership:</h3>
                        <ul>
                            <li>🎯 <strong>Exclusive Access:</strong> Early access to new features and tools</li>
                            <li>💰 <strong>Revenue Sharing:</strong> Earn from successful collaborations</li>
                            <li>🤝 <strong>Direct Collaboration:</strong> Work directly with our team</li>
                            <li>📚 <strong>Resources & Training:</strong> Exclusive educational content</li>
                            <li>👥 <strong>Community Access:</strong> Connect with other co-creators</li>
                            <li>🔧 <strong>Priority Support:</strong> Fast-track support for your needs</li>
                        </ul>
                    </div>
                    
                    <div style="background: #dbeafe; border: 1px solid #3b82f6; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                        <h3 style="color: #1d4ed8; margin-top: 0;">Next Steps:</h3>
                        <ol>
                            <li>Check your email for onboarding instructions</li>
                            <li>Join our exclusive Co-Creator community</li>
                            <li>Schedule your welcome call with our team</li>
                            <li>Start exploring collaboration opportunities</li>
                        </ol>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px;">
                        <p><strong>Questions or need assistance?</strong></p>
                        <p>Our dedicated support team is here for you:</p>
                        <p><strong>Email:</strong> <a href="mailto:{self.support_email}">{self.support_email}</a></p>
                        <p style="color: #6b7280; font-size: 14px;">
                            Welcome aboard! Let's build something amazing together. 🚀
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            result = await self.email_service.send_email(
                to_email=customer_email,
                subject=subject,
                html_content=html_content,
                from_email=self.from_email
            )
            
            return {
                "success": True,
                "message": "Welcome email sent successfully",
                "email_sent": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to send welcome email: {str(e)}"
            }


# Global instance
_payment_support_service = None

def get_payment_support_service() -> PaymentSupportService:
    """Get the global payment support service instance"""
    global _payment_support_service
    if _payment_support_service is None:
        _payment_support_service = PaymentSupportService()
    return _payment_support_service
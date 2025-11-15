"""
Email Service for Co-Creator Program
Handles payment receipts, welcome emails, and notifications
"""

import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional, Tuple
from jinja2 import Template

from app.models.payment_transaction import PaymentTransaction
from app.models.co_creator_program import CoCreator
from app.core.config import get_settings

settings = get_settings()


class EmailService:
    """Service for sending co-creator program emails"""

    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", "support@unitasa.in")
        self.from_name = os.getenv("FROM_NAME", "Unitasa")
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str = None
    ) -> Tuple[bool, str]:
        """Send an email"""
        try:
            if not self.smtp_username or not self.smtp_password:
                return False, "SMTP credentials not configured"
            
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email
            
            # Add text content
            if text_content:
                text_part = MIMEText(text_content, "plain")
                msg.attach(text_part)
            
            # Add HTML content
            html_part = MIMEText(html_content, "html")
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            return True, "Email sent successfully"
            
        except Exception as e:
            return False, f"Failed to send email: {str(e)}"
    
    def send_payment_receipt(
        self,
        transaction: PaymentTransaction,
        co_creator: CoCreator
    ) -> Tuple[bool, str]:
        """Send payment receipt email"""
        try:
            if not transaction.receipt_email:
                return False, "No receipt email provided"
            
            # Prepare template data
            template_data = {
                "transaction": transaction,
                "co_creator": co_creator,
                "program": co_creator.program,
                "amount": f"${transaction.amount:.2f}",
                "currency": transaction.currency,
                "seat_number": co_creator.seat_number,
                "payment_date": transaction.processed_at.strftime("%B %d, %Y") if transaction.processed_at else "N/A",
                "transaction_id": transaction.stripe_payment_intent_id,
                "app_name": settings.app_name
            }
            
            # HTML template
            html_template = Template("""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Payment Receipt - {{ app_name }}</title>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background: #2563eb; color: white; padding: 20px; text-align: center; }
                    .content { padding: 20px; background: #f9fafb; }
                    .receipt-details { background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }
                    .amount { font-size: 24px; font-weight: bold; color: #059669; }
                    .footer { text-align: center; padding: 20px; color: #6b7280; }
                    .button { display: inline-block; background: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Payment Receipt</h1>
                        <p>{{ app_name }} Co-Creator Program</p>
                    </div>
                    
                    <div class="content">
                        <h2>Thank you for your payment!</h2>
                        <p>Your payment has been successfully processed and your co-creator seat has been activated.</p>
                        
                        <div class="receipt-details">
                            <h3>Payment Details</h3>
                            <p><strong>Amount:</strong> <span class="amount">{{ amount }} {{ currency }}</span></p>
                            <p><strong>Payment Date:</strong> {{ payment_date }}</p>
                            <p><strong>Transaction ID:</strong> {{ transaction_id }}</p>
                            <p><strong>Co-Creator Seat:</strong> #{{ seat_number }}</p>
                            <p><strong>Program:</strong> {{ program.program_name }}</p>
                        </div>
                        
                        <h3>What's Next?</h3>
                        <ul>
                            <li>You now have lifetime access to the Unitasa platform</li>
                            <li>Priority integration support for your CRM setup</li>
                            <li>Direct access to founder calls and feature discussions</li>
                            <li>Exclusive co-creator badge and recognition</li>
                            <li>Early access to new features and integrations</li>
                        </ul>
                        
                        <p style="text-align: center; margin: 30px 0;">
                            <a href="https://app.automark.ai/co-creator" class="button">Access Your Co-Creator Dashboard</a>
                        </p>
                    </div>
                    
                    <div class="footer">
                        <p>Questions? Reply to this email or contact support@automark.ai</p>
                        <p>{{ app_name }} - AI Marketing Automation Platform</p>
                    </div>
                </div>
            </body>
            </html>
            """)
            
            # Text template
            text_template = Template("""
            Payment Receipt - {{ app_name }}
            
            Thank you for your payment!
            
            Your payment has been successfully processed and your co-creator seat has been activated.
            
            Payment Details:
            - Amount: {{ amount }} {{ currency }}
            - Payment Date: {{ payment_date }}
            - Transaction ID: {{ transaction_id }}
            - Co-Creator Seat: #{{ seat_number }}
            - Program: {{ program.program_name }}
            
            What's Next?
            - You now have lifetime access to the Unitasa platform
            - Priority integration support for your CRM setup
            - Direct access to founder calls and feature discussions
            - Exclusive co-creator badge and recognition
            - Early access to new features and integrations
            
            Access your co-creator dashboard: https://app.automark.ai/co-creator
            
            Questions? Reply to this email or contact support@automark.ai
            
            {{ app_name }} - AI Marketing Automation Platform
            """)
            
            html_content = html_template.render(**template_data)
            text_content = text_template.render(**template_data)
            
            subject = f"Payment Receipt - Co-Creator Seat #{co_creator.seat_number}"
            
            return self.send_email(
                to_email=transaction.receipt_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
        except Exception as e:
            return False, f"Failed to send payment receipt: {str(e)}"
    
    def send_welcome_email(
        self,
        co_creator: CoCreator,
        email: str
    ) -> Tuple[bool, str]:
        """Send welcome email to new co-creator"""
        try:
            # Prepare template data
            template_data = {
                "co_creator": co_creator,
                "program": co_creator.program,
                "seat_number": co_creator.seat_number,
                "app_name": settings.app_name,
                "user_name": co_creator.user.full_name if co_creator.user else "Co-Creator"
            }
            
            # HTML template
            html_template = Template("""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Welcome to the Co-Creator Program!</title>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background: #059669; color: white; padding: 20px; text-align: center; }
                    .content { padding: 20px; background: #f9fafb; }
                    .welcome-box { background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #059669; }
                    .benefits { background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }
                    .footer { text-align: center; padding: 20px; color: #6b7280; }
                    .button { display: inline-block; background: #059669; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px; }
                    .seat-badge { background: #fbbf24; color: #92400e; padding: 8px 16px; border-radius: 20px; font-weight: bold; display: inline-block; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎉 Welcome to the Co-Creator Program!</h1>
                        <p>{{ app_name }} Founding Users</p>
                    </div>
                    
                    <div class="content">
                        <div class="welcome-box">
                            <h2>Welcome, {{ user_name }}!</h2>
                            <p>Congratulations! You're now officially a <span class="seat-badge">Co-Creator #{{ seat_number }}</span> in the Unitasa founding users program.</p>
                            <p>You're part of an exclusive group of 25 visionaries who are helping shape the future of AI marketing automation.</p>
                        </div>
                        
                        <div class="benefits">
                            <h3>Your Co-Creator Benefits</h3>
                            <ul>
                                <li><strong>Lifetime Platform Access</strong> - Never lose access, regardless of future pricing</li>
                                <li><strong>Priority Integration Support</strong> - White-glove assistance with your CRM setup</li>
                                <li><strong>Direct Founder Access</strong> - Monthly calls and direct communication</li>
                                <li><strong>Feature Influence</strong> - Vote on new features and suggest improvements</li>
                                <li><strong>Exclusive Badge</strong> - Recognition as a founding supporter</li>
                                <li><strong>Early Access</strong> - First to try new integrations and AI capabilities</li>
                            </ul>
                        </div>
                        
                        <h3>Next Steps</h3>
                        <ol>
                            <li>Access your co-creator dashboard</li>
                            <li>Complete your CRM integration setup</li>
                            <li>Join our exclusive Slack community</li>
                            <li>Schedule your welcome call with the founder</li>
                        </ol>
                        
                        <p style="text-align: center; margin: 30px 0;">
                            <a href="https://app.automark.ai/co-creator" class="button">Access Dashboard</a>
                            <a href="https://calendly.com/automark-founder" class="button">Schedule Welcome Call</a>
                        </p>
                    </div>
                    
                    <div class="footer">
                        <p>Thank you for believing in our vision and supporting the future of AI marketing automation!</p>
                        <p>Questions? Reply to this email or reach out directly to founder@automark.ai</p>
                        <p>{{ app_name }} - AI Marketing Automation Platform</p>
                    </div>
                </div>
            </body>
            </html>
            """)
            
            # Text template
            text_template = Template("""
            Welcome to the Co-Creator Program!
            
            {{ app_name }} Founding Users
            
            Welcome, {{ user_name }}!
            
            Congratulations! You're now officially Co-Creator #{{ seat_number }} in the Unitasa founding users program.
            
            You're part of an exclusive group of 25 visionaries who are helping shape the future of AI marketing automation.
            
            Your Co-Creator Benefits:
            - Lifetime Platform Access - Never lose access, regardless of future pricing
            - Priority Integration Support - White-glove assistance with your CRM setup
            - Direct Founder Access - Monthly calls and direct communication
            - Feature Influence - Vote on new features and suggest improvements
            - Exclusive Badge - Recognition as a founding supporter
            - Early Access - First to try new integrations and AI capabilities
            
            Next Steps:
            1. Access your co-creator dashboard: https://app.automark.ai/co-creator
            2. Complete your CRM integration setup
            3. Join our exclusive Slack community
            4. Schedule your welcome call: https://calendly.com/automark-founder
            
            Thank you for believing in our vision and supporting the future of AI marketing automation!
            
            Questions? Reply to this email or reach out directly to founder@automark.ai
            
            {{ app_name }} - AI Marketing Automation Platform
            """)
            
            html_content = html_template.render(**template_data)
            text_content = text_template.render(**template_data)
            
            subject = f"🎉 Welcome to Co-Creator Program - Seat #{co_creator.seat_number}!"
            
            return self.send_email(
                to_email=email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
        except Exception as e:
            return False, f"Failed to send welcome email: {str(e)}"
    
    def send_payment_failed_notification(
        self,
        email: str,
        co_creator: CoCreator,
        failure_reason: str = None
    ) -> Tuple[bool, str]:
        """Send payment failure notification"""
        try:
            template_data = {
                "co_creator": co_creator,
                "program": co_creator.program,
                "seat_number": co_creator.seat_number,
                "failure_reason": failure_reason or "Payment processing failed",
                "app_name": settings.app_name
            }
            
            html_template = Template("""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Payment Issue - Co-Creator Program</title>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background: #dc2626; color: white; padding: 20px; text-align: center; }
                    .content { padding: 20px; background: #f9fafb; }
                    .alert-box { background: #fef2f2; border: 1px solid #fecaca; padding: 20px; border-radius: 8px; margin: 20px 0; }
                    .footer { text-align: center; padding: 20px; color: #6b7280; }
                    .button { display: inline-block; background: #dc2626; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Payment Issue</h1>
                        <p>{{ app_name }} Co-Creator Program</p>
                    </div>
                    
                    <div class="content">
                        <div class="alert-box">
                            <h2>Payment Processing Issue</h2>
                            <p>We encountered an issue processing your payment for Co-Creator Seat #{{ seat_number }}.</p>
                            <p><strong>Issue:</strong> {{ failure_reason }}</p>
                        </div>
                        
                        <h3>What happens now?</h3>
                        <ul>
                            <li>Your seat reservation has been temporarily held</li>
                            <li>You have 24 hours to retry your payment</li>
                            <li>No charges have been made to your account</li>
                            <li>Your seat will be released if payment isn't completed</li>
                        </ul>
                        
                        <p style="text-align: center; margin: 30px 0;">
                            <a href="https://app.automark.ai/co-creator/payment" class="button">Retry Payment</a>
                        </p>
                    </div>
                    
                    <div class="footer">
                        <p>Need help? Contact support@automark.ai or reply to this email</p>
                        <p>{{ app_name }} - AI Marketing Automation Platform</p>
                    </div>
                </div>
            </body>
            </html>
            """)
            
            html_content = html_template.render(**template_data)
            subject = f"Payment Issue - Co-Creator Seat #{co_creator.seat_number}"
            
            return self.send_email(
                to_email=email,
                subject=subject,
                html_content=html_content
            )
            
        except Exception as e:
            return False, f"Failed to send payment failed notification: {str(e)}"

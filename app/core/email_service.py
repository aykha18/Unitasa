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
        # Default to Hostinger SMTP settings
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.hostinger.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "support@unitasa.in")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "Miral@18")
        self.from_email = os.getenv("FROM_EMAIL", "support@unitasa.in")
        self.from_name = os.getenv("FROM_NAME", "Unitasa")

        print(f"[EMAIL_SERVICE] Initialized with server: {self.smtp_server}, port: {self.smtp_port}")
        print(f"[EMAIL_SERVICE] From: {self.from_name} <{self.from_email}>")
    
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
            try:
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.smtp_username, self.smtp_password)
                    server.send_message(msg)
            except OSError as e:
                 print(f"[EMAIL_SERVICE] Network error sending email: {e}")
                 if "Network is unreachable" in str(e) or "[Errno 101]" in str(e):
                     return False, f"Network unreachable. Please check server connectivity and firewall settings for port {self.smtp_port}."
                 raise e
            
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
                        <h1>Welcome to the Co-Creator Program!</h1>
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
            
            subject = f"Welcome to Co-Creator Program - Seat #{co_creator.seat_number}!"
            
            return self.send_email(
                to_email=email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
        except Exception as e:
            return False, f"Failed to send welcome email: {str(e)}"
    
    def send_free_trial_welcome_email(
        self,
        user,
        verification_token: str = None
    ) -> Tuple[bool, str]:
        """Send welcome email to new free trial user"""
        try:
            # Prepare template data
            template_data = {
                "user": user,
                "user_name": user.first_name or "there",
                "trial_days": 15,
                "trial_end_date": user.trial_end_date.strftime("%B %d, %Y") if user.trial_end_date else "N/A",
                "verification_token": verification_token,
                "verification_url": f"https://app.unitasa.in/verify-email?token={verification_token}" if verification_token else None,
                "app_name": settings.app_name
            }
            
            # HTML template
            html_template = Template("""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Welcome to Your Free Trial!</title>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background: #2563eb; color: white; padding: 20px; text-align: center; }
                    .content { padding: 20px; background: #f9fafb; }
                    .welcome-box { background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #10b981; }
                    .trial-info { background: #ecfdf5; border: 1px solid #d1fae5; padding: 20px; border-radius: 8px; margin: 20px 0; }
                    .footer { text-align: center; padding: 20px; color: #6b7280; }
                    .button { display: inline-block; background: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px; }
                    .verify-button { background: #10b981; }
                    .trial-badge { background: #10b981; color: white; padding: 8px 16px; border-radius: 20px; font-weight: bold; display: inline-block; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Welcome to {{ app_name }}!</h1>
                        <p>Your 15-Day Free Trial Starts Now</p>
                    </div>
                    
                    <div class="content">
                        <div class="welcome-box">
                            <h2>Hi {{ user_name }}!</h2>
                            <p>Welcome to Unitasa! Your <span class="trial-badge">15-Day Free Trial</span> has been activated and you now have full access to our AI marketing automation platform.</p>
                        </div>
                        
                        {% if verification_token %}
                        <div style="background: #fef3c7; border: 1px solid #f59e0b; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <h3 style="color: #92400e; margin-top: 0;">Please Verify Your Email</h3>
                            <p style="color: #92400e;">To ensure you receive important updates and don't lose access to your account, please verify your email address:</p>
                            <p style="text-align: center; margin: 20px 0;">
                                <a href="{{ verification_url }}" class="button verify-button">Verify Email Address</a>
                            </p>
                        </div>
                        {% endif %}
                        
                        <div class="trial-info">
                            <h3 style="color: #065f46; margin-top: 0;">What You Get During Your Trial</h3>
                            <ul style="color: #065f46;">
                                <li><strong>Full Platform Access</strong> - All features unlocked for 15 days</li>
                                <li><strong>AI Content Generation</strong> - Create engaging social media posts</li>
                                <li><strong>CRM Integration</strong> - Connect with HubSpot, Salesforce, and more</li>
                                <li><strong>Analytics Dashboard</strong> - Track your marketing performance</li>
                                <li><strong>Email Support</strong> - Get help when you need it</li>
                            </ul>
                            <p style="color: #065f46;"><strong>Trial ends:</strong> {{ trial_end_date }}</p>
                        </div>
                        
                        <h3>Get Started in 3 Easy Steps</h3>
                        <ol>
                            <li><strong>Complete Your Profile</strong> - Add your company details and preferences</li>
                            <li><strong>Connect Your CRM</strong> - Integrate with your existing tools</li>
                            <li><strong>Create Your First Campaign</strong> - Use AI to generate your first marketing content</li>
                        </ol>
                        
                        <p style="text-align: center; margin: 30px 0;">
                            <a href="https://app.unitasa.in/dashboard" class="button">Access Your Dashboard</a>
                            <a href="https://app.unitasa.in/onboarding" class="button">Start Setup Guide</a>
                        </p>
                        
                        <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <h3>Need Help Getting Started?</h3>
                            <p>Our team is here to help you succeed:</p>
                            <ul>
                                <li><a href="https://docs.unitasa.in">Browse our documentation</a></li>
                                <li><a href="mailto:support@unitasa.in">Email our support team</a></li>
                                <li><a href="https://unitasa.in/tutorials">Watch video tutorials</a></li>
                            </ul>
                        </div>
                    </div>
                    
                    <div class="footer">
                        <p>Ready to supercharge your marketing with AI? We're excited to have you on board!</p>
                        <p>Questions? Reply to this email or contact support@unitasa.in</p>
                        <p>{{ app_name }} - AI Marketing Automation Platform</p>
                    </div>
                </div>
            </body>
            </html>
            """)
            
            # Text template
            text_template = Template("""
            Welcome to {{ app_name }}!
            
            Your 15-Day Free Trial Starts Now
            
            Hi {{ user_name }}!
            
            Welcome to Unitasa! Your 15-Day Free Trial has been activated and you now have full access to our AI marketing automation platform.
            
            {% if verification_token %}
            IMPORTANT: Please verify your email address
            Click here to verify: {{ verification_url }}
            {% endif %}
            
            What You Get During Your Trial:
            - Full Platform Access - All features unlocked for 15 days
            - AI Content Generation - Create engaging social media posts
            - CRM Integration - Connect with HubSpot, Salesforce, and more
            - Analytics Dashboard - Track your marketing performance
            - Email Support - Get help when you need it
            
            Trial ends: {{ trial_end_date }}
            
            Get Started in 3 Easy Steps:
            1. Complete Your Profile - Add your company details and preferences
            2. Connect Your CRM - Integrate with your existing tools
            3. Create Your First Campaign - Use AI to generate your first marketing content
            
            Access your dashboard: https://app.unitasa.in/dashboard
            Start setup guide: https://app.unitasa.in/onboarding
            
            Need Help Getting Started?
            - Browse our documentation: https://docs.unitasa.in
            - Email our support team: support@unitasa.in
            - Watch video tutorials: https://unitasa.in/tutorials
            
            Ready to supercharge your marketing with AI? We're excited to have you on board!
            
            Questions? Reply to this email or contact support@unitasa.in
            
            {{ app_name }} - AI Marketing Automation Platform
            """)
            
            html_content = html_template.render(**template_data)
            text_content = text_template.render(**template_data)
            
            subject = f"Welcome to {settings.app_name} - Your Free Trial is Active!"
            
            return self.send_email(
                to_email=user.email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
        except Exception as e:
            return False, f"Failed to send welcome email: {str(e)}"

    def send_email_verification(
        self,
        user,
        verification_token: str
    ) -> Tuple[bool, str]:
        """Send email verification email"""
        try:
            template_data = {
                "user": user,
                "user_name": user.first_name or "there",
                "verification_token": verification_token,
                "verification_url": f"https://app.unitasa.in/verify-email?token={verification_token}",
                "app_name": settings.app_name
            }
            
            html_template = Template("""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Verify Your Email Address</title>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background: #2563eb; color: white; padding: 20px; text-align: center; }
                    .content { padding: 20px; background: #f9fafb; }
                    .verify-box { background: white; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center; }
                    .footer { text-align: center; padding: 20px; color: #6b7280; }
                    .button { display: inline-block; background: #10b981; color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; font-weight: bold; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Verify Your Email</h1>
                        <p>{{ app_name }}</p>
                    </div>
                    
                    <div class="content">
                        <div class="verify-box">
                            <h2>Hi {{ user_name }}!</h2>
                            <p>Thanks for signing up for {{ app_name }}! To complete your registration and secure your account, please verify your email address.</p>
                            
                            <p style="margin: 30px 0;">
                                <a href="{{ verification_url }}" class="button">Verify Email Address</a>
                            </p>
                            
                            <p style="font-size: 14px; color: #6b7280;">
                                If the button doesn't work, copy and paste this link into your browser:<br>
                                <a href="{{ verification_url }}">{{ verification_url }}</a>
                            </p>
                            
                            <p style="font-size: 14px; color: #6b7280; margin-top: 20px;">
                                This verification link will expire in 24 hours for security reasons.
                            </p>
                        </div>
                    </div>
                    
                    <div class="footer">
                        <p>If you didn't create an account with {{ app_name }}, you can safely ignore this email.</p>
                        <p>Questions? Contact support@unitasa.in</p>
                    </div>
                </div>
            </body>
            </html>
            """)
            
            html_content = html_template.render(**template_data)
            subject = f"Verify your email address - {settings.app_name}"
            
            return self.send_email(
                to_email=user.email,
                subject=subject,
                html_content=html_content
            )
            
        except Exception as e:
            return False, f"Failed to send verification email: {str(e)}"

    def send_password_reset_email(
        self,
        user,
        reset_token: str
    ) -> Tuple[bool, str]:
        """Send password reset email"""
        try:
            template_data = {
                "user": user,
                "user_name": user.first_name or "there",
                "reset_token": reset_token,
                "reset_url": f"https://app.unitasa.in/reset-password?token={reset_token}",
                "app_name": settings.app_name
            }
            
            html_template = Template("""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Reset Your Password</title>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background: #dc2626; color: white; padding: 20px; text-align: center; }
                    .content { padding: 20px; background: #f9fafb; }
                    .reset-box { background: white; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center; }
                    .footer { text-align: center; padding: 20px; color: #6b7280; }
                    .button { display: inline-block; background: #dc2626; color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; font-weight: bold; }
                    .warning { background: #fef2f2; border: 1px solid #fecaca; padding: 15px; border-radius: 6px; margin: 20px 0; color: #991b1b; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Reset Your Password</h1>
                        <p>{{ app_name }}</p>
                    </div>
                    
                    <div class="content">
                        <div class="reset-box">
                            <h2>Hi {{ user_name }}!</h2>
                            <p>We received a request to reset your password for your {{ app_name }} account.</p>
                            
                            <p style="margin: 30px 0;">
                                <a href="{{ reset_url }}" class="button">Reset My Password</a>
                            </p>
                            
                            <p style="font-size: 14px; color: #6b7280;">
                                If the button doesn't work, copy and paste this link into your browser:<br>
                                <a href="{{ reset_url }}">{{ reset_url }}</a>
                            </p>
                        </div>
                        
                        <div class="warning">
                            <strong>Security Notice:</strong>
                            <ul style="margin: 10px 0; text-align: left;">
                                <li>This reset link will expire in 24 hours</li>
                                <li>If you didn't request this reset, please ignore this email</li>
                                <li>Your password will remain unchanged until you create a new one</li>
                            </ul>
                        </div>
                    </div>
                    
                    <div class="footer">
                        <p>If you didn't request a password reset, you can safely ignore this email.</p>
                        <p>Questions? Contact support@unitasa.in</p>
                        <p>{{ app_name }} - AI Marketing Automation Platform</p>
                    </div>
                </div>
            </body>
            </html>
            """)
            
            html_content = html_template.render(**template_data)
            subject = f"Reset your password - {settings.app_name}"
            
            return self.send_email(
                to_email=user.email,
                subject=subject,
                html_content=html_content
            )
            
        except Exception as e:
            return False, f"Failed to send password reset email: {str(e)}"

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

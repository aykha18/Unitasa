#!/usr/bin/env python3
"""
Test email functionality locally
"""

import asyncio
import os
from app.core.email_service import EmailService

async def test_email():
    """Test email sending functionality"""

    # Set test environment variables
    os.environ["SMTP_SERVER"] = "smtp.hostinger.com"
    os.environ["SMTP_PORT"] = "587"
    os.environ["SMTP_USERNAME"] = "support@unitasa.in"
    os.environ["SMTP_PASSWORD"] = "Miral@18"
    os.environ["FROM_EMAIL"] = "support@unitasa.in"
    os.environ["FROM_NAME"] = "Unitasa"

    print("Testing email configuration...")
    print("=" * 50)

    # Initialize email service
    email_service = EmailService()

    # Test sending a simple email
    success, message = email_service.send_email(
        to_email="khanayub25@outlook.com",  # Replace with your test email
        subject="Test Email from Unitasa",
        html_content="<h1>Test Email</h1><p>This is a test email from Unitasa.</p>",
        text_content="Test Email\nThis is a test email from Unitasa."
    )

    if success:
        print("Email sent successfully!")
        print(f"Message: {message}")
    else:
        print("❌ Email failed!")
        print(f"Error: {message}")

if __name__ == "__main__":
    asyncio.run(test_email())
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
import logging
from datetime import datetime
from app.core.email_service import EmailService
from app.models.lead import Lead
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

router = APIRouter()
logger = logging.getLogger(__name__)

class ConsultationBookingRequest(BaseModel):
    name: str
    email: EmailStr
    company: Optional[str] = None
    phone: Optional[str] = None
    preferred_time: Optional[str] = None
    timezone: str = "UTC"
    challenges: str
    current_crm: Optional[str] = None
    source: str = "ai_assessment"
    consultation_type: str = "ai_strategy_session"

class ConsultationBookingResponse(BaseModel):
    success: bool
    message: str
    booking_id: Optional[str] = None
    calendly_url: Optional[str] = None

@router.post("/book", response_model=ConsultationBookingResponse)
async def book_consultation(
    booking_request: ConsultationBookingRequest
):
    """
    Handle consultation booking requests from prospects
    """
    try:
        logger.info(f"📅 New consultation booking request from {booking_request.email}")
        
        # For now, just log the booking request and return success
        # Database integration will be added later
        logger.info(f"Consultation booking details:")
        logger.info(f"  Name: {booking_request.name}")
        logger.info(f"  Email: {booking_request.email}")
        logger.info(f"  Company: {booking_request.company}")
        logger.info(f"  Phone: {booking_request.phone}")
        logger.info(f"  CRM: {booking_request.current_crm}")
        logger.info(f"  Challenges: {booking_request.challenges}")
        
        # Generate a booking ID
        booking_id = f"booking_{int(datetime.utcnow().timestamp())}"
        
        logger.info(f"✅ Consultation booking processed successfully for {booking_request.email}")
        
        return ConsultationBookingResponse(
            success=True,
            message="Consultation booking request received successfully",
            booking_id=booking_id,
            calendly_url="https://calendly.com/khanayubchand/ai-strategy-session"
        )
        
    except Exception as e:
        logger.error(f"❌ Error processing consultation booking: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process consultation booking request"
        )

async def send_consultation_confirmation_email(booking_request: ConsultationBookingRequest):
    """Send confirmation email to the prospect"""
    try:
        email_service = EmailService()
        
        subject = "🎯 Your AI Strategy Session is Almost Booked!"
        
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; color: white;">
                <h1 style="margin: 0; font-size: 28px;">AI Strategy Session</h1>
                <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">Unitasa AI Marketing Platform</p>
            </div>
            
            <div style="padding: 30px; background: #f8f9fa;">
                <h2 style="color: #333; margin-bottom: 20px;">Hi {booking_request.name}! 👋</h2>
                
                <p style="color: #666; line-height: 1.6; margin-bottom: 20px;">
                    Thank you for your interest in scheduling an AI Strategy Session with Unitasa! 
                    We're excited to help you transform your marketing with AI automation.
                </p>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #667eea;">
                    <h3 style="color: #333; margin-top: 0;">What We Received:</h3>
                    <p><strong>Company:</strong> {booking_request.company or 'Not specified'}</p>
                    <p><strong>Current CRM:</strong> {booking_request.current_crm or 'Not specified'}</p>
                    <p><strong>Challenges:</strong> {booking_request.challenges}</p>
                </div>
                
                <div style="background: #e3f2fd; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #1976d2; margin-top: 0;">Next Steps:</h3>
                    <ol style="color: #666; line-height: 1.6;">
                        <li>Click the calendar link in your booking confirmation</li>
                        <li>Choose your preferred time slot</li>
                        <li>Add the meeting to your calendar</li>
                        <li>We'll send you a preparation guide 24 hours before</li>
                    </ol>
                </div>
                
                <div style="background: #f3e5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #7b1fa2; margin-top: 0;">What to Expect in Your Session:</h3>
                    <ul style="color: #666; line-height: 1.6;">
                        <li>🎯 Personalized AI marketing strategy for your business</li>
                        <li>🔗 CRM integration roadmap and recommendations</li>
                        <li>⚡ Automation opportunities assessment</li>
                        <li>📅 Implementation timeline and next steps</li>
                        <li>❓ Q&A about Unitasa platform capabilities</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://calendly.com/unitasa/ai-strategy-session" 
                       style="background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">
                        📅 Complete Your Booking
                    </a>
                </div>
                
                <p style="color: #666; line-height: 1.6; margin-top: 30px;">
                    Questions before our call? Reply to this email or reach out at 
                    <a href="mailto:hello@unitasa.in" style="color: #667eea;">hello@unitasa.in</a>
                </p>
                
                <p style="color: #666; line-height: 1.6;">
                    Looking forward to our conversation!<br>
                    <strong>The Unitasa Team</strong>
                </p>
            </div>
            
            <div style="background: #333; color: white; padding: 20px; text-align: center; font-size: 14px;">
                <p style="margin: 0;">Unitasa AI Marketing Platform | Automate. Scale. Succeed.</p>
                <p style="margin: 5px 0 0 0; opacity: 0.7;">www.unitasa.in</p>
            </div>
        </div>
        """
        
        email_service.send_email(
            to_email=booking_request.email,
            subject=subject,
            html_content=html_content
        )
        
        logger.info(f"✅ Confirmation email sent to {booking_request.email}")
        
    except Exception as e:
        logger.error(f"❌ Failed to send confirmation email: {str(e)}")

async def send_team_notification_email(booking_request: ConsultationBookingRequest, lead_id: int):
    """Send notification to the team about new consultation request"""
    try:
        email_service = EmailService()
        
        subject = f"🔥 New AI Strategy Session Request - {booking_request.name}"
        
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #f44336; padding: 20px; text-align: center; color: white;">
                <h1 style="margin: 0;">🔥 New Consultation Request</h1>
            </div>
            
            <div style="padding: 20px; background: #f8f9fa;">
                <h2 style="color: #333;">Lead Details:</h2>
                
                <div style="background: white; padding: 15px; border-radius: 8px; margin: 10px 0;">
                    <p><strong>Name:</strong> {booking_request.name}</p>
                    <p><strong>Email:</strong> {booking_request.email}</p>
                    <p><strong>Company:</strong> {booking_request.company or 'Not specified'}</p>
                    <p><strong>Phone:</strong> {booking_request.phone or 'Not provided'}</p>
                    <p><strong>Current CRM:</strong> {booking_request.current_crm or 'Not specified'}</p>
                    <p><strong>Source:</strong> {booking_request.source}</p>
                    <p><strong>Lead ID:</strong> {lead_id}</p>
                </div>
                
                <div style="background: #fff3e0; padding: 15px; border-radius: 8px; margin: 10px 0;">
                    <h3 style="color: #f57c00; margin-top: 0;">Challenges/Goals:</h3>
                    <p style="color: #666;">{booking_request.challenges}</p>
                </div>
                
                <div style="text-align: center; margin: 20px 0;">
                    <a href="https://calendly.com/unitasa/ai-strategy-session" 
                       style="background: #4caf50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; margin: 5px;">
                        View Calendar
                    </a>
                    <a href="mailto:{booking_request.email}" 
                       style="background: #2196f3; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; margin: 5px;">
                        Email Lead
                    </a>
                </div>
                
                <p style="color: #666; font-size: 14px;">
                    <strong>Action Required:</strong> Follow up within 2 hours for best conversion rates.
                </p>
            </div>
        </div>
        """
        
        # Send to team email
        email_service.send_email(
            to_email="hello@unitasa.in",  # Replace with your team email
            subject=subject,
            html_content=html_content
        )
        
        logger.info(f"✅ Team notification sent for consultation request from {booking_request.email}")
        
    except Exception as e:
        logger.error(f"❌ Failed to send team notification: {str(e)}")

@router.get("/status")
async def get_consultation_status():
    """Get consultation booking system status"""
    return {
        "status": "active",
        "calendly_url": "https://calendly.com/unitasa/ai-strategy-session",
        "available_slots": "Monday-Friday, 9 AM - 6 PM EST"
    }
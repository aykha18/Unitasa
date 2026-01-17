"""
Razorpay payment API endpoints for Co-Creator Program
"""

from typing import Dict, Any, Optional
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.razorpay_service import get_razorpay_service
from app.core.payment_support_service import get_payment_support_service
from app.core.jwt_handler import JWTHandler, get_password_hash
from app.models.payment_transaction import PaymentTransaction
from app.models.co_creator_program import CoCreator
from app.models.lead import Lead
from app.models.user import User

router = APIRouter()
security = HTTPBearer(auto_error=False)

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, otherwise None"""
    if not credentials:
        return None
    try:
        user_info = JWTHandler.get_user_from_token(credentials.credentials)
        result = await db.execute(select(User).where(User.id == user_info["user_id"]))
        return result.scalar_one_or_none()
    except Exception:
        return None

class PaymentOrderRequest(BaseModel):
    amount: float = 1.05  # Default Co-Creator Program amount in USD (approx 87 INR for testing)
    customer_email: EmailStr
    customer_name: str
    lead_id: Optional[int] = None
    program_type: str = "co_creator"
    currency: str = "USD"  # USD for international, INR for India
    customer_country: str = "US"  # Country code for currency determination

class PaymentVerificationRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

@router.post("/create-order")
async def create_razorpay_order(
    request: PaymentOrderRequest,
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """Create a Razorpay order for Co-Creator Program"""
    try:
        razorpay_service = get_razorpay_service(db_session=db)
        
        # Create Razorpay order
        success, message, order_data = await razorpay_service.create_co_creator_payment(
            co_creator_id=user.id if user else 0,  # Use user ID if available, or 0 (temp)
            customer_email=request.customer_email,
            customer_name=request.customer_name,
            amount=request.amount,
            currency=request.currency,
            customer_country=request.customer_country
        )
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        # Create payment transaction record
        payment_transaction = PaymentTransaction(
            razorpay_order_id=order_data["order_id"],
            lead_id=request.lead_id,
            user_id=user.id if user else None,
            amount=order_data["amount_usd"],
            currency="USD",
            payment_method="razorpay",
            status="created",
            customer_email=request.customer_email,
            customer_name=request.customer_name,
            customer_country=request.customer_country,
            program_type=request.program_type,
            description=f"Unitasa {request.program_type.replace('_', ' ').title()} Program",
            payment_metadata={
                "program_type": request.program_type,
                "razorpay_order_id": order_data["order_id"],
                "amount_inr": order_data["amount"],
                "currency_inr": order_data["currency"],
                "key_id": order_data["key_id"]
            }
        )
        
        db.add(payment_transaction)
        await db.commit()
        
        return {
            "success": True,
            "order_id": order_data["order_id"],
            "amount": order_data["amount"],
            "currency": order_data["currency"],
            "amount_usd": order_data["amount_usd"],
            "amount_inr": order_data.get("amount_inr"),
            "key_id": order_data["key_id"],
            "customer_email": request.customer_email,
            "customer_name": request.customer_name,
            "customer_country": order_data.get("customer_country"),
            "message": "Order created successfully"
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Order creation failed: {str(e)}")

@router.post("/verify-payment")
async def verify_razorpay_payment(
    request: PaymentVerificationRequest,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Verify Razorpay payment signature and update status"""
    try:
        razorpay_service = get_razorpay_service(db_session=db)
        
        # Get payment transaction
        result = await db.execute(
            select(PaymentTransaction).where(
                PaymentTransaction.razorpay_order_id == request.razorpay_order_id
            )
        )
        payment_transaction = result.scalar_one_or_none()
        
        if not payment_transaction:
            raise HTTPException(status_code=404, detail="Payment transaction not found")
        
        # Verify payment signature
        verification_result = await razorpay_service.verify_payment_signature(
            razorpay_order_id=request.razorpay_order_id,
            razorpay_payment_id=request.razorpay_payment_id,
            razorpay_signature=request.razorpay_signature
        )
        
        if not verification_result["success"]:
            raise HTTPException(status_code=400, detail=verification_result["error"])
        
        if verification_result["verified"]:
            # Update payment transaction
            payment_transaction.status = "completed"
            payment_transaction.razorpay_payment_id = request.razorpay_payment_id
            payment_transaction.paid_at = datetime.utcnow()
            payment_transaction.amount_paid = verification_result["amount"]
            
            # Update metadata with payment details
            if not payment_transaction.payment_metadata:
                payment_transaction.payment_metadata = {}
            payment_transaction.payment_metadata.update({
                "razorpay_payment_id": request.razorpay_payment_id,
                "payment_method": verification_result.get("method", "unknown"),
                "verification_status": "verified"
            })
            
            # Create Co-Creator record if payment is successful
            if payment_transaction.payment_metadata.get("program_type") == "co_creator":
                # Get or create active co-creator program
                from app.models.co_creator_program import CoCreatorProgram
                program_result = await db.execute(
                    select(CoCreatorProgram).where(CoCreatorProgram.is_active == True)
                )
                program = program_result.scalar_one_or_none()
                
                if not program:
                    # Create default program if none exists
                    program = CoCreatorProgram(
                        program_name="Founding Users Co-Creator Program",
                        total_seats=25,
                        seats_filled=0,
                        program_price=29000.0,  # Default price in INR
                        is_active=True
                    )
                    db.add(program)
                    await db.flush()
                
                # Check if co-creator already exists for this user
                # We'll use customer_email to find existing user or create association
                existing_co_creator = None
                
                # First check by user_id if we have it
                if payment_transaction.user_id:
                    result = await db.execute(
                        select(CoCreator).where(CoCreator.user_id == payment_transaction.user_id)
                    )
                    existing_co_creator = result.scalar_one_or_none()
                
                # Then check by lead_id
                if not existing_co_creator and payment_transaction.lead_id:
                    result = await db.execute(
                        select(CoCreator).where(CoCreator.lead_id == payment_transaction.lead_id)
                    )
                    existing_co_creator = result.scalar_one_or_none()
                
                if not existing_co_creator and program.seats_remaining > 0:
                    # Reserve a seat in the program
                    program.reserve_seat()
                    
                    # Find user
                    user = None
                    
                    # Try to get user from transaction
                    if payment_transaction.user_id:
                        result = await db.execute(select(User).where(User.id == payment_transaction.user_id))
                        user = result.scalar_one_or_none()
                    
                    # Fallback to email lookup if no user_id or user not found
                    if not user:
                        result = await db.execute(select(User).where(User.email == payment_transaction.customer_email))
                        user = result.scalar_one_or_none()
                    
                    if not user:
                        # User not found - Auto-create user for new customers
                        try:
                            temp_password = uuid.uuid4().hex[:12]
                            hashed_password = get_password_hash(temp_password)
                            
                            user = User(
                                email=payment_transaction.customer_email,
                                hashed_password=hashed_password,
                                full_name=payment_transaction.customer_name,
                                role="user",
                                is_active=True,
                                is_verified=True,  # Auto-verify email since they paid
                                subscription_tier="free"  # Will be upgraded below
                            )
                            db.add(user)
                            await db.flush()
                            await db.refresh(user)
                            
                        except Exception as create_error:
                            raise HTTPException(
                                status_code=500, 
                                detail=f"Failed to create user account: {str(create_error)}"
                            )
                    
                    co_creator = CoCreator(
                        program_id=program.id,
                        user_id=user.id,
                        lead_id=payment_transaction.lead_id,
                        seat_number=program.seats_filled,
                        status="active",
                        access_level="co_creator",
                        lifetime_access=True
                    )
                    
                    # Add metadata with payment info
                    co_creator.add_metadata("customer_email", payment_transaction.customer_email)
                    co_creator.add_metadata("customer_name", payment_transaction.customer_name)
                    co_creator.add_metadata("payment_transaction_id", payment_transaction.id)
                    co_creator.add_metadata("program_type", "co_creator")
                    co_creator.add_metadata("onboarding_completed", False)
                    
                    db.add(co_creator)
                    
                    # Update user status if exists
                    if user:
                        user.activate_co_creator_status(
                            seat_number=program.seats_filled,
                            benefits="Lifetime Platform Access, Priority Support, Founder Engagement"
                        )
                        db.add(user)
                    
                    # Update lead status if exists
                    if payment_transaction.lead_id:
                        result = await db.execute(
                            select(Lead).where(Lead.id == payment_transaction.lead_id)
                        )
                        lead = result.scalar_one_or_none()
                        if lead:
                            lead.status = "co_creator"
                            if not lead.tags:
                                lead.tags = []
                            lead.tags.append("co_creator_member")
            
            await db.commit()
            
            # Send payment confirmation and welcome emails
            try:
                support_service = get_payment_support_service()
                
                # Send payment confirmation
                await support_service.send_payment_confirmation({
                    "customer_email": payment_transaction.customer_email,
                    "customer_name": payment_transaction.customer_name,
                    "amount": verification_result["amount"],
                    "currency": verification_result["currency"],
                    "order_id": request.razorpay_order_id
                })
                
                # Send welcome email if co-creator was created
                if payment_transaction.payment_metadata.get("program_type") == "co_creator":
                    await support_service.send_co_creator_welcome_email({
                        "email": payment_transaction.customer_email,
                        "name": payment_transaction.customer_name
                    })
                    
            except Exception as email_error:
                print(f"Email notification error: {email_error}")
                # Don't fail the payment verification if email fails
            
            return {
                "success": True,
                "verified": True,
                "payment_id": request.razorpay_payment_id,
                "order_id": request.razorpay_order_id,
                "status": "completed",
                "amount": verification_result["amount"],
                "currency": verification_result["currency"],
                "method": verification_result.get("method"),
                "co_creator_created": True,
                "message": "Payment verified and Co-Creator account created successfully"
            }
        else:
            return {
                "success": False,
                "verified": False,
                "error": "Payment signature verification failed"
            }
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Payment verification failed: {str(e)}")

@router.post("/webhook")
async def razorpay_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Handle Razorpay webhook notifications"""
    try:
        # Get raw body and signature
        body = await request.body()
        signature = request.headers.get("X-Razorpay-Signature", "")
        
        razorpay_service = get_razorpay_service(db_session=db)
        
        # Process webhook
        webhook_result = await razorpay_service.process_webhook(
            payload=body.decode(),
            signature=signature
        )
        
        if webhook_result["success"] and webhook_result.get("event") == "payment_captured":
            order_id = webhook_result.get("order_id")
            payment_id = webhook_result.get("payment_id")
            
            # Update payment transaction
            result = await db.execute(
                select(PaymentTransaction).where(
                    PaymentTransaction.razorpay_order_id == order_id
                )
            )
            payment_transaction = result.scalar_one_or_none()
            
            if payment_transaction:
                payment_transaction.status = "completed"
                payment_transaction.razorpay_payment_id = payment_id
                payment_transaction.amount_paid = webhook_result.get("amount", payment_transaction.amount)
                await db.commit()
        
        return {"success": True, "processed": True}
        
    except Exception as e:
        await db.rollback()
        return {"success": False, "error": str(e)}

@router.get("/payment-status/{payment_id}")
async def get_payment_status(
    payment_id: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get payment status by Razorpay payment ID"""
    try:
        razorpay_service = get_razorpay_service(db_session=db)
        
        # Get status from Razorpay
        status_result = await razorpay_service.get_payment_status(payment_id)
        
        if not status_result["success"]:
            raise HTTPException(status_code=400, detail=status_result["error"])
        
        # Also get local transaction record
        result = await db.execute(
            select(PaymentTransaction).where(
                PaymentTransaction.razorpay_payment_id == payment_id
            )
        )
        payment_transaction = result.scalar_one_or_none()
        
        return {
            "success": True,
            "payment_id": payment_id,
            "status": status_result["status"],
            "amount": status_result["amount"],
            "currency": status_result["currency"],
            "method": status_result.get("method"),
            "captured": status_result.get("captured", False),
            "created_at": status_result.get("created_at"),
            "local_status": payment_transaction.status if payment_transaction else "not_found"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get payment status: {str(e)}")

@router.get("/config-test")
async def test_razorpay_config() -> Dict[str, Any]:
    """Test Razorpay configuration"""
    try:
        razorpay_service = get_razorpay_service()
        
        return {
            "success": True,
            "configured": razorpay_service.is_configured(),
            "key_id": razorpay_service.key_id,
            "has_key_secret": bool(getattr(razorpay_service, 'key_secret', False)),
            "service_type": "mock" if hasattr(razorpay_service, 'mock') or 'mock' in razorpay_service.key_id else "real"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/test-order")
async def test_razorpay_order(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Test Razorpay order creation"""
    try:
        razorpay_service = get_razorpay_service(db_session=db)

        # Test order creation
        success, message, order_data = await razorpay_service.create_co_creator_payment(
            co_creator_id=999,  # Test ID
            customer_email="test@unitasa.in",
            customer_name="Test User",
            amount=250.0
        )

        return {
            "success": success,
            "message": message,
            "order_data": order_data,
            "test_mode": True
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "test_mode": True
        }

@router.post("/test-email")
async def test_email_sending() -> Dict[str, Any]:
    """Test email sending functionality"""
    try:
        from app.core.payment_support_service import get_payment_support_service

        support_service = get_payment_support_service()

        # Test payment confirmation email
        result = await support_service.send_payment_confirmation({
            "customer_email": "test@unitasa.in",
            "customer_name": "Test User",
            "amount": 497.00,
            "currency": "USD",
            "order_id": "test_order_123"
        })

        return {
            "success": True,
            "email_sent": result.get("email_sent", False),
            "message": result.get("message", "Email test completed"),
            "test_mode": True
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "test_mode": True
        }
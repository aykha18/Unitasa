"""
Razorpay payment service for Co-Creator Program payments
"""

import os
import json
import hmac
import hashlib
import razorpay
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from app.core.config import get_settings

settings = get_settings()


class RazorpayPaymentService:
    """Service for handling Razorpay payments"""
    
    def __init__(self, db_session=None):
        self.db = db_session
        self.key_id = os.getenv("RAZORPAY_KEY_ID", "")
        self.key_secret = os.getenv("RAZORPAY_KEY_SECRET", "")
        self.webhook_secret = os.getenv("RAZORPAY_WEBHOOK_SECRET", "")
        
        # Initialize Razorpay client
        if self.key_id and self.key_secret:
            self.client = razorpay.Client(auth=(self.key_id, self.key_secret))
        else:
            self.client = None
            
    def is_configured(self) -> bool:
        """Check if Razorpay is properly configured"""
        return bool(self.key_id and self.key_secret and self.client)
    
    async def create_payment_order(self, amount: float, currency: str = "INR", 
                                 customer_email: str = "", customer_name: str = "",
                                 description: str = "Co-Creator Program Payment") -> Dict[str, Any]:
        """Create a Razorpay order for payment"""
        try:
            if not self.is_configured():
                return {
                    "success": False,
                    "error": "Razorpay not configured. Please set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET"
                }
            
            # Convert amount to paise (Razorpay uses smallest currency unit)
            amount_paise = int(amount * 100)
            
            order_data = {
                "amount": amount_paise,
                "currency": currency,
                "receipt": f"co_creator_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "notes": {
                    "customer_email": customer_email,
                    "customer_name": customer_name,
                    "program_type": "co_creator",
                    "description": description
                }
            }
            
            order = self.client.order.create(data=order_data)
            
            return {
                "success": True,
                "order": order,
                "order_id": order["id"],
                "amount": amount,
                "currency": currency,
                "key_id": self.key_id  # Frontend needs this for Razorpay checkout
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Order creation failed: {str(e)}"
            }
    
    async def verify_payment_signature(self, razorpay_order_id: str, razorpay_payment_id: str,
                                     razorpay_signature: str) -> Dict[str, Any]:
        """Verify Razorpay payment signature"""
        try:
            if not self.is_configured():
                return {
                    "success": False,
                    "error": "Razorpay not configured"
                }
            
            # Create signature verification string
            message = f"{razorpay_order_id}|{razorpay_payment_id}"
            
            # Generate expected signature
            expected_signature = hmac.new(
                self.key_secret.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Verify signature
            if hmac.compare_digest(expected_signature, razorpay_signature):
                # Get payment details
                payment = self.client.payment.fetch(razorpay_payment_id)
                
                return {
                    "success": True,
                    "verified": True,
                    "payment": payment,
                    "payment_id": razorpay_payment_id,
                    "order_id": razorpay_order_id,
                    "amount": payment.get("amount", 0) / 100,  # Convert back from paise
                    "currency": payment.get("currency", "INR"),
                    "status": payment.get("status", "unknown"),
                    "method": payment.get("method", "unknown")
                }
            else:
                return {
                    "success": False,
                    "verified": False,
                    "error": "Invalid payment signature"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Signature verification failed: {str(e)}"
            }
    
    async def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """Get payment status from Razorpay"""
        try:
            if not self.is_configured():
                return {
                    "success": False,
                    "error": "Razorpay not configured"
                }
            
            payment = self.client.payment.fetch(payment_id)
            
            return {
                "success": True,
                "payment_id": payment_id,
                "status": payment.get("status", "unknown"),
                "amount": payment.get("amount", 0) / 100,
                "currency": payment.get("currency", "INR"),
                "method": payment.get("method", "unknown"),
                "created_at": payment.get("created_at"),
                "captured": payment.get("captured", False),
                "details": payment
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Payment status check failed: {str(e)}"
            }
    
    async def capture_payment(self, payment_id: str, amount: Optional[float] = None) -> Dict[str, Any]:
        """Capture a payment (for authorized payments)"""
        try:
            if not self.is_configured():
                return {
                    "success": False,
                    "error": "Razorpay not configured"
                }
            
            capture_data = {}
            if amount:
                capture_data["amount"] = int(amount * 100)  # Convert to paise
            
            payment = self.client.payment.capture(payment_id, capture_data)
            
            return {
                "success": True,
                "payment": payment,
                "payment_id": payment_id,
                "captured": True,
                "amount": payment.get("amount", 0) / 100
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Payment capture failed: {str(e)}"
            }
    
    async def process_webhook(self, payload: str, signature: str) -> Dict[str, Any]:
        """Process Razorpay webhook"""
        try:
            # If webhook secret is not configured, skip signature verification
            # This is acceptable for development/testing
            if not self.webhook_secret or self.webhook_secret == "your_razorpay_webhook_secret_here":
                print("⚠️  Webhook secret not configured - skipping signature verification")
                # Process webhook without verification (development mode)
                webhook_data = json.loads(payload)
            else:
                # Verify webhook signature in production
                expected_signature = hmac.new(
                    self.webhook_secret.encode(),
                    payload.encode(),
                    hashlib.sha256
                ).hexdigest()
                
                if not hmac.compare_digest(f"sha256={expected_signature}", signature):
                    return {
                        "success": False,
                        "error": "Invalid webhook signature"
                    }
                
                # Parse webhook payload
                webhook_data = json.loads(payload)

            event = webhook_data.get("event", "")
            
            if event == "payment.captured":
                payment_entity = webhook_data.get("payload", {}).get("payment", {}).get("entity", {})
                
                return {
                    "success": True,
                    "event": "payment_captured",
                    "payment_id": payment_entity.get("id"),
                    "order_id": payment_entity.get("order_id"),
                    "amount": payment_entity.get("amount", 0) / 100,
                    "currency": payment_entity.get("currency"),
                    "status": payment_entity.get("status"),
                    "method": payment_entity.get("method")
                }
            elif event == "payment.failed":
                payment_entity = webhook_data.get("payload", {}).get("payment", {}).get("entity", {})
                
                return {
                    "success": True,
                    "event": "payment_failed",
                    "payment_id": payment_entity.get("id"),
                    "order_id": payment_entity.get("order_id"),
                    "error_code": payment_entity.get("error_code"),
                    "error_description": payment_entity.get("error_description")
                }
            else:
                return {
                    "success": True,
                    "event": "unknown",
                    "event_type": event
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Webhook processing failed: {str(e)}"
            }
    
    async def create_co_creator_payment(self, co_creator_id: int, customer_email: str,
                                      customer_name: Optional[str] = None, 
                                      amount: float = 497.0,
                                      currency: str = "USD",
                                      customer_country: str = "US") -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Create a Razorpay payment for co-creator program"""
        try:
            # Determine currency and amount based on customer location
            if currency.upper() == "INR":
                # If specifically requested in INR, use the amount as is
                final_currency = "INR"
                final_amount = amount
            elif customer_country.upper() == "IN":
                # Indian customers pay in INR
                final_currency = "INR"
                final_amount = amount * 83  # USD to INR conversion
            else:
                # International customers pay in USD
                final_currency = "USD"
                final_amount = amount
            
            order_result = await self.create_payment_order(
                amount=final_amount,
                currency=final_currency,
                customer_email=customer_email,
                customer_name=customer_name or "Co-Creator",
                description=f"Unitasa Co-Creator Program - {customer_email}"
            )
            
            if not order_result["success"]:
                return False, order_result["error"], None
            
            return True, "Payment order created successfully", {
                "order_id": order_result["order_id"],
                "amount": final_amount,
                "currency": final_currency,
                "amount_usd": final_amount if final_currency == "USD" else final_amount / 83,
                "amount_inr": final_amount if final_currency == "INR" else final_amount * 83,
                "key_id": order_result["key_id"],
                "customer_email": customer_email,
                "customer_name": customer_name,
                "co_creator_id": co_creator_id,
                "customer_country": customer_country
            }
            
        except Exception as e:
            return False, f"Co-creator payment creation failed: {str(e)}", None


# Mock service for testing without Razorpay credentials
class MockRazorpayPaymentService:
    """Mock Razorpay service for testing"""
    
    def __init__(self, db_session=None):
        self.db = db_session
        self.key_id = "rzp_test_mock_key_id"
        self.key_secret = "mock_key_secret"
        
    def is_configured(self) -> bool:
        return True
    
    async def create_payment_order(self, amount: float, currency: str = "INR", 
                                 customer_email: str = "", customer_name: str = "",
                                 description: str = "Co-Creator Program Payment") -> Dict[str, Any]:
        """Create mock payment order"""
        import uuid
        
        order_id = f"order_mock_{uuid.uuid4().hex[:10]}"
        
        return {
            "success": True,
            "order": {
                "id": order_id,
                "amount": int(amount * 100),
                "currency": currency,
                "status": "created"
            },
            "order_id": order_id,
            "amount": amount,
            "currency": currency,
            "key_id": self.key_id
        }
    
    async def verify_payment_signature(self, razorpay_order_id: str, razorpay_payment_id: str,
                                     razorpay_signature: str) -> Dict[str, Any]:
        """Mock payment verification - always succeeds"""
        return {
            "success": True,
            "verified": True,
            "payment": {
                "id": razorpay_payment_id,
                "order_id": razorpay_order_id,
                "status": "captured",
                "amount": 41251,  # 497 USD * 83 INR * 100 paise
                "currency": "INR"
            },
            "payment_id": razorpay_payment_id,
            "order_id": razorpay_order_id,
            "amount": 412.51,
            "currency": "INR",
            "status": "captured",
            "method": "card"
        }
    
    async def create_co_creator_payment(self, co_creator_id: int, customer_email: str,
                                      customer_name: Optional[str] = None, 
                                      amount: float = 497.0,
                                      currency: str = "USD",
                                      customer_country: str = "US") -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Mock co-creator payment creation"""
        import uuid
        
        # Determine currency and amount based on customer location
        if customer_country.upper() == "IN" or currency.upper() == "INR":
            final_currency = "INR"
            final_amount = amount * 83
        else:
            final_currency = "USD"
            final_amount = amount
        
        order_id = f"order_mock_{uuid.uuid4().hex[:10]}"
        
        return True, "Mock payment order created successfully", {
            "order_id": order_id,
            "amount": final_amount,
            "currency": final_currency,
            "amount_usd": amount,
            "amount_inr": amount * 83 if final_currency == "USD" else final_amount,
            "key_id": self.key_id,
            "customer_email": customer_email,
            "customer_name": customer_name,
            "co_creator_id": co_creator_id,
            "customer_country": customer_country,
            "mock": True
        }


def get_razorpay_service(db_session=None, use_mock=None):
    """Get Razorpay service (real or mock based on configuration)"""
    
    # Auto-detect if we should use mock
    if use_mock is None:
        key_id = os.getenv("RAZORPAY_KEY_ID", "")
        key_secret = os.getenv("RAZORPAY_KEY_SECRET", "")
        
        use_mock = (
            not key_id or not key_secret or
            key_id in ["", "your_razorpay_key_id_here"] or
            key_secret in ["", "your_razorpay_key_secret_here"]
        )
    
    if use_mock:
        print("Using Mock Razorpay Service for testing")
        return MockRazorpayPaymentService(db_session)
    else:
        print("Using Real Razorpay Service")
        return RazorpayPaymentService(db_session)
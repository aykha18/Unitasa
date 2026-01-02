"""
Webhook Security Validation
Implements secure webhook processing with signature verification and fraud detection
"""

import hmac
import hashlib
import time
import logging
from typing import Dict, Any, Optional, Tuple
# import stripe
from fastapi import Request, HTTPException

from app.core.config import get_settings
from app.core.security_middleware import FraudDetectionService

logger = logging.getLogger(__name__)
settings = get_settings()


class WebhookSecurityManager:
    """
    Manages webhook security validation and processing
    """
    
    def __init__(self):
        self.fraud_detector = FraudDetectionService()
        self.webhook_secrets = {
            # "stripe": settings.stripe.webhook_secret,
            # Add other webhook secrets as needed
        }
    
    # async def validate_stripe_webhook(
    #     self,
    #     request: Request,
    #     payload: str,
    #     signature: str
    # ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    #     """
    #     Validate Stripe webhook with comprehensive security checks
    #     """
    #     try:
    #         # Verify webhook signature
    #         event = stripe.Webhook.construct_event(
    #             payload,
    #             signature,
    #             self.webhook_secrets["stripe"]
    #         )
    #         
    #         # Additional security validations
    #         security_result = await self._perform_webhook_security_checks(
    #             request, event, "stripe"
    #         )
    #         
    #         if not security_result["is_secure"]:
    #             logger.warning(f"Webhook security check failed: {security_result['reason']}")
    #             return False, None, security_result["reason"]
    #         
    #         return True, event, None
    #         
    #     except stripe.error.SignatureVerificationError as e:
    #         logger.warning(f"Invalid Stripe webhook signature: {e}")
    #         return False, None, "Invalid webhook signature"
    #     except Exception as e:
    #         logger.error(f"Webhook validation error: {e}")
    #         return False, None, "Webhook validation failed"
    
    async def _perform_webhook_security_checks(
        self,
        request: Request,
        event: Dict[str, Any],
        provider: str
    ) -> Dict[str, Any]:
        """
        Perform comprehensive security checks on webhook
        """
        # Check timestamp to prevent replay attacks
        event_timestamp = event.get("created", 0)
        current_timestamp = int(time.time())
        
        if abs(current_timestamp - event_timestamp) > 300:  # 5 minutes tolerance
            return {
                "is_secure": False,
                "reason": "Webhook timestamp too old (potential replay attack)"
            }
        
        # Check for duplicate events (idempotency)
        event_id = event.get("id")
        if event_id and self._is_duplicate_event(event_id, provider):
            return {
                "is_secure": False,
                "reason": "Duplicate webhook event detected"
            }
        
        # Rate limiting check
        client_ip = self._get_client_ip(request)
        if self._is_rate_limited(client_ip, provider):
            return {
                "is_secure": False,
                "reason": "Rate limit exceeded for webhook source"
            }
        
        # Provider-specific security checks
        if provider == "stripe":
            stripe_checks = self._validate_stripe_event_security(event)
            if not stripe_checks["is_secure"]:
                return stripe_checks
        
        # Record successful webhook for duplicate detection
        if event_id:
            self._record_webhook_event(event_id, provider)
        
        return {"is_secure": True, "reason": None}
    
    def _validate_stripe_event_security(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Stripe-specific security validations
        """
        event_type = event.get("type", "")
        event_data = event.get("data", {}).get("object", {})
        
        # Validate payment intent events
        if event_type.startswith("payment_intent."):
            # Check for suspicious payment patterns
            if event_type == "payment_intent.created":
                payment_data = {
                    "amount": event_data.get("amount", 0) / 100,
                    "currency": event_data.get("currency", ""),
                    "email": event_data.get("receipt_email", ""),
                    "metadata": event_data.get("metadata", {})
                }
                
                # Basic fraud detection
                if payment_data["amount"] > 10000:  # $10,000 limit
                    return {
                        "is_secure": False,
                        "reason": "Payment amount exceeds security threshold"
                    }
        
        # Validate charge dispute events
        elif event_type == "charge.dispute.created":
            dispute_reason = event_data.get("reason", "")
            if dispute_reason in ["fraudulent", "unrecognized"]:
                logger.warning(f"Fraudulent dispute detected: {event_data.get('id')}")
                # Additional fraud detection logic here
        
        return {"is_secure": True, "reason": None}
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request"""
        # Check for forwarded headers (common in cloud deployments)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _is_duplicate_event(self, event_id: str, provider: str) -> bool:
        """Check if webhook event is duplicate"""
        # In production, use Redis or database
        # For now, simple in-memory cache
        cache_key = f"{provider}:{event_id}"
        return hasattr(self, '_processed_events') and cache_key in self._processed_events
    
    def _record_webhook_event(self, event_id: str, provider: str):
        """Record processed webhook event"""
        if not hasattr(self, '_processed_events'):
            self._processed_events = set()
        
        cache_key = f"{provider}:{event_id}"
        self._processed_events.add(cache_key)
        
        # Clean old events (keep last 1000)
        if len(self._processed_events) > 1000:
            # Remove oldest 100 events
            old_events = list(self._processed_events)[:100]
            for event in old_events:
                self._processed_events.remove(event)
    
    def _is_rate_limited(self, ip_address: str, provider: str) -> bool:
        """Check if IP is rate limited for webhooks"""
        # Simple rate limiting: max 100 webhooks per minute per IP
        current_time = time.time()
        cache_key = f"webhook_rate:{provider}:{ip_address}"
        
        if not hasattr(self, '_rate_cache'):
            self._rate_cache = {}
        
        if cache_key not in self._rate_cache:
            self._rate_cache[cache_key] = []
        
        # Clean old requests (older than 1 minute)
        self._rate_cache[cache_key] = [
            t for t in self._rate_cache[cache_key]
            if current_time - t < 60
        ]
        
        # Add current request
        self._rate_cache[cache_key].append(current_time)
        
        # Check rate limit
        return len(self._rate_cache[cache_key]) > 100


class PaymentFraudDetector:
    """
    Enhanced fraud detection for payment processing
    """
    
    def __init__(self):
        self.risk_patterns = {
            "velocity_threshold": 5,  # Max payments per email per hour
            "amount_threshold": 1000,  # Suspicious amount in USD
            "country_blacklist": ["XX", "YY"],  # ISO country codes
            "email_patterns": [
                r".*\+.*@.*",  # Email with plus addressing
                r".*test.*@.*",  # Test emails
                r".*temp.*@.*"  # Temporary emails
            ]
        }
    
    def analyze_payment_risk(
        self,
        payment_data: Dict[str, Any],
        user_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive payment fraud analysis
        """
        risk_score = 0
        risk_factors = []
        
        # Amount-based risk
        amount = payment_data.get("amount", 0)
        if amount > self.risk_patterns["amount_threshold"]:
            risk_score += 25
            risk_factors.append(f"High payment amount: ${amount}")
        
        # Email pattern analysis
        email = payment_data.get("email", "")
        if self._check_suspicious_email_patterns(email):
            risk_score += 20
            risk_factors.append("Suspicious email pattern")
        
        # Geographic risk
        country = payment_data.get("country", "")
        if country in self.risk_patterns["country_blacklist"]:
            risk_score += 30
            risk_factors.append(f"High-risk country: {country}")
        
        # Velocity check
        if self._check_payment_velocity(email):
            risk_score += 35
            risk_factors.append("High payment velocity")
        
        # Card fingerprint analysis
        card_fingerprint = payment_data.get("card_fingerprint", "")
        if self._check_card_reuse(card_fingerprint, email):
            risk_score += 15
            risk_factors.append("Card reused across multiple accounts")
        
        # Determine final risk assessment
        risk_level = self._calculate_risk_level(risk_score)
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "should_block": risk_score >= 80,
            "requires_manual_review": risk_score >= 50,
            "recommended_actions": self._get_recommended_actions(risk_score, risk_factors)
        }
    
    def _check_suspicious_email_patterns(self, email: str) -> bool:
        """Check email against suspicious patterns"""
        import re
        
        for pattern in self.risk_patterns["email_patterns"]:
            if re.match(pattern, email, re.IGNORECASE):
                return True
        return False
    
    def _check_payment_velocity(self, email: str) -> bool:
        """Check payment velocity for email"""
        # Implementation would check database for recent payments
        # For now, return False (no velocity risk)
        return False
    
    def _check_card_reuse(self, card_fingerprint: str, email: str) -> bool:
        """Check if card is being reused across accounts"""
        # Implementation would check database for card fingerprint usage
        # For now, return False (no reuse detected)
        return False
    
    def _calculate_risk_level(self, risk_score: int) -> str:
        """Calculate risk level from score"""
        if risk_score >= 70:
            return "high"
        elif risk_score >= 40:
            return "medium"
        else:
            return "low"
    
    def _get_recommended_actions(self, risk_score: int, risk_factors: list) -> list:
        """Get recommended actions based on risk assessment"""
        actions = []
        
        if risk_score >= 80:
            actions.append("Block payment immediately")
            actions.append("Flag account for investigation")
        elif risk_score >= 50:
            actions.append("Require manual review")
            actions.append("Request additional verification")
        elif risk_score >= 30:
            actions.append("Monitor for additional suspicious activity")
        
        return actions

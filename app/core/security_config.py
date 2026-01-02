"""
Security Configuration
Centralized security settings and configurations
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from app.core.config import get_settings

settings = get_settings()


@dataclass
class SecurityConfig:
    """Security configuration settings"""
    
    # HTTPS enforcement
    force_https: bool = not settings.is_development()
    hsts_max_age: int = 31536000  # 1 year
    hsts_include_subdomains: bool = True
    hsts_preload: bool = True
    
    # Content Security Policy
    csp_default_src: List[str] = None
    csp_script_src: List[str] = None
    csp_style_src: List[str] = None
    csp_img_src: List[str] = None
    csp_connect_src: List[str] = None
    csp_font_src: List[str] = None
    csp_frame_src: List[str] = None
    
    # OAuth2 Security
    oauth2_pkce_required: bool = True
    oauth2_state_required: bool = True
    oauth2_token_encryption: bool = True
    oauth2_session_timeout: int = 300  # 5 minutes
    
    # Webhook Security
    webhook_signature_required: bool = True
    webhook_timestamp_tolerance: int = 300  # 5 minutes
    webhook_rate_limit: int = 100  # per minute per IP
    
    # Fraud Detection
    fraud_detection_enabled: bool = True
    fraud_max_attempts: int = 5
    fraud_time_window: int = 300  # 5 minutes
    fraud_amount_threshold: float = 1000.0
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # 1 minute
    
    def __post_init__(self):
        """Initialize default values"""
        if self.csp_default_src is None:
            self.csp_default_src = ["'self'"]
        
        if self.csp_script_src is None:
            self.csp_script_src = [
                "'self'",
                "https://js.stripe.com",
                "https://www.google-analytics.com",
                "https://www.googletagmanager.com"
            ]
        
        if self.csp_style_src is None:
            self.csp_style_src = [
                "'self'",
                "'unsafe-inline'",
                "https://fonts.googleapis.com"
            ]
        
        if self.csp_img_src is None:
            self.csp_img_src = [
                "'self'",
                "data:",
                "https:",
                "blob:"
            ]
        
        if self.csp_connect_src is None:
            self.csp_connect_src = [
                "'self'",
                "https://api.stripe.com",
                "https://www.google-analytics.com",
                "https://analytics.google.com"
            ]
        
        if self.csp_font_src is None:
            self.csp_font_src = [
                "'self'",
                "https://fonts.gstatic.com"
            ]
        
        if self.csp_frame_src is None:
            self.csp_frame_src = [
                "'self'",
                # "https://js.stripe.com",
                # "https://hooks.stripe.com"
            ]
    
    def get_csp_header(self, nonce: str = None) -> str:
        """Generate Content Security Policy header"""
        directives = [
            f"default-src {' '.join(self.csp_default_src)}",
            f"script-src {' '.join(self.csp_script_src)}" + (f" 'nonce-{nonce}'" if nonce else ""),
            f"style-src {' '.join(self.csp_style_src)}",
            f"img-src {' '.join(self.csp_img_src)}",
            f"connect-src {' '.join(self.csp_connect_src)}",
            f"font-src {' '.join(self.csp_font_src)}",
            f"frame-src {' '.join(self.csp_frame_src)}",
            "object-src 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "frame-ancestors 'none'"
        ]
        
        if self.force_https:
            directives.append("upgrade-insecure-requests")
        
        return "; ".join(directives)
    
    def get_security_headers(self, nonce: str = None) -> Dict[str, str]:
        """Get all security headers"""
        headers = {
            "Content-Security-Policy": self.get_csp_header(nonce),
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": self._get_permissions_policy(),
            "Cross-Origin-Embedder-Policy": "require-corp",
            "Cross-Origin-Opener-Policy": "same-origin",
            "Cross-Origin-Resource-Policy": "same-origin"
        }
        
        if self.force_https:
            hsts_value = f"max-age={self.hsts_max_age}"
            if self.hsts_include_subdomains:
                hsts_value += "; includeSubDomains"
            if self.hsts_preload:
                hsts_value += "; preload"
            headers["Strict-Transport-Security"] = hsts_value
        
        return headers
    
    def _get_permissions_policy(self) -> str:
        """Generate Permissions Policy header"""
        policies = [
            "geolocation=()",
            "microphone=()",
            "camera=()",
            "payment=(self)",
            "usb=()",
            "magnetometer=()",
            "gyroscope=()",
            "accelerometer=()"
        ]
        return ", ".join(policies)


# Global security configuration instance
security_config = SecurityConfig()


def get_security_config() -> SecurityConfig:
    """Get security configuration"""
    return security_config


# Security validation rules
SECURITY_VALIDATION_RULES = {
    "oauth2": {
        "required_fields": ["client_id", "client_secret", "redirect_uri"],
        "secure_redirect_schemes": ["https"],
        "required_pkce": True,
        "required_state": True,
        "max_session_duration": 300
    },
    "webhooks": {
        "required_signature": True,
        "max_timestamp_age": 300,
        "rate_limit_per_ip": 100,
        "rate_limit_window": 60
    },
    "payments": {
        "max_amount": 10000.0,
        "fraud_detection": True,
        "require_3ds": False,  # Stripe handles this
        "max_attempts_per_email": 5,
        "max_attempts_window": 300
    },
    "api": {
        "rate_limit_requests": 1000,
        "rate_limit_window": 3600,
        "require_https": not settings.is_development(),
        "max_request_size": 10 * 1024 * 1024,  # 10MB
        "timeout": 30
    }
}


def validate_security_compliance() -> Dict[str, Any]:
    """Validate overall security compliance"""
    compliance_checks = {
        "https_enforcement": {
            "enabled": security_config.force_https,
            "score": 100 if security_config.force_https else 0
        },
        "security_headers": {
            "csp_enabled": True,
            "xss_protection": True,
            "frame_options": True,
            "content_type_options": True,
            "score": 100
        },
        "oauth2_security": {
            "pkce_required": security_config.oauth2_pkce_required,
            "state_required": security_config.oauth2_state_required,
            "token_encryption": security_config.oauth2_token_encryption,
            "score": 100 if all([
                security_config.oauth2_pkce_required,
                security_config.oauth2_state_required,
                security_config.oauth2_token_encryption
            ]) else 75
        },
        "webhook_security": {
            "signature_verification": security_config.webhook_signature_required,
            "timestamp_validation": True,
            "rate_limiting": True,
            "score": 100
        },
        "fraud_detection": {
            "enabled": security_config.fraud_detection_enabled,
            "rate_limiting": True,
            "amount_validation": True,
            "score": 100 if security_config.fraud_detection_enabled else 50
        }
    }
    
    # Calculate overall score
    total_score = sum(check["score"] for check in compliance_checks.values())
    average_score = total_score / len(compliance_checks)
    
    return {
        "overall_compliance": average_score >= 95,
        "compliance_score": average_score,
        "detailed_checks": compliance_checks,
        "recommendations": _get_security_recommendations(compliance_checks)
    }


def _get_security_recommendations(checks: Dict[str, Any]) -> List[str]:
    """Get security recommendations based on compliance checks"""
    recommendations = []
    
    for check_name, check_data in checks.items():
        if check_data["score"] < 100:
            if check_name == "https_enforcement":
                recommendations.append("Enable HTTPS enforcement for production")
            elif check_name == "oauth2_security":
                recommendations.append("Implement all OAuth2 security best practices")
            elif check_name == "fraud_detection":
                recommendations.append("Enable comprehensive fraud detection")
    
    if not recommendations:
        recommendations.append("Security configuration is optimal")
    
    return recommendations

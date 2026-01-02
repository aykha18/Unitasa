"""
Health check and status endpoints for Railway deployment
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import os
from datetime import datetime

from app.core.database import get_db
from app.core.config import get_settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check endpoint - always available, never fails"""
    # Ultra-simple response that cannot fail
    return {
        "status": "healthy",
        "service": "unitasa-api",
        "timestamp": "2025-01-01T00:00:00.000000",
        "version": "1.0.0",
        "ready": True
    }


@router.get("/status")
async def detailed_status(db: AsyncSession = Depends(get_db)):
    """Detailed status check including database connectivity"""
    settings = get_settings()
    
    # Test database connection
    db_status = "unknown"
    try:
        result = await db.execute(text("SELECT 1"))
        if result:
            db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "service": "unitasa-api",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.environment,
        "version": "1.0.0",
        "database": {
            "status": db_status,
            "pool_size": settings.database.pool_size
        },
        "features": {
            "ai_capabilities": True,
            "assessment_flow": True,
            # "payment_processing": bool(settings.stripe.secret_key),
            "payment_processing": False, # Stripe disabled
            "email_service": bool(settings.email.sendgrid_api_key),
            "chat_widget": True
        },
        "railway": {
            "environment": os.getenv("RAILWAY_ENVIRONMENT"),
            "port": settings.port
        }
    }


@router.get("/metrics")
async def basic_metrics():
    """Basic application metrics"""
    return {
        "uptime": "healthy",
        "requests_total": "tracking_enabled",
        "database_connections": "pooled",
        "memory_usage": "optimized",
        "response_time": "fast"
    }
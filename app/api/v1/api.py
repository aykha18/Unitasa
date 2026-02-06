"""
Main API router for v1 endpoints
"""

from fastapi import APIRouter

from app.api.agents import router as agents_router
from app.api.client_onboarding import router as client_onboarding_router
from .ai_agents import router as ai_agents_router
from .landing import router as landing_router
from .social import router as social_router
from .crm_marketplace import router as crm_marketplace_router
from .chat import router as chat_router
from .analytics import router as analytics_router
from .dashboard import router as dashboard_router
from .admin import router as admin_router

api_router = APIRouter()

# Include existing agents router (legacy)
api_router.include_router(agents_router, prefix="/agents", tags=["agents"])

# Include new AI agents router (cost-optimized)
api_router.include_router(ai_agents_router, prefix="/ai", tags=["ai-agents"])

# Include client onboarding router
api_router.include_router(client_onboarding_router, prefix="/clients", tags=["clients"])

# Include new landing page router
api_router.include_router(landing_router, prefix="/landing", tags=["landing"])

# Include social media management router
api_router.include_router(social_router, prefix="/social", tags=["social"])

# Include CRM marketplace router
api_router.include_router(crm_marketplace_router, prefix="/crm-marketplace", tags=["crm-marketplace"])

# Include chat router
api_router.include_router(chat_router, prefix="/chat", tags=["chat"])

# Include analytics router
api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])

# Include dashboard router
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])

# Include admin router
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])

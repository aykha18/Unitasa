"""
Onboarding API endpoints for One-Click Onboarding
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.user import User
from app.api.v1.auth import get_current_user as get_current_active_user
from app.agents.ingestion_agent import ingest_website
from app.agents.social_content_knowledge_base import get_social_content_knowledge_base

router = APIRouter()

class OnboardingRequest(BaseModel):
    url: str = Field(..., description="Website URL to analyze")
    generate_content: bool = Field(True, description="Whether to generate initial content ideas")

@router.post("/start")
async def start_onboarding(
    request: OnboardingRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    One-Click Onboarding:
    1. Ingests the provided website URL.
    2. Extracts brand profile (Mission, Audience, Tone, etc.).
    3. Creates/Updates the Client Knowledge Base.
    4. Generates initial social media content ideas.
    """
    try:
        # 1. Ingest Website
        print(f"Onboarding: Ingesting {request.url} for user {current_user.id}")
        ingest_result = await ingest_website(request.url)
        
        if not ingest_result.get("success"):
            raise HTTPException(status_code=400, detail=f"Website ingestion failed: {ingest_result.get('error')}")
        
        summary = ingest_result.get("summary", {})
        
        # 2. Construct Brand Profile from Summary
        # Map the AI summary to our profile structure
        brand_profile = {
            "company_info": {
                "company_name": summary.get("business_offering", "My Company"), # Fallback if name not explicit
                "industry": summary.get("industry", "General"),
                "brand_voice": summary.get("brand_tone", "Professional"),
                "website": request.url
            },
            "target_audience": {
                "description": summary.get("target_audience", "General Audience"),
                "pain_points": [], # AI might not extract this explicitly yet
                "interests": []
            },
            "features": [{"title": f, "description": ""} for f in summary.get("key_features", [])],
            "how_it_works": summary.get("how_it_works", [])
        }
        
        # 3. Update Client Knowledge Base
        kb = await get_social_content_knowledge_base()
        
        # Construct a robust client_id
        client_id = f"client_{current_user.id}"
        if current_user.company:
             safe_company = "".join(c for c in current_user.company if c.isalnum())
             if safe_company:
                 client_id = f"client_{safe_company}_{current_user.id}"
        
        # Create or Update KB
        await kb.create_client_kb(client_id, brand_profile)
        print(f"Onboarding: Created KB for {client_id}")
        
        # 4. Generate Content Ideas
        content_ideas = []
        if request.generate_content:
            try:
                # Generate for multiple platforms
                platforms = ["twitter", "linkedin"]
                for platform in platforms:
                    suggestions = await kb.get_client_content(
                        client_id=client_id,
                        content_request={
                            "topic": "industry trends", # Generic starter topic
                            "platform": platform,
                            "content_type": "educational",
                            "limit": 3
                        }
                    )
                    content_ideas.extend(suggestions)
            except Exception as e:
                print(f"Onboarding: Content generation warning: {e}")
                # Don't fail the whole request if generation fails
        
        return {
            "success": True,
            "message": "Onboarding completed successfully",
            "analysis": summary,
            "brand_profile": brand_profile,
            "generated_content": content_ideas
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Onboarding Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

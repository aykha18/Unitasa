"""
Client Onboarding API
Complete client onboarding workflow with analysis and knowledge base creation
"""

import asyncio
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import structlog
from datetime import datetime

# from app.agents.client_analysis import ClientAnalysisAgent # Moved to function scope
from app.agents.social_content_knowledge_base import get_social_content_knowledge_base
from app.llm.router import get_optimal_llm
from app.core.config import settings

logger = structlog.get_logger(__name__)

router = APIRouter()


# Pydantic models for request/response
class CompanyInfo(BaseModel):
    company_name: str = Field(..., description="Legal company name")
    brand_name: Optional[str] = Field(None, description="Brand/marketing name")
    industry: Optional[str] = Field("General Business", description="Primary industry (SaaS, Healthcare, Finance, etc.)")
    company_size: Optional[str] = Field("1-10", description="Employee count range")
    founding_year: Optional[int] = Field(None, description="When company was founded")
    headquarters: Optional[str] = Field(None, description="Location for localization")
    website: Optional[str] = Field(None, description="Company website URL")
    mission_statement: Optional[str] = Field(None, description="Company mission/values")
    brand_voice: Optional[str] = Field("professional", description="Professional, casual, technical, friendly")


class TargetAudience(BaseModel):
    primary_persona: Optional[str] = Field("General Customer", description="Main customer type (Founder, CTO, Marketing Manager)")
    secondary_personas: Optional[List[str]] = Field(default_factory=list, description="Additional customer types")
    pain_points: Optional[List[str]] = Field(default_factory=list, description="Customer problems/challenges")
    goals: Optional[List[str]] = Field(default_factory=list, description="Customer objectives")
    demographics: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Age range, company size, geography")


class BrandAssets(BaseModel):
    logo_url: Optional[str] = Field(None, description="Primary logo URL")
    brand_colors: Optional[List[str]] = Field(default_factory=list, description="Hex color codes")
    brand_fonts: Optional[List[str]] = Field(default_factory=list, description="Font families")
    visual_style: Optional[str] = Field("modern", description="Modern, traditional, minimalist, etc.")
    existing_content: Optional[List[str]] = Field(default_factory=list, description="URLs to existing marketing content")


class ContentPreferences(BaseModel):
    key_messages: Optional[List[str]] = Field(default_factory=list, description="3-5 core messages to communicate")
    competitors: Optional[List[str]] = Field(default_factory=list, description="Main competitors to differentiate from")
    unique_value_props: Optional[List[str]] = Field(default_factory=list, description="What makes them different")
    content_tone: Optional[str] = Field("professional", description="Professional, conversational, technical")
    taboo_topics: Optional[List[str]] = Field(default_factory=list, description="Topics to avoid")
    required_mentions: Optional[List[str]] = Field(default_factory=list, description="Must-include terms/phrases")


class SocialMediaAccounts(BaseModel):
    platforms: Optional[List[str]] = Field(default_factory=list, description="Active platforms (Twitter, LinkedIn, etc.)")
    existing_handles: Optional[Dict[str, str]] = Field(default_factory=dict, description="Current social media handles")
    posting_frequency: Optional[Dict[str, str]] = Field(default_factory=dict, description="Current posting frequency per platform")
    peak_times: Optional[Dict[str, str]] = Field(default_factory=dict, description="Known engagement times")
    competitor_handles: Optional[List[str]] = Field(default_factory=list, description="Competitors to monitor")


class PerformanceData(BaseModel):
    current_metrics: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Current engagement rates, follower counts")
    past_campaigns: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Previous campaign data")
    successful_content: Optional[List[str]] = Field(default_factory=list, description="High-performing posts/content")
    failed_content: Optional[List[str]] = Field(default_factory=list, description="Low-performing content to avoid")


class ClientOnboardingRequest(BaseModel):
    company_info: CompanyInfo
    target_audience: TargetAudience
    brand_assets: Optional[BrandAssets] = None
    content_preferences: ContentPreferences
    social_media_accounts: SocialMediaAccounts
    performance_data: Optional[PerformanceData] = None


class ClientOnboardingResponse(BaseModel):
    client_id: str
    onboarding_status: str
    knowledge_base_ready: bool
    sample_content_generated: int
    estimated_content_quality: float
    analysis_timestamp: str
    next_steps: Optional[List[str]] = None
    estimated_completion_time: Optional[str] = None


class ClientProfileResponse(BaseModel):
    client_id: str
    company_info: Dict[str, Any]
    brand_profile: Optional[Dict[str, Any]] = None
    audience_profile: Dict[str, Any]
    content_strategy: Dict[str, Any]
    features: Optional[List[Any]] = None
    how_it_works: Optional[List[Any]] = None
    assessments: Optional[List[Any]] = None

class UpdateClientProfileRequest(BaseModel):
    company_info: CompanyInfo
    target_audience: TargetAudience
    content_preferences: ContentPreferences
    features: Optional[List[Any]] = None
    how_it_works: Optional[List[Any]] = None
    assessments: Optional[List[Any]] = None

@router.get("/profile/{client_id}/knowledge")
async def get_client_knowledge_base(client_id: str):
    """Get knowledge base documents for a client"""
    from app.rag.vectorstore_manager import get_vector_store_manager
    
    try:
        manager = await get_vector_store_manager()
        documents = await manager.get_client_documents(client_id)
        
        # Simplify for frontend
        return {
            "client_id": client_id,
            "document_count": len(documents),
            "documents": [
                {
                    "id": doc["id"],
                    "title": doc["metadata"].get("title", "Untitled"),
                    "source": doc["metadata"].get("source", "unknown"),
                    "category": doc["metadata"].get("category", "General"),
                    "platform": doc["metadata"].get("platform", "General"),
                    "content_preview": doc["content"][:200] + "..." if len(doc["content"]) > 200 else doc["content"],
                    "added_at": doc["metadata"].get("added_at")
                }
                for doc in documents
            ]
        }
    except Exception as e:
        logger.error(f"Failed to get knowledge base: {e}")
        return {
            "client_id": client_id,
            "document_count": 0,
            "documents": [],
            "error": str(e)
        }

@router.get("/profile/{client_id}", response_model=ClientProfileResponse)
async def get_client_profile(client_id: str):
    """Get a client's profile"""
    try:
        kb = await get_social_content_knowledge_base()
        profile = await kb.get_client_profile(client_id)
        
        if not profile:
            raise HTTPException(status_code=404, detail="Client profile not found")
            
        return {
            "client_id": client_id,
            "company_info": profile.get("company_info", {}),
            "brand_profile": profile.get("brand_profile", {}),
            "audience_profile": profile.get("target_audience", {}),
            "content_strategy": profile.get("content_strategy", {}),
            "features": profile.get("features", []),
            "how_it_works": profile.get("how_it_works", []),
            "assessments": profile.get("assessments", [])
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get client profile: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get client profile: {str(e)}")

@router.put("/profile/{client_id}")
async def update_client_profile(client_id: str, request: UpdateClientProfileRequest):
    """Update a client's profile and regenerate their KB"""
    try:
        logger.info(f"Updating profile for client: {client_id}")
        kb = await get_social_content_knowledge_base()
        
        # Merge existing profile with updates
        current_profile = await kb.get_client_profile(client_id)
        
        # Update fields
        current_profile["company_info"] = request.company_info.dict()
        current_profile["target_audience"] = request.target_audience.dict()
        # Merge content strategy preferences
        if "content_strategy" not in current_profile:
            current_profile["content_strategy"] = {}
            
        current_profile["content_strategy"]["tone"] = request.content_preferences.content_tone
        current_profile["content_strategy"]["themes"] = request.content_preferences.key_messages
        
        if request.features is not None:
            current_profile["features"] = request.features
        if request.how_it_works is not None:
            current_profile["how_it_works"] = request.how_it_works
        if request.assessments is not None:
            current_profile["assessments"] = request.assessments
            
        updated_profile = await kb.update_client_profile(client_id, current_profile)
        
        return {
            "success": True,
            "message": "Profile updated and Knowledge Base regenerated",
            "profile": updated_profile
        }
    except Exception as e:
        logger.error(f"Failed to update client profile: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update client profile: {str(e)}")

@router.post("/analyze")
async def onboard_client(
    request: ClientOnboardingRequest, 
    background_tasks: BackgroundTasks
):
    platform_strategy: Dict[str, Any]
    onboarding_complete: bool
    estimated_content_quality: float


# Global agent instances (would be managed by dependency injection in production)
_client_analysis_agent = None
_knowledge_base = None


async def get_client_analysis_agent():
    """Get or create client analysis agent instance"""
    from app.agents.client_analysis import ClientAnalysisAgent
    global _client_analysis_agent
    if _client_analysis_agent is None:
        # Initialize knowledge base
        global _knowledge_base
        if _knowledge_base is None:
            try:
                _knowledge_base = await get_social_content_knowledge_base()
            except Exception as e:
                logger.warning(f"Knowledge base initialization failed: {e}")
                _knowledge_base = None

        # Initialize client analysis agent
        try:
            llm = get_optimal_llm("Analyze client brand voice and content strategy")
            _client_analysis_agent = ClientAnalysisAgent(llm, _knowledge_base)
        except Exception as e:
            logger.error(f"Client analysis agent initialization failed: {e}")
            raise HTTPException(status_code=500, detail=f"Agent initialization failed: {str(e)}")

    return _client_analysis_agent


@router.post("/onboard", response_model=ClientOnboardingResponse)
async def onboard_client(
    request: ClientOnboardingRequest,
    background_tasks: BackgroundTasks
) -> ClientOnboardingResponse:
    """
    Complete client onboarding workflow with analysis and knowledge base creation.

    This endpoint:
    1. Validates input data completeness
    2. Runs automated client analysis (brand voice, audience, competition)
    3. Creates client-specific knowledge base
    4. Generates initial content samples
    5. Sets up performance tracking

    Returns client ID and onboarding status.
    """

    try:
        logger.info(f"Starting client onboarding for {request.company_info.company_name}")

        # Get client analysis agent
        analysis_agent = await get_client_analysis_agent()

        # Convert request to dict for analysis
        client_data = request.dict()

        # Step 1: Validate input data
        validation_result = await validate_client_data(client_data)
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid input data: {', '.join(validation_result['errors'])}"
            )

        # Step 2: Run client analysis (this is the heavy lifting)
        client_profile = await analysis_agent.analyze_client(client_data)

        # Step 3: Create client knowledge base
        knowledge_base_result = await setup_client_knowledge_base(client_profile)
        
        # Save client profile to disk for persistence
        try:
            import json
            import os
            
            # Create data directory if it doesn't exist
            data_dir = os.path.join(os.getcwd(), "data", "clients")
            os.makedirs(data_dir, exist_ok=True)
            
            # Save profile
            file_path = os.path.join(data_dir, f"{client_profile['client_id']}.json")
            with open(file_path, "w") as f:
                # Convert datetime objects to strings if needed, though dict() usually handles it
                # For safety, we can use a custom encoder or just ensure basic types
                json.dump(client_profile, f, default=str, indent=2)
                
            logger.info(f"Persisted client profile to {file_path}")
        except Exception as e:
            logger.error(f"Failed to persist client profile: {e}")

        # Step 4: Generate initial content samples
        sample_content = await generate_initial_content_samples(
            client_profile["client_id"],
            client_profile
        )

        # Step 5: Setup performance tracking
        await setup_client_analytics(client_profile["client_id"])

        # Prepare response
        response = ClientOnboardingResponse(
            client_id=client_profile["client_id"],
            onboarding_status="complete",
            knowledge_base_ready=True,
            sample_content_generated=len(sample_content),
            estimated_content_quality=client_profile["estimated_content_quality"],
            analysis_timestamp=datetime.utcnow().isoformat(),
            next_steps=[
                "Review generated content samples",
                "Customize brand voice if needed",
                "Set up social media API connections",
                "Schedule first content campaign"
            ],
            estimated_completion_time="2-3 days"
        )

        logger.info(f"Client onboarding completed for {client_profile['client_id']}")

        # Background task for additional setup
        background_tasks.add_task(
            post_onboarding_setup,
            client_profile["client_id"],
            client_data
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Client onboarding failed: {e}")
        raise HTTPException(status_code=500, detail=f"Onboarding failed: {str(e)}")




@router.get("/profile/{client_id}", response_model=ClientProfileResponse)
async def get_client_profile(client_id: str):
    """Get client profile"""
    try:
        kb = await get_social_content_knowledge_base()
        profile = await kb.get_client_profile(client_id)
        
        # Ensure company_info exists and populate from brand_profile if needed
        if not isinstance(profile.get("company_info"), dict) or len(profile.get("company_info") or {}) == 0:
            bp = profile.get("brand_profile", {})
            if isinstance(bp, dict) and len(bp) > 0:
                ci = {}
                for key in [
                    "company_name",
                    "brand_name",
                    "industry",
                    "company_size",
                    "founding_year",
                    "headquarters",
                    "website",
                    "mission_statement",
                    "brand_voice",
                ]:
                    val = bp.get(key)
                    if val is not None:
                        ci[key] = val
                profile["company_info"] = ci
            else:
                profile["company_info"] = {}

        # Normalize content strategy themes for frontend
        if isinstance(profile.get("content_strategy"), dict):
            cs = profile["content_strategy"]
            if "themes" not in cs and "content_themes" in cs:
                cs["themes"] = cs.get("content_themes") or []
            profile["content_strategy"] = cs
        
        # Map audience pain_points for frontend if nested under primary_persona.psychographics
        if isinstance(profile.get("audience_profile"), dict):
            ap = profile["audience_profile"]
            if "pain_points" not in ap:
                pp = (
                    (ap.get("primary_persona") or {})
                    .get("psychographics", {})
                    .get("pain_points")
                )
                if isinstance(pp, list):
                    ap["pain_points"] = pp
            profile["audience_profile"] = ap

        # Normalize how_it_works for frontend (expects objects with title/description)
        if "how_it_works" in profile and isinstance(profile["how_it_works"], list):
            normalized_steps = []
            for i, item in enumerate(profile["how_it_works"]):
                if isinstance(item, str):
                    normalized_steps.append({
                        "step": i + 1,
                        "title": item,
                        "description": ""
                    })
                elif isinstance(item, dict):
                    # Ensure step number exists
                    if "step" not in item:
                        item["step"] = i + 1
                    normalized_steps.append(item)
            profile["how_it_works"] = normalized_steps

        # Normalize features for frontend
        if "features" in profile and isinstance(profile["features"], list):
            normalized_features = []
            for item in profile["features"]:
                if isinstance(item, str):
                    normalized_features.append({
                        "title": item,
                        "description": ""
                    })
                elif isinstance(item, dict):
                    normalized_features.append(item)
            profile["features"] = normalized_features

        # If essential sections are missing, try loading full profile from disk
        try:
            needs_enrichment = (
                not profile.get("features") and
                not profile.get("how_it_works") and
                not profile.get("audience_profile")
            )
            if needs_enrichment:
                import os, json
                data_dir = os.path.join(os.getcwd(), "data", "clients")
                file_path = os.path.join(data_dir, f"{client_id}.json")
                if os.path.exists(file_path):
                    with open(file_path, "r") as f:
                        disk_profile = json.load(f)
                    # Merge disk profile into current profile
                    for key in ["company_info", "brand_profile", "audience_profile", "content_strategy", "features", "how_it_works", "assessments"]:
                        if disk_profile.get(key) and not profile.get(key):
                            profile[key] = disk_profile[key]
        except Exception:
            pass

        return profile
    except Exception as e:
        logger.error(f"Failed to get client profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clients", response_model=List[Dict[str, Any]])
async def list_clients(status: Optional[str] = None) -> List[Dict[str, Any]]:
    """List all clients with optional status filter"""

    try:
        # In a real implementation, this would query the database
        # For now, return mock data

        mock_clients = [
            {
                "client_id": "client_acme_corp_1640995200",
                "company_name": "Acme Corporation",
                "industry": "Technology",
                "status": "active",
                "onboarding_date": "2024-01-15T10:00:00Z",
                "content_quality_score": 4.5,
                "platforms": ["LinkedIn", "Twitter", "Facebook"]
            },
            {
                "client_id": "client_techflow_1641081600",
                "company_name": "TechFlow Solutions",
                "industry": "SaaS",
                "status": "active",
                "onboarding_date": "2024-01-16T08:00:00Z",
                "content_quality_score": 4.2,
                "platforms": ["LinkedIn", "Twitter"]
            }
        ]

        if status:
            mock_clients = [c for c in mock_clients if c["status"] == status]

        return mock_clients

    except Exception as e:
        logger.error(f"Failed to list clients: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve clients")




@router.delete("/clients/{client_id}")
async def deactivate_client(client_id: str, reason: str = "contract_ended") -> Dict[str, Any]:
    """Deactivate a client account"""

    try:
        # Validate client exists
        if not client_id.startswith("client_"):
            raise HTTPException(status_code=404, detail="Client not found")

        # In a real implementation, this would mark client as inactive
        # Stop automated posting, archive data, etc.

        logger.info(f"Client deactivated: {client_id}, reason: {reason}")

        return {
            "client_id": client_id,
            "status": "deactivated",
            "deactivation_reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
            "data_retention": "30_days"  # Configurable retention policy
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to deactivate client: {e}")
        raise HTTPException(status_code=500, detail="Failed to deactivate client")


# Helper functions
async def validate_client_data(client_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate client onboarding data completeness"""

    errors = []
    warnings = []

    # Required fields validation
    required_fields = [
        "company_info.company_name",
        "company_info.industry",
        "target_audience.primary_persona"
    ]

    for field_path in required_fields:
        keys = field_path.split('.')
        value = client_data
        try:
            for key in keys:
                value = value[key]
            if not value or (isinstance(value, (list, dict)) and len(value) == 0):
                errors.append(f"Missing required field: {field_path}")
        except (KeyError, TypeError):
            errors.append(f"Missing required field: {field_path}")

    # Optional but recommended fields
    recommended_fields = [
        "brand_assets.logo_url",
        "performance_data.successful_content"
    ]

    for field_path in recommended_fields:
        keys = field_path.split('.')
        value = client_data
        try:
            for key in keys:
                if not isinstance(value, dict):
                    value = None
                    break
                value = value.get(key)
            
            if not value or (isinstance(value, (list, dict)) and len(value) == 0):
                warnings.append(f"Recommended field missing: {field_path}")
        except (KeyError, TypeError, AttributeError):
            warnings.append(f"Recommended field missing: {field_path}")

    # Business logic validations
    company_info = client_data.get("company_info", {})
    if company_info.get("founding_year") and company_info["founding_year"] > datetime.utcnow().year:
        errors.append("Founding year cannot be in the future")

    social_platforms = client_data.get("social_media_accounts", {}).get("platforms", [])
    # if len(social_platforms) == 0:
    #     errors.append("At least one social media platform must be specified")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "data_completeness": calculate_completeness_score(client_data)
    }


def calculate_completeness_score(client_data: Dict[str, Any]) -> float:
    """Calculate data completeness score (0-1)"""

    total_fields = 0
    completed_fields = 0

    def check_field(data: Dict, path: str) -> bool:
        keys = path.split('.')
        value = data
        try:
            for key in keys:
                value = value[key]
            return value is not None and (not isinstance(value, (list, dict)) or len(value) > 0)
        except (KeyError, TypeError):
            return False

    # Count all possible fields
    all_field_paths = [
        "company_info.company_name",
        "company_info.brand_name",
        "company_info.industry",
        "company_info.company_size",
        "company_info.founding_year",
        "company_info.headquarters",
        "company_info.website",
        "company_info.mission_statement",
        "company_info.brand_voice",
        "target_audience.primary_persona",
        "target_audience.secondary_personas",
        "target_audience.pain_points",
        "target_audience.goals",
        "target_audience.demographics",
        "brand_assets.logo_url",
        "brand_assets.brand_colors",
        "brand_assets.brand_fonts",
        "brand_assets.visual_style",
        "brand_assets.existing_content",
        "content_preferences.key_messages",
        "content_preferences.competitors",
        "content_preferences.unique_value_props",
        "content_preferences.content_tone",
        "content_preferences.taboo_topics",
        "content_preferences.required_mentions",
        "social_media_accounts.platforms",
        "social_media_accounts.existing_handles",
        "social_media_accounts.posting_frequency",
        "social_media_accounts.peak_times",
        "social_media_accounts.competitor_handles",
        "performance_data.current_metrics",
        "performance_data.past_campaigns",
        "performance_data.successful_content",
        "performance_data.failed_content"
    ]

    for field_path in all_field_paths:
        total_fields += 1
        if check_field(client_data, field_path):
            completed_fields += 1

    return completed_fields / total_fields if total_fields > 0 else 0


async def setup_client_knowledge_base(client_profile: Dict[str, Any]) -> Dict[str, Any]:
    """Setup client-specific knowledge base"""

    try:
        global _knowledge_base
        if _knowledge_base is None:
            _knowledge_base = await get_social_content_knowledge_base()

        # Create client knowledge base
        kb_result = await _knowledge_base.create_client_kb(
            client_profile["client_id"],
            client_profile
        )

        return {
            "status": "success",
            "knowledge_base_id": client_profile["client_id"],
            "templates_created": getattr(kb_result, 'template_count', 0),
            "patterns_created": getattr(kb_result, 'pattern_count', 0)
        }

    except Exception as e:
        logger.error(f"Knowledge base setup failed: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }


async def generate_initial_content_samples(client_id: str, client_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate initial content samples for client review using the Knowledge Base"""

    try:
        # Log profile data for debugging
        features = client_profile.get("features", [])
        how_it_works = client_profile.get("how_it_works", [])
        logger.info(f"Generating samples for {client_id}. Features: {len(features)}, Steps: {len(how_it_works)}")
        if not features:
            logger.warning(f"Client profile {client_id} has no features!")
        
        # Use the SocialContentKnowledgeBase to generate real, customized samples
        kb = await get_social_content_knowledge_base()
        
        # CRITICAL: Initialize the KB with the current profile data immediately
        # This ensures the KB has the features/steps in memory even if not yet saved to disk
        await kb.create_client_kb(client_id, client_profile)
        
        real_samples = []
        
        # 1. LinkedIn Educational Post
        try:
            linkedin_content = await kb.get_client_content(client_id, {
                "platform": "linkedin",
                "content_type": "educational",
                "topic": "industry trends"
            })
            if linkedin_content:
                real_samples.extend(linkedin_content[:1])
            else:
                logger.warning(f"No LinkedIn content generated for {client_id}")
        except Exception as e:
            logger.warning(f"Failed to generate LinkedIn sample: {e}")

        # 2. Twitter Engagement Post
        try:
            twitter_content = await kb.get_client_content(client_id, {
                "platform": "twitter",
                "content_type": "engagement",
                "topic": "community question"
            })
            if twitter_content:
                real_samples.extend(twitter_content[:1])
            else:
                logger.warning(f"No Twitter content generated for {client_id}")
        except Exception as e:
            logger.warning(f"Failed to generate Twitter sample: {e}")

        if real_samples:
            return real_samples

        # Fallback to mock samples if generation fails or returns nothing
        logger.warning("Falling back to mock samples due to generation failure or empty result")
        
        company_name = client_profile.get("company_info", {}).get("company_name", "Our Company")
        industry = client_profile.get("company_info", {}).get("industry", "industry")

        samples = [
            {
                "platform": "LinkedIn",
                "content_type": "educational",
                "content": f"🚀 How {company_name} is transforming the {industry} landscape...",
                "hashtags": ["#Business", "#Innovation", "#Leadership"],
                "character_count": 245
            },
            {
                "platform": "Twitter",
                "content_type": "engagement",
                "content": f"What's your biggest challenge in {industry}? We're here to help! #Business #Growth",
                "hashtags": ["#Business", "#Growth"],
                "character_count": 128
            }
        ]

        return samples

    except Exception as e:
        logger.error(f"Content sample generation failed: {e}")
        return []


async def setup_client_analytics(client_id: str) -> Dict[str, Any]:
    """Setup performance tracking for new client"""

    try:
        # In a real implementation, this would initialize analytics tracking
        # Set up dashboards, metrics collection, etc.

        return {
            "analytics_setup": "complete",
            "tracking_metrics": ["engagement_rate", "reach", "clicks", "conversions"],
            "reporting_schedule": "weekly",
            "dashboard_url": f"/analytics/clients/{client_id}"
        }

    except Exception as e:
        logger.error(f"Analytics setup failed: {e}")
        return {"analytics_setup": "failed", "error": str(e)}


async def post_onboarding_setup(client_id: str, client_data: Dict[str, Any]):
    """Background tasks for post-onboarding setup"""

    try:
        logger.info(f"Running post-onboarding setup for {client_id}")

        # Additional setup tasks:
        # - Schedule welcome email
        # - Setup automated reporting
        # - Initialize content calendar
        # - Configure platform integrations

        # Mock implementation
        await asyncio.sleep(1)  # Simulate work

        logger.info(f"Post-onboarding setup completed for {client_id}")

    except Exception as e:
        logger.error(f"Post-onboarding setup failed for {client_id}: {e}")

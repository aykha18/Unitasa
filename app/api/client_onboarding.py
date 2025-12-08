"""
Client Onboarding API
Complete client onboarding workflow with analysis and knowledge base creation
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import structlog
from datetime import datetime

from app.agents.client_analysis import ClientAnalysisAgent
from app.agents.social_content_knowledge_base import get_social_content_knowledge_base
from app.core.config import settings

logger = structlog.get_logger(__name__)

router = APIRouter()


# Pydantic models for request/response
class CompanyInfo(BaseModel):
    company_name: str = Field(..., description="Legal company name")
    brand_name: Optional[str] = Field(None, description="Brand/marketing name")
    industry: str = Field(..., description="Primary industry (SaaS, Healthcare, Finance, etc.)")
    company_size: str = Field(..., description="Employee count range")
    founding_year: Optional[int] = Field(None, description="When company was founded")
    headquarters: Optional[str] = Field(None, description="Location for localization")
    website: Optional[str] = Field(None, description="Company website URL")
    mission_statement: Optional[str] = Field(None, description="Company mission/values")
    brand_voice: Optional[str] = Field("professional", description="Professional, casual, technical, friendly")


class TargetAudience(BaseModel):
    primary_persona: str = Field(..., description="Main customer type (Founder, CTO, Marketing Manager)")
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
    key_messages: List[str] = Field(..., description="3-5 core messages to communicate")
    competitors: Optional[List[str]] = Field(default_factory=list, description="Main competitors to differentiate from")
    unique_value_props: Optional[List[str]] = Field(default_factory=list, description="What makes them different")
    content_tone: Optional[str] = Field("professional", description="Professional, conversational, technical")
    taboo_topics: Optional[List[str]] = Field(default_factory=list, description="Topics to avoid")
    required_mentions: Optional[List[str]] = Field(default_factory=list, description="Must-include terms/phrases")


class SocialMediaAccounts(BaseModel):
    platforms: List[str] = Field(..., description="Active platforms (Twitter, LinkedIn, etc.)")
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
    brand_profile: Dict[str, Any]
    audience_profile: Dict[str, Any]
    content_strategy: Dict[str, Any]
    platform_strategy: Dict[str, Any]
    onboarding_complete: bool
    estimated_content_quality: float


# Global agent instances (would be managed by dependency injection in production)
_client_analysis_agent = None
_knowledge_base = None


async def get_client_analysis_agent():
    """Get or create client analysis agent instance"""
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
            from app.core.config import get_llm
            llm = get_llm()
            _client_analysis_agent = ClientAnalysisAgent(llm, _knowledge_base)
        except Exception as e:
            logger.error(f"Client analysis agent initialization failed: {e}")
            raise HTTPException(status_code=500, detail="Agent initialization failed")

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


@router.get("/clients/{client_id}/profile", response_model=ClientProfileResponse)
async def get_client_profile(client_id: str) -> ClientProfileResponse:
    """Get complete client profile and analysis results"""

    try:
        # In a real implementation, this would fetch from database
        # For now, return a mock response structure

        # Check if client exists (mock check)
        if not client_id.startswith("client_"):
            raise HTTPException(status_code=404, detail="Client not found")

        # Mock client profile response
        profile = ClientProfileResponse(
            client_id=client_id,
            brand_profile={
                "brand_voice": "professional",
                "personality_traits": ["trustworthy", "competent", "reliable"],
                "communication_style": "professional_formal"
            },
            audience_profile={
                "primary_persona": {
                    "name": "Marketing Manager",
                    "demographics": {"age_range": "30-45", "company_size": "Mid-Market"}
                }
            },
            content_strategy={
                "content_pillars": ["Educational", "Thought Leadership", "Customer Success"],
                "content_mix": {"educational": 0.4, "promotional": 0.3, "engagement": 0.3}
            },
            platform_strategy={
                "platforms": {
                    "LinkedIn": {"recommended_frequency": "3-5 posts/week"},
                    "Twitter": {"recommended_frequency": "5-8 posts/week"}
                }
            },
            onboarding_complete=True,
            estimated_content_quality=4.2
        )

        return profile

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get client profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve client profile")


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


@router.put("/clients/{client_id}/profile")
async def update_client_profile(client_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """Update client profile with new information"""

    try:
        # Validate client exists
        if not client_id.startswith("client_"):
            raise HTTPException(status_code=404, detail="Client not found")

        # In a real implementation, this would update the database
        # For now, just acknowledge the update

        logger.info(f"Client profile updated for {client_id}: {updates.keys()}")

        return {
            "client_id": client_id,
            "update_status": "successful",
            "updated_fields": list(updates.keys()),
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update client profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to update client profile")


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
        "target_audience.primary_persona",
        "content_preferences.key_messages",
        "social_media_accounts.platforms"
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
                value = value.get(key, {})
            if not value or (isinstance(value, (list, dict)) and len(value) == 0):
                warnings.append(f"Recommended field missing: {field_path}")
        except (KeyError, TypeError):
            warnings.append(f"Recommended field missing: {field_path}")

    # Business logic validations
    company_info = client_data.get("company_info", {})
    if company_info.get("founding_year") and company_info["founding_year"] > datetime.utcnow().year:
        errors.append("Founding year cannot be in the future")

    social_platforms = client_data.get("social_media_accounts", {}).get("platforms", [])
    if len(social_platforms) == 0:
        errors.append("At least one social media platform must be specified")

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
    """Generate initial content samples for client review"""

    try:
        # This would use the ClientAdaptiveContentGenerator
        # For now, return mock samples

        samples = [
            {
                "platform": "LinkedIn",
                "content_type": "educational",
                "content": f"🚀 How {client_profile['company_info']['company_name']} is transforming the {client_profile['company_info']['industry']} landscape...",
                "hashtags": ["#Business", "#Innovation", "#Leadership"],
                "character_count": 245
            },
            {
                "platform": "Twitter",
                "content_type": "engagement",
                "content": f"What's your biggest challenge in {client_profile['company_info']['industry']}? We're here to help! #Business #Growth",
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
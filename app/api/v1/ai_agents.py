"""
New AI Agent API endpoints using cost-optimized OpenRouter + Groq + OpenAI fallback
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from app.agents.ingestion_agent import get_ingestion_agent, ingest_website
from app.agents.knowledge_base_agent import get_knowledge_base_agent, store_content, search_content
from app.agents.business_analysis_agent import get_business_analysis_agent, analyze_business_profile
from app.agents.content_generation_agent import get_content_generation_agent, generate_social_post, generate_blog_post
from app.agents.base import get_agent_registry
from app.llm.router import get_llm_router
# Simple API key auth for development - replace with proper JWT auth in production
from fastapi import Header, HTTPException

async def get_api_key(authorization: str = Header(None, alias="Authorization")):
    """Simple API key validation for development"""
    if not authorization:
        # For development, allow requests without auth
        return "dev-key"
    return authorization

router = APIRouter()


# Pydantic models for API requests/responses
class WebsiteIngestionRequest(BaseModel):
    """Website ingestion request"""
    url: str = Field(..., description="Website URL to analyze")
    client_id: Optional[str] = Field("default", description="Client identifier")


class ContentStorageRequest(BaseModel):
    """Content storage request"""
    content: str = Field(..., description="Content to store")
    client_id: str = Field(..., description="Client identifier")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ContentSearchRequest(BaseModel):
    """Content search request"""
    query: str = Field(..., description="Search query")
    client_id: str = Field(..., description="Client identifier")
    limit: Optional[int] = Field(5, description="Maximum results to return")


class BusinessAnalysisRequest(BaseModel):
    """Business analysis request"""
    client_data: Optional[Dict[str, Any]] = Field(None, description="Direct client data")
    website_summary: Optional[Dict[str, Any]] = Field(None, description="Website analysis summary")
    knowledge_context: Optional[List[Dict[str, Any]]] = Field(None, description="Additional knowledge context")


class ContentGenerationRequest(BaseModel):
    """Content generation request"""
    content_type: str = Field(..., description="Type of content (social_post, blog_post, ad_copy)")
    topic: str = Field(..., description="Content topic")
    platform: Optional[str] = Field(None, description="Platform for social posts")
    business_profile: Optional[Dict[str, Any]] = Field(None, description="Business profile context")
    tone: Optional[str] = Field("professional", description="Content tone")
    target_length: Optional[str] = Field("medium", description="Content length for blog posts")


class AgentHealthResponse(BaseModel):
    """Agent health status"""
    agent_name: str
    status: str
    last_check: str
    error: Optional[str] = None


class SystemHealthResponse(BaseModel):
    """System health response"""
    status: str
    timestamp: str
    agents: Dict[str, Dict[str, Any]]
    llm_providers: Dict[str, Any]
    overall_health: str


@router.post("/ingest/website")
async def ingest_website_endpoint(
    request: WebsiteIngestionRequest,
    api_key: str = Depends(get_api_key)
):
    """Ingest and analyze a website"""
    try:
        result = await ingest_website(request.url)

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Ingestion failed"))

        return {
            "success": True,
            "url": request.url,
            "client_id": request.client_id,
            "analysis": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Website ingestion failed: {str(e)}")


@router.post("/knowledge/store")
async def store_content_endpoint(
    request: ContentStorageRequest,
    api_key: str = Depends(get_api_key)
):
    """Store content in knowledge base"""
    try:
        result = await store_content(
            content=request.content,
            client_id=request.client_id,
            metadata=request.metadata
        )

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Storage failed"))

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content storage failed: {str(e)}")


@router.post("/knowledge/search")
async def search_content_endpoint(
    request: ContentSearchRequest,
    api_key: str = Depends(get_api_key)
):
    """Search content in knowledge base"""
    try:
        result = await search_content(
            query=request.query,
            client_id=request.client_id,
            limit=request.limit
        )

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Search failed"))

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content search failed: {str(e)}")


@router.post("/business/analyze")
async def analyze_business_endpoint(
    request: BusinessAnalysisRequest,
    api_key: str = Depends(get_api_key)
):
    """Analyze business and create profile"""
    try:
        result = await analyze_business_profile(
            client_data=request.client_data or {},
            website_summary=request.website_summary or {},
            knowledge_context=request.knowledge_context or []
        )

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Analysis failed"))

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Business analysis failed: {str(e)}")


@router.post("/content/generate")
async def generate_content_endpoint(
    request: ContentGenerationRequest,
    api_key: str = Depends(get_api_key)
):
    """Generate marketing content"""
    try:
        agent = get_content_generation_agent()

        if request.content_type == "social_post":
            if not request.platform:
                raise HTTPException(status_code=400, detail="Platform required for social posts")

            result = await generate_social_post(
                platform=request.platform,
                topic=request.topic,
                business_profile=request.business_profile,
                tone=request.tone
            )

        elif request.content_type == "blog_post":
            result = await generate_blog_post(
                topic=request.topic,
                business_profile=request.business_profile,
                target_length=request.target_length,
                tone=request.tone
            )

        else:
            # Generic content generation
            task_input = {
                "content_type": request.content_type,
                "topic": request.topic,
                "platform": request.platform,
                "business_profile": request.business_profile,
                "tone": request.tone,
                "target_length": request.target_length
            }
            result = await agent.execute_task(task_input)

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Content generation failed"))

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")


@router.get("/health", response_model=SystemHealthResponse)
async def get_system_health(api_key: str = Depends(get_api_key)):
    """Get system health status"""
    try:
        # Get agent health
        registry = get_agent_registry()
        agent_health = await registry.health_check_all()

        # Get LLM router status
        llm_router = get_llm_router()
        llm_stats = llm_router.get_usage_stats()
        available_providers = llm_router.get_available_providers()

        # Determine overall health
        agent_healthy = all(
            health.get("status") == "healthy"
            for health in agent_health.values()
        )
        llm_healthy = len(available_providers) > 0

        overall_health = "healthy" if (agent_healthy and llm_healthy) else "degraded"

        return SystemHealthResponse(
            status="healthy" if overall_health == "healthy" else "degraded",
            timestamp=datetime.utcnow().isoformat(),
            agents=agent_health,
            llm_providers={
                "available_providers": available_providers,
                "usage_stats": llm_stats
            },
            overall_health=overall_health
        )

    except Exception as e:
        return SystemHealthResponse(
            status="unhealthy",
            timestamp=datetime.utcnow().isoformat(),
            agents={},
            llm_providers={"error": str(e)},
            overall_health="error"
        )


@router.get("/agents")
async def get_available_agents(api_key: str = Depends(get_api_key)):
    """Get information about available agents"""
    registry = get_agent_registry()
    return {
        "agents": registry.list_agents(),
        "count": len(registry.list_agents())
    }


@router.get("/llm/stats")
async def get_llm_stats(api_key: str = Depends(get_api_key)):
    """Get LLM usage statistics"""
    llm_router = get_llm_router()
    return {
        "usage_stats": llm_router.get_usage_stats(),
        "available_providers": llm_router.get_available_providers()
    }


# Test endpoints for development
@router.get("/test/ingestion")
async def test_ingestion(api_key: str = Depends(get_api_key)):
    """Test website ingestion with a sample URL"""
    try:
        result = await ingest_website("https://example.com")
        return {
            "test": "ingestion",
            "success": result["success"],
            "result": result
        }
    except Exception as e:
        return {
            "test": "ingestion",
            "success": False,
            "error": str(e)
        }


@router.get("/test/content-generation")
async def test_content_generation(api_key: str = Depends(get_api_key)):
    """Test content generation"""
    try:
        result = await generate_social_post(
            platform="twitter",
            topic="AI Marketing",
            business_profile={"brand_positioning": {"industry_sector": "technology"}}
        )
        return {
            "test": "content_generation",
            "success": result["success"],
            "result": result
        }
    except Exception as e:
        return {
            "test": "content_generation",
            "success": False,
            "error": str(e)
        }


@router.get("/test/business-analysis")
async def test_business_analysis(api_key: str = Depends(get_api_key)):
    """Test business analysis"""
    try:
        result = await analyze_business_profile(
            client_data={"company_name": "Test Corp", "industry": "technology"},
            website_summary={"business_offering": "Software solutions"}
        )
        return {
            "test": "business_analysis",
            "success": result["success"],
            "result": result
        }
    except Exception as e:
        return {
            "test": "business_analysis",
            "success": False,
            "error": str(e)
        }
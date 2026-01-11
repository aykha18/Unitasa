"""
Shared state management for marketing agents using LangGraph
"""

from typing import Dict, Any, List, Optional
from typing_extensions import TypedDict
from datetime import datetime


class MarketingAgentState(TypedDict):
    """Shared state across all marketing agents"""

    # Campaign configuration
    campaign_config: Dict[str, Any]
    campaign_id: Optional[str]

    # Audience and lead data
    target_audience: Dict[str, Any]
    leads: List[Dict[str, Any]]
    qualified_leads: List[Dict[str, Any]]

    # Content data
    content_requirements: Dict[str, Any]
    generated_content: List[Dict[str, Any]]
    content_performance: Dict[str, Any]

    # Ad campaign data
    ad_platforms: List[str]
    ad_creatives: List[Dict[str, Any]]
    campaign_performance: Dict[str, Any]

    # Agent coordination
    current_agent: str
    next_agent: Optional[str]
    agent_messages: List[Dict[str, Any]]

    # Error handling
    errors: List[Dict[str, Any]]

    # Metadata
    created_at: str
    updated_at: str


def create_initial_state(campaign_config: Dict[str, Any]) -> MarketingAgentState:
    """Create initial state for a marketing campaign"""
    return MarketingAgentState(
        campaign_config=campaign_config,
        campaign_id=None,
        target_audience=campaign_config.get('target_audience', {}),
        client_profile={},
        brand_profile={},
        leads=[],
        qualified_leads=[],
        content_requirements=campaign_config.get('content_requirements', {}),
        generated_content=[],
        ad_platforms=campaign_config.get('ad_platforms', []),
        ad_creatives=[],
        campaign_performance={},
        current_agent="lead_generation",
        agent_messages=[],
        errors=[],
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat()
    )


def update_state_timestamp(state: MarketingAgentState) -> MarketingAgentState:
    """Update the updated_at timestamp in state"""
    state["updated_at"] = datetime.utcnow().isoformat()
    return state

"""
BusinessAnalysisAgent - Client Profiling and Analysis
Analyzes client data to build comprehensive business profiles
"""

import logging
from typing import Dict, Any, List, Optional

from app.agents.base import CostOptimizedAgent

logger = logging.getLogger(__name__)


class BusinessAnalysisAgent(CostOptimizedAgent):
    """
    Agent responsible for analyzing client businesses and creating structured profiles
    """

    def __init__(self, name: str = "business_analysis"):
        super().__init__(name)

    def get_system_prompt(self) -> str:
        return """You are a senior business strategist and market analyst. Your expertise includes:

1. Business model analysis and revenue stream identification
2. Target audience profiling and segmentation
3. Competitive positioning and differentiation
4. Market opportunity assessment
5. Growth strategy development

You provide data-driven insights that help businesses understand their market position and growth opportunities."""

    async def execute_task(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute business analysis tasks
        """
        task_type = task_input.get("task_type", "profile_analysis")

        if task_type == "profile_analysis":
            return await self._analyze_business_profile(task_input)
        elif task_type == "competitor_analysis":
            return await self._analyze_competition(task_input)
        elif task_type == "market_opportunities":
            return await self._identify_market_opportunities(task_input)
        else:
            return {
                "success": False,
                "error": f"Unsupported task type: {task_type}"
            }

    async def _analyze_business_profile(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create comprehensive business profile from client data
        """
        client_data = task_input.get("client_data", {})
        website_summary = task_input.get("website_summary", {})
        knowledge_context = task_input.get("knowledge_context", [])

        if not client_data and not website_summary:
            return {"success": False, "error": "No client data provided"}

        try:
            # Build comprehensive analysis prompt
            analysis_prompt = self._build_profile_analysis_prompt(
                client_data, website_summary, knowledge_context
            )

            # Generate business profile
            response = await self.generate_response(
                user_prompt=analysis_prompt,
                task_description="comprehensive business profile analysis"
            )

            if not response["success"]:
                return response

            # Parse and structure the response
            profile_data = self._parse_profile_response(response["content"])

            return {
                "success": True,
                "task_type": "profile_analysis",
                "business_profile": profile_data,
                "confidence_score": self._calculate_profile_confidence(profile_data),
                "analysis_metadata": {
                    "data_sources": len(knowledge_context) + (1 if website_summary else 0),
                    "processing_cost": response.get("cost", 0),
                    "provider_used": response.get("provider", "unknown")
                }
            }

        except Exception as e:
            logger.error(f"Business profile analysis failed: {e}")
            return {"success": False, "error": str(e)}

    async def _analyze_competition(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze competitive landscape
        """
        business_profile = task_input.get("business_profile", {})
        competitor_data = task_input.get("competitor_data", [])

        if not business_profile:
            return {"success": False, "error": "Business profile required for competitor analysis"}

        try:
            analysis_prompt = f"""
Based on this business profile, analyze the competitive landscape:

BUSINESS PROFILE:
{self._format_business_profile(business_profile)}

COMPETITOR DATA:
{competitor_data if competitor_data else "No specific competitor data provided"}

Provide:
1. Main competitors and their positioning
2. Competitive advantages and disadvantages
3. Market gaps and opportunities
4. Recommended differentiation strategies

Return structured analysis in JSON format.
"""

            response = await self.generate_response(
                user_prompt=analysis_prompt,
                task_description="competitive landscape analysis"
            )

            if response["success"]:
                competitor_analysis = self._parse_competitor_response(response["content"])
                return {
                    "success": True,
                    "task_type": "competitor_analysis",
                    "competitor_analysis": competitor_analysis
                }
            else:
                return response

        except Exception as e:
            logger.error(f"Competitor analysis failed: {e}")
            return {"success": False, "error": str(e)}

    async def _identify_market_opportunities(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Identify market opportunities and growth strategies
        """
        business_profile = task_input.get("business_profile", {})
        competitor_analysis = task_input.get("competitor_analysis", {})

        if not business_profile:
            return {"success": False, "error": "Business profile required"}

        try:
            analysis_prompt = f"""
Based on the business profile and competitive analysis, identify market opportunities:

BUSINESS PROFILE:
{self._format_business_profile(business_profile)}

COMPETITIVE ANALYSIS:
{competitor_analysis if competitor_analysis else "No competitor analysis available"}

Identify:
1. Underserved market segments
2. New product/service opportunities
3. Partnership or acquisition opportunities
4. Geographic expansion possibilities
5. Digital transformation opportunities

Return prioritized list of opportunities with implementation difficulty and potential impact.
"""

            response = await self.generate_response(
                user_prompt=analysis_prompt,
                task_description="market opportunity identification"
            )

            if response["success"]:
                opportunities = self._parse_opportunities_response(response["content"])
                return {
                    "success": True,
                    "task_type": "market_opportunities",
                    "market_opportunities": opportunities
                }
            else:
                return response

        except Exception as e:
            logger.error(f"Market opportunity analysis failed: {e}")
            return {"success": False, "error": str(e)}

    def _build_profile_analysis_prompt(self, client_data: Dict, website_summary: Dict, knowledge_context: List) -> str:
        """Build comprehensive business profile analysis prompt"""

        context_str = ""
        if knowledge_context:
            context_str = "\n\nADDITIONAL CONTEXT:\n" + "\n".join([
                f"- {ctx.get('content', '')[:200]}..." for ctx in knowledge_context[:3]
            ])

        return f"""
Analyze this business information and create a comprehensive business profile:

CLIENT DATA:
{client_data if client_data else "No direct client data provided"}

WEBSITE SUMMARY:
{website_summary if website_summary else "No website summary available"}{context_str}

Create a structured business profile that includes:

1. **Business Model & Revenue**
   - Primary business model (B2B, B2C, marketplace, etc.)
   - Main revenue streams
   - Pricing strategy indicators

2. **Target Audience & Market**
   - Ideal customer profile (ICP)
   - Market size and maturity
   - Geographic focus

3. **Value Proposition & Differentiation**
   - Core value proposition
   - Unique selling points
   - Competitive advantages

4. **Brand & Positioning**
   - Brand personality and tone
   - Market positioning
   - Industry sector

5. **Growth & Challenges**
   - Current growth stage
   - Main challenges or weaknesses
   - Growth opportunities

Return the analysis in this exact JSON format:
{{
    "business_model": {{
        "type": "B2B/B2C/etc",
        "revenue_streams": ["stream1", "stream2"],
        "pricing_model": "subscription/freemium/etc"
    }},
    "target_audience": {{
        "icp": "detailed description",
        "market_size": "estimate",
        "geographic_focus": "local/regional/global"
    }},
    "value_proposition": {{
        "core_offer": "main value",
        "unique_selling_points": ["usp1", "usp2"],
        "competitive_advantages": ["adv1", "adv2"]
    }},
    "brand_positioning": {{
        "personality": "professional/friendly/innovative",
        "market_position": "leader/challenger/follower",
        "industry_sector": "technology/healthcare/etc"
    }},
    "growth_analysis": {{
        "current_stage": "startup/growth/mature",
        "challenges": ["challenge1", "challenge2"],
        "opportunities": ["opp1", "opp2"]
    }}
}}
"""

    def _parse_profile_response(self, response_content: str) -> Dict[str, Any]:
        """Parse AI response into structured business profile"""
        import json

        try:
            # Extract JSON from response
            json_start = response_content.find('{')
            json_end = response_content.rfind('}') + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response_content[json_start:json_end]
                return json.loads(json_str)
            else:
                # Fallback structure
                return {
                    "business_model": {"type": "unknown", "revenue_streams": [], "pricing_model": "unknown"},
                    "target_audience": {"icp": "unknown", "market_size": "unknown", "geographic_focus": "unknown"},
                    "value_proposition": {"core_offer": response_content[:200], "unique_selling_points": [], "competitive_advantages": []},
                    "brand_positioning": {"personality": "unknown", "market_position": "unknown", "industry_sector": "unknown"},
                    "growth_analysis": {"current_stage": "unknown", "challenges": [], "opportunities": []}
                }
        except Exception as e:
            logger.error(f"Failed to parse profile response: {e}")
            return {"error": "Failed to parse analysis", "raw_response": response_content[:500]}

    def _parse_competitor_response(self, response_content: str) -> Dict[str, Any]:
        """Parse competitor analysis response"""
        # Simplified parsing - would be more sophisticated in production
        return {
            "main_competitors": [],
            "competitive_advantages": [],
            "market_gaps": [],
            "differentiation_strategies": [],
            "raw_analysis": response_content
        }

    def _parse_opportunities_response(self, response_content: str) -> List[Dict[str, Any]]:
        """Parse market opportunities response"""
        # Simplified parsing
        return [
            {
                "opportunity": "Identified from analysis",
                "description": response_content[:200],
                "impact": "medium",
                "difficulty": "medium",
                "timeline": "3-6 months"
            }
        ]

    def _format_business_profile(self, profile: Dict) -> str:
        """Format business profile for prompts"""
        return "\n".join([
            f"- Business Model: {profile.get('business_model', {}).get('type', 'Unknown')}",
            f"- Target Audience: {profile.get('target_audience', {}).get('icp', 'Unknown')}",
            f"- Value Proposition: {profile.get('value_proposition', {}).get('core_offer', 'Unknown')}",
            f"- Industry: {profile.get('brand_positioning', {}).get('industry_sector', 'Unknown')}"
        ])

    def _calculate_profile_confidence(self, profile: Dict) -> float:
        """Calculate confidence score for business profile"""
        filled_fields = 0
        total_fields = 0

        def count_filled(obj, path=""):
            nonlocal filled_fields, total_fields
            if isinstance(obj, dict):
                for key, value in obj.items():
                    total_fields += 1
                    if value and value != "unknown" and value != []:
                        filled_fields += 1
                    elif isinstance(value, (dict, list)):
                        count_filled(value, f"{path}.{key}")
            elif isinstance(obj, list):
                total_fields += 1
                if len(obj) > 0:
                    filled_fields += 1

        count_filled(profile)
        return filled_fields / max(total_fields, 1)


# Convenience functions
async def analyze_business_profile(client_data: Dict, website_summary: Dict = None, knowledge_context: List = None) -> Dict[str, Any]:
    """Analyze business and create comprehensive profile"""
    agent = BusinessAnalysisAgent()
    return await agent.execute_task({
        "task_type": "profile_analysis",
        "client_data": client_data,
        "website_summary": website_summary or {},
        "knowledge_context": knowledge_context or []
    })


def get_business_analysis_agent() -> BusinessAnalysisAgent:
    """Get business analysis agent instance"""
    return BusinessAnalysisAgent()
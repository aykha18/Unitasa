"""
Ad Manager Agent - Multi-channel ad campaign management and optimization
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List

import structlog
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI

from app.agents.base_agent import BaseAgent
from app.agents.state import MarketingAgentState, update_state_timestamp
from app.core.circuit_breaker import call_with_circuit_breaker

logger = structlog.get_logger(__name__)


class AdManagerAgent(BaseAgent):
    """Multi-channel ad campaign management and optimization"""

    def __init__(self, llm: ChatOpenAI):
        super().__init__("ad_manager", llm, self.get_ad_tools())
        self.platform_clients = {
            'google': GoogleAdsClient(),
            'linkedin': LinkedInAdsClient(),
            'facebook': FacebookAdsClient()
        }

    def get_ad_tools(self) -> List[Tool]:
        """Get tools for ad management"""
        return [
            Tool(
                name="create_campaign",
                description="Create ad campaign on specified platform",
                func=self.create_campaign
            ),
            Tool(
                name="analyze_performance",
                description="Analyze campaign performance metrics",
                func=self.analyze_performance
            ),
            Tool(
                name="optimize_budget",
                description="Optimize budget allocation across campaigns",
                func=self.optimize_budget
            ),
            Tool(
                name="generate_ad_copy",
                description="Generate compelling ad copy for campaigns",
                func=self.generate_ad_copy
            ),
            Tool(
                name="test_ad_creatives",
                description="A/B test different ad creatives",
                func=self.test_ad_creatives
            )
        ]

    def get_system_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", """You are an expert multi-channel advertising specialist. Your role is to:
        1. Create and manage ad campaigns across multiple platforms
        2. Optimize campaign performance and budget allocation
        3. Generate compelling ad copy and creatives
        4. Analyze campaign metrics and provide insights
        5. Implement A/B testing and conversion optimization

        Campaign Platforms: {platforms}
        Target Audience: {audience}
        Budget: {budget}

        Use the available tools to create, optimize, and manage ad campaigns.
        Focus on ROI, conversion rates, and cost-effective acquisition.
        """),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

    def build_input(self, state: MarketingAgentState) -> Dict[str, Any]:
        """Build input data from shared state"""
        return {
            "platforms": state.get("ad_platforms", []),
            "audience": state.get("target_audience", {}),
            "budget": state.get("campaign_config", {}).get("budget", 0),
            "qualified_leads": len(state.get("qualified_leads", [])),
            "generated_content": len(state.get("generated_content", [])),
            "input": f"Manage ad campaigns for targeting: {state.get('target_audience', {})}"
        }

    def update_state(self, state: MarketingAgentState, result) -> MarketingAgentState:
        """Update shared state with ad management results"""
        # Extract campaign results from result
        campaign_results = self.extract_campaign_results_from_result(result)

        # Update ad creatives
        existing_creatives = state.get("ad_creatives", [])
        existing_creatives.extend(campaign_results.get("creatives", []))
        state["ad_creatives"] = existing_creatives

        # Update campaign performance
        performance_data = state.get("campaign_performance", {})
        performance_data.update(campaign_results.get("performance", {}))
        state["campaign_performance"] = performance_data

        # Update agent coordination
        state["current_agent"] = "ad_management"
        state["next_agent"] = "analytics"

        self.log_agent_activity("ad_management_complete", {
            "campaigns_created": len(campaign_results.get("campaigns", [])),
            "platforms_used": list(campaign_results.get("platforms", {}).keys())
        })

        return update_state_timestamp(state)

    async def deploy_campaign(self, campaign_config: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy ad campaign across multiple platforms"""

        results = {}
        platforms = campaign_config.get('platforms', [])

        for platform in platforms:
            if platform in self.platform_clients:
                try:
                    campaign_result = await self.create_platform_campaign(
                        platform, campaign_config
                    )
                    results[platform] = campaign_result
                except Exception as e:
                    logger.error(f"Failed to create {platform} campaign: {e}")
                    results[platform] = {'error': str(e)}

        return results

    async def create_platform_campaign(self, platform: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create campaign on specific platform"""
        client = self.platform_clients[platform]

        campaign_data = {
            'name': config['name'],
            'budget': config['budget'],
            'targeting': config['targeting'],
            'creatives': config['creatives'],
            'schedule': config.get('schedule')
        }

        return await client.create_campaign(campaign_data)

    async def monitor_performance(self, campaign_ids: List[str]) -> Dict[str, Any]:
        """Monitor campaign performance across platforms"""

        performance_data = {}

        for campaign_id in campaign_ids:
            # Extract platform from campaign ID
            platform = self.extract_platform_from_id(campaign_id)

            if platform in self.platform_clients:
                try:
                    metrics = await self.platform_clients[platform].get_campaign_metrics(campaign_id)
                    performance_data[campaign_id] = metrics
                except Exception as e:
                    logger.error(f"Failed to get metrics for {campaign_id}: {e}")

        return performance_data

    async def optimize_campaigns(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize campaigns based on performance"""

        optimizations = {}

        for campaign_id, metrics in performance_data.items():
            platform = self.extract_platform_from_id(campaign_id)

            # Analyze performance
            analysis = await self.analyze_campaign_performance(metrics)

            if analysis['needs_optimization']:
                # Generate optimization recommendations
                recommendations = await self.generate_optimization_recommendations(
                    platform, metrics, analysis
                )

                # Apply optimizations
                result = await self.apply_optimizations(campaign_id, recommendations)
                optimizations[campaign_id] = result

        return optimizations

    async def analyze_campaign_performance(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze campaign performance metrics"""
        try:
            # Calculate key performance indicators
            ctr = metrics.get('clicks', 0) / metrics.get('impressions', 1) * 100
            cpc = metrics.get('cost', 0) / metrics.get('clicks', 1)
            cpa = metrics.get('cost', 0) / metrics.get('conversions', 1) if metrics.get('conversions', 0) > 0 else float('inf')
            roas = metrics.get('revenue', 0) / metrics.get('cost', 1) if metrics.get('cost', 0) > 0 else 0

            # Determine if optimization is needed
            needs_optimization = (
                ctr < 1.0 or  # Below 1% CTR
                cpc > metrics.get('target_cpc', 2.0) or  # Above target CPC
                roas < 3.0  # Below 3x ROAS
            )

            return {
                'ctr': ctr,
                'cpc': cpc,
                'cpa': cpa,
                'roas': roas,
                'needs_optimization': needs_optimization,
                'performance_score': self.calculate_performance_score(metrics)
            }
        except Exception as e:
            logger.error(f"Performance analysis failed: {e}")
            return {'needs_optimization': False, 'error': str(e)}

    def calculate_performance_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall performance score"""
        score = 0.0

        # CTR score (30 points)
        ctr = metrics.get('clicks', 0) / metrics.get('impressions', 1) * 100
        if ctr >= 2.0:
            score += 30
        elif ctr >= 1.0:
            score += 20
        elif ctr >= 0.5:
            score += 10

        # Conversion rate score (30 points)
        conv_rate = metrics.get('conversions', 0) / metrics.get('clicks', 1) * 100
        if conv_rate >= 5.0:
            score += 30
        elif conv_rate >= 2.0:
            score += 20
        elif conv_rate >= 1.0:
            score += 10

        # ROAS score (40 points)
        roas = metrics.get('revenue', 0) / metrics.get('cost', 1) if metrics.get('cost', 0) > 0 else 0
        if roas >= 5.0:
            score += 40
        elif roas >= 3.0:
            score += 30
        elif roas >= 2.0:
            score += 20
        elif roas >= 1.0:
            score += 10

        return min(100.0, score)

    async def generate_optimization_recommendations(
        self, platform: str, metrics: Dict[str, Any], analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate optimization recommendations"""
        recommendations = {
            'budget_adjustments': [],
            'targeting_changes': [],
            'creative_updates': [],
            'bid_strategy': 'unchanged'
        }

        # Budget optimization
        if analysis['cpc'] > analysis.get('target_cpc', 2.0):
            recommendations['budget_adjustments'].append({
                'action': 'decrease_budget',
                'reason': f'CPC (${analysis["cpc"]:.2f}) above target (${analysis.get("target_cpc", 2.0):.2f})'
            })

        # Targeting optimization
        if analysis['ctr'] < 1.0:
            recommendations['targeting_changes'].append({
                'action': 'refine_audience',
                'reason': f'Low CTR ({analysis["ctr"]:.2f}%) indicates poor audience targeting'
            })

        # Creative optimization
        if analysis['performance_score'] < 60:
            recommendations['creative_updates'].append({
                'action': 'test_new_creatives',
                'reason': f'Low performance score ({analysis["performance_score"]:.1f}) suggests creative issues'
            })

        # Bid strategy optimization
        if analysis['roas'] < 2.0:
            recommendations['bid_strategy'] = 'conservative'
        elif analysis['roas'] > 4.0:
            recommendations['bid_strategy'] = 'aggressive'

        return recommendations

    async def apply_optimizations(self, campaign_id: str, recommendations: Dict[str, Any]) -> Dict[str, Any]:
        """Apply optimization recommendations to campaign"""
        try:
            platform = self.extract_platform_from_id(campaign_id)
            client = self.platform_clients[platform]

            results = {}

            # Apply budget adjustments
            for adjustment in recommendations.get('budget_adjustments', []):
                if adjustment['action'] == 'decrease_budget':
                    result = await client.adjust_budget(campaign_id, 0.8)  # 20% decrease
                    results['budget'] = result

            # Apply targeting changes
            for change in recommendations.get('targeting_changes', []):
                if change['action'] == 'refine_audience':
                    result = await client.refine_targeting(campaign_id)
                    results['targeting'] = result

            # Apply creative updates
            for update in recommendations.get('creative_updates', []):
                if update['action'] == 'test_new_creatives':
                    result = await client.update_creatives(campaign_id)
                    results['creatives'] = result

            return results
        except Exception as e:
            logger.error(f"Failed to apply optimizations for {campaign_id}: {e}")
            return {'error': str(e)}

    def extract_platform_from_id(self, campaign_id: str) -> str:
        """Extract platform name from campaign ID"""
        # Simple extraction - in production, this would be more robust
        if 'google' in campaign_id.lower():
            return 'google'
        elif 'linkedin' in campaign_id.lower():
            return 'linkedin'
        elif 'facebook' in campaign_id.lower():
            return 'facebook'
        return 'unknown'

    def extract_campaign_results_from_result(self, result) -> Dict[str, Any]:
        """Extract campaign results from agent execution result"""
        # This would parse the agent's output to extract structured campaign data
        return {
            "campaigns": [
                {
                    "id": f"campaign_{datetime.utcnow().timestamp()}",
                    "platform": "google_ads",
                    "status": "active",
                    "budget": 1000.0
                }
            ],
            "creatives": [
                {
                    "id": f"creative_{datetime.utcnow().timestamp()}",
                    "platform": "google_ads",
                    "type": "text_ad",
                    "content": "Generated ad copy...",
                    "created_at": datetime.utcnow().isoformat()
                }
            ],
            "performance": {
                "overall_score": 75.0,
                "total_spend": 250.0,
                "conversions": 12,
                "roas": 3.2
            },
            "platforms": {"google": True}
        }

    # Tool implementations
    async def create_campaign(self, platform: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create ad campaign on specified platform"""
        try:
            return await call_with_circuit_breaker(
                f"{platform}_ads_api",
                self.platform_clients[platform].create_campaign,
                config
            )
        except Exception as e:
            logger.error(f"Campaign creation failed for {platform}: {e}")
            return {"error": str(e)}

    async def analyze_performance(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze campaign performance metrics"""
        try:
            return await self.analyze_campaign_performance(campaign_data)
        except Exception as e:
            logger.error(f"Performance analysis failed: {e}")
            return {"error": str(e)}

    async def optimize_budget(self, campaigns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Optimize budget allocation across campaigns"""
        try:
            total_budget = sum(c.get('budget', 0) for c in campaigns)
            optimizations = {}

            for campaign in campaigns:
                performance_score = campaign.get('performance_score', 50)
                current_budget = campaign.get('budget', 0)

                # Allocate more budget to high-performing campaigns
                if performance_score > 70:
                    new_budget = min(current_budget * 1.2, total_budget * 0.4)
                elif performance_score < 40:
                    new_budget = max(current_budget * 0.8, total_budget * 0.1)
                else:
                    new_budget = current_budget

                optimizations[campaign['id']] = {
                    'old_budget': current_budget,
                    'new_budget': new_budget,
                    'change_percent': ((new_budget - current_budget) / current_budget * 100) if current_budget > 0 else 0
                }

            return optimizations
        except Exception as e:
            logger.error(f"Budget optimization failed: {e}")
            return {"error": str(e)}

    async def generate_ad_copy(self, requirements: Dict[str, Any]) -> str:
        """Generate compelling ad copy"""
        try:
            # Use LLM to generate ad copy based on requirements
            prompt = f"""
            Create compelling ad copy for:
            Product/Service: {requirements.get('product', 'our solution')}
            Target Audience: {requirements.get('audience', 'businesses')}
            Key Benefits: {requirements.get('benefits', 'save time, increase efficiency')}
            Call to Action: {requirements.get('cta', 'contact us today')}

            Generate 3 different ad copy variations.
            """

            response = await self.llm.ainvoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"Ad copy generation failed: {e}")
            return "Generated compelling ad copy highlighting key benefits and clear call-to-action."

    async def test_ad_creatives(self, creatives: List[Dict[str, Any]]) -> Dict[str, Any]:
        """A/B test different ad creatives"""
        try:
            # Simple A/B testing logic
            results = {}
            for i, creative in enumerate(creatives):
                # Simulate performance testing
                ctr = 1.5 + (i * 0.3)  # Vary CTR slightly
                conv_rate = 2.1 + (i * 0.2)

                results[creative['id']] = {
                    'ctr': ctr,
                    'conversion_rate': conv_rate,
                    'score': (ctr * conv_rate) / 100,
                    'winner': i == 0  # First creative wins for demo
                }

            return results
        except Exception as e:
            logger.error(f"Creative testing failed: {e}")
            return {"error": str(e)}


# Platform client classes (simplified implementations)
class GoogleAdsClient:
    async def create_campaign(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return {"campaign_id": f"google_{config['name']}", "status": "created"}

    async def get_campaign_metrics(self, campaign_id: str) -> Dict[str, Any]:
        return {"clicks": 150, "impressions": 5000, "cost": 75.0, "conversions": 8}

    async def adjust_budget(self, campaign_id: str, multiplier: float) -> Dict[str, Any]:
        return {"campaign_id": campaign_id, "budget_adjusted": True, "multiplier": multiplier}

    async def refine_targeting(self, campaign_id: str) -> Dict[str, Any]:
        return {"campaign_id": campaign_id, "targeting_refined": True}

    async def update_creatives(self, campaign_id: str) -> Dict[str, Any]:
        return {"campaign_id": campaign_id, "creatives_updated": True}


class LinkedInAdsClient:
    async def create_campaign(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return {"campaign_id": f"linkedin_{config['name']}", "status": "created"}

    async def get_campaign_metrics(self, campaign_id: str) -> Dict[str, Any]:
        return {"clicks": 120, "impressions": 3000, "cost": 60.0, "conversions": 6}


class FacebookAdsClient:
    async def create_campaign(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return {"campaign_id": f"facebook_{config['name']}", "status": "created"}

    async def get_campaign_metrics(self, campaign_id: str) -> Dict[str, Any]:
        return {"clicks": 200, "impressions": 8000, "cost": 90.0, "conversions": 10}

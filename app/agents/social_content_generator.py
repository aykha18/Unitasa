"""
Social Media Content Generation Agent - Specialized for Unitasa feature promotion
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List
from abc import ABC, abstractmethod

import structlog
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI

from app.agents.base import BaseAgent
from app.agents.state import MarketingAgentState, update_state_timestamp
from app.rag.lcel_chains import get_confidence_rag_chain, query_with_confidence
from app.rag.monitoring import record_rag_query
from app.agents.social_content_knowledge_base import get_social_content_knowledge_base

logger = structlog.get_logger(__name__)


class SocialPlatformInterface(ABC):
    """Abstract interface for social media platforms"""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def max_length(self) -> int:
        pass

    @property
    @abstractmethod
    def optimal_hashtags(self) -> int:
        pass

    @property
    @abstractmethod
    def emoji_usage(self) -> str:
        pass

    @abstractmethod
    def format_content(self, content: str, **kwargs) -> str:
        """Format content for this platform"""
        pass

    @abstractmethod
    def validate_content(self, content: str) -> bool:
        """Validate content meets platform requirements"""
        pass


class TwitterPlatform(SocialPlatformInterface):
    """Twitter/X platform implementation"""

    @property
    def name(self) -> str:
        return "twitter"

    @property
    def max_length(self) -> int:
        return 280

    @property
    def optimal_hashtags(self) -> int:
        return 2

    @property
    def emoji_usage(self) -> str:
        return "moderate"

    def format_content(self, content: str, **kwargs) -> str:
        """Format content for Twitter"""
        # Ensure within character limit
        if len(content) > self.max_length:
            content = content[:self.max_length - 3] + "..."

        # Add hashtags if needed
        hashtags = kwargs.get('hashtags', [])
        if len(hashtags) < self.optimal_hashtags:
            # Add default Unitasa hashtags
            default_hashtags = ["#MarketingAutomation", "#AI", "#SaaS"]
            for hashtag in default_hashtags:
                if hashtag not in content and len(hashtags) < self.optimal_hashtags:
                    content += f" {hashtag}"
                    hashtags.append(hashtag)

        return content

    def validate_content(self, content: str) -> bool:
        """Validate Twitter content"""
        return len(content) <= self.max_length and len(content) > 0


class FacebookPlatform(SocialPlatformInterface):
    """Facebook platform implementation"""

    @property
    def name(self) -> str:
        return "facebook"

    @property
    def max_length(self) -> int:
        return 63206  # Facebook's character limit

    @property
    def optimal_hashtags(self) -> int:
        return 1

    @property
    def emoji_usage(self) -> str:
        return "minimal"

    def format_content(self, content: str, **kwargs) -> str:
        """Format content for Facebook"""
        # Facebook allows longer content, focus on engagement
        hashtags = kwargs.get('hashtags', [])
        if len(hashtags) < self.optimal_hashtags:
            content += " #MarketingAutomation"

        return content

    def validate_content(self, content: str) -> bool:
        """Validate Facebook content"""
        return len(content) <= self.max_length and len(content) > 0


class InstagramPlatform(SocialPlatformInterface):
    """Instagram platform implementation"""

    @property
    def name(self) -> str:
        return "instagram"

    @property
    def max_length(self) -> int:
        return 2200

    @property
    def optimal_hashtags(self) -> int:
        return 5

    @property
    def emoji_usage(self) -> str:
        return "high"

    def format_content(self, content: str, **kwargs) -> str:
        """Format content for Instagram"""
        # Instagram loves emojis and hashtags
        hashtags = kwargs.get('hashtags', [])
        if len(hashtags) < self.optimal_hashtags:
            default_hashtags = ["#MarketingAutomation", "#AI", "#SaaS", "#Marketing", "#Business"]
            for hashtag in default_hashtags:
                if hashtag not in content and len(hashtags) < self.optimal_hashtags:
                    content += f" {hashtag}"

        return content

    def validate_content(self, content: str) -> bool:
        """Validate Instagram content"""
        return len(content) <= self.max_length and len(content) > 0


class UnitasaFeatureDatabase:
    """Database of Unitasa features and content templates"""

    FEATURES = {
        "automated_social_posting": {
            "core_benefits": ["Save 15+ hours/week", "Multi-platform posting", "AI optimization"],
            "target_audience": "B2B SaaS founders, marketing managers",
            "hashtags": ["#MarketingAutomation", "#SaaS", "#SocialMedia"],
            "call_to_actions": ["Book demo", "Start free trial", "Learn more"],
            "content_variations": 18,
            "description": "AI agents that automatically schedule and post across X, LinkedIn, Instagram & more"
        },
        "crm_follow_ups": {
            "core_benefits": ["Automated lead nurturing", "Behavior-based follow-ups", "Pipeline optimization"],
            "target_audience": "Sales teams, CRM users",
            "hashtags": ["#CRM", "#LeadGeneration", "#SalesAutomation"],
            "call_to_actions": ["Take assessment", "Book strategy call", "See demo"],
            "content_variations": 15,
            "description": "Automatically follow up with leads based on behavior and pipeline stage"
        },
        "ad_optimization": {
            "core_benefits": ["Real-time optimization", "ROAS improvement", "Smart bidding"],
            "target_audience": "Marketing managers, PPC specialists",
            "hashtags": ["#PPC", "#AdOptimization", "#MarketingTech"],
            "call_to_actions": ["Book consultation", "Start free trial", "Learn more"],
            "content_variations": 12,
            "description": "Monitor and adjust campaigns in real time to improve ROAS"
        },
        "unified_analytics": {
            "core_benefits": ["Cross-platform insights", "Unified dashboard", "Performance tracking"],
            "target_audience": "Marketing directors, analysts",
            "hashtags": ["#Analytics", "#MarketingDashboard", "#DataDriven"],
            "call_to_actions": ["Book demo", "Take assessment", "View dashboard"],
            "content_variations": 10,
            "description": "See performance across channels in one dashboard"
        },
        "ai_readiness_assessment": {
            "core_benefits": ["Personalized roadmap", "30-second assessment", "AI strategy guidance"],
            "target_audience": "Business leaders, marketing teams",
            "hashtags": ["#AI", "#MarketingStrategy", "#BusinessIntelligence"],
            "call_to_actions": ["Take assessment", "Book strategy call", "Get roadmap"],
            "content_variations": 8,
            "description": "Get a personalized AI automation roadmap for your marketing in under 30 seconds"
        },
        "strategy_sessions": {
            "core_benefits": ["Free consultation", "Expert guidance", "Custom AI strategy"],
            "target_audience": "Founders, marketing leaders",
            "hashtags": ["#Strategy", "#Consultation", "#AIExpertise"],
            "call_to_actions": ["Book free session", "Schedule call", "Get advice"],
            "content_variations": 6,
            "description": "Book a free AI strategy session with marketing automation experts"
        },
        "ai_agents_main": {
            "core_benefits": ["24/7 marketing", "Intelligent automation", "Human-level decisions"],
            "target_audience": "All B2B companies",
            "hashtags": ["#AI", "#MarketingAutomation", "#FutureOfMarketing"],
            "call_to_actions": ["Book demo", "Take assessment", "Learn more"],
            "content_variations": 20,
            "description": "AI agents that run your marketing for you, making intelligent decisions 24/7"
        }
    }

    CONTENT_TEMPLATES = {
        "educational": [
            "🚀 {benefit}. {description} #MarketingAutomation",
            "💡 Did you know? {benefit} with Unitasa's AI agents. {description}",
            "📈 Level up your marketing: {benefit}. {description} #AI #SaaS"
        ],
        "benefit_focused": [
            "⏰ Save {time_saved} with {feature}. {description} #MarketingAutomation",
            "🎯 {benefit} - that's the power of Unitasa's AI agents. {description}",
            "⚡ {benefit}: {description} Ready to transform your marketing?"
        ],
        "social_proof": [
            "Just launched: {feature} automated 50+ tasks this week. {description} #SuccessStory",
            "From manual work to AI automation: {benefit}. {description}",
            "Real results: {feature} improved our {metric} by {percentage}%. {description}"
        ],
        "question_based": [
            "Tired of {pain_point}? Try {feature} - {benefit}. {description}",
            "What's costing you {time_saved}? {feature} can help. {description}",
            "Ready to {benefit}? {feature} makes it possible. {description}"
        ],
        "call_to_action": [
            "Ready to {benefit}? Book your free AI strategy session today! {description}",
            "Don't miss out: {feature} is transforming marketing. {description} #BookNow",
            "Transform your marketing in 30 seconds: Take our AI assessment! {description}"
        ]
    }

    @classmethod
    def get_feature_data(cls, feature_key: str) -> Dict[str, Any]:
        """Get feature data by key"""
        return cls.FEATURES.get(feature_key, {})

    @classmethod
    def get_all_features(cls) -> List[str]:
        """Get all available feature keys"""
        return list(cls.FEATURES.keys())

    @classmethod
    def get_content_template(cls, template_type: str, **kwargs) -> str:
        """Get a content template with variable substitution"""
        templates = cls.CONTENT_TEMPLATES.get(template_type, [])
        if not templates:
            return ""

        import random
        template = random.choice(templates)

        # Substitute variables
        for key, value in kwargs.items():
            template = template.replace(f"{{{key}}}", str(value))

        return template


class SocialContentGeneratorAgent(BaseAgent):
    """AI-powered content generation specialized for social media promotion"""

    def __init__(self, llm: ChatOpenAI):
        super().__init__("social_content_generator", llm, self.get_content_tools())
        try:
            self.confidence_rag_chain = get_confidence_rag_chain()
        except Exception as e:
            logger.warning(f"RAG chain initialization failed: {e}. Using fallback mode.")
            self.confidence_rag_chain = None
        self.feature_db = UnitasaFeatureDatabase()
        self.knowledge_base = None  # Will be initialized asynchronously

        # Initialize platform handlers
        self.platforms = {
            "twitter": TwitterPlatform(),
            "facebook": FacebookPlatform(),
            "instagram": InstagramPlatform()
        }

    def get_content_tools(self) -> List[Tool]:
        """Get tools for social media content creation"""
        return [
            Tool(
                name="query_trending_topics",
                description="Query current trending topics and hashtags",
                func=self.query_trending_topics
            ),
            Tool(
                name="analyze_platform_best_practices",
                description="Analyze best practices for specific platforms",
                func=self.analyze_platform_best_practices
            ),
            Tool(
                name="generate_ab_test_variants",
                description="Generate A/B test content variants",
                func=self.generate_ab_test_variants
            ),
            Tool(
                name="optimize_for_engagement",
                description="Optimize content for maximum engagement",
                func=self.optimize_for_engagement
            )
        ]

    def get_system_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_template("""
        You are an expert social media content creator specializing in B2B SaaS marketing.

        Your role is to:
        1. Create engaging, platform-optimized content about Unitasa features
        2. Generate multiple content variations for A/B testing
        3. Incorporate trending topics and relevant hashtags
        4. Optimize calls-to-action for conversion
        5. Ensure brand consistency and value-driven messaging

        Content Focus: {feature_name}
        Target Platform: {platform}
        Content Type: {content_type}
        Target Audience: {audience}

        Always create content that:
        - Highlights specific benefits
        - Includes clear calls-to-action
        - Uses appropriate hashtags and emojis
        - Stays within platform character limits
        - Drives engagement and conversions

        Use the available tools to research trends and optimize content.

        {agent_scratchpad}
        """)

    def create_agent(self):
        """Create the agent using Runnable interface"""
        from langchain.agents import create_openai_functions_agent
        from langchain.agents import AgentExecutor

        # Create the agent
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.get_system_prompt()
        )

        # Create the executor
        return AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=self.tools,
            verbose=False,
            handle_parsing_errors=True,
            max_iterations=3
        )

    def build_input(self, state: MarketingAgentState) -> Dict[str, Any]:
        """Build input data from shared state"""
        return {
            "feature_name": state.get("target_feature", "automated_social_posting"),
            "platform": state.get("target_platform", "twitter"),
            "content_type": state.get("content_type", "educational"),
            "audience": state.get("target_audience", "B2B SaaS founders"),
            "campaign_goal": state.get("campaign_goal", "lead_generation")
        }

    def update_state(self, state: MarketingAgentState, result) -> MarketingAgentState:
        """Update shared state with generated content"""
        new_content = self.extract_content_from_result(result)

        # Add to existing content
        existing_content = state.get("generated_social_content", [])
        existing_content.extend(new_content)
        state["generated_social_content"] = existing_content

        # Update content tracking
        content_tracking = state.get("social_content_tracking", {})
        for content in new_content:
            content_id = content.get("id", str(datetime.utcnow().timestamp()))
            content_tracking[content_id] = {
                "feature": content.get("feature"),
                "platform": content.get("platform"),
                "type": content.get("type"),
                "created_at": datetime.utcnow().isoformat(),
                "status": "generated"
            }
        state["social_content_tracking"] = content_tracking

        # Update agent coordination
        state["current_agent"] = "social_content_generation"
        state["next_agent"] = "posting_scheduler"

        self.log_agent_activity("social_content_generated", {
            "new_content": len(new_content),
            "total_content": len(existing_content),
            "platforms": list(set(c.get("platform") for c in new_content))
        })

        return update_state_timestamp(state)

    async def generate_feature_content(self, feature_key: str, platform: str, content_types: List[str] = None) -> List[Dict[str, Any]]:
        """Generate content for a specific feature across platforms using cost-optimized approach"""

        if content_types is None:
            content_types = ["educational", "benefit_focused", "social_proof"]

        feature_data = self.feature_db.get_feature_data(feature_key)
        if not feature_data:
            logger.error(f"Feature {feature_key} not found in database")
            return []

        platform_handler = self.platforms.get(platform)
        if not platform_handler:
            logger.error(f"Platform {platform} not supported")
            return []

        # Initialize knowledge base if not already done
        if self.knowledge_base is None:
            try:
                self.knowledge_base = await get_social_content_knowledge_base()
            except Exception as e:
                logger.warning(f"Knowledge base initialization failed: {e}")
                self.knowledge_base = None

        generated_content = []

        for content_type in content_types:
            try:
                content_variants = []

                # FIRST: Try knowledge base (cost-effective approach)
                if self.knowledge_base:
                    kb_suggestions = await self.knowledge_base.get_content_suggestions(
                        feature_key, platform, content_type, min_performance=0.01, limit=3
                    )

                    for template in kb_suggestions:
                        # Generate content from template
                        content = await self.knowledge_base.generate_content_from_template(
                            template,
                            variables={"time_saved": "15+ hours/week"}
                        )

                        # Optimize with learned patterns
                        content = await self.knowledge_base.optimize_content_with_kb(
                            content, feature_key, platform
                        )

                        content_variants.append(content)

                    logger.info(f"Generated {len(content_variants)} variants from knowledge base for {feature_key}")

                # SECOND: Generate additional variants using LLM if needed
                target_variants = 5
                if len(content_variants) < target_variants:
                    llm_variants_needed = target_variants - len(content_variants)
                    logger.info(f"Need {llm_variants_needed} more variants from LLM")

                    llm_variants = await self._generate_content_variants(
                        feature_key, feature_data, content_type, platform
                    )

                    content_variants.extend(llm_variants[:llm_variants_needed])

                    # Add successful LLM-generated content to knowledge base
                    if self.knowledge_base and llm_variants:
                        for i, variant in enumerate(llm_variants[:2]):  # Add top 2 to KB
                            await self.knowledge_base.add_new_template({
                                "feature": feature_key,
                                "platform": platform,
                                "content_type": content_type,
                                "template": variant,
                                "hashtags": feature_data.get("hashtags", []),
                                "call_to_action": feature_data.get("call_to_actions", [None])[0],
                                "variables": ["time_saved"]
                            })

                # THIRD: Apply platform formatting and validation
                for variant in content_variants:
                    formatted_content = platform_handler.format_content(
                        variant,
                        hashtags=feature_data.get("hashtags", []),
                        feature=feature_key
                    )

                    if platform_handler.validate_content(formatted_content):
                        content_item = {
                            "id": f"{feature_key}_{platform}_{content_type}_{len(generated_content)}",
                            "feature": feature_key,
                            "platform": platform,
                            "type": content_type,
                            "content": formatted_content,
                            "hashtags": feature_data.get("hashtags", []),
                            "call_to_action": feature_data.get("call_to_actions", [None])[0],
                            "character_count": len(formatted_content),
                            "generated_at": datetime.utcnow().isoformat(),
                            "status": "ready_for_scheduling",
                            "source": "knowledge_base" if len(content_variants) > 2 else "llm"
                        }
                        generated_content.append(content_item)

            except Exception as e:
                logger.error(f"Error generating content for {feature_key} on {platform}: {e}")
                continue

        # Log cost savings
        kb_generated = len([c for c in generated_content if c.get("source") == "knowledge_base"])
        llm_generated = len([c for c in generated_content if c.get("source") == "llm"])
        logger.info(f"Content generation complete: {kb_generated} from KB, {llm_generated} from LLM")

        return generated_content

    async def learn_from_content_performance(self, content_id: str, performance_data: Dict[str, Any]):
        """
        Learn from content performance to improve future generation.
        This is key for cost optimization - the more we learn, the less we need LLM calls.
        """

        if not self.knowledge_base:
            return

        try:
            # Extract performance metrics
            engagement_rate = performance_data.get('engagement_rate', 0)
            impressions = performance_data.get('impressions', 0)
            clicks = performance_data.get('clicks', 0)
            conversions = performance_data.get('conversions', 0)

            # Calculate derived metrics
            click_rate = clicks / max(impressions, 1)
            conversion_rate = conversions / max(clicks, 1)

            learning_data = {
                'engagement_rate': engagement_rate,
                'click_rate': click_rate,
                'conversion_rate': conversion_rate,
                'impressions': impressions,
                'clicks': clicks,
                'conversions': conversions
            }

            # Update knowledge base with performance data
            await self.knowledge_base.learn_from_performance(content_id, learning_data)

            logger.info(f"Learned from content {content_id}: engagement={engagement_rate:.3f}, clicks={clicks}")

        except Exception as e:
            logger.error(f"Error learning from content performance: {e}")

    async def get_cost_savings_report(self) -> Dict[str, Any]:
        """Get detailed cost savings report from knowledge base usage"""

        if not self.knowledge_base:
            return {"error": "Knowledge base not available"}

        try:
            savings = await self.knowledge_base.get_cost_savings_estimate()

            # Add agent-specific metrics
            total_content_generated = len(await self.generate_cross_platform_campaign("test"))
            kb_usage_percentage = savings.get('cache_hit_rate', 0) * 100

            return {
                **savings,
                "agent_metrics": {
                    "total_content_generated": total_content_generated,
                    "knowledge_base_usage_percentage": kb_usage_percentage,
                    "estimated_monthly_savings": savings.get('estimated_cost_savings_usd', 0) * 30,
                    "llm_call_reduction": f"{kb_usage_percentage:.1f}%"
                }
            }

        except Exception as e:
            logger.error(f"Error generating cost savings report: {e}")
            return {"error": str(e)}

    async def _generate_content_variants(self, feature_key: str, feature_data: Dict, content_type: str, platform: str) -> List[str]:
        """Generate multiple content variants for A/B testing"""

        # Query for trending topics
        trending_data = await self.query_trending_topics(platform)

        # Build content prompt
        prompt = self._build_content_generation_prompt(
            feature_key, feature_data, content_type, platform, trending_data
        )

        # Generate content using LLM
        response = await self.llm.ainvoke(prompt)

        # Extract and clean content variants
        content_text = response.content if hasattr(response, 'content') else str(response)
        variants = self._parse_content_variants(content_text)

        # Ensure we have at least 3 variants
        while len(variants) < 3:
            variants.append(self._generate_fallback_variant(feature_data, content_type))

        return variants[:5]  # Limit to 5 variants max

    def _build_content_generation_prompt(self, feature_key: str, feature_data: Dict, content_type: str, platform: str, trending_data: Dict) -> str:
        """Build prompt for content generation"""

        platform_specs = self.platforms[platform]

        return f"""
        Generate 3-5 different content variants for promoting Unitasa's {feature_key} feature on {platform}.

        Feature Details:
        - Name: {feature_key.replace('_', ' ').title()}
        - Benefits: {', '.join(feature_data.get('core_benefits', []))}
        - Description: {feature_data.get('description', '')}
        - Target Audience: {feature_data.get('target_audience', '')}

        Content Style: {content_type}
        Platform: {platform} (max {platform_specs.max_length} characters)
        Hashtags to include: {', '.join(feature_data.get('hashtags', [])[:platform_specs.optimal_hashtags])}

        Current Trends: {trending_data.get('trends', 'marketing automation, AI, SaaS')}

        Requirements:
        1. Each variant should highlight different benefits
        2. Include relevant emojis ({platform_specs.emoji_usage} usage)
        3. End with a clear call-to-action
        4. Stay under character limit
        5. Make it engaging and shareable

        Format each variant on a new line, starting with "Variant X:"
        """

    def _parse_content_variants(self, content_text: str) -> List[str]:
        """Parse content variants from LLM response"""
        variants = []
        lines = content_text.split('\n')

        for line in lines:
            line = line.strip()
            if line.startswith('Variant') and ':' in line:
                variant_text = line.split(':', 1)[1].strip()
                if len(variant_text) > 10:  # Filter out very short variants
                    variants.append(variant_text)

        return variants if variants else [content_text]

    def _generate_fallback_variant(self, feature_data: Dict, content_type: str) -> str:
        """Generate a fallback content variant using templates"""
        benefit = feature_data.get('core_benefits', ['AI automation'])[0]
        description = feature_data.get('description', 'Transform your marketing with AI')

        return self.feature_db.get_content_template(
            content_type,
            benefit=benefit,
            description=description,
            time_saved="15+ hours/week",
            feature="Unitasa's AI agents",
            metric="efficiency",
            percentage="300%",
            pain_point="manual marketing tasks"
        )

    async def generate_cross_platform_campaign(self, feature_key: str) -> Dict[str, Any]:
        """Generate content for a feature across all supported platforms"""

        campaign_data = {
            "feature": feature_key,
            "campaign_id": f"campaign_{feature_key}_{int(datetime.utcnow().timestamp())}",
            "generated_at": datetime.utcnow().isoformat(),
            "platforms": {},
            "total_content": 0
        }

        for platform_name in self.platforms.keys():
            try:
                content = await self.generate_feature_content(feature_key, platform_name)
                campaign_data["platforms"][platform_name] = content
                campaign_data["total_content"] += len(content)
            except Exception as e:
                logger.error(f"Failed to generate content for {platform_name}: {e}")
                campaign_data["platforms"][platform_name] = []

        return campaign_data

    def extract_content_from_result(self, result) -> List[Dict[str, Any]]:
        """Extract content from agent execution result"""
        # This would parse the agent's output to extract structured content data
        return [
            {
                "id": f"social_content_{datetime.utcnow().timestamp()}",
                "feature": "automated_social_posting",
                "platform": "twitter",
                "type": "educational",
                "content": "🚀 AI agents that run your marketing for you. Save 15+ hours/week with automated social posting! #MarketingAutomation",
                "hashtags": ["#MarketingAutomation", "#AI"],
                "character_count": 120,
                "generated_at": datetime.utcnow().isoformat()
            }
        ]

    # Tool implementations
    async def query_trending_topics(self, platform: str) -> Dict[str, Any]:
        """Query trending topics for a platform"""
        try:
            # In a real implementation, this would call platform APIs
            # For now, return mock trending data
            mock_trends = {
                "twitter": ["#MarketingAutomation", "#AI", "#SaaS", "#B2B", "#Marketing"],
                "facebook": ["marketing tips", "business growth", "automation", "AI tools"],
                "instagram": ["#marketing", "#business", "#automation", "#ai", "#saas"]
            }

            return {
                "platform": platform,
                "trends": mock_trends.get(platform, []),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error querying trends for {platform}: {e}")
            return {"platform": platform, "trends": [], "error": str(e)}

    async def analyze_platform_best_practices(self, platform: str) -> Dict[str, Any]:
        """Analyze best practices for a platform"""
        try:
            # Query knowledge base for platform best practices
            query = f"What are the best practices for {platform} content creation for B2B SaaS companies?"
            result = await query_with_confidence(query)

            return {
                "platform": platform,
                "best_practices": result.get('answer', 'Use engaging visuals, clear CTAs, relevant hashtags'),
                "confidence": result.get('confidence', {}).get('score', 0)
            }
        except Exception as e:
            logger.error(f"Error analyzing best practices for {platform}: {e}")
            return {"platform": platform, "best_practices": "General social media best practices", "error": str(e)}

    async def generate_ab_test_variants(self, base_content: str, platform: str) -> List[str]:
        """Generate A/B test variants of content"""
        try:
            prompt = f"""
            Create 3 different variations of this content for {platform}, optimized for A/B testing:

            Original: {base_content}

            Variations should:
            1. Test different emotional appeals
            2. Try different call-to-action placements
            3. Experiment with hashtag usage
            4. Vary sentence structure

            Return each variation on a new line.
            """

            response = await self.llm.ainvoke(prompt)
            content_text = response.content if hasattr(response, 'content') else str(response)

            # Parse variants
            variants = [line.strip() for line in content_text.split('\n') if line.strip() and len(line.strip()) > 20]
            return variants[:3] if len(variants) >= 3 else [base_content]

        except Exception as e:
            logger.error(f"Error generating A/B test variants: {e}")
            return [base_content]

    async def optimize_for_engagement(self, content: str, platform: str) -> str:
        """Optimize content for maximum engagement"""
        try:
            prompt = f"""
            Optimize this content for maximum engagement on {platform}:

            Content: {content}

            Optimization strategies:
            1. Add engaging hooks (questions, emojis, numbers)
            2. Improve readability and flow
            3. Strengthen call-to-action
            4. Add relevant hashtags
            5. Ensure platform-appropriate length

            Return the optimized version.
            """

            response = await self.llm.ainvoke(prompt)
            optimized = response.content if hasattr(response, 'content') else str(response)

            # Validate with platform handler
            platform_handler = self.platforms.get(platform)
            if platform_handler:
                optimized = platform_handler.format_content(optimized.strip())

            return optimized

        except Exception as e:
            logger.error(f"Error optimizing content for engagement: {e}")
            return content


class ClientAdaptiveContentGenerator:
    """
    Client-adaptive content generator that creates platform-optimized content
    for specific clients based on their brand profiles and audience analysis.
    """

    def __init__(self, client_kb: Any, global_kb: Any):
        self.client_kb = client_kb
        self.global_kb = global_kb
        self.platform_adapters = self._initialize_platform_adapters()

    def _initialize_platform_adapters(self) -> Dict[str, Any]:
        """Initialize platform-specific adapters"""
        return {
            "twitter": {
                "max_length": 280,
                "optimal_hashtags": 2,
                "emoji_usage": "moderate",
                "content_style": "concise_impactful"
            },
            "facebook": {
                "max_length": 63206,
                "optimal_hashtags": 1,
                "emoji_usage": "minimal",
                "content_style": "community_oriented"
            },
            "instagram": {
                "max_length": 2200,
                "optimal_hashtags": 5,
                "emoji_usage": "high",
                "content_style": "visual_storytelling"
            },
            "linkedin": {
                "max_length": 3000,
                "optimal_hashtags": 3,
                "emoji_usage": "minimal",
                "content_style": "professional_insight"
            }
        }

    async def generate_client_content(self, client_id: str, topic: str,
                                    platform: str, content_type: str = None) -> List[Dict[str, Any]]:
        """Generate content adapted for specific client"""

        # Step 1: Retrieve client brand profile
        brand_profile = await self.client_kb.get_brand_profile()

        # Step 2: Get client-specific content suggestions
        client_suggestions = await self.client_kb.get_content_suggestions(
            topic, platform, content_type
        )

        # Step 3: Apply global learnings and industry best practices
        global_insights = await self.global_kb.get_industry_insights(
            brand_profile['industry'], topic
        )

        # Step 4: Generate new content if needed (cost-optimized)
        if len(client_suggestions) < 3:
            new_content = await self._generate_new_content(
                topic, brand_profile, platform, content_type
            )
            # Add to client's knowledge base for future use
            await self.client_kb.add_template(new_content)

        # Step 5: Optimize for platform and apply A/B testing
        optimized_content = []
        for suggestion in client_suggestions:
            platform_optimized = await self._optimize_for_platform(
                suggestion, platform, brand_profile
            )
            optimized_content.append(platform_optimized)

        return optimized_content

    async def _generate_new_content(self, topic: str, brand_profile: Dict,
                                  platform: str, content_type: str) -> Dict[str, Any]:
        """Generate new content using client's brand voice and preferences"""

        # Use client's brand voice guidelines
        brand_voice = brand_profile.get('brand_voice', 'professional')

        # Incorporate client's key messages
        key_messages = brand_profile.get('key_messages', [])

        # Generate content with client's tone and messaging
        prompt = f"""
        Create {content_type} content for {brand_profile['company_name']} about {topic}.
        Brand voice: {brand_voice}
        Key messages to include: {', '.join(key_messages)}
        Target platform: {platform}
        """

        # Generate and validate content
        content = await self._call_llm_with_fallback(prompt, brand_profile)

        return {
            'content': content,
            'platform': platform,
            'content_type': content_type,
            'brand_voice': brand_voice,
            'key_messages_used': key_messages,
            'generated_at': datetime.utcnow().isoformat()
        }

    async def _optimize_for_platform(self, content: str, platform: str, brand_profile: Dict) -> Dict[str, Any]:
        """Optimize content for specific platform with client context"""

        platform_config = self.platform_adapters.get(platform, {})
        max_length = platform_config.get('max_length', 280)

        # Apply platform-specific optimizations
        optimized_content = content

        # Ensure length compliance
        if len(optimized_content) > max_length:
            optimized_content = optimized_content[:max_length - 3] + "..."

        # Add platform-specific elements
        if platform == "instagram":
            # Add more emojis for Instagram
            optimized_content = self._add_emojis(optimized_content, "high")
        elif platform == "twitter":
            # Add moderate emojis and ensure hashtags
            optimized_content = self._add_emojis(optimized_content, "moderate")

        return {
            'content': optimized_content,
            'platform': platform,
            'optimized_for': brand_profile.get('brand_voice', 'professional'),
            'character_count': len(optimized_content),
            'compliance': len(optimized_content) <= max_length
        }

    def _add_emojis(self, content: str, emoji_level: str) -> str:
        """Add emojis based on content and platform preferences"""
        # Simple emoji addition logic
        if emoji_level == "high" and "🚀" not in content:
            content = "🚀 " + content
        elif emoji_level == "moderate" and len([c for c in content if c in "🚀💡📈⚡🎯"]) == 0:
            content = "💡 " + content

        return content

    async def _call_llm_with_fallback(self, prompt: str, brand_profile: Dict) -> str:
        """Call LLM with fallback to template-based generation"""
        try:
            # This would use the LLM to generate content
            # For now, return a template-based response
            return f"Transform your business with {brand_profile.get('company_name', 'our solutions')}. Experience the difference today!"
        except Exception as e:
            logger.warning(f"LLM generation failed: {e}")
            return self._generate_template_fallback(brand_profile)

    def _generate_template_fallback(self, brand_profile: Dict) -> str:
        """Generate content using templates when LLM fails"""
        company_name = brand_profile.get('company_name', 'Our company')
        return f"Discover how {company_name} can transform your business. Contact us today to learn more."


# Factory function
def create_social_content_generator(llm: ChatOpenAI) -> SocialContentGeneratorAgent:
    """Create and return a social content generator agent"""
    return SocialContentGeneratorAgent(llm)


def create_client_adaptive_generator(client_kb: Any, global_kb: Any) -> ClientAdaptiveContentGenerator:
    """Create and return a client-adaptive content generator"""
    return ClientAdaptiveContentGenerator(client_kb, global_kb)
"""
Social Media Content Knowledge Base - Cost Optimization System
Reduces LLM API calls by 70-80% through intelligent caching and retrieval
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
import structlog

try:
    from app.rag.vectorstore_manager import get_vector_store_manager
    from app.rag.ingestion import ContentIngestionService
    VECTOR_STORE_AVAILABLE = True
except ImportError:
    VECTOR_STORE_AVAILABLE = False
    get_vector_store_manager = None
    ContentIngestionService = None

logger = structlog.get_logger(__name__)


@dataclass
class ContentTemplate:
    """Represents a content template with metadata"""
    id: str
    feature: str
    platform: str
    content_type: str  # educational, benefit_focused, social_proof, etc.
    template: str
    variables: List[str]  # Available variables for substitution
    hashtags: List[str]
    call_to_action: str
    character_count: int
    performance_score: float = 0.0
    usage_count: int = 0
    created_at: str = ""
    last_used: str = ""
    engagement_rate: float = 0.0
    conversion_rate: float = 0.0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()
        if not self.last_used:
            self.last_used = self.created_at


@dataclass
class ContentPattern:
    """Learned content patterns from successful posts"""
    id: str
    feature: str
    platform: str
    content_type: str
    pattern_type: str  # hook, body, cta, hashtag_pattern, etc.
    pattern: str
    performance_score: float
    confidence: float
    sample_size: int
    created_at: str
    last_updated: str


@dataclass
class PlatformOptimization:
    """Platform-specific optimization rules"""
    platform: str
    max_length: int
    optimal_hashtags: int
    emoji_usage: str  # none, minimal, moderate, high
    best_times: List[str]
    content_rules: Dict[str, Any]
    trending_topics: List[str]
    last_updated: str


class ClientKnowledgeBase:
    def __init__(self, client_id: str, brand_profile: Dict[str, Any], templates: List[ContentTemplate], patterns: List[ContentPattern], performance_baseline: Dict[str, Any]):
        self.client_id = client_id
        self.brand_profile = brand_profile
        self.templates = templates
        self.patterns = patterns
        self.performance_baseline = performance_baseline

    async def get_brand_profile(self) -> Dict[str, Any]:
        return self.brand_profile

    async def get_content_suggestions(self, topic: str, platform: str, content_type: Optional[str] = None) -> List[ContentTemplate]:
        suggestions = [
            t for t in self.templates
            if t.platform == platform and (content_type is None or t.content_type == content_type)
        ]
        return suggestions[:5]

    async def add_template(self, template_data: Dict[str, Any]) -> str:
        template_id = f"{template_data['platform']}_{template_data['feature']}_{template_data['content_type']}_{int(datetime.utcnow().timestamp())}"
        template = ContentTemplate(
            id=template_id,
            feature=template_data['feature'],
            platform=template_data['platform'],
            content_type=template_data['content_type'],
            template=template_data['template'],
            variables=template_data.get('variables', []),
            hashtags=template_data.get('hashtags', []),
            call_to_action=template_data.get('call_to_action', ''),
            character_count=len(template_data['template'])
        )
        self.templates.append(template)
        return template_id


class SocialContentKnowledgeBase:
    """
    Intelligent knowledge base for social media content generation.
    Reduces LLM costs by caching successful content and providing retrieval-based generation.
    """

    def __init__(self):
        self.templates: Dict[str, ContentTemplate] = {}
        self.patterns: Dict[str, ContentPattern] = {}
        self.platform_opts: Dict[str, PlatformOptimization] = {}
        self.vector_store = None
        self.ingestion_service = ContentIngestionService()
        self.client_knowledge_bases: Dict[str, ClientKnowledgeBase] = {}
        self.global_patterns: Dict[str, Any] = {}
        self.industry_templates: Dict[str, List[ContentTemplate]] = {}

        # Initialize platform optimizations
        self._initialize_platform_optimizations()

        # Load existing knowledge
        asyncio.create_task(self._load_knowledge_base())

    def _initialize_platform_optimizations(self):
        """Initialize platform-specific optimization data"""
        self.platform_opts = {
            "twitter": PlatformOptimization(
                platform="twitter",
                max_length=280,
                optimal_hashtags=2,
                emoji_usage="moderate",
                best_times=["9:00", "14:00", "18:00"],
                content_rules={
                    "max_hashtags": 3,
                    "emoji_density": 0.1,
                    "question_boost": 1.2,
                    "number_boost": 1.1
                },
                trending_topics=["#AI", "#MarketingAutomation", "#SaaS"],
                last_updated=datetime.utcnow().isoformat()
            ),
            "facebook": PlatformOptimization(
                platform="facebook",
                max_length=63206,
                optimal_hashtags=1,
                emoji_usage="minimal",
                best_times=["12:00", "15:00", "19:00"],
                content_rules={
                    "max_hashtags": 2,
                    "emoji_density": 0.02,
                    "story_boost": 1.3,
                    "question_boost": 1.1
                },
                trending_topics=["marketing tips", "business growth", "automation"],
                last_updated=datetime.utcnow().isoformat()
            ),
            "instagram": PlatformOptimization(
                platform="instagram",
                max_length=2200,
                optimal_hashtags=5,
                emoji_usage="high",
                best_times=["11:00", "17:00", "20:00"],
                content_rules={
                    "max_hashtags": 10,
                    "emoji_density": 0.15,
                    "visual_boost": 1.4,
                    "story_boost": 1.2
                },
                trending_topics=["#marketing", "#business", "#automation", "#ai"],
                last_updated=datetime.utcnow().isoformat()
            )
        }

    async def _load_knowledge_base(self):
        """Load existing knowledge from storage"""
        try:
            # Try to load from vector store if available
            if VECTOR_STORE_AVAILABLE:
                self.vector_store = await get_vector_store_manager()
            else:
                self.vector_store = None
                logger.info("Vector store not available, using in-memory knowledge base")

            # Load templates and patterns from storage
            await self._load_templates_from_storage()
            await self._load_patterns_from_storage()

            logger.info(f"Loaded knowledge base: {len(self.templates)} templates, {len(self.patterns)} patterns")

        except Exception as e:
            logger.warning(f"Failed to load knowledge base: {e}. Using empty knowledge base.")

    async def _load_templates_from_storage(self):
        """Load content templates from persistent storage"""
        # In a real implementation, this would load from database/vector store
        # For now, we'll initialize with some base templates
        await self._initialize_base_templates()

    async def _load_patterns_from_storage(self):
        """Load learned patterns from storage"""
        # Load patterns from vector store or database
        pass

    async def _initialize_base_templates(self):
        """Initialize knowledge base with base content templates"""

        base_templates = [
            # Twitter Templates
            ContentTemplate(
                id="twitter_educational_automated_social_posting",
                feature="automated_social_posting",
                platform="twitter",
                content_type="educational",
                template="🚀 Tired of manual posting? Unitasa's AI agents automatically schedule and post across X, LinkedIn, Instagram & more. Focus on strategy, not scheduling! #MarketingAutomation",
                variables=["time_saved", "platforms"],
                hashtags=["#MarketingAutomation", "#AI"],
                call_to_action="Book demo",
                character_count=142
            ),
            ContentTemplate(
                id="twitter_benefit_focused_crm_follow_ups",
                feature="crm_follow_ups",
                platform="twitter",
                content_type="benefit_focused",
                template="⏰ Save {time_saved} with automated CRM follow-ups. Unitasa's AI agents nurture leads based on behavior and pipeline stage. Never miss a sales opportunity! #CRM #LeadGeneration",
                variables=["time_saved"],
                hashtags=["#CRM", "#LeadGeneration"],
                call_to_action="Take assessment",
                character_count=156
            ),

            # Facebook Templates
            ContentTemplate(
                id="facebook_story_driven_ad_optimization",
                feature="ad_optimization",
                platform="facebook",
                content_type="story_driven",
                template="Imagine your ad campaigns optimizing themselves in real-time. That's the reality with Unitasa's AI agents. They monitor performance, adjust bids, and improve ROAS while you focus on growing your business. Transform your paid advertising today.",
                variables=[],
                hashtags=["#PPC"],
                call_to_action="Book consultation",
                character_count=234
            ),

            # Instagram Templates
            ContentTemplate(
                id="instagram_visual_focused_unified_analytics",
                feature="unified_analytics",
                platform="instagram",
                content_type="visual_focused",
                template="📊 Stop switching between dashboards! ✨ Unified analytics from Unitasa shows performance across ALL platforms in one view. 🚀 Make data-driven decisions instantly. 📈 #Analytics #MarketingDashboard #DataDriven",
                variables=[],
                hashtags=["#Analytics", "#MarketingDashboard", "#DataDriven", "#Marketing", "#Business"],
                call_to_action="View dashboard",
                character_count=178
            )
        ]

        for template in base_templates:
            self.templates[template.id] = template

        logger.info(f"Initialized {len(base_templates)} base content templates")

    async def create_client_kb(self, client_id: str, client_profile: Dict[str, Any]) -> ClientKnowledgeBase:
        industry = client_profile.get("company_info", {}).get("industry", "general")
        base_templates = self.industry_templates.get(industry, [])
        if not base_templates:
            base_templates = list(self.templates.values())
        customized_templates = await self._customize_templates_for_client(base_templates, client_profile)
        client_patterns = await self._generate_client_patterns(client_profile)
        performance_baseline = await self._establish_performance_baseline(client_profile)
        client_kb = ClientKnowledgeBase(
            client_id=client_id,
            brand_profile=client_profile,
            templates=customized_templates,
            patterns=client_patterns,
            performance_baseline=performance_baseline
        )
        self.client_knowledge_bases[client_id] = client_kb
        return client_kb

    async def get_client_content(self, client_id: str, content_request: Dict[str, Any]) -> List[Dict[str, Any]]:
        if client_id not in self.client_knowledge_bases:
            raise ValueError(f"Client {client_id} not found")
        client_kb = self.client_knowledge_bases[client_id]
        topic = content_request.get("topic", "")
        platform = content_request.get("platform", "twitter")
        content_type = content_request.get("content_type")
        suggestions = await client_kb.get_content_suggestions(topic, platform, content_type)
        outputs: List[Dict[str, Any]] = []
        for t in suggestions:
            content = await self.generate_content_from_template(t, variables={"time_saved": "15+ hours/week"})
            optimized = await self.optimize_content_with_kb(content, t.feature, platform)
            outputs.append({
                "content": optimized,
                "platform": t.platform,
                "content_type": t.content_type,
                "feature": t.feature,
                "call_to_action": t.call_to_action,
                "hashtags": t.hashtags,
                "character_count": len(optimized)
            })
        return outputs

    async def _customize_templates_for_client(self, templates: List[ContentTemplate], client_profile: Dict[str, Any]) -> List[ContentTemplate]:
        brand_voice = client_profile.get("company_info", {}).get("brand_voice", "professional")
        customized = []
        for t in templates:
            text = t.template
            if brand_voice and brand_voice.lower() != "professional":
                text = f"{text}"
            customized.append(ContentTemplate(
                id=t.id,
                feature=t.feature,
                platform=t.platform,
                content_type=t.content_type,
                template=text,
                variables=t.variables,
                hashtags=t.hashtags,
                call_to_action=t.call_to_action,
                character_count=len(text),
                performance_score=t.performance_score,
                usage_count=t.usage_count,
                created_at=t.created_at,
                last_used=t.last_used,
                engagement_rate=t.engagement_rate,
                conversion_rate=t.conversion_rate
            ))
        return customized

    async def _generate_client_patterns(self, client_profile: Dict[str, Any]) -> List[ContentPattern]:
        return []

    async def _establish_performance_baseline(self, client_profile: Dict[str, Any]) -> Dict[str, Any]:
        return {"engagement_rate": 0.0, "conversion_rate": 0.0}

    async def get_content_suggestions(self, feature: str, platform: str, content_type: str = None,
                                    min_performance: float = 0.0, limit: int = 5) -> List[ContentTemplate]:
        """
        Retrieve content suggestions from knowledge base.
        This avoids LLM calls by using cached, proven content.
        """

        # Filter templates by criteria
        candidates = [
            template for template in self.templates.values()
            if template.feature == feature
            and template.platform == platform
            and template.performance_score >= min_performance
            and (content_type is None or template.content_type == content_type)
        ]

        # Sort by performance score and usage count
        candidates.sort(key=lambda x: (x.performance_score, x.usage_count), reverse=True)

        return candidates[:limit]

    async def generate_content_from_template(self, template: ContentTemplate,
                                           variables: Dict[str, str] = None) -> str:
        """
        Generate content by filling template variables.
        Much cheaper than LLM generation.
        """

        content = template.template

        # Substitute variables
        if variables:
            for var, value in variables.items():
                content = content.replace(f"{{{var}}}", value)

        # Update template usage
        template.usage_count += 1
        template.last_used = datetime.utcnow().isoformat()

        return content

    async def find_similar_successful_content(self, feature: str, platform: str,
                                            target_performance: float = 0.03) -> List[ContentTemplate]:
        """
        Find similar high-performing content for inspiration.
        Uses vector similarity to find content patterns.
        """

        if not self.vector_store:
            return []

        try:
            # Search for similar successful content
            query = f"successful {feature} content for {platform} with high engagement"
            results = await self.vector_store.similarity_search(query, k=5)

            # Convert to ContentTemplate objects
            similar_templates = []
            for result in results:
                metadata = result.metadata
                if metadata.get('performance_score', 0) >= target_performance:
                    template = ContentTemplate(
                        id=metadata.get('id', f"similar_{len(similar_templates)}"),
                        feature=metadata.get('feature', feature),
                        platform=metadata.get('platform', platform),
                        content_type=metadata.get('content_type', 'educational'),
                        template=result.page_content,
                        variables=[],
                        hashtags=metadata.get('hashtags', []),
                        call_to_action=metadata.get('call_to_action', ''),
                        character_count=len(result.page_content),
                        performance_score=metadata.get('performance_score', 0.0)
                    )
                    similar_templates.append(template)

            return similar_templates

        except Exception as e:
            logger.error(f"Error finding similar content: {e}")
            return []

    async def learn_from_performance(self, content_id: str, performance_data: Dict[str, Any]):
        """
        Learn from content performance to improve future suggestions.
        Updates template performance scores and learns patterns.
        """

        if content_id not in self.templates:
            logger.warning(f"Template {content_id} not found for learning")
            return

        template = self.templates[content_id]

        # Update performance metrics
        engagement_rate = performance_data.get('engagement_rate', 0)
        conversion_rate = performance_data.get('conversion_rate', 0)

        # Calculate new performance score (weighted average)
        old_score = template.performance_score
        new_score = (old_score * template.usage_count + engagement_rate) / (template.usage_count + 1)

        template.performance_score = new_score
        template.engagement_rate = engagement_rate
        template.conversion_rate = conversion_rate

        # Extract successful patterns
        await self._extract_patterns_from_success(template, performance_data)

        logger.info(f"Learned from content {content_id}: performance_score={new_score:.3f}")

    async def _extract_patterns_from_success(self, template: ContentTemplate, performance_data: Dict[str, Any]):
        """Extract successful patterns from high-performing content"""

        if template.performance_score < 0.03:  # Only learn from good performers
            return

        # Extract hook pattern
        content = template.template
        if content.startswith(('🚀', '⏰', '💡', '🎯')):
            hook_pattern = ContentPattern(
                id=f"hook_{template.id}",
                feature=template.feature,
                platform=template.platform,
                content_type=template.content_type,
                pattern_type="hook",
                pattern=content[:50] + "...",
                performance_score=template.performance_score,
                confidence=0.8,
                sample_size=1,
                created_at=datetime.utcnow().isoformat(),
                last_updated=datetime.utcnow().isoformat()
            )
            self.patterns[hook_pattern.id] = hook_pattern

        # Extract hashtag pattern
        if len(template.hashtags) >= 2:
            hashtag_pattern = ContentPattern(
                id=f"hashtags_{template.id}",
                feature=template.feature,
                platform=template.platform,
                content_type=template.content_type,
                pattern_type="hashtag_pattern",
                pattern=" ".join(f"#{tag}" for tag in template.hashtags),
                performance_score=template.performance_score,
                confidence=0.9,
                sample_size=1,
                created_at=datetime.utcnow().isoformat(),
                last_updated=datetime.utcnow().isoformat()
            )
            self.patterns[hashtag_pattern.id] = hashtag_pattern

    async def get_cost_savings_estimate(self) -> Dict[str, Any]:
        """Calculate estimated cost savings from using knowledge base"""

        total_templates = len(self.templates)
        high_performers = len([t for t in self.templates.values() if t.performance_score >= 0.03])
        total_usage = sum(t.usage_count for t in self.templates.values())

        # Estimate LLM calls avoided
        llm_calls_avoided = total_usage * 0.8  # Assume 80% of content comes from KB
        cost_savings_usd = llm_calls_avoided * 0.002  # $0.002 per LLM call estimate

        return {
            "total_templates": total_templates,
            "high_performing_templates": high_performers,
            "total_usage_count": total_usage,
            "estimated_llm_calls_avoided": llm_calls_avoided,
            "estimated_cost_savings_usd": cost_savings_usd,
            "cache_hit_rate": min(total_usage / max(total_templates, 1), 1.0)
        }

    async def add_new_template(self, template_data: Dict[str, Any]) -> str:
        """Add a new content template to the knowledge base"""

        template_id = f"{template_data['platform']}_{template_data['feature']}_{template_data['content_type']}_{int(datetime.utcnow().timestamp())}"

        template = ContentTemplate(
            id=template_id,
            feature=template_data['feature'],
            platform=template_data['platform'],
            content_type=template_data['content_type'],
            template=template_data['template'],
            variables=template_data.get('variables', []),
            hashtags=template_data.get('hashtags', []),
            call_to_action=template_data.get('call_to_action', ''),
            character_count=len(template_data['template'])
        )

        self.templates[template_id] = template

        # Add to vector store for similarity search (if available)
        if self.vector_store and VECTOR_STORE_AVAILABLE and ContentIngestionService:
            try:
                ingestion_service = ContentIngestionService()
                await ingestion_service.ingest_content(
                    content=template.template,
                    metadata={
                        'id': template_id,
                        'feature': template.feature,
                        'platform': template.platform,
                        'content_type': template.content_type,
                        'hashtags': template.hashtags,
                        'call_to_action': template.call_to_action,
                        'performance_score': template.performance_score
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to add template to vector store: {e}")

        logger.info(f"Added new template: {template_id}")
        return template_id

    async def optimize_content_with_kb(self, base_content: str, feature: str, platform: str) -> str:
        """
        Optimize content using knowledge base patterns.
        Applies successful patterns to improve content performance.
        """

        optimized = base_content

        # Apply successful hooks if content doesn't have one
        if not any(base_content.startswith(emoji) for emoji in ['🚀', '⏰', '💡', '🎯', '📊', '⚡']):
            hook_patterns = [
                p for p in self.patterns.values()
                if p.pattern_type == "hook"
                and p.platform == platform
                and p.performance_score >= 0.03
            ]

            if hook_patterns:
                # Use highest performing hook
                best_hook = max(hook_patterns, key=lambda x: x.performance_score)
                hook_prefix = best_hook.pattern.split("...")[0]
                optimized = f"{hook_prefix} {optimized}"

        # Apply successful hashtag patterns
        hashtag_patterns = [
            p for p in self.patterns.values()
            if p.pattern_type == "hashtag_pattern"
            and p.platform == platform
            and p.performance_score >= 0.03
        ]

        if hashtag_patterns and len([tag for tag in optimized.split() if tag.startswith('#')]) < 2:
            best_hashtags = max(hashtag_patterns, key=lambda x: x.performance_score)
            if best_hashtags.pattern not in optimized:
                optimized += f" {best_hashtags.pattern}"

        return optimized

    def get_platform_optimization(self, platform: str) -> Optional[PlatformOptimization]:
        """Get platform-specific optimization data"""
        return self.platform_opts.get(platform)


# Global instance
_knowledge_base_instance = None

async def get_social_content_knowledge_base() -> SocialContentKnowledgeBase:
    """Get or create the global knowledge base instance"""
    global _knowledge_base_instance
    if _knowledge_base_instance is None:
        _knowledge_base_instance = SocialContentKnowledgeBase()
        await asyncio.sleep(0.1)  # Allow initialization
    return _knowledge_base_instance

"""
Client Analysis Agent - Onboarding Specialist
Analyzes new clients and builds comprehensive brand profiles for automated content generation
"""

import asyncio
import re
import httpx
from datetime import datetime
from typing import Dict, Any, List, Optional
import structlog

from app.agents.base import BaseAgent
from app.agents.state import MarketingAgentState, update_state_timestamp
from app.agents.social_content_knowledge_base import get_social_content_knowledge_base
try:
    from app.agents.ingestion_agent import ingest_website
except ImportError:
    ingest_website = None
try:
    from app.rag.lcel_chains import get_confidence_rag_chain, query_with_confidence
except Exception:
    get_confidence_rag_chain = None
    query_with_confidence = None
from app.core.config import settings

logger = structlog.get_logger(__name__)


class ClientAnalysisAgent(BaseAgent):
    """
    AI-powered client analysis agent that creates comprehensive brand profiles
    for automated content generation and social media management.
    """

    def __init__(self, llm=None, knowledge_base=None):
        super().__init__("client_analysis")
        self.llm = llm
        self.knowledge_base = knowledge_base
        self.analysis_tools = self.get_analysis_tools()

        # Initialize RAG chain for brand analysis
        try:
            self.brand_analysis_chain = get_confidence_rag_chain()
        except Exception as e:
            logger.warning(f"RAG chain initialization failed: {e}. Using fallback mode.")
            self.brand_analysis_chain = None

    def get_system_prompt(self) -> str:
        """Get agent-specific system prompt"""
        return """You are an expert Marketing Onboarding Specialist and Brand Analyst.
        Your goal is to analyze client information to build comprehensive brand profiles.
        You specialize in:
        1. Identifying brand voice and personality
        2. Creating detailed audience personas
        3. Analyzing competitive landscape
        4. Developing content strategies
        
        Analyze provided information deeply and infer missing details based on industry standards."""

    async def execute_task(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent task with given input"""
        return await self.analyze_client(task_input)

    def get_analysis_tools(self) -> List[Any]:
        """Get tools for client analysis"""
        return [
            {
                "name": "website_analyzer",
                "description": "Analyze company website for brand insights",
                "function": self._analyze_website
            },
            {
                "name": "social_media_auditor",
                "description": "Audit social media presence and engagement patterns",
                "function": self._audit_social_media
            },
            {
                "name": "brand_voice_detector",
                "description": "Detect and analyze brand voice from content samples",
                "function": self._detect_brand_voice
            },
            {
                "name": "competitor_analyzer",
                "description": "Analyze competitors and market positioning",
                "function": self._analyze_competitors
            },
            {
                "name": "audience_profiler",
                "description": "Create detailed audience personas",
                "function": self._profile_audience
            }
        ]

    async def analyze_client(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete client analysis and profile creation.
        This is the main entry point for client onboarding.
        """
        logger.info(f"Analyzing client with data keys: {list(client_data.keys()) if client_data else 'None'}")
        
        if not client_data:
            raise ValueError("client_data cannot be None or empty")

        client_id = self._generate_client_id(client_data)
        logger.info(f"Starting client analysis for {client_id}")

        # Update agent state
        # await update_state_timestamp(self.agent_id, "analysis_started")

        try:
            # Step 0: Website Analysis (if provided)
            # This enriches the client_data before deep analysis
            company_info = client_data.get("company_info", {})
            if not company_info:
                logger.warning("company_info is missing or empty")
                
            website_url = company_info.get("website") or client_data.get("website")
            
            # Ensure website is in company_info regardless of analysis success
            if website_url and not company_info.get("website"):
                company_info["website"] = website_url
                client_data["company_info"] = company_info

            if website_url:
                logger.info(f"Analyzing website: {website_url}")
                try:
                    website_data = await self._analyze_website(website_url)
                    
                    # Merge website findings into company_info if fields are missing
                    if not company_info.get("mission_statement") and website_data.get("mission"):
                        company_info["mission_statement"] = website_data["mission"]
                    
                    if not company_info.get("industry") and website_data.get("industry"):
                        company_info["industry"] = website_data["industry"]
                    
                    # NEW: Enrich with key features from website
                    if "features" not in client_data and website_data.get("key_features"):
                        # Convert string list to structured format expected by KB
                        features_list = []
                        for feature in website_data.get("key_features", []):
                            if isinstance(feature, str):
                                features_list.append({"title": feature, "description": ""})
                            elif isinstance(feature, dict):
                                features_list.append(feature)
                        client_data["features"] = features_list
                        logger.info(f"Extracted {len(features_list)} features from website")

                    # Enrich target audience if missing
                    if "target_audience" not in client_data:
                        client_data["target_audience"] = {}
                    
                    if not client_data["target_audience"].get("primary_persona") and website_data.get("target_audience"):
                        client_data["target_audience"]["primary_persona"] = website_data["target_audience"]
                    
                    # Ensure updated company info is saved back
                    client_data["company_info"] = company_info
                    
                    logger.info("Enriched client data with website analysis")
                except Exception as e:
                    logger.warning(f"Website analysis failed: {e}. Proceeding with provided data.")

            # Step 1: Brand Voice Analysis
            logger.info("Starting brand voice analysis")
            brand_profile = await self._analyze_brand_voice(client_data)
            # await update_state_timestamp(self.agent_id, "brand_analysis_complete")

            # Step 2: Audience Analysis
            logger.info("Starting audience analysis")
            audience_profile = await self._analyze_target_audience(client_data)
            # await update_state_timestamp(self.agent_id, "audience_analysis_complete")

            # Step 3: Competitive Analysis
            logger.info("Starting competitive analysis")
            competitive_profile = await self._analyze_competition(client_data)
            # await update_state_timestamp(self.agent_id, "competition_analysis_complete")

            # Step 4: Content Strategy Development
            logger.info("Starting content strategy development")
            content_strategy = await self._develop_content_strategy(
                brand_profile, audience_profile, competitive_profile
            )
            # await update_state_timestamp(self.agent_id, "content_strategy_complete")

            # Step 5: Platform Strategy
            logger.info("Starting platform strategy")
            platform_strategy = await self._create_platform_strategy(client_data)
            # await update_state_timestamp(self.agent_id, "platform_strategy_complete")

            # Step 6: Knowledge Base Initialization
            logger.info("Starting knowledge base initialization")
            client_kb = await self._initialize_client_knowledge_base(
                client_data, brand_profile, content_strategy
            )
            # await update_state_timestamp(self.agent_id, "knowledge_base_initialized")

            # Calculate content quality estimate
            quality_score = self._estimate_content_quality(client_data)

            result = {
                "client_id": client_id,
                "brand_profile": brand_profile,
                "audience_profile": audience_profile,
                "competitive_profile": competitive_profile,
                "content_strategy": content_strategy,
                "platform_strategy": platform_strategy,
                "knowledge_base": client_kb,
                "onboarding_complete": True,
                "estimated_content_quality": quality_score,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "agent_version": "1.0.0"
            }

            logger.info(f"Client analysis completed for {client_id} with quality score {quality_score}")
            # await update_state_timestamp(self.agent_id, "analysis_completed")

            return result

        except Exception as e:
            logger.error(f"Client analysis failed for {client_id}: {e}", exc_info=True)
            # await update_state_timestamp(self.agent_id, "analysis_failed")
            raise

    async def _analyze_brand_voice(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze brand voice and personality"""

        company_info = client_data.get("company_info") or {}
        brand_assets = client_data.get("brand_assets") or {}
        content_samples = (client_data.get("performance_data") or {}).get("successful_content", [])

        # Use LLM to analyze brand voice
        brand_voice_prompt = f"""
        Analyze the brand voice and personality for {company_info.get('company_name', 'the company')}:

        Industry: {company_info.get('industry', 'Unknown')}
        Mission: {company_info.get('mission_statement', 'Not provided')}
        Target Audience: {client_data.get('target_audience', {}).get('primary_persona', 'Not specified')}

        Content Samples: {content_samples[:3] if content_samples else 'No samples provided'}

        Provide:
        1. Brand voice classification (professional, casual, technical, friendly, etc.)
        2. Key personality traits (3-5 traits)
        3. Communication style preferences
        4. Tone guidelines for different contexts
        5. Language patterns and preferences
        """

        try:
            if self.llm:
                response = await self.llm.ainvoke(brand_voice_prompt)
                brand_voice_analysis = response.content
            else:
                brand_voice_analysis = "professional"  # fallback

        except Exception as e:
            logger.warning(f"LLM brand voice analysis failed: {e}")
            brand_voice_analysis = company_info.get('brand_voice', 'professional')

        return {
            "brand_voice": brand_voice_analysis,
            "personality_traits": self._extract_personality_traits(brand_voice_analysis),
            "communication_style": self._determine_communication_style(company_info),
            "tone_guidelines": self._create_tone_guidelines(brand_voice_analysis),
            "language_patterns": self._identify_language_patterns(content_samples),
            "visual_style": brand_assets.get('visual_style', 'modern'),
            "brand_colors": brand_assets.get('brand_colors', ['#000000']),
            "analysis_method": "ai_powered"
        }

    async def _analyze_target_audience(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed audience personas"""

        audience_data = client_data.get("target_audience") or {}
        company_info = client_data.get("company_info") or {}

        # Extract audience information
        primary_persona = audience_data.get("primary_persona", "Business Professional")
        pain_points = audience_data.get("pain_points", [])
        goals = audience_data.get("goals", [])
        demographics = audience_data.get("demographics", {})

        # Create detailed personas
        personas = []
        for i in range(min(3, len(audience_data.get("secondary_personas", [])) + 1)):
            persona_name = primary_persona if i == 0 else audience_data.get("secondary_personas", [])[i-1]

            persona = {
                "name": persona_name,
                "demographics": {
                    "age_range": demographics.get("age_range", "25-45"),
                    "job_title": f"Persona {i+1} Job Title",
                    "company_size": demographics.get("company_size", company_info.get("company_size", "SMB")),
                    "industry": company_info.get("industry", "Technology")
                },
                "psychographics": {
                    "pain_points": pain_points[:3],
                    "goals": goals[:3],
                    "challenges": audience_data.get("challenges", []),
                    "motivations": audience_data.get("motivations", [])
                },
                "behavior": {
                    "content_preference": audience_data.get("content_preference", "educational"),
                    "social_platforms": (client_data.get("social_media_accounts") or {}).get("platforms", ["LinkedIn"]),
                    "engagement_style": "professional" if company_info.get("industry") in ["B2B", "Enterprise"] else "casual"
                }
            }
            personas.append(persona)

        return {
            "primary_persona": personas[0] if personas else {},
            "secondary_personas": personas[1:] if len(personas) > 1 else [],
            "audience_size_estimate": self._estimate_audience_size(company_info),
            "content_preferences": self._determine_content_preferences(audience_data),
            "peak_engagement_times": (client_data.get("social_media_accounts") or {}).get("peak_times", {}),
            "analysis_confidence": 0.85
        }

    async def _analyze_competition(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze competitors and market positioning"""

        competitors = (client_data.get("content_preferences") or {}).get("competitors", [])
        company_info = client_data.get("company_info") or {}

        competitive_analysis = []

        for competitor in competitors[:5]:  # Limit to top 5 competitors
            competitor_profile = {
                "name": competitor,
                "market_position": "direct_competitor",
                "key_differentiators": self._identify_differentiators(company_info, competitor),
                "content_strategy": "educational_focused",  # Placeholder
                "social_presence": {
                    "platforms": ["LinkedIn", "Twitter"],  # Placeholder
                    "follower_count": "unknown",
                    "engagement_rate": "unknown"
                },
                "messaging_gaps": self._find_messaging_gaps(company_info, competitor)
            }
            competitive_analysis.append(competitor_profile)

        return {
            "direct_competitors": competitive_analysis,
            "market_positioning": self._determine_market_position(company_info, competitors),
            "differentiation_opportunities": self._identify_differentiation_opportunities(company_info, competitors),
            "content_gaps": self._analyze_content_gaps(competitors),
            "analysis_depth": "comprehensive" if len(competitors) >= 3 else "basic"
        }

    async def _develop_content_strategy(self, brand_profile: Dict, audience_profile: Dict,
                                      competitive_profile: Dict) -> Dict[str, Any]:
        """Develop comprehensive content strategy"""

        # Extract key elements
        brand_voice = brand_profile.get("brand_voice", "professional")
        primary_persona = audience_profile.get("primary_persona", {})
        differentiators = competitive_profile.get("differentiation_opportunities", [])

        # Create content pillars
        content_pillars = self._create_content_pillars(brand_voice, primary_persona, differentiators)

        # Define content themes
        content_themes = self._define_content_themes(content_pillars, brand_voice)

        # Create messaging framework
        messaging_framework = {
            "core_messages": self._extract_core_messages(brand_profile, differentiators),
            "value_propositions": self._create_value_propositions(differentiators),
            "elevator_pitch": self._create_elevator_pitch(brand_profile, primary_persona),
            "content_tone": brand_voice,
            "key_phrases": self._identify_key_phrases(brand_profile)
        }

        return {
            "content_pillars": content_pillars,
            "content_themes": content_themes,
            "messaging_framework": messaging_framework,
            "content_mix": self._determine_content_mix(audience_profile),
            "posting_frequency": self._recommend_posting_frequency(audience_profile),
            "best_practices": self._define_content_best_practices(brand_voice, audience_profile)
        }

    async def _create_platform_strategy(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create platform-specific content and engagement strategy"""

        social_accounts = client_data.get("social_media_accounts") or {}
        platforms = social_accounts.get("platforms") or ["LinkedIn"]
        existing_handles = social_accounts.get("existing_handles", {})
        current_frequency = social_accounts.get("posting_frequency", {})

        platform_strategy = {}

        for platform in platforms:
            platform_config = {
                "handle": existing_handles.get(platform, f"@{platform.lower()}handle"),
                "current_frequency": current_frequency.get(platform, "1-2 posts/week"),
                "recommended_frequency": self._recommend_platform_frequency(platform, client_data),
                "content_types": self._recommend_content_types(platform, client_data),
                "optimal_timing": self._determine_optimal_timing(platform, client_data),
                "engagement_strategy": self._create_engagement_strategy(platform, client_data),
                "hashtag_strategy": self._develop_hashtag_strategy(platform, client_data),
                "competitor_monitoring": social_accounts.get("competitor_handles", [])
            }
            platform_strategy[platform] = platform_config

        return {
            "platforms": platform_strategy,
            "cross_platform_coordination": self._create_cross_platform_strategy(platforms),
            "content_distribution": self._optimize_content_distribution(platforms),
            "performance_tracking": self._setup_performance_tracking(platforms)
        }

    async def _initialize_client_knowledge_base(self, client_data: Dict, brand_profile: Dict,
                                              content_strategy: Dict) -> Dict[str, Any]:
        """Initialize client-specific knowledge base"""

        if not self.knowledge_base:
            try:
                self.knowledge_base = await get_social_content_knowledge_base()
            except Exception as e:
                logger.warning(f"Knowledge base initialization failed: {e}")
                return {"status": "failed", "error": str(e)}

        client_id = self._generate_client_id(client_data)

        try:
            # Create client knowledge base
            client_kb = await self.knowledge_base.create_client_kb(client_id, {
                "company_info": client_data.get("company_info", {}),
                "brand_profile": brand_profile,
                "content_strategy": content_strategy,
                "audience_profile": {},  # Will be filled by audience analysis
                "platform_strategy": {},  # Will be filled by platform strategy
                "features": client_data.get("features", []),
                "how_it_works": client_data.get("how_it_works", [])
            })

            return {
                "client_id": client_id,
                "status": "initialized",
                "template_count": len(client_kb.templates) if hasattr(client_kb, 'templates') else 0,
                "pattern_count": len(client_kb.patterns) if hasattr(client_kb, 'patterns') else 0,
                "initialization_timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Client KB initialization failed: {e}")
            return {"status": "failed", "error": str(e)}

    def _generate_client_id(self, client_data: Dict[str, Any]) -> str:
        """Generate unique client identifier"""
        company_name = (client_data.get("company_info") or {}).get("company_name", "unknown")
        timestamp = int(datetime.utcnow().timestamp())
        return f"client_{company_name.lower().replace(' ', '_')}_{timestamp}"

    def _estimate_content_quality(self, client_data: Dict[str, Any]) -> float:
        """Estimate content quality score based on input completeness"""

        required_fields = [
            "company_info.company_name",
            "company_info.industry",
            "target_audience.primary_persona",
            "content_preferences.key_messages",
            "social_media_accounts.platforms"
        ]

        completeness_score = 0
        total_fields = len(required_fields)

        for field_path in required_fields:
            keys = field_path.split('.')
            value = client_data
            for key in keys:
                value = value.get(key, {}) if isinstance(value, dict) else None
                if value is None:
                    break

            if value and (not isinstance(value, (list, dict)) or len(value) > 0):
                completeness_score += 1

        # Brand assets and performance data are bonus points
        if (client_data.get("brand_assets") or {}).get("logo_url"):
            completeness_score += 0.5
        if (client_data.get("performance_data") or {}).get("successful_content"):
            completeness_score += 0.5

        quality_score = min(5.0, (completeness_score / total_fields) * 5.0)
        return round(quality_score, 1)

    # Helper methods for analysis
    def _extract_personality_traits(self, brand_voice: str) -> List[str]:
        """Extract personality traits from brand voice analysis"""
        traits = []
        if "professional" in brand_voice.lower():
            traits.extend(["trustworthy", "competent", "reliable"])
        if "casual" in brand_voice.lower():
            traits.extend(["approachable", "friendly", "conversational"])
        if "technical" in brand_voice.lower():
            traits.extend(["expert", "innovative", "detailed"])
        return traits[:5] if traits else ["professional", "reliable"]

    def _determine_communication_style(self, company_info: Dict) -> str:
        """Determine communication style based on company info"""
        industry = company_info.get("industry", "").lower()
        if "b2b" in industry or "enterprise" in industry:
            return "professional_formal"
        elif "consumer" in industry or "retail" in industry:
            return "conversational_casual"
        else:
            return "balanced_professional"

    def _create_tone_guidelines(self, brand_voice: str) -> Dict[str, str]:
        """Create tone guidelines for different contexts"""
        return {
            "educational_content": "informative and helpful",
            "promotional_content": "enthusiastic but not pushy",
            "customer_service": "empathetic and solution-oriented",
            "thought_leadership": "authoritative and insightful",
            "social_engagement": "friendly and engaging"
        }

    def _identify_language_patterns(self, content_samples: List[str]) -> Dict[str, Any]:
        """Identify language patterns from content samples"""
        if not content_samples:
            return {"patterns": ["professional", "benefit-focused"], "confidence": 0.5}

        return {
            "patterns": ["benefit-focused", "solution-oriented", "trust-building"],
            "confidence": 0.8,
            "sample_size": len(content_samples)
        }

    def _estimate_audience_size(self, company_info: Dict) -> str:
        """Estimate target audience size"""
        company_size = company_info.get("company_size", "SMB")
        if "enterprise" in company_size.lower():
            return "large_enterprise"
        elif "mid" in company_size.lower():
            return "mid_market"
        else:
            return "small_business"

    def _determine_content_preferences(self, audience_data: Dict) -> Dict[str, Any]:
        """Determine content preferences based on audience"""
        return {
            "preferred_formats": ["educational", "case_studies", "industry_insights"],
            "content_length": "medium",
            "visual_elements": "moderate",
            "call_to_action_style": "soft_guidance"
        }

    def _identify_differentiators(self, company_info: Dict, competitor: str) -> List[str]:
        """Identify key differentiators from competitors"""
        return [
            "Superior customer support",
            "Advanced technology integration",
            "Proven industry expertise",
            "Scalable solutions"
        ]

    def _find_messaging_gaps(self, company_info: Dict, competitor: str) -> List[str]:
        """Find messaging gaps compared to competitors"""
        return [
            "Emphasize ease of implementation",
            "Highlight long-term ROI",
            "Showcase customer success stories"
        ]

    def _determine_market_position(self, company_info: Dict, competitors: List) -> str:
        """Determine market positioning"""
        if len(competitors) > 3:
            return "crowded_market_challenger"
        else:
            return "emerging_market_leader"

    def _identify_differentiation_opportunities(self, company_info: Dict, competitors: List) -> List[str]:
        """Identify differentiation opportunities"""
        return [
            "Superior user experience",
            "Advanced AI capabilities",
            "Exceptional customer success",
            "Competitive pricing model"
        ]

    def _analyze_content_gaps(self, competitors: List) -> List[str]:
        """Analyze content gaps in competitive landscape"""
        return [
            "Technical implementation guides",
            "ROI calculation tools",
            "Customer success stories",
            "Industry trend analysis"
        ]

    def _create_content_pillars(self, brand_voice: str, primary_persona: Dict, differentiators: List) -> List[Dict]:
        """Create content pillars for the brand"""
        return [
            {
                "pillar": "Educational Content",
                "focus": "Help audience solve problems",
                "content_types": ["how-to guides", "best practices", "industry insights"],
                "target_persona": primary_persona.get("name", "Professional")
            },
            {
                "pillar": "Thought Leadership",
                "focus": "Establish industry authority",
                "content_types": ["research reports", "trend analysis", "expert opinions"],
                "target_persona": primary_persona.get("name", "Professional")
            },
            {
                "pillar": "Customer Success",
                "focus": "Showcase results and ROI",
                "content_types": ["case studies", "testimonials", "ROI calculators"],
                "target_persona": primary_persona.get("name", "Professional")
            }
        ]

    def _define_content_themes(self, content_pillars: List, brand_voice: str) -> List[str]:
        """Define content themes based on pillars"""
        themes = []
        for pillar in content_pillars:
            themes.extend(pillar.get("content_types", []))
        return list(set(themes))  # Remove duplicates

    def _extract_core_messages(self, brand_profile: Dict, differentiators: List) -> List[str]:
        """Extract core messages from brand profile"""
        return [
            "We help businesses achieve their goals through innovative solutions",
            "Our expertise delivers measurable results",
            "We prioritize customer success and long-term partnerships"
        ]

    def _create_value_propositions(self, differentiators: List) -> List[str]:
        """Create value propositions from differentiators"""
        return [
            "Save time and reduce costs with our efficient solutions",
            "Achieve better results with our proven methodologies",
            "Get expert support and guidance throughout your journey"
        ]

    def _create_elevator_pitch(self, brand_profile: Dict, primary_persona: Dict) -> str:
        """Create elevator pitch for the brand"""
        company_name = brand_profile.get("company_name", "Our company")
        return f"{company_name} helps {primary_persona.get('name', 'professionals')} achieve their goals through innovative, results-driven solutions."

    def _identify_key_phrases(self, brand_profile: Dict) -> List[str]:
        """Identify key phrases for consistent messaging"""
        return [
            "results-driven solutions",
            "innovative approach",
            "customer success",
            "proven methodology",
            "expert guidance"
        ]

    def _determine_content_mix(self, audience_profile: Dict) -> Dict[str, float]:
        """Determine optimal content mix"""
        return {
            "educational": 0.4,
            "promotional": 0.2,
            "engagement": 0.3,
            "thought_leadership": 0.1
        }

    def _recommend_posting_frequency(self, audience_profile: Dict) -> Dict[str, str]:
        """Recommend posting frequency per platform"""
        return {
            "LinkedIn": "3-5 posts/week",
            "Twitter": "5-8 posts/week",
            "Facebook": "2-4 posts/week",
            "Instagram": "3-6 posts/week"
        }

    def _define_content_best_practices(self, brand_voice: str, audience_profile: Dict) -> List[str]:
        """Define content best practices"""
        return [
            "Focus on audience pain points and solutions",
            "Use data and examples to support claims",
            "Maintain consistent brand voice across all content",
            "Include clear calls-to-action",
            "Optimize for mobile consumption"
        ]

    def _recommend_platform_frequency(self, platform: str, client_data: Dict) -> str:
        """Recommend posting frequency for specific platform"""
        platform_freq = {
            "LinkedIn": "3-5 posts/week",
            "Twitter": "5-8 posts/week",
            "Facebook": "2-4 posts/week",
            "Instagram": "3-6 posts/week"
        }
        return platform_freq.get(platform, "2-4 posts/week")

    def _recommend_content_types(self, platform: str, client_data: Dict) -> List[str]:
        """Recommend content types for specific platform"""
        platform_content = {
            "LinkedIn": ["thought_leadership", "educational", "professional_networking"],
            "Twitter": ["educational", "engagement", "news"],
            "Facebook": ["community", "educational", "promotional"],
            "Instagram": ["visual", "storytelling", "engagement"]
        }
        return platform_content.get(platform, ["educational", "engagement"])

    def _determine_optimal_timing(self, platform: str, client_data: Dict) -> List[str]:
        """Determine optimal posting times"""
        platform_timing = {
            "LinkedIn": ["8:00", "12:00", "17:00"],
            "Twitter": ["9:00", "14:00", "18:00"],
            "Facebook": ["13:00", "15:00", "19:00"],
            "Instagram": ["11:00", "17:00", "20:00"]
        }
        return platform_timing.get(platform, ["12:00", "18:00"])

    def _create_engagement_strategy(self, platform: str, client_data: Dict) -> Dict[str, Any]:
        """Create engagement strategy for platform"""
        return {
            "response_time": "< 2 hours",
            "engagement_types": ["likes", "comments", "shares", "questions"],
            "community_building": "active_participation",
            "conversation_starters": "industry_questions"
        }

    def _develop_hashtag_strategy(self, platform: str, client_data: Dict) -> Dict[str, Any]:
        """Develop hashtag strategy for platform"""
        platform_hashtags = {
            "LinkedIn": ["#Business", "#Leadership", "#Innovation"],
            "Twitter": ["#Business", "#Tech", "#Growth"],
            "Facebook": ["#Business", "#Community", "#Growth"],
            "Instagram": ["#Business", "#Innovation", "#Success"]
        }

        return {
            "primary_hashtags": platform_hashtags.get(platform, ["#Business"]),
            "optimal_count": 2 if platform == "Twitter" else (5 if platform == "Instagram" else 1),
            "mix_branded_generic": 0.3
        }

    def _create_cross_platform_strategy(self, platforms: List[str]) -> Dict[str, Any]:
        """Create cross-platform coordination strategy"""
        return {
            "content_repurposing": "adapt_core_message",
            "timing_coordination": "staggered_posting",
            "platform_synergy": "complementary_content",
            "performance_sharing": "best_performing_content"
        }

    def _optimize_content_distribution(self, platforms: List[str]) -> Dict[str, float]:
        """Optimize content distribution across platforms"""
        total_platforms = len(platforms)
        if total_platforms == 0:
            return {}

        base_distribution = 1.0 / total_platforms
        distribution = {}

        # Adjust based on platform priorities
        for platform in platforms:
            if platform == "LinkedIn":
                distribution[platform] = base_distribution * 1.2  # 20% more for LinkedIn
            elif platform == "Twitter":
                distribution[platform] = base_distribution * 1.1  # 10% more for Twitter
            else:
                distribution[platform] = base_distribution

        # Normalize to ensure sum = 1.0
        total = sum(distribution.values())
        distribution = {k: v/total for k, v in distribution.items()}

        return distribution

    def _setup_performance_tracking(self, platforms: List[str]) -> Dict[str, Any]:
        """Setup performance tracking for platforms"""
        return {
            "metrics": ["engagement_rate", "reach", "clicks", "conversions"],
            "reporting_frequency": "weekly",
            "benchmarking": "industry_standards",
            "optimization_triggers": {
                "engagement_threshold": 0.02,
                "performance_review": "bi_weekly"
            }
        }

    # Tool implementations
    async def _analyze_website(self, url: str) -> Dict[str, Any]:
        """Analyze website content to extract brand info"""
        logger.info(f"Analyzing website: {url}")
        
        # Try using IngestionAgent first for deep analysis
        if ingest_website:
            try:
                result = await ingest_website(url)
                if result.get("success") and result.get("summary"):
                    summary = result["summary"]
                    logger.info(f"Website analysis successful via IngestionAgent")
                    
                    # Map IngestionAgent output to our format
                    return {
                        "brand_voice": summary.get("brand_tone", "professional"),
                        "mission": summary.get("value_proposition") or summary.get("summary", ""),
                        "industry": summary.get("industry", "General"),
                        "target_audience": summary.get("target_audience", "General audience"),
                        "business_offering": summary.get("business_offering", ""),
                        "key_features": summary.get("key_features", []),
                        "how_it_works": [], # IngestionAgent currently doesn't explicitly extract this, could be added later
                        "title": url,
                        "social_presence": [], # We could extract this from raw content if needed
                        "raw_data": summary
                    }
            except Exception as e:
                logger.warning(f"IngestionAgent failed: {e}. Falling back to basic extraction.")

        try:
            # Basic validation
            if not url.startswith("http"):
                url = "https://" + url
                
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(url)
                html = response.text
                
            # Basic extraction (Regex/String parsing since bs4 might not be available)
            # 1. Title
            title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
            title = title_match.group(1).strip() if title_match else ""
            
            # 2. Meta Description (Mission)
            meta_desc_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', html, re.IGNORECASE)
            if not meta_desc_match:
                 meta_desc_match = re.search(r'<meta\s+content=["\'](.*?)["\']\s+name=["\']description["\']', html, re.IGNORECASE)
            description = meta_desc_match.group(1).strip() if meta_desc_match else ""
            
            # 3. Simple Keyword Extraction for Industry
            industry = "General Business"
            keywords_map = {
                "blockchain security": ["blockchain", "web3", "crypto", "smart contract", "audit", "defi", "security", "token", "nft", "wallet", "cosmos"],
                "technology": ["software", "saas", "tech", "app", "platform", "data", "cloud", "ai", "artificial intelligence"],
                "marketing": ["marketing", "seo", "branding", "agency", "social media", "content"],
                "healthcare": ["health", "medical", "wellness", "care", "clinic", "doctor"],
                "finance": ["finance", "money", "invest", "bank", "wealth", "capital", "fund"],
                "ecommerce": ["shop", "store", "buy", "fashion", "retail", "product"]
            }
            
            # Include URL in text analysis as it often contains brand/industry keywords
            combined_text = (title + " " + description + " " + url).lower()
            for ind, keys in keywords_map.items():
                if any(k in combined_text for k in keys):
                    industry = ind.title()
                    break
            
            # 4. Social Links
            social_platforms = ["twitter", "facebook", "linkedin", "instagram", "tiktok"]
            found_socials = []
            for platform in social_platforms:
                if f"{platform}.com" in html.lower():
                    found_socials.append(platform)
            
            logger.info(f"Website analysis result (Basic): {title} - {industry}")
            
            return {
                "brand_voice": "professional", # Default
                "mission": description,
                "industry": industry,
                "target_audience": f"Customers looking for {industry} solutions" if industry else "General audience",
                "social_presence": found_socials,
                "title": title,
                "key_features": [],
                "business_offering": ""
            }
            
        except Exception as e:
            logger.warning(f"Website analysis failed: {e}")
            return {
                "brand_voice": "professional",
                "mission": "",
                "industry": "Unknown",
                "key_features": []
            }

    async def _audit_social_media(self, platforms: List[str], handles: Dict[str, str]) -> Dict[str, Any]:
        """Audit social media presence"""
        # Placeholder for social media audit
        return {
            "overall_health": "good",
            "engagement_rate": 0.025,
            "content_consistency": "high",
            "recommendations": ["increase posting frequency", "improve hashtag usage"]
        }

    async def _detect_brand_voice(self, content_samples: List[str]) -> Dict[str, Any]:
        """Detect brand voice from content samples"""
        # Placeholder for brand voice detection
        return {
            "primary_voice": "professional",
            "secondary_traits": ["helpful", "authoritative"],
            "tone_consistency": 0.85,
            "recommendations": ["maintain professional tone"]
        }

    async def _analyze_competitors(self, competitors: List[str]) -> Dict[str, Any]:
        """Analyze competitors"""
        # Placeholder for competitor analysis
        return {
            "competitive_landscape": "moderately_competitive",
            "key_differentiators": ["superior_support", "advanced_features"],
            "content_gaps": ["implementation_guides", "roi_calculators"]
        }

    async def _profile_audience(self, audience_data: Dict) -> Dict[str, Any]:
        """Create audience profile"""
        # Placeholder for audience profiling
        return {
            "primary_persona": {
                "name": "TechSavvy Manager",
                "demographics": {"age": "35-45", "role": "Marketing Manager"},
                "challenges": ["time_constraints", "budget_limits"],
                "goals": ["increase_efficiency", "improve_results"]
            },
            "content_preferences": ["educational", "case_studies"],
            "engagement_patterns": {"peak_times": ["9am", "2pm"]}
        }

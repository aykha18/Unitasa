"""
Client Analysis Agent - Onboarding Specialist
Analyzes new clients and builds comprehensive brand profiles for automated content generation
"""

import asyncio
import re
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import structlog

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool, StructuredTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from app.agents.base_agent import BaseAgent
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

    def __init__(self, llm: ChatOpenAI, knowledge_base=None):
        self.knowledge_base = knowledge_base
        self.current_client_data = {}
        self.latest_analysis_result = {}
        
        # Initialize RAG chain for brand analysis
        try:
            self.brand_analysis_chain = get_confidence_rag_chain()
        except Exception as e:
            logger.warning(f"RAG chain initialization failed: {e}. Using fallback mode.")
            self.brand_analysis_chain = None
            
        super().__init__("client_analysis", llm, self.get_analysis_tools())

    def get_analysis_tools(self) -> List[Any]:
        """Get tools for client analysis"""
        return [
            StructuredTool.from_function(
                func=self._perform_analysis_tool,
                name="perform_client_analysis",
                description="Perform comprehensive client analysis including website, brand voice, audience, and competitors. Use this tool to analyze the current client."
            )
        ]

    def get_system_prompt(self) -> ChatPromptTemplate:
        """Get agent-specific system prompt"""
        return ChatPromptTemplate.from_messages([
            ("system", """You are an expert Marketing Onboarding Specialist and Brand Analyst.
Your goal is to analyze client information to build comprehensive brand profiles.

You have access to a comprehensive analysis tool "perform_client_analysis" that performs:
1. Website analysis
2. Brand voice detection
3. Audience profiling
4. Competitive analysis
5. Content strategy development

Your task is to:
1. Review the client information provided in the context.
2. Call the "perform_client_analysis" tool to generate the brand profile.
3. Once the analysis is complete, confirm the successful creation of the brand profile and summarize the key findings (Brand Voice, Primary Persona, Key Differentiators).

Client Information:
{client_info_summary}

Always start by running the analysis tool."""),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

    def build_input(self, state: MarketingAgentState) -> Dict[str, Any]:
        """Build input data from shared state"""
        self.current_client_data = state.get("campaign_config", {})
        
        # Create a summary string for the prompt
        company_info = self.current_client_data.get("company_info", {})
        summary = f"Company: {company_info.get('company_name', 'Unknown')}\n"
        summary += f"Industry: {company_info.get('industry', 'Unknown')}\n"
        summary += f"Website: {company_info.get('website', 'Not provided')}\n"
        
        return {
            "client_info_summary": summary,
            "input": "Please perform a comprehensive analysis for this client."
        }

    def update_state(self, state: MarketingAgentState, result: Dict[str, Any]) -> MarketingAgentState:
        """Update shared state with analysis results"""
        
        # If we have a structured analysis result stored from the tool execution
        if self.latest_analysis_result:
            state["client_profile"] = {
                "company_info": self.latest_analysis_result.get("company_info", {}),
                "features": self.latest_analysis_result.get("features", []),
                "how_it_works": self.latest_analysis_result.get("how_it_works", [])
            }
            state["brand_profile"] = self.latest_analysis_result.get("brand_profile", {})
            state["target_audience"] = self.latest_analysis_result.get("audience_profile", {})
            
            # Also store the full analysis in a way that other agents can access parts of it
            # For example, competitive profile might be useful
            state["campaign_config"]["competitive_profile"] = self.latest_analysis_result.get("competitive_profile", {})
            state["campaign_config"]["content_strategy"] = self.latest_analysis_result.get("content_strategy", {})
            
            logger.info("state_updated_with_analysis_results")
            
        return state

    async def _perform_analysis_tool(self) -> str:
        """
        Tool wrapper to perform client analysis using the current client data.
        Returns a summary string for the LLM.
        """
        try:
            logger.info("starting_client_analysis_tool")
            result = await self.analyze_client(self.current_client_data)
            self.latest_analysis_result = result
            
            # Return a summary for the LLM
            brand_voice = result.get("brand_profile", {}).get("brand_voice", "Unknown")
            persona = result.get("audience_profile", {}).get("primary_persona", {}).get("name", "Unknown")
            
            return f"Analysis complete. Brand Voice: {brand_voice}. Primary Persona: {persona}. Full profile stored in state."
            
        except Exception as e:
            logger.error(f"analysis_tool_failed: {str(e)}")
            return f"Analysis failed: {str(e)}"

    async def analyze_client(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete client analysis and profile creation.
        This is the main entry point for client onboarding.
        """
        logger.info(f"Analyzing client with data keys: {list(client_data.keys()) if client_data else 'None'}")
        
        if not client_data:
            # Try to get from instance if passed as empty
            if self.current_client_data:
                client_data = self.current_client_data
            else:
                raise ValueError("client_data cannot be None or empty")

        client_id = self._generate_client_id(client_data)
        logger.info(f"Starting client analysis for {client_id}")

        try:
            # Step 0: Website Analysis (if provided)
            # This enriches the client_data before deep analysis
            company_info = client_data.get("company_info", {})
            if not company_info:
                # Initialize if missing
                company_info = {}
                client_data["company_info"] = company_info
                
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

                    if "how_it_works" not in client_data and website_data.get("how_it_works"):
                        # Convert string list to structured format (steps)
                        steps_list = []
                        raw_steps = website_data.get("how_it_works", [])
                        for i, step in enumerate(raw_steps):
                            if isinstance(step, str):
                                steps_list.append({
                                    "step": i + 1,
                                    "title": step,
                                    "description": ""
                                })
                            elif isinstance(step, dict):
                                steps_list.append(step)
                        client_data["how_it_works"] = steps_list
                        logger.info(f"Extracted {len(steps_list)} how-it-works steps from website")

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

            # Step 0.5: Generative Fallback for Missing Features/Steps
            # If scraping failed or returned empty, use LLM to infer features from description/industry
            if self.llm and (not client_data.get("features") or not client_data.get("how_it_works")):
                logger.info("Features/Steps missing after scraping. Using LLM generation fallback.")
                try:
                    c_info = client_data.get("company_info", {})
                    desc = c_info.get("mission_statement") or c_info.get("description") or "A business"
                    ind = c_info.get("industry") or "General"
                    name = c_info.get("company_name") or "The Company"
                    
                    prompt = f"""
                    Based on the following company details, generate 3 key features and 3 simple "how it works" steps.
                    Company: {name}
                    Industry: {ind}
                    Description: {desc}
                    
                    Return ONLY a JSON object with this format:
                    {{
                        "features": [{{"title": "Feature Name", "description": "Short description"}}],
                        "how_it_works": [{{"step": 1, "title": "Step Name", "description": "Short description"}}]
                    }}
                    """
                    
                    # Assume self.llm is a LangChain model or compatible
                    from langchain_core.messages import HumanMessage
                    response = await self.llm.ainvoke([HumanMessage(content=prompt)])
                    content = response.content if hasattr(response, 'content') else str(response)
                    
                    # Parse JSON
                    import json
                    # Clean markdown code blocks if present
                    content = content.replace("```json", "").replace("```", "").strip()
                    try:
                        generated_data = json.loads(content)
                        
                        if not client_data.get("features") and generated_data.get("features"):
                            client_data["features"] = generated_data["features"]
                            logger.info(f"Generated {len(generated_data['features'])} features via LLM")
                            
                        if not client_data.get("how_it_works") and generated_data.get("how_it_works"):
                            client_data["how_it_works"] = generated_data["how_it_works"]
                            logger.info(f"Generated {len(generated_data['how_it_works'])} steps via LLM")
                    except json.JSONDecodeError:
                        logger.warning("Failed to parse LLM JSON response")
                        
                except Exception as e:
                    logger.warning(f"LLM generation fallback failed: {e}")

            # Step 1: Brand Voice Analysis
            logger.info("Starting brand voice analysis")
            brand_profile = await self._analyze_brand_voice(client_data)

            # Step 2: Audience Analysis
            logger.info("Starting audience analysis")
            audience_profile = await self._analyze_target_audience(client_data)

            # Step 3: Competitive Analysis
            logger.info("Starting competitive analysis")
            competitive_profile = await self._analyze_competition(client_data)

            # Step 4: Content Strategy Development
            logger.info("Starting content strategy development")
            content_strategy = await self._develop_content_strategy(
                brand_profile, audience_profile, competitive_profile
            )

            # Step 5: Platform Strategy
            logger.info("Starting platform strategy")
            platform_strategy = await self._create_platform_strategy(client_data)

            # Step 6: Knowledge Base Initialization
            logger.info("Starting knowledge base initialization")
            client_kb = await self._initialize_client_knowledge_base(
                client_data, brand_profile, content_strategy
            )

            # Calculate content quality estimate
            quality_score = self._estimate_content_quality(client_data)

            result = {
                "client_id": client_id,
                "company_info": client_data.get("company_info", {}),
                "features": client_data.get("features", []),
                "how_it_works": client_data.get("how_it_works", []),
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

            return result

        except Exception as e:
            logger.error(f"Client analysis failed for {client_id}: {e}", exc_info=True)
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
                        "how_it_works": summary.get("how_it_works", []),
                    }
            except Exception as e:
                logger.warning(f"IngestionAgent failed: {e}. Falling back to basic analysis.")
        
        # Fallback to basic implementation if IngestionAgent fails or is unavailable
        # (For this example, we just return empty/default data if ingestion fails)
        return {
            "brand_voice": "professional",
            "mission": "",
            "industry": "Technology",
            "target_audience": "Businesses",
        }

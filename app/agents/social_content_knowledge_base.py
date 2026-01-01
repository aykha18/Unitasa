"""
Social Media Content Knowledge Base - Cost Optimization System
Reduces LLM API calls by 70-80% through intelligent caching and retrieval
"""

import json
import asyncio
import os
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
import structlog

# Import LLM Router for intelligent template customization
try:
    from app.llm.router import get_optimal_llm
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

try:
    from app.rag.vectorstore_manager import get_vector_store_manager
    from app.rag.ingestion import DocumentIngestionPipeline as ContentIngestionService
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

    async def get_content_suggestions(self, topic: str, platform: str, content_type: Optional[str] = None, limit: int = 1) -> List[ContentTemplate]:
        import random
        
        # Filter matching templates
        matching = [
            t for t in self.templates
            if t.platform == platform and (content_type is None or t.content_type == content_type)
        ]
        
        # If not enough specific matches, try relaxing content_type constraint
        if len(matching) < limit and content_type:
            matching = [t for t in self.templates if t.platform == platform]
            
        # Shuffle to ensure variety on every call
        random.shuffle(matching)
        
        return matching[:limit]

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
        # 1. Load Vector Store (Optional)
        try:
            if VECTOR_STORE_AVAILABLE:
                self.vector_store = await get_vector_store_manager()
            else:
                self.vector_store = None
                logger.info("Vector store not available, using in-memory knowledge base")
        except Exception as e:
            logger.warning(f"Failed to load vector store: {e}. Continuing without it.")
            self.vector_store = None

        # 2. Load Templates (Critical)
        try:
            await self._load_templates_from_storage()
            await self._load_patterns_from_storage()
            
            logger.info(f"Loaded knowledge base: {len(self.templates)} templates, {len(self.patterns)} patterns")
        except Exception as e:
            logger.error(f"Failed to load templates/patterns: {e}")

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

    def _get_generic_templates(self) -> List[ContentTemplate]:
        """Return generic templates that can be customized for any industry"""
        return [
            # Twitter Generic
            ContentTemplate(
                id="twitter_generic_educational",
                feature="core_service",
                platform="twitter",
                content_type="educational",
                template="🚀 Ready to transform your {industry}? {company_name} helps you {value_proposition}. Don't settle for less! #{industry_hashtag} #Growth",
                variables=["industry", "company_name", "value_proposition", "industry_hashtag"],
                hashtags=[],
                call_to_action="Learn more",
                character_count=100
            ),
             ContentTemplate(
                id="twitter_generic_benefit",
                feature="benefit_focused",
                platform="twitter",
                content_type="benefit_focused",
                template="💡 Did you know? {pain_point} can cost you time and money. {company_name} provides the solution you need. #{industry_hashtag} #Tips",
                variables=["pain_point", "company_name", "industry", "industry_hashtag"],
                hashtags=[],
                call_to_action="Get started",
                character_count=120
            ),
            # Facebook Generic
            ContentTemplate(
                id="facebook_generic_story",
                feature="story_driven",
                platform="facebook",
                content_type="story_driven",
                template="Every business faces challenges. For {industry} leaders, it's often {pain_point}. At {company_name}, we're on a mission to change that. Our {mission_statement} approach ensures you get results. Join hundreds of satisfied clients today.",
                variables=["industry", "pain_point", "company_name", "mission_statement"],
                hashtags=[],
                call_to_action="Book consultation",
                character_count=200
            ),
            # Instagram Generic
            ContentTemplate(
                id="instagram_generic_visual",
                feature="visual_focused",
                platform="instagram",
                content_type="visual_focused",
                template="✨ Elevate your {industry} game! 🚀\n\n{company_name} brings you top-tier solutions for {pain_point}.\n\n✅ {value_proposition}\n✅ Trusted by experts\n\nLink in bio to learn more! 👇\n\n#{industry_hashtag} #{company_hashtag} #Success",
                variables=["industry", "company_name", "pain_point", "value_proposition", "industry_hashtag", "company_hashtag"],
                hashtags=[],
                call_to_action="Link in bio",
                character_count=150
            )
        ]

    def _get_blockchain_security_templates(self) -> List[ContentTemplate]:
        """Return highly specialized templates for Blockchain Security"""
        return [
            # Twitter Specialized
            ContentTemplate(
                id="twitter_blockchain_audit_alert",
                feature="smart_contract_audit",
                platform="twitter",
                content_type="educational",
                template="🛡️ Smart Contract Security Alert: Reentrancy attacks are still a top threat in DeFi. At {company_name}, we use formal verification to ensure your protocol is hack-proof. Secure your launch today. #{industry_hashtag} #DeFiSecurity #Audit",
                variables=["company_name", "industry_hashtag"],
                hashtags=["#DeFi", "#Web3Security"],
                call_to_action="Request Audit",
                character_count=160
            ),
            ContentTemplate(
                id="twitter_blockchain_gas_optimization",
                feature="gas_optimization",
                platform="twitter",
                content_type="benefit_focused",
                template="⛽ Stop burning user funds on high gas fees! Our optimization experts at {company_name} can reduce your contract's gas usage by up to 30%. Better UX, lower costs. #{industry_hashtag} #GasOptimization",
                variables=["company_name", "industry_hashtag"],
                hashtags=["#Ethereum", "#Solidity"],
                call_to_action="Optimize Now",
                character_count=150
            ),
             ContentTemplate(
                id="twitter_blockchain_trust",
                feature="trust_building",
                platform="twitter",
                content_type="social_proof",
                template="🤝 Trust is the currency of Web3. Don't let a vulnerability destroy your reputation. {company_name} provides comprehensive {industry} services to give your community peace of mind. #Web3 #{industry_hashtag}",
                variables=["company_name", "industry", "industry_hashtag"],
                hashtags=["#CryptoSafety"],
                call_to_action="View Portfolio",
                character_count=170
            ),
            # LinkedIn Specialized
            ContentTemplate(
                id="linkedin_blockchain_thought_leadership",
                feature="thought_leadership",
                platform="linkedin",
                content_type="educational",
                template="The cost of a smart contract bug isn't just financial—it's existential for your protocol.\n\nAt {company_name}, we've seen how {pain_point} destroys promising projects overnight.\n\nOur rigorous audit process includes:\n✅ Manual Line-by-Line Review\n✅ Automated Static Analysis\n✅ Formal Verification\n\nDon't launch until you're sure. Let's secure the future of finance together.\n\n#{industry_hashtag} #SmartContractAudit #Web3 #DeFi",
                variables=["company_name", "pain_point", "industry_hashtag"],
                hashtags=["#Blockchain", "#CyberSecurity"],
                call_to_action="Contact our team",
                character_count=350
            )
        ]

    async def get_client_profile(self, client_id: str) -> Dict[str, Any]:
        """Get the effective profile for a client (loaded or fallback)"""
        # If already loaded, return it
        if client_id in self.client_knowledge_bases:
            return self.client_knowledge_bases[client_id].brand_profile
            
        # Otherwise, try to load it (which handles disk load or fallback)
        # We can reuse the logic in get_client_content by factoring it out, 
        # or just call create_client_kb if we can find the data.
        
        # 1. Try disk
        data_dir = os.path.join(os.getcwd(), "data", "clients")
        file_path = os.path.join(data_dir, f"{client_id}.json")
        
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    profile = json.load(f)
                await self.create_client_kb(client_id, profile)
                return profile
            except Exception:
                pass
                
        # 2. Fallback
        parts = client_id.split('_')
        company_name = "Your Company"
        if len(parts) >= 3 and parts[0] == 'client':
             company_name_parts = parts[1:-1]
             company_name = " ".join(company_name_parts).title()
             
        fallback_profile = {
             "company_info": {
                 "company_name": company_name,
                 "industry": "General",
                 "brand_voice": "professional"
             }
        }
        await self.create_client_kb(client_id, fallback_profile)
        return fallback_profile

    async def update_client_profile(self, client_id: str, new_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Update a client's profile and regenerate their KB"""
        # Save to disk
        data_dir = os.path.join(os.getcwd(), "data", "clients")
        os.makedirs(data_dir, exist_ok=True)
        file_path = os.path.join(data_dir, f"{client_id}.json")
        
        with open(file_path, "w") as f:
            json.dump(new_profile, f, indent=2)
            
        # Re-create KB
        await self.create_client_kb(client_id, new_profile)
        return new_profile

    async def create_client_kb(self, client_id: str, client_profile: Dict[str, Any]) -> ClientKnowledgeBase:
        company_info = client_profile.get("company_info", {})
        industry = company_info.get("industry") or "general"
        mission = company_info.get("mission_statement") or ""
        company_name = company_info.get("company_name") or ""
        
        # Check for specific industry templates first
        base_templates = []
        
        # Normalize strings for matching
        industry_norm = industry.lower()
        mission_norm = mission.lower()
        name_norm = company_name.lower()
        
        # Enhanced detection for Blockchain Security
        is_blockchain_security = (
            "blockchain" in industry_norm or 
            "security" in industry_norm or 
            "audit" in industry_norm or
            "web3" in industry_norm or
            "crypto" in industry_norm or
            "smart contract" in mission_norm or
            "audit" in mission_norm or
            "security" in mission_norm or
            "audit" in name_norm or
            "security" in name_norm or
            "cosmos" in name_norm
        )
        
        if is_blockchain_security:
            base_templates = self._get_blockchain_security_templates()
            # Also mix in some generics for variety
            base_templates.extend(self._get_generic_templates())
        else:
            base_templates = self.industry_templates.get(industry, [])
        
        if not base_templates:
             # ALWAYS use generic templates as fallback for clients
             # NEVER use self.templates (Unitasa specifics) unless the client IS Unitasa
             if client_id == "unitasa_internal":
                 base_templates = list(self.templates.values())
             else:
                 base_templates = self._get_generic_templates()
                 
        customized_templates = await self._customize_templates_for_client(base_templates, client_profile)
        
        # Create a new KB instance for this client
        client_kb = ClientKnowledgeBase(
            client_id=client_id,
            brand_profile=client_profile,
            templates=customized_templates,
            patterns=[],
            performance_baseline={"engagement_rate": 0.0, "conversion_rate": 0.0}
        )
        self.client_knowledge_bases[client_id] = client_kb
        return client_kb

    async def get_client_content(self, client_id: str, content_request: Dict[str, Any]) -> List[Dict[str, Any]]:
        # If we don't have the KB loaded for this client, try to load or create it
        if client_id not in self.client_knowledge_bases:
            # 1. Try to load from disk persistence first (best source of truth)
            profile_loaded = False
            client_profile = {}
            
            try:
                # Look for client file in data/clients/
                data_dir = os.path.join(os.getcwd(), "data", "clients")
                file_path = os.path.join(data_dir, f"{client_id}.json")
                
                if os.path.exists(file_path):
                    try:
                        with open(file_path, "r") as f:
                            client_profile = json.load(f)
                        logger.info(f"Loaded persisted profile for {client_id}")
                        profile_loaded = True
                    except Exception as e:
                        logger.error(f"Failed to read client profile file: {e}")
            except Exception as e:
                logger.error(f"Error checking for client profile file: {e}")
            
            # 2. If not found on disk, try minimal reconstruction from ID (fallback)
            if not profile_loaded:
                logger.warning(f"No profile found for {client_id}, using minimal fallback.")
                # client_id format: client_companyname_timestamp
                parts = client_id.split('_')
                if len(parts) >= 3 and parts[0] == 'client':
                    # Reconstruct company name (everything between client_ and _timestamp)
                    company_name_parts = parts[1:-1]
                    company_name = " ".join(company_name_parts).title()
                    
                    client_profile = {
                        "company_info": {
                            "company_name": company_name,
                            "industry": "General", # Default to General to use generic templates
                            "brand_voice": "professional"
                        }
                    }
                else:
                    # Fallback for completely unknown ID format
                    client_profile = {
                        "company_info": {
                            "company_name": "Your Company",
                            "industry": "General",
                            "brand_voice": "professional"
                        }
                    }
            
            await self.create_client_kb(client_id, client_profile)
        
        client_kb = self.client_knowledge_bases[client_id]
        
        # Handle both dict and kwargs input
        if content_request is None:
            content_request = kwargs
            
        topic = content_request.get("topic", "")
        platform = content_request.get("platform", "twitter")
        content_type = content_request.get("content_type")
        
        suggestions = await client_kb.get_content_suggestions(topic, platform, content_type)
        
        # Prepare dynamic variables from client profile
        profile = client_kb.brand_profile
        company_info = profile.get("company_info", {})
        target_audience = profile.get("target_audience", {})
        
        # Extract pain points safely
        pain_points = target_audience.get("pain_points", [])
        primary_pain_point = pain_points[0] if pain_points and isinstance(pain_points, list) else "inefficiency"
        
        company_name = company_info.get("company_name") or "Our Company"
        industry = company_info.get("industry") or "Business"
        
        dynamic_variables = {
            "company_name": company_name,
            "industry": industry,
            "mission_statement": company_info.get("mission_statement") or "help you grow",
            "value_proposition": company_info.get("mission_statement") or "delivers results", # Fallback mapping
            "pain_point": primary_pain_point,
            "time_saved": "valuable time", # Generic fallback
            "platforms": "all your channels",
            "industry_hashtag": industry.replace(" ", "") if industry else "Business",
            "company_hashtag": company_name.replace(" ", "") if company_name else "Company"
        }
        
        outputs: List[Dict[str, Any]] = []
        import uuid
        for t in suggestions:
            content = await self.generate_content_from_template(t, variables=dynamic_variables)
            optimized = await self.optimize_content_with_kb(content, t.feature, platform)
            outputs.append({
                "id": f"{t.id}_{uuid.uuid4().hex[:8]}",
                "content": optimized,
                "platform": t.platform,
                "content_type": t.content_type,
                "feature": t.feature,
                "call_to_action": t.call_to_action,
                "hashtags": t.hashtags,
                "character_count": len(optimized),
                "generated_at": datetime.utcnow().isoformat()
            })
        return outputs

    async def _customize_templates_for_client(self, templates: List[ContentTemplate], client_profile: Dict[str, Any]) -> List[ContentTemplate]:
        brand_voice = client_profile.get("company_info", {}).get("brand_voice") or "professional"
        company_name = client_profile.get("company_info", {}).get("company_name") or "Our Company"
        industry = client_profile.get("company_info", {}).get("industry") or "Business"
        website = client_profile.get("company_info", {}).get("website") or ""
        
        # Use LLM for intelligent rewriting if available and client profile is rich
        if LLM_AVAILABLE and len(templates) > 0: # Customized for all industries
            try:
                llm = get_optimal_llm("content_generation")
                
                # Format rich context from profile
                features = client_profile.get("features", [])
                how_it_works = client_profile.get("how_it_works", [])
                
                features_text = ""
                if features:
                    features_text = "Key Features:\n" + "\n".join([f"- {f.get('title', '')}: {f.get('description', '')}" for f in features])
                
                how_it_works_text = ""
                if how_it_works:
                    how_it_works_text = "How It Works:\n" + "\n".join([f"{s.get('step', '')}. {s.get('title', '')}: {s.get('description', '')}" for s in how_it_works])

                # Batch rewrite for efficiency
                # In production, we might do this one by one or in smaller batches
                template_texts = [t.template for t in templates[:5]] # Limit to 5 for speed
                
                prompt = f"""
                Rewrite the following social media templates to match this specific client's business:
                
                Client: {company_name}
                Industry: {industry}
                Voice: {brand_voice}
                Website: {website}
                Target Audience: {client_profile.get('target_audience', {}).get('primary_persona', 'Professionals')}
                
                {features_text}
                
                {how_it_works_text}
                
                Original Templates (Generic):
                {json.dumps(template_texts, indent=2)}
                
                Instructions:
                1. Keep the same format and intent (educational, promotional, etc.)
                2. Replace generic marketing terms with specific details from the Features and How It Works sections above.
                3. High Priority: Use the "How It Works" steps and "Key Features" to make the content concrete and accurate.
                4. Maintain the same length constraints roughly
                5. If appropriate for the content type (promotional), include the website link {website} naturally (e.g., "Visit {website}" or just the link).
                6. Return ONLY a JSON list of rewritten strings
                """
                
                response = await llm.ainvoke(prompt)
                
                # Clean up response to ensure valid JSON
                content = response.content.strip()
                
                # Remove markdown code blocks if present
                if "```" in content:
                    # Remove ```json ... ``` or just ``` ... ```
                    content = re.sub(r"```(?:json)?\s*", "", content)
                    content = re.sub(r"```\s*$", "", content)
                
                # Ensure we only try to parse the array part
                start_idx = content.find('[')
                end_idx = content.rfind(']')
                
                if start_idx != -1 and end_idx != -1:
                    content = content[start_idx:end_idx+1]
                
                rewritten_texts = json.loads(content)
                
                if len(rewritten_texts) == len(template_texts):
                    # Update the first 5 templates
                    for i, new_text in enumerate(rewritten_texts):
                        templates[i].template = new_text
                        
                    logger.info(f"Successfully customized {len(rewritten_texts)} templates using LLM for {company_name}")
            except Exception as e:
                logger.warning(f"LLM customization failed: {e}. Falling back to simple replacement.")

        # Re-detect context for hashtag customization
        company_info = client_profile.get("company_info", {})
        industry = (company_info.get("industry") or "general").lower()
        mission = (company_info.get("mission_statement") or "").lower()
        website = company_info.get("website") or ""
        company_name_lower = (company_info.get("company_name") or "").lower()
        
        is_blockchain = (
            "blockchain" in industry or 
            "security" in industry or 
            "web3" in industry or
            "crypto" in industry or
            "smart contract" in mission or
            "audit" in mission or
            "defi" in mission or
            "audit" in company_name_lower or
            "security" in company_name_lower or
            "cosmos" in company_name_lower
        )

        customized = []
        for t in templates:
            text = t.template
            hashtags = t.hashtags.copy() if t.hashtags else []
            
            # Replace Unitasa specific references with client name
            text = text.replace("Unitasa", company_name)
            text = text.replace("Unitasa's", f"{company_name}'s")
            
            # Simple tone adjustment
            if brand_voice and brand_voice.lower() == "casual":
                text = text.replace("Transform your", "Level up your")
                text = text.replace("Discover", "Check out")
            
            # Inject website link if available and appropriate
            if website and t.platform.lower() not in ["instagram", "tiktok"]:
                # Replace "Link in bio" with actual link
                if "Link in bio" in text:
                    text = text.replace("Link in bio", f"Visit {website}")
                elif "link in bio" in text:
                    text = text.replace("link in bio", f"Visit {website}")
                elif website not in text:
                    # Append it nicely
                    if t.call_to_action:
                        text += f"\n\n{t.call_to_action}: {website}"
                    else:
                        text += f"\n\n{website}"
            
            # Customize hashtags for blockchain/security
            if is_blockchain:
                # Remove generic business tags if they exist
                generic_tags = ["#business", "#growth", "#efficiency", "#businessgrowth", "#marketing", "#success", "#tips"]
                hashtags = [h for h in hashtags if h.lower() not in generic_tags]
                
                # Also remove these hashtags from the text body if present
                for tag in generic_tags:
                    # Case insensitive replacement
                    pattern = re.compile(re.escape(tag), re.IGNORECASE)
                    text = pattern.sub("", text)
                
                # Add specific tags if not present
                specific_tags = ["#Web3Security", "#Blockchain", "#SmartContracts", "#DeFi"]
                # Only add if we have space (e.g. max 5 tags)
                for tag in specific_tags:
                    if tag not in hashtags and len(hashtags) < 5:
                        hashtags.append(tag)
                
                # Clean up any double spaces created by removal
                text = re.sub(r'\s+', ' ', text).strip()

            customized.append(ContentTemplate(
                id=t.id,
                feature=t.feature,
                platform=t.platform,
                content_type=t.content_type,
                template=text,
                variables=t.variables,
                hashtags=hashtags,
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
                replacement = str(value) if value is not None else ""
                content = content.replace(f"{{{var}}}", replacement)

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

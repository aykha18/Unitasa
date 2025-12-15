"""
ContentGenerationAgent - AI-Powered Content Creation
Generates marketing content, social media posts, and creative assets
"""

import logging
from typing import Dict, Any, List, Optional

from app.agents.base import CostOptimizedAgent

logger = logging.getLogger(__name__)


class ContentGenerationAgent(CostOptimizedAgent):
    """
    Agent responsible for generating various types of marketing content
    """

    def __init__(self, name: str = "content_generation"):
        super().__init__(name)
        self.content_templates = self._load_content_templates()

    def get_system_prompt(self) -> str:
        return """You are an expert marketing copywriter and content strategist. Your expertise includes:

1. Creating compelling marketing copy across all channels
2. Adapting content for different platforms and audiences
3. Developing brand-consistent messaging
4. Optimizing content for engagement and conversion
5. Understanding platform-specific best practices

You create content that resonates with target audiences while maintaining brand integrity."""

    async def execute_task(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute content generation tasks
        """
        content_type = task_input.get("content_type", "social_post")

        if content_type == "social_post":
            return await self._generate_social_post(task_input)
        elif content_type == "blog_post":
            return await self._generate_blog_post(task_input)
        elif content_type == "email_campaign":
            return await self._generate_email_campaign(task_input)
        elif content_type == "ad_copy":
            return await self._generate_ad_copy(task_input)
        elif content_type == "landing_page":
            return await self._generate_landing_page_content(task_input)
        else:
            return {
                "success": False,
                "error": f"Unsupported content type: {content_type}"
            }

    async def _generate_social_post(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate social media post content
        """
        platform = task_input.get("platform", "twitter")
        topic = task_input.get("topic", "")
        business_profile = task_input.get("business_profile", {})
        tone = task_input.get("tone", "professional")
        goal = task_input.get("goal", "engagement")

        if not topic:
            return {"success": False, "error": "Topic is required for content generation"}

        try:
            # Get platform-specific template
            template = self._get_platform_template(platform)

            # Build content generation prompt
            prompt = self._build_social_post_prompt(
                platform, topic, business_profile, tone, goal, template
            )

            # Generate content
            response = await self.generate_response(
                user_prompt=prompt,
                task_description=f"social media content generation for {platform}"
            )

            if not response["success"]:
                return response

            # Parse and enhance the generated content
            content_variants = self._parse_content_response(response["content"])

            return {
                "success": True,
                "content_type": "social_post",
                "platform": platform,
                "topic": topic,
                "content_variants": content_variants,
                "metadata": {
                    "tone": tone,
                    "goal": goal,
                    "estimated_engagement": self._estimate_engagement_potential(content_variants[0] if content_variants else ""),
                    "hashtags_suggested": self._extract_hashtags(content_variants[0] if content_variants else "")
                }
            }

        except Exception as e:
            logger.error(f"Social post generation failed: {e}")
            return {"success": False, "error": str(e)}

    async def _generate_blog_post(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate blog post content
        """
        topic = task_input.get("topic", "")
        business_profile = task_input.get("business_profile", {})
        target_length = task_input.get("target_length", "medium")  # short, medium, long
        keywords = task_input.get("keywords", [])

        if not topic:
            return {"success": False, "error": "Topic is required"}

        try:
            prompt = self._build_blog_post_prompt(topic, business_profile, target_length, keywords)

            response = await self.generate_response(
                user_prompt=prompt,
                task_description="blog post content generation"
            )

            if response["success"]:
                blog_content = self._parse_blog_response(response["content"])
                return {
                    "success": True,
                    "content_type": "blog_post",
                    "topic": topic,
                    "blog_content": blog_content,
                    "seo_score": self._calculate_seo_score(blog_content, keywords)
                }
            else:
                return response

        except Exception as e:
            logger.error(f"Blog post generation failed: {e}")
            return {"success": False, "error": str(e)}

    async def _generate_ad_copy(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate advertising copy
        """
        product_service = task_input.get("product_service", "")
        target_audience = task_input.get("target_audience", "")
        business_profile = task_input.get("business_profile", {})
        ad_format = task_input.get("ad_format", "text")  # text, display, video_script

        if not product_service:
            return {"success": False, "error": "Product/service description required"}

        try:
            prompt = self._build_ad_copy_prompt(product_service, target_audience, business_profile, ad_format)

            response = await self.generate_response(
                user_prompt=prompt,
                task_description="advertising copy generation"
            )

            if response["success"]:
                ad_content = self._parse_ad_response(response["content"])
                return {
                    "success": True,
                    "content_type": "ad_copy",
                    "product_service": product_service,
                    "ad_content": ad_content,
                    "ad_format": ad_format
                }
            else:
                return response

        except Exception as e:
            logger.error(f"Ad copy generation failed: {e}")
            return {"success": False, "error": str(e)}

    def _load_content_templates(self) -> Dict[str, Dict[str, str]]:
        """Load content templates for different platforms and types"""
        return {
            "twitter": {
                "engagement": "What's your take on {topic}? Share below! 💭 #{hashtag}",
                "educational": "Did you know? {fact} Learn more: {link} #{hashtag}",
                "promotional": "Transform your {benefit} with {product}. Start today! {cta} #{hashtag}"
            },
            "linkedin": {
                "professional": "In today's competitive landscape, {insight}. What's your experience? #{hashtag}",
                "thought_leadership": "Here's why {topic} matters for {industry}: {key_point} #{hashtag}",
                "networking": "Connecting with {audience} about {topic}. What's working for you? #{hashtag}"
            },
            "facebook": {
                "community": "What's your biggest challenge with {topic}? Let's discuss! 👇 #{hashtag}",
                "storytelling": "Real talk: {story}. What's your story? #{hashtag}",
                "value_driven": "Stop struggling with {problem}. Here's how to {solution}. #{hashtag}"
            }
        }

    def _get_platform_template(self, platform: str) -> Dict[str, str]:
        """Get content templates for specific platform"""
        return self.content_templates.get(platform.lower(), self.content_templates.get("twitter", {}))

    def _build_social_post_prompt(self, platform: str, topic: str, business_profile: Dict,
                                tone: str, goal: str, template: Dict) -> str:
        """Build social media post generation prompt"""

        brand_context = ""
        if business_profile:
            brand_context = f"""
BRAND CONTEXT:
- Industry: {business_profile.get('brand_positioning', {}).get('industry_sector', 'general')}
- Personality: {business_profile.get('brand_positioning', {}).get('personality', 'professional')}
- Target Audience: {business_profile.get('target_audience', {}).get('icp', 'business professionals')}
"""

        return f"""{brand_context}
Generate 3 variations of a {platform} post about: {topic}

REQUIREMENTS:
- Platform: {platform} (adapt style accordingly)
- Tone: {tone}
- Goal: {goal} (engagement/awareness/conversion)
- Length: Optimal for {platform} ({'280 chars' if platform == 'twitter' else 'appropriate length'})
- Include relevant emojis and hashtags
- Make it conversational and engaging

CONTENT TEMPLATES FOR REFERENCE:
{template}

Return 3 different post variations, each with:
1. The post text
2. Why it works for this platform
3. Expected engagement potential (high/medium/low)

Format as JSON array of objects.
"""

    def _build_blog_post_prompt(self, topic: str, business_profile: Dict, target_length: str, keywords: List) -> str:
        """Build blog post generation prompt"""

        length_guide = {
            "short": "800-1200 words",
            "medium": "1500-2000 words",
            "long": "2500-3500 words"
        }

        brand_context = ""
        if business_profile:
            brand_context = f"""
BRAND CONTEXT:
- Industry: {business_profile.get('brand_positioning', {}).get('industry_sector', 'general')}
- Expertise: {business_profile.get('value_proposition', {}).get('core_offer', 'business solutions')}
- Target Audience: {business_profile.get('target_audience', {}).get('icp', 'business professionals')}
"""

        return f"""{brand_context}
Write a comprehensive blog post about: {topic}

REQUIREMENTS:
- Target Length: {length_guide.get(target_length, '1500-2000 words')}
- SEO Keywords: {', '.join(keywords) if keywords else 'naturally incorporate relevant keywords'}
- Structure: Introduction, {3-5} main sections with headers, conclusion
- Include: Statistics, examples, actionable tips
- Tone: Professional but approachable
- Call-to-Action: Include at end

BLOG POST STRUCTURE:
1. Compelling headline
2. Engaging introduction with hook
3. Main content sections with subheaders
4. Practical examples or case studies
5. Key takeaways or summary
6. Strong call-to-action

Make it valuable, shareable, and optimized for search engines.
"""

    def _build_ad_copy_prompt(self, product_service: str, target_audience: str,
                            business_profile: Dict, ad_format: str) -> str:
        """Build advertising copy generation prompt"""

        format_specs = {
            "text": "Compelling headline + 2-3 benefit-focused sentences + strong CTA",
            "display": "Eye-catching headline + key benefits + social proof + CTA button",
            "video_script": "15-30 second script with hook, problem/solution, CTA"
        }

        return f"""
Create compelling ad copy for: {product_service}

TARGET AUDIENCE: {target_audience}
AD FORMAT: {ad_format}
FORMAT SPECIFICATIONS: {format_specs.get(ad_format, 'Standard ad copy')}

BRAND CONTEXT:
- Unique Value: {business_profile.get('value_proposition', {}).get('core_offer', 'quality solutions')}
- Competitive Edge: {', '.join(business_profile.get('value_proposition', {}).get('competitive_advantages', ['quality']))}

REQUIREMENTS:
- Focus on benefits, not features
- Create urgency or social proof
- Include clear call-to-action
- Match brand voice and positioning
- Optimize for conversion

Return 3 different ad copy variations.
"""

    def _parse_content_response(self, response_content: str) -> List[Dict[str, Any]]:
        """Parse AI response into structured content variants"""
        # Simple parsing - in production would be more sophisticated
        lines = response_content.strip().split('\n')
        variants = []

        current_variant = {}
        for line in lines:
            line = line.strip()
            if line.startswith(('1.', '2.', '3.', 'Variant', 'Post')):
                if current_variant:
                    variants.append(current_variant)
                current_variant = {"text": "", "reasoning": "", "engagement": "medium"}
            elif current_variant:
                if "text" not in current_variant or not current_variant["text"]:
                    current_variant["text"] = line
                elif "reasoning" not in current_variant or not current_variant["reasoning"]:
                    current_variant["reasoning"] = line

        if current_variant:
            variants.append(current_variant)

        # Ensure we have at least one variant
        if not variants:
            variants = [{
                "text": response_content[:200],
                "reasoning": "Generated content",
                "engagement": "medium"
            }]

        return variants[:3]  # Return up to 3 variants

    def _parse_blog_response(self, response_content: str) -> Dict[str, Any]:
        """Parse blog post response"""
        return {
            "title": self._extract_title(response_content),
            "content": response_content,
            "word_count": len(response_content.split()),
            "sections": self._extract_sections(response_content)
        }

    def _parse_ad_response(self, response_content: str) -> Dict[str, Any]:
        """Parse ad copy response"""
        return {
            "headline": self._extract_headline(response_content),
            "body": response_content,
            "cta": self._extract_cta(response_content)
        }

    def _extract_title(self, content: str) -> str:
        """Extract title from content"""
        lines = content.split('\n')[:5]
        for line in lines:
            if len(line.strip()) > 10 and not line.lower().startswith(('the ', 'a ', 'an ')):
                return line.strip()
        return "Generated Blog Post"

    def _extract_sections(self, content: str) -> List[str]:
        """Extract section headers from blog content"""
        lines = content.split('\n')
        sections = []
        for line in lines:
            if line.strip().startswith(('#', '##', '###')) or (
                len(line.strip()) < 100 and line.strip() and line[0].isupper()
            ):
                sections.append(line.strip())
        return sections[:5]

    def _extract_headline(self, content: str) -> str:
        """Extract headline from ad copy"""
        first_line = content.split('\n')[0].strip()
        return first_line if len(first_line) < 100 else first_line[:97] + "..."

    def _extract_cta(self, content: str) -> str:
        """Extract call-to-action from content"""
        cta_keywords = ['click here', 'sign up', 'learn more', 'get started', 'contact us', 'buy now']
        lines = content.lower().split('\n')
        for line in lines:
            if any(keyword in line for keyword in cta_keywords):
                return line.strip()
        return "Learn More"

    def _estimate_engagement_potential(self, content: str) -> str:
        """Estimate engagement potential of content"""
        score = 0
        content_lower = content.lower()

        # Engagement indicators
        if '?' in content: score += 2  # Questions drive engagement
        if any(word in content_lower for word in ['you', 'your', 'we']): score += 1
        if '!' in content: score += 1  # Exclamation shows enthusiasm
        if len(content.split()) < 50: score += 1  # Concise content performs better
        if any(emoji in content for emoji in ['💭', '👇', '🔥', '🚀']): score += 1

        if score >= 5: return "high"
        elif score >= 3: return "medium"
        else: return "low"

    def _extract_hashtags(self, content: str) -> List[str]:
        """Extract or suggest hashtags from content"""
        # Simple hashtag extraction - in production would use AI
        words = content.split()
        hashtags = [word for word in words if word.startswith('#')]
        return hashtags[:3] if hashtags else ["#Business", "#Marketing"]

    def _calculate_seo_score(self, content: str, keywords: List[str]) -> float:
        """Calculate basic SEO score"""
        if not keywords:
            return 0.5

        score = 0
        content_lower = content.lower()

        for keyword in keywords:
            if keyword.lower() in content_lower:
                score += 0.2

        # Length bonus
        if len(content.split()) > 1000:
            score += 0.2

        # Structure bonus
        if '##' in content:  # Has headers
            score += 0.1

        return min(score, 1.0)


# Convenience functions
async def generate_social_post(platform: str, topic: str, business_profile: Dict = None, **kwargs) -> Dict[str, Any]:
    """Generate social media post"""
    agent = ContentGenerationAgent()
    return await agent.execute_task({
        "content_type": "social_post",
        "platform": platform,
        "topic": topic,
        "business_profile": business_profile or {},
        **kwargs
    })


async def generate_blog_post(topic: str, business_profile: Dict = None, **kwargs) -> Dict[str, Any]:
    """Generate blog post"""
    agent = ContentGenerationAgent()
    return await agent.execute_task({
        "content_type": "blog_post",
        "topic": topic,
        "business_profile": business_profile or {},
        **kwargs
    })


def get_content_generation_agent() -> ContentGenerationAgent:
    """Get content generation agent instance"""
    return ContentGenerationAgent()
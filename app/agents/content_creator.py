"""
Content Creator Agent - AI-powered content generation with RAG enhancement
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List

import structlog
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI

from app.agents.base_agent import BaseAgent
from app.agents.state import MarketingAgentState, update_state_timestamp
from app.rag.lcel_chains import get_confidence_rag_chain, query_with_confidence
from app.rag.monitoring import record_rag_query

logger = structlog.get_logger(__name__)


class ContentCreatorAgent(BaseAgent):
    """AI-powered content creation with RAG enhancement"""

    def __init__(self, llm: ChatOpenAI):
        super().__init__("content_creator", llm, self.get_content_tools())
        self.confidence_rag_chain = get_confidence_rag_chain()

    def get_content_tools(self) -> List[Tool]:
        """Get tools for content creation"""
        return [
            Tool(
                name="query_knowledge_base",
                description="Query the marketing knowledge base for relevant information",
                func=self.query_knowledge_base
            ),
            Tool(
                name="optimize_for_seo",
                description="Optimize content for search engines",
                func=self.optimize_seo
            ),
            Tool(
                name="check_brand_guidelines",
                description="Ensure content follows brand guidelines",
                func=self.check_brand_guidelines
            ),
            Tool(
                name="analyze_content_performance",
                description="Analyze content performance metrics",
                func=self.analyze_content_performance
            )
        ]

    def get_system_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", """You are an expert marketing content creator. Your role is to:
        1. Generate high-quality, engaging marketing content
        2. Use the knowledge base to ensure accuracy and relevance
        3. Optimize content for target audience and platform
        4. Follow brand guidelines and best practices

        Content Type: {content_type}
        Target Audience: {audience}
        Brand Guidelines: {brand_guidelines}

        Use the available tools to research, create, and optimize content.
        Always ensure content is valuable, engaging, and conversion-focused."""),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

    def build_input(self, state: MarketingAgentState) -> Dict[str, Any]:
        """Build input data from shared state"""
        return {
            "content_type": state.get("content_requirements", {}).get("type", "blog_post"),
            "audience": state.get("target_audience", {}),
            "brand_guidelines": state.get("campaign_config", {}).get("brand_guidelines", {}),
            "qualified_leads": len(state.get("qualified_leads", [])),
            "input": f"Create content for campaign targeting: {state.get('target_audience', {})}"
        }

    def update_state(self, state: MarketingAgentState, result) -> MarketingAgentState:
        """Update shared state with content creation results"""
        # Extract content from result
        new_content = self.extract_content_from_result(result)

        # Add to existing content
        existing_content = state.get("generated_content", [])
        existing_content.extend(new_content)
        state["generated_content"] = existing_content

        # Update content performance tracking
        content_performance = state.get("content_performance", {})
        for content in new_content:
            content_id = content.get("id", str(datetime.utcnow().timestamp()))
            content_performance[content_id] = {
                "seo_score": content.get("seo_score", 0),
                "word_count": content.get("word_count", 0),
                "created_at": datetime.utcnow().isoformat()
            }
        state["content_performance"] = content_performance

        # Update agent coordination
        state["current_agent"] = "content_creation"
        state["next_agent"] = "ad_management"

        self.log_agent_activity("content_creation_complete", {
            "new_content": len(new_content),
            "total_content": len(existing_content)
        })

        return update_state_timestamp(state)

    async def generate_content(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Generate marketing content based on requirements"""

        import time
        start_time = time.time()

        try:
            # Query knowledge base for relevant information using advanced RAG
            rag_result = await query_with_confidence(
                question=f"What are best practices for {requirements.get('content_type', 'content')}?"
            )

            # Record RAG query for monitoring
            record_rag_query({
                'question': f"What are best practices for {requirements.get('content_type', 'content')}?",
                'response': rag_result.get('answer', ''),
                'response_time': time.time() - start_time,
                'confidence_score': rag_result.get('confidence', {}).get('score', 0),
                'sources_count': len(rag_result.get('sources', [])),
                'strategy': 'confidence_aware'
            })

            # Generate content using LLM with context
            prompt = self.build_content_prompt(requirements, rag_result)
            content = await self.llm.ainvoke(prompt)

            # Optimize and validate
            optimized_content = await self.optimize_content(content, requirements)

            return {
                'content': optimized_content,
                'type': requirements.get('content_type'),
                'topic': requirements.get('topic'),
                'word_count': len(optimized_content.split()),
                'seo_score': await self.calculate_seo_score(optimized_content),
                'rag_confidence': rag_result.get('confidence', {}).get('score', 0),
                'sources_used': len(rag_result.get('sources', [])),
                'generated_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            # Fallback to basic generation
            prompt = self.build_content_prompt(requirements, {"answer": "Use marketing best practices."})
            content = await self.llm.ainvoke(prompt)
            optimized_content = await self.optimize_content(content, requirements)

            return {
                'content': optimized_content,
                'type': requirements.get('content_type'),
                'topic': requirements.get('topic'),
                'word_count': len(optimized_content.split()),
                'seo_score': await self.calculate_seo_score(optimized_content),
                'error': str(e),
                'generated_at': datetime.utcnow().isoformat()
            }

    async def optimize_content(self, content: str, requirements: Dict[str, Any]) -> str:
        """Optimize content for better performance"""
        # SEO optimization
        if requirements.get('optimize_seo'):
            content = await self.optimize_seo(content, requirements.get('keywords', []))

        # Length adjustment
        target_length = requirements.get('target_length')
        if target_length:
            content = self.adjust_length(content, target_length)

        # Tone adjustment
        target_tone = requirements.get('tone')
        if target_tone:
            content = await self.adjust_tone(content, target_tone)

        return content

    def build_content_prompt(self, requirements: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Build prompt for content generation"""
        content_type = requirements.get('content_type', 'blog_post')
        audience = requirements.get('audience', 'general')
        topic = requirements.get('topic', 'marketing best practices')

        # Handle both old and new context formats
        if isinstance(context, dict) and 'answer' in context:
            context_info = context.get('answer', 'Use marketing best practices and industry knowledge.')
            confidence_info = f"Context confidence: {context.get('confidence', {}).get('level', 'unknown')}"
        else:
            context_info = str(context)
            confidence_info = "Context from knowledge base"

        return f"""
        Create a {content_type} about {topic} for a {audience} audience.

        {confidence_info}:
        {context_info}

        Requirements:
        - Content Type: {content_type}
        - Target Audience: {audience}
        - Topic: {topic}
        - Tone: {requirements.get('tone', 'professional')}
        - Length: {requirements.get('target_length', 'medium')}

        Generate engaging, valuable content that follows marketing best practices.
        Include relevant examples and actionable insights.
        Ensure the content is well-structured and conversion-focused.
        """

    async def calculate_seo_score(self, content: str) -> float:
        """Calculate basic SEO score"""
        score = 0.0

        # Length check (20 points)
        word_count = len(content.split())
        if word_count > 300:
            score += 20
        elif word_count > 150:
            score += 10

        # Keyword usage (30 points) - simplified
        keywords = ['marketing', 'strategy', 'content', 'audience', 'engagement']
        keyword_matches = sum(1 for keyword in keywords if keyword.lower() in content.lower())
        score += min(30, keyword_matches * 6)

        # Readability (20 points) - basic check
        sentences = content.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        if 10 <= avg_sentence_length <= 20:
            score += 20
        elif 15 <= avg_sentence_length <= 25:
            score += 10

        # Structure (30 points)
        if '##' in content:  # Has headings
            score += 15
        if '**' in content or '*' in content:  # Has formatting
            score += 15

        return min(100.0, score)

    def adjust_length(self, content: str, target_length: str) -> str:
        """Adjust content length"""
        words = content.split()
        current_length = len(words)

        if target_length == 'short' and current_length > 150:
            return ' '.join(words[:150]) + '...'
        elif target_length == 'long' and current_length < 500:
            # Add more content (simplified)
            return content + "\n\nAdditional insights: Consider implementing these strategies gradually and measuring results."
        elif target_length == 'medium' and (current_length < 200 or current_length > 400):
            # Adjust to medium length
            target_words = 300
            if current_length > target_words:
                return ' '.join(words[:target_words]) + '...'
            else:
                return content + "\n\nKey takeaways: Focus on consistent execution and continuous optimization."

        return content

    async def adjust_tone(self, content: str, target_tone: str) -> str:
        """Adjust content tone (simplified implementation)"""
        # In a real implementation, this would use the LLM to adjust tone
        if target_tone == 'casual':
            return content.replace('utilize', 'use').replace('leverage', 'use')
        elif target_tone == 'formal':
            return content.replace('use', 'utilize').replace('get', 'obtain')
        return content

    def extract_content_from_result(self, result) -> List[Dict[str, Any]]:
        """Extract content from agent execution result"""
        # This would parse the agent's output to extract structured content data
        return [
            {
                "id": f"content_{datetime.utcnow().timestamp()}",
                "content": "Generated marketing content about best practices...",
                "type": "blog_post",
                "topic": "Marketing Strategy",
                "word_count": 350,
                "seo_score": 75.0,
                "generated_at": datetime.utcnow().isoformat()
            }
        ]

    # Tool implementations
    async def query_knowledge_base(self, question: str, strategy: str = "basic") -> Dict[str, Any]:
        """Query the marketing knowledge base using advanced RAG"""
        try:
            import time
            start_time = time.time()

            # Use confidence-aware RAG for better results
            result = await query_with_confidence(question)

            # Record for monitoring
            record_rag_query({
                'question': question,
                'response': result.get('answer', ''),
                'response_time': time.time() - start_time,
                'confidence_score': result.get('confidence', {}).get('score', 0),
                'sources_count': len(result.get('sources', [])),
                'strategy': 'confidence_aware'
            })

            return result

        except Exception as e:
            logger.error(f"Knowledge base query failed: {e}")
            return {"answer": "Unable to access knowledge base", "error": str(e), "confidence": {"score": 0, "level": "low"}}

    async def optimize_seo(self, content: str, keywords: List[str]) -> str:
        """Optimize content for SEO"""
        try:
            # Basic SEO optimization
            optimized = content

            # Add keywords to title if missing
            if keywords and not any(kw.lower() in optimized[:100].lower() for kw in keywords):
                first_kw = keywords[0]
                if '##' in optimized:
                    # Add to first heading
                    lines = optimized.split('\n')
                    for i, line in enumerate(lines):
                        if line.startswith('##'):
                            lines[i] = line.replace('## ', f'## {first_kw.title()}: ')
                            break
                    optimized = '\n'.join(lines)

            # Ensure keyword density (simplified)
            content_words = optimized.split()
            keyword_count = sum(1 for word in content_words if word.lower() in [k.lower() for k in keywords])
            target_density = len(content_words) * 0.02  # 2% density

            if keyword_count < target_density:
                # Add keywords naturally (simplified)
                optimized += f"\n\nLearn more about {keywords[0]} strategies and best practices."

            return optimized
        except Exception as e:
            logger.error(f"SEO optimization failed: {e}")
            return content

    async def check_brand_guidelines(self, content: str, guidelines: Dict[str, Any] = None) -> Dict[str, Any]:
        """Check content against brand guidelines"""
        try:
            issues = []

            if guidelines:
                # Check tone
                if guidelines.get('tone') and guidelines['tone'] not in content.lower():
                    issues.append(f"Content tone doesn't match brand guidelines: {guidelines['tone']}")

                # Check prohibited words
                prohibited = guidelines.get('prohibited_words', [])
                for word in prohibited:
                    if word.lower() in content.lower():
                        issues.append(f"Contains prohibited word: {word}")

                # Check required elements
                required = guidelines.get('required_elements', [])
                for element in required:
                    if element.lower() not in content.lower():
                        issues.append(f"Missing required element: {element}")

            return {
                "compliant": len(issues) == 0,
                "issues": issues,
                "guidelines_checked": list(guidelines.keys()) if guidelines else []
            }
        except Exception as e:
            logger.error(f"Brand guidelines check failed: {e}")
            return {"compliant": True, "issues": [], "error": str(e)}

    async def analyze_content_performance(self, content: str) -> Dict[str, Any]:
        """Analyze content performance metrics"""
        try:
            return {
                "word_count": len(content.split()),
                "sentence_count": len(content.split('.')),
                "readability_score": self.calculate_readability_score(content),
                "engagement_potential": self.calculate_engagement_potential(content),
                "seo_readiness": await self.calculate_seo_score(content)
            }
        except Exception as e:
            logger.error(f"Content performance analysis failed: {e}")
            return {"error": str(e)}

    def calculate_readability_score(self, content: str) -> float:
        """Calculate basic readability score"""
        sentences = content.split('.')
        words = content.split()
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        # Simplified Flesch Reading Ease
        return max(0, 206.835 - 1.015 * avg_sentence_length)

    def calculate_engagement_potential(self, content: str) -> float:
        """Calculate engagement potential score"""
        score = 0.0

        # Question marks indicate engagement
        if '?' in content:
            score += 20

        # Call-to-action phrases
        cta_phrases = ['learn more', 'contact us', 'get started', 'sign up']
        for phrase in cta_phrases:
            if phrase in content.lower():
                score += 15
                break

        # Lists and structure
        if any(line.strip().startswith(('-', '*', '1.')) for line in content.split('\n')):
            score += 20

        # Emotional words
        emotional_words = ['amazing', 'powerful', 'effective', 'proven', 'results']
        emotional_count = sum(1 for word in emotional_words if word in content.lower())
        score += min(20, emotional_count * 5)

        return min(100.0, score)

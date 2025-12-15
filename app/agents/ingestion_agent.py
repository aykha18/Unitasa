"""
IngestionAgent - Website Crawling and Content Processing
Handles data ingestion from websites, documents, and other sources
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup

from app.agents.base import CostOptimizedAgent

logger = logging.getLogger(__name__)


class IngestionAgent(CostOptimizedAgent):
    """
    Agent responsible for ingesting and processing content from various sources
    """

    def __init__(self, name: str = "ingestion"):
        super().__init__(name)
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )

    def get_system_prompt(self) -> str:
        return """You are a content analysis expert. Your task is to analyze web content and extract structured business information.

Focus on:
1. Core business offerings and value propositions
2. Target audience and customer segments
3. Industry positioning and competitive advantages
4. Brand voice and communication style
5. Key products, services, and features

Provide concise, factual summaries that capture the essence of the business."""

    async def execute_task(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute ingestion task based on input type
        """
        task_type = task_input.get("type", "website")

        if task_type == "website":
            return await self._ingest_website(task_input)
        elif task_type == "document":
            return await self._ingest_document(task_input)
        else:
            return {
                "success": False,
                "error": f"Unsupported ingestion type: {task_type}"
            }

    async def _ingest_website(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ingest and analyze website content
        """
        url = task_input.get("url")
        if not url:
            return {"success": False, "error": "No URL provided"}

        try:
            # Crawl website
            crawl_result = await self._crawl_website(url)
            if not crawl_result["success"]:
                return crawl_result

            # Extract and clean content
            content = self._extract_content(crawl_result["html"])
            if not content:
                return {"success": False, "error": "No content extracted from website"}

            # Summarize with AI
            summary = await self._summarize_content(content, url)

            return {
                "success": True,
                "type": "website",
                "url": url,
                "content_length": len(content),
                "summary": summary,
                "raw_content": content[:5000]  # Truncate for storage
            }

        except Exception as e:
            logger.error(f"Website ingestion failed for {url}: {e}")
            return {"success": False, "error": str(e)}

    async def _crawl_website(self, url: str) -> Dict[str, Any]:
        """
        Crawl website and return HTML content
        """
        try:
            # Validate URL
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return {"success": False, "error": "Invalid URL format"}

            # Make request
            response = await self.client.get(url)
            response.raise_for_status()

            return {
                "success": True,
                "url": url,
                "html": response.text,
                "status_code": response.status_code,
                "content_type": response.headers.get("content-type", "")
            }

        except httpx.TimeoutException:
            return {"success": False, "error": "Request timeout"}
        except httpx.HTTPStatusError as e:
            return {"success": False, "error": f"HTTP {e.response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _extract_content(self, html: str) -> Optional[str]:
        """
        Extract clean text content from HTML
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Remove script and style elements
            for element in soup(["script", "style", "nav", "footer", "header"]):
                element.decompose()

            # Extract text from main content areas
            content_selectors = [
                'main', 'article', '.content', '#content',
                '.main-content', '.post-content', '.entry-content'
            ]

            content = None
            for selector in content_selectors:
                element = soup.select_one(selector)
                if element:
                    content = element.get_text(separator=' ', strip=True)
                    break

            # Fallback to body text
            if not content:
                body = soup.find('body')
                if body:
                    content = body.get_text(separator=' ', strip=True)

            # Clean up whitespace
            if content:
                content = ' '.join(content.split())
                # Limit content length
                if len(content) > 50000:
                    content = content[:50000] + "..."

            return content

        except Exception as e:
            logger.error(f"Content extraction failed: {e}")
            return None

    async def _summarize_content(self, content: str, url: str) -> Dict[str, Any]:
        """
        Use AI to summarize and analyze website content
        """
        prompt = f"""
Analyze this website content from {url} and extract key business information:

CONTENT:
{content[:10000]}  # Limit for token efficiency

Please provide a structured analysis in JSON format:
{{
    "business_offering": "main product/service",
    "target_audience": "who they serve",
    "value_proposition": "unique value",
    "industry": "industry/sector",
    "brand_tone": "communication style",
    "key_features": ["feature1", "feature2"],
    "summary": "2-3 sentence overview"
}}
"""

        try:
            response = await self.generate_response(
                user_prompt=prompt,
                task_description="website content analysis and summarization"
            )

            if response["success"]:
                # Try to parse JSON response
                import json
                try:
                    # Extract JSON from response
                    content = response["content"]
                    # Find JSON block
                    json_start = content.find('{')
                    json_end = content.rfind('}') + 1
                    if json_start >= 0 and json_end > json_start:
                        json_str = content[json_start:json_end]
                        summary_data = json.loads(json_str)
                        return summary_data
                except json.JSONDecodeError:
                    pass

                # Fallback: return structured response
                return {
                    "summary": response["content"],
                    "business_offering": "Analysis completed",
                    "confidence": "high"
                }
            else:
                return {"error": "AI summarization failed", "raw_content": content[:500]}

        except Exception as e:
            logger.error(f"Content summarization failed: {e}")
            return {"error": str(e), "raw_content": content[:500]}

    async def _ingest_document(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ingest document content (PDF, DOC, etc.)
        """
        # Placeholder for document processing
        # Would integrate with libraries like PyPDF2, python-docx
        return {
            "success": False,
            "error": "Document ingestion not yet implemented"
        }

    async def close(self):
        """Clean up resources"""
        await self.client.aclose()


# Convenience functions
async def ingest_website(url: str) -> Dict[str, Any]:
    """Convenience function for website ingestion"""
    agent = IngestionAgent()
    try:
        result = await agent.execute_task({"type": "website", "url": url})
        await agent.close()
        return result
    except Exception as e:
        await agent.close()
        raise e


def get_ingestion_agent() -> IngestionAgent:
    """Get ingestion agent instance"""
    return IngestionAgent()
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

    async def _fetch_with_jina(self, url: str) -> Optional[str]:
        """Fetch website content using Jina Reader (for SPAs)"""
        try:
            jina_url = f"https://r.jina.ai/{url}"
            response = await self.client.get(jina_url)
            if response.status_code == 200:
                return response.text
            return None
        except Exception as e:
            logger.warning(f"Jina Reader fetch failed: {e}")
            return None

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
            
            # Check if content is insufficient (SPA shell)
            is_spa_shell = False
            if content:
                lower_content = content.lower()
                # Heuristic for SPA shells or empty pages
                if len(content) < 1000 or "enable javascript" in lower_content or "you need to enable javascript" in lower_content:
                    is_spa_shell = True
            
            if not content or is_spa_shell:
                headless_content = await self._render_with_headless(url)
                if headless_content:
                    content = self._extract_content(headless_content) or headless_content
            
            if not content or (is_spa_shell and len(content) < 1000):
                logger.info(f"Content seems to be SPA shell or sparse, trying Jina Reader for {url}")
                jina_content = await self._fetch_with_jina(url)
                if jina_content:
                    content = jina_content
                    logger.info("Successfully retrieved content via Jina Reader")

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

            response = await self.client.get(url)
            response.raise_for_status()
            base_html = response.text

            extra_paths = ["/about", "/pricing", "/product", "/services", "/features", "/solutions"]
            base = f"{parsed.scheme}://{parsed.netloc}"
            extra_htmls: List[str] = []
            for path in extra_paths:
                extra_url = base + path
                try:
                    r = await self.client.get(extra_url)
                    if r.status_code == 200 and len(r.text) > 2000:
                        extra_htmls.append(r.text)
                except Exception:
                    pass

            combined_html = base_html + ("\n".join(extra_htmls) if extra_htmls else "")

            return {
                "success": True,
                "url": url,
                "html": combined_html,
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
        Extract clean text content from HTML, including meta tags and JSON-LD
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            extracted_parts = []

            # 1. Extract Meta Tags (critical for SPAs)
            meta_desc = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
            if meta_desc and meta_desc.get('content'):
                extracted_parts.append(f"META DESCRIPTION: {meta_desc['content']}")
                
            title = soup.title.string if soup.title else ""
            if title:
                extracted_parts.append(f"PAGE TITLE: {title}")

            # 2. Extract JSON-LD and other Data Scripts
            json_ld = soup.find_all('script', type='application/ld+json')
            for script in json_ld:
                if script.string:
                    extracted_parts.append(f"STRUCTURED DATA: {script.string}")
            
            # Extract Next.js or other hydration data
            next_data = soup.find('script', id='__NEXT_DATA__')
            if next_data and next_data.string:
                extracted_parts.append(f"APP DATA: {next_data.string[:5000]}") # Truncate to avoid massive payloads

            # 3. Extract Main Content
            # Remove script and style elements (but keep JSON-LD which we already handled)
            for element in soup(["style", "nav", "footer", "header"]):
                element.decompose()
            
            # Don't decompose script tags yet as they might contain config data, 
            # but for text extraction we usually skip them. 
            # We already extracted LD-JSON.
            for element in soup("script"):
                element.decompose()

            # Extract text from main content areas
            content_selectors = [
                'main', 'article', '.content', '#content',
                '.main-content', '.post-content', '.entry-content'
            ]

            body_content = None
            for selector in content_selectors:
                element = soup.select_one(selector)
                if element:
                    body_content = element.get_text(separator=' ', strip=True)
                    break

            # Fallback to body text
            if not body_content:
                body = soup.find('body')
                if body:
                    body_content = body.get_text(separator=' ', strip=True)
            
            if body_content:
                extracted_parts.append(f"BODY CONTENT: {body_content}")

            # Combine all parts
            full_content = "\n\n".join(extracted_parts)

            # Clean up whitespace
            if full_content:
                full_content = ' '.join(full_content.split())
                # Limit content length
                if len(full_content) > 50000:
                    full_content = full_content[:50000] + "..."

            return full_content

        except Exception as e:
            logger.error(f"Content extraction failed: {e}")
            return None

    async def _render_with_headless(self, url: str) -> Optional[str]:
        try:
            try:
                from playwright.async_api import async_playwright
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    context = await browser.new_context()
                    page = await context.new_page()
                    await page.goto(url, wait_until="networkidle")
                    content = await page.content()
                    await context.close()
                    await browser.close()
                    return content
            except Exception:
                try:
                    import pyppeteer
                    from pyppeteer import launch
                    browser = await launch(headless=True, args=["--no-sandbox"])
                    page = await browser.newPage()
                    await page.goto(url, {"waitUntil": "networkidle2"})
                    content = await page.content()
                    await browser.close()
                    return content
                except Exception:
                    return None
        except Exception:
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
    "how_it_works": ["step 1", "step 2", "step 3"],
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

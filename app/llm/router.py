"""
Cost-Optimized LLM Router for OpenRouter + Groq + OpenAI Fallback
Implements intelligent routing with automatic fallback for cost optimization
"""

import asyncio
import time
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

import httpx
from openai import OpenAI
from groq import Groq

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Available LLM providers in order of preference"""
    OPENROUTER = "openrouter"
    GROQ = "groq"
    OPENAI = "openai"  # Fallback only


@dataclass
class LLMConfig:
    """Configuration for an LLM provider"""
    provider: LLMProvider
    api_key: Optional[str]
    base_url: Optional[str] = None
    model: str = ""
    temperature: float = 0.7
    max_tokens: int = 4096
    cost_per_1k_tokens: float = 0.0
    timeout: int = 30


@dataclass
class RoutingDecision:
    """Decision made by the router"""
    provider: LLMProvider
    reason: str
    estimated_cost: float
    confidence: float


class CostOptimizedLLMRouter:
    """Intelligent LLM router with cost optimization and fallback"""

    def __init__(self):
        self.providers = self._initialize_providers()
        self.usage_stats = {}
        self._initialize_usage_tracking()

    def _initialize_providers(self) -> Dict[LLMProvider, LLMConfig]:
        """Initialize LLM provider configurations"""
        return {
            LLMProvider.OPENROUTER: LLMConfig(
                provider=LLMProvider.OPENROUTER,
                api_key=settings.openrouter.api_key,
                base_url="https://openrouter.ai/api/v1",
                model=settings.openrouter.model,
                temperature=settings.openrouter.temperature,
                max_tokens=settings.openrouter.max_tokens,
                cost_per_1k_tokens=settings.openrouter.cost_per_1k_tokens,
                timeout=30
            ),
            LLMProvider.GROQ: LLMConfig(
                provider=LLMProvider.GROQ,
                api_key=settings.groq.api_key,
                model=settings.groq.model,
                temperature=settings.groq.temperature,
                max_tokens=settings.groq.max_tokens,
                cost_per_1k_tokens=settings.groq.cost_per_1k_tokens,
                timeout=30
            ),
            LLMProvider.OPENAI: LLMConfig(
                provider=LLMProvider.OPENAI,
                api_key=settings.openai.api_key,
                model=settings.openai.model,
                temperature=settings.openai.temperature,
                max_tokens=settings.openai.max_tokens,
                cost_per_1k_tokens=0.01,  # GPT-4 cost
                timeout=30
            )
        }

    def _initialize_usage_tracking(self):
        """Initialize usage tracking for cost monitoring"""
        for provider in LLMProvider:
            self.usage_stats[provider.value] = {
                'total_tokens': 0,
                'total_cost': 0.0,
                'requests_count': 0,
                'errors_count': 0
            }

    def _analyze_task_complexity(self, task_description: str) -> Dict[str, Any]:
        """Analyze task to determine optimal provider selection"""
        task_lower = task_description.lower()

        # Complexity indicators
        complexity_score = 0
        if len(task_description.split()) > 200:
            complexity_score += 2
        if any(keyword in task_lower for keyword in ['analyze', 'compare', 'evaluate', 'strategic']):
            complexity_score += 1
        if any(keyword in task_lower for keyword in ['creative', 'generate', 'design']):
            complexity_score += 1

        # Task type classification
        is_creative = any(keyword in task_lower for keyword in ['write', 'create', 'generate', 'design'])
        is_analytical = any(keyword in task_lower for keyword in ['analyze', 'compare', 'evaluate'])
        is_simple = len(task_description.split()) < 50

        return {
            'complexity': complexity_score,
            'is_creative': is_creative,
            'is_analytical': is_analytical,
            'is_simple': is_simple
        }

    def _make_routing_decision(self, task_analysis: Dict[str, Any]) -> RoutingDecision:
        """Make intelligent routing decision based on task analysis and availability"""

        # Priority order: OpenRouter → Groq → OpenAI (fallback)
        provider_priority = [
            LLMProvider.OPENROUTER,
            LLMProvider.GROQ,
            LLMProvider.OPENAI
        ]

        for provider in provider_priority:
            config = self.providers[provider]

            # Check if provider is available
            if not config.api_key:
                continue

            # Calculate estimated cost for this task
            estimated_tokens = 1000 if task_analysis['complexity'] > 2 else 500
            estimated_cost = (estimated_tokens / 1000) * config.cost_per_1k_tokens

            # Determine selection reason
            reason = self._get_selection_reason(provider, task_analysis)

            return RoutingDecision(
                provider=provider,
                reason=reason,
                estimated_cost=estimated_cost,
                confidence=0.9
            )

        # Ultimate fallback
        return RoutingDecision(
            provider=LLMProvider.OPENAI,
            reason="All preferred providers unavailable - using OpenAI fallback",
            estimated_cost=0.01,
            confidence=0.5
        )

    def _get_selection_reason(self, provider: LLMProvider, task_analysis: Dict[str, Any]) -> str:
        """Get reason for selecting this provider"""
        reasons = {
            LLMProvider.OPENROUTER: "OpenRouter selected for balanced performance and cost",
            LLMProvider.GROQ: "Groq selected for fast, cost-effective processing",
            LLMProvider.OPENAI: "OpenAI selected as reliable fallback"
        }
        return reasons.get(provider, "Default selection")

    async def generate(self, prompt: str, task_description: str = "", **kwargs) -> Dict[str, Any]:
        """Generate response using optimal provider with fallback"""
        start_time = time.time()

        # Analyze task for routing
        task_analysis = self._analyze_task_complexity(task_description or prompt)
        decision = self._make_routing_decision(task_analysis)

        # Try providers in order until success
        last_error = None
        providers_tried = []

        for provider in [decision.provider, LLMProvider.GROQ, LLMProvider.OPENROUTER, LLMProvider.OPENAI]:
            if provider in providers_tried:
                continue

            providers_tried.append(provider)
            config = self.providers[provider]

            if not config.api_key:
                continue

            try:
                logger.info(f"Trying provider: {provider.value}")
                response = await self._call_provider(provider, prompt, **kwargs)

                # Record successful usage
                tokens_used = response.get('tokens_used', 500)  # Estimate if not provided
                cost = (tokens_used / 1000) * config.cost_per_1k_tokens

                self.usage_stats[provider.value]['total_tokens'] += tokens_used
                self.usage_stats[provider.value]['total_cost'] += cost
                self.usage_stats[provider.value]['requests_count'] += 1

                response['provider'] = provider.value
                response['cost'] = cost
                response['processing_time'] = time.time() - start_time

                logger.info(f"Success with {provider.value}: ${cost:.4f}")
                return response

            except Exception as e:
                logger.warning(f"Provider {provider.value} failed: {e}")
                last_error = e
                self.usage_stats[provider.value]['errors_count'] += 1
                continue

        # All providers failed
        raise Exception(f"All LLM providers failed. Last error: {last_error}")

    async def _call_provider(self, provider: LLMProvider, prompt: str, **kwargs) -> Dict[str, Any]:
        """Call specific LLM provider"""
        config = self.providers[provider]

        if provider == LLMProvider.OPENROUTER:
            return await self._call_openrouter(prompt, config, **kwargs)
        elif provider == LLMProvider.GROQ:
            return await self._call_groq(prompt, config, **kwargs)
        elif provider == LLMProvider.OPENAI:
            return await self._call_openai(prompt, config, **kwargs)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    async def _call_openrouter(self, prompt: str, config: LLMConfig, **kwargs) -> Dict[str, Any]:
        """Call OpenRouter API"""
        async with httpx.AsyncClient(timeout=config.timeout) as client:
            response = await client.post(
                f"{config.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {config.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": config.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": config.temperature,
                    "max_tokens": config.max_tokens,
                    **kwargs
                }
            )
            response.raise_for_status()
            data = response.json()

            return {
                "content": data["choices"][0]["message"]["content"],
                "tokens_used": data["usage"]["total_tokens"],
                "finish_reason": data["choices"][0]["finish_reason"]
            }

    async def _call_groq(self, prompt: str, config: LLMConfig, **kwargs) -> Dict[str, Any]:
        """Call Groq API"""
        client = Groq(api_key=config.api_key)

        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: client.chat.completions.create(
                model=config.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                **kwargs
            )
        )

        return {
            "content": response.choices[0].message.content,
            "tokens_used": response.usage.total_tokens,
            "finish_reason": response.choices[0].finish_reason
        }

    async def _call_openai(self, prompt: str, config: LLMConfig, **kwargs) -> Dict[str, Any]:
        """Call OpenAI API (fallback)"""
        client = OpenAI(api_key=config.api_key)

        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: client.chat.completions.create(
                model=config.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                **kwargs
            )
        )

        return {
            "content": response.choices[0].message.content,
            "tokens_used": response.usage.total_tokens,
            "finish_reason": response.choices[0].finish_reason
        }

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics for all providers"""
        return self.usage_stats.copy()

    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        available = []
        for provider, config in self.providers.items():
            if config.api_key:
                available.append(provider.value)
        return available


# Global router instance
_router = None


def get_llm_router() -> CostOptimizedLLMRouter:
    """Get global LLM router instance"""
    global _router
    if _router is None:
        _router = CostOptimizedLLMRouter()
    return _router


async def generate_with_fallback(prompt: str, task_description: str = "", **kwargs) -> Dict[str, Any]:
    """Convenience function for generating with automatic fallback"""
    router = get_llm_router()
    return await router.generate(prompt, task_description, **kwargs)
"""
Cost-Optimized Base Agent Class
Simplified agent architecture using OpenRouter + Groq with OpenAI fallback
"""

import time
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime

from app.core.config import get_settings
from app.llm.router import get_llm_router

settings = get_settings()
logger = logging.getLogger(__name__)


class CostOptimizedAgent(ABC):
    """
    Base class for cost-optimized AI agents using OpenRouter + Groq + OpenAI fallback
    """

    def __init__(self, name: str):
        self.name = name
        self.llm_router = get_llm_router()
        self.logger = logging.getLogger(f"{__name__}.{name}")

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get agent-specific system prompt"""
        pass

    @abstractmethod
    async def execute_task(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent task with given input"""
        pass

    async def generate_response(self, user_prompt: str, task_description: str = "", **kwargs) -> Dict[str, Any]:
        """
        Generate AI response using cost-optimized routing

        Args:
            user_prompt: The user prompt to send to the LLM
            task_description: Description of the task for routing optimization
            **kwargs: Additional parameters for the LLM

        Returns:
            Dict containing response content, metadata, and cost information
        """
        try:
            # Build full prompt with system context
            system_prompt = self.get_system_prompt()
            full_prompt = f"{system_prompt}\n\n{user_prompt}"

            # Generate response with automatic fallback
            response = await self.llm_router.generate(
                prompt=full_prompt,
                task_description=task_description or f"{self.name} agent task",
                **kwargs
            )

            # Add agent metadata
            response.update({
                "agent": self.name,
                "timestamp": datetime.utcnow().isoformat(),
                "success": True
            })

            self.logger.info(f"Agent {self.name} completed task successfully")
            return response

        except Exception as e:
            self.logger.error(f"Agent {self.name} failed: {e}")
            return {
                "agent": self.name,
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "content": "I apologize, but I encountered an error processing your request. Please try again."
            }

    def validate_input(self, task_input: Dict[str, Any]) -> bool:
        """Validate task input before processing"""
        if not isinstance(task_input, dict):
            return False
        return True

    def log_task_execution(self, task_input: Dict[str, Any], response: Dict[str, Any]):
        """Log task execution for monitoring"""
        self.logger.info(
            f"Agent {self.name} task execution",
            extra={
                "input_keys": list(task_input.keys()),
                "success": response.get("success", False),
                "provider": response.get("provider"),
                "cost": response.get("cost", 0),
                "processing_time": response.get("processing_time", 0)
            }
        )

# Alias for backward compatibility
BaseAgent = CostOptimizedAgent

# Agent Registry
_agent_registry = {}

def get_agent_registry():
    """Get the global agent registry"""
    return _agent_registry

def register_agent(name: str, agent_instance: Any):
    """Register an agent instance"""
    _agent_registry[name] = agent_instance

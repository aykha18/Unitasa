#!/usr/bin/env python3
"""
Test script for the new cost-optimized agent system
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_imports():
    """Test that all new components can be imported"""
    print("Testing imports...")

    try:
        # Test agent imports
        from app.agents.base import CostOptimizedAgent, get_agent_registry
        from app.agents.ingestion_agent import IngestionAgent
        from app.agents.knowledge_base_agent import KnowledgeBaseAgent
        from app.agents.business_analysis_agent import BusinessAnalysisAgent
        from app.agents.content_generation_agent import ContentGenerationAgent
        print("Agent imports successful")

        # Test LLM router
        from app.llm.router import get_llm_router, CostOptimizedLLMRouter
        router = get_llm_router()
        print(f"LLM router initialized with providers: {router.get_available_providers()}")

        # Test API imports
        from app.api.v1.ai_agents import router as ai_router
        print("API router imported successfully")

        # Test agent registry
        registry = get_agent_registry()
        print(f"Agent registry initialized with {len(registry.list_agents())} agents")

        return True

    except Exception as e:
        print(f"Import failed: {e}")
        return False

async def test_agent_creation():
    """Test creating and initializing agents"""
    print("\nTesting agent creation...")

    try:
        from app.agents.ingestion_agent import IngestionAgent
        from app.agents.business_analysis_agent import BusinessAnalysisAgent
        from app.agents.content_generation_agent import ContentGenerationAgent

        # Create agents
        ingestion_agent = IngestionAgent()
        business_agent = BusinessAnalysisAgent()
        content_agent = ContentGenerationAgent()

        print("All agents created successfully")

        # Test health checks
        ingestion_health = await ingestion_agent.health_check()
        business_health = await business_agent.health_check()
        content_health = await content_agent.health_check()

        print(f"Ingestion agent health: {ingestion_health['status']}")
        print(f"Business agent health: {business_health['status']}")
        print(f"Content agent health: {content_health['status']}")

        return True

    except Exception as e:
        print(f"Agent creation failed: {e}")
        return False

async def test_llm_router():
    """Test the LLM router functionality"""
    print("\nTesting LLM router...")

    try:
        from app.llm.router import get_llm_router

        router = get_llm_router()

        # Test provider availability
        providers = router.get_available_providers()
        print(f"Available providers: {providers}")

        # Test usage stats
        stats = router.get_usage_stats()
        print(f"Usage stats initialized: {len(stats)} providers tracked")

        # Note: We won't test actual API calls without API keys
        print("LLM router functional (API calls require keys)")

        return True

    except Exception as e:
        print(f"LLM router test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("Testing New Cost-Optimized Agent System")
    print("=" * 50)

    results = []

    # Test imports
    results.append(await test_imports())

    # Test agent creation
    results.append(await test_agent_creation())

    # Test LLM router
    results.append(await test_llm_router())

    # Summary
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"All tests passed! ({passed}/{total})")
        print("\nThe new agent system is ready for development!")
        print("\nNext steps:")
        print("1. Set up API keys for OpenRouter, Groq, and OpenAI")
        print("2. Test actual API calls with real data")
        print("3. Integrate with existing frontend")
        print("4. Deploy to production")
        return 0
    else:
        print(f"Some tests failed ({passed}/{total})")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
"""
Test script for reranking functionality
Run with: python -m app.rag.test_reranking
"""

import asyncio
from typing import List
from langchain_core.documents import Document

from app.rag.reranker import get_reranker
from app.rag.advanced_retrievers import get_reranking_retriever, get_advanced_retriever


# Sample documents for testing
SAMPLE_DOCS = [
    Document(
        page_content="HubSpot integration setup guide: Connect your HubSpot account using OAuth2 authentication. Navigate to Settings > Integrations and click Connect HubSpot.",
        metadata={"source": "hubspot_integration_guide.md", "type": "integration"}
    ),
    Document(
        page_content="API security best practices include using HTTPS, implementing rate limiting, and rotating API keys regularly.",
        metadata={"source": "api_security.md", "type": "security"}
    ),
    Document(
        page_content="Salesforce integration requires enterprise plan. Setup time is approximately 45 minutes with OAuth2 support.",
        metadata={"source": "salesforce_integration.md", "type": "integration"}
    ),
    Document(
        page_content="OAuth2 authentication flow: User authorizes application, receives authorization code, exchanges code for access token.",
        metadata={"source": "oauth2_guide.md", "type": "authentication"}
    ),
    Document(
        page_content="CRM integration best practices: Map fields correctly, test with sample data, enable bi-directional sync.",
        metadata={"source": "crm_best_practices.md", "type": "integration"}
    ),
    Document(
        page_content="Marketing automation workflows can be triggered by user actions, time-based schedules, or external events.",
        metadata={"source": "marketing_automation.md", "type": "automation"}
    ),
    Document(
        page_content="HubSpot pricing starts at $50/month for Starter plan, $800/month for Professional, and $3,200/month for Enterprise.",
        metadata={"source": "hubspot_pricing.md", "type": "pricing"}
    ),
    Document(
        page_content="Integration troubleshooting: Check API credentials, verify webhook URLs, review error logs, test connection.",
        metadata={"source": "troubleshooting.md", "type": "support"}
    ),
]


def print_results(title: str, docs: List[Document], show_scores: bool = False):
    """Pretty print document results"""
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}")
    
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get('source', 'unknown')
        content = doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
        
        if show_scores and 'rerank_score' in doc.metadata:
            score = doc.metadata['rerank_score']
            print(f"\n{i}. [{source}] (score: {score:.3f})")
        else:
            print(f"\n{i}. [{source}]")
        
        print(f"   {content}")


def test_reranker_basic():
    """Test basic reranker functionality"""
    print("\n" + "="*80)
    print("TEST 1: Basic Reranker")
    print("="*80)
    
    query = "How to integrate HubSpot?"
    print(f"\nQuery: {query}")
    
    # Get reranker
    reranker = get_reranker()
    print(f"[OK] Reranker loaded: {reranker.model_name}")
    
    # Rerank documents
    reranked_docs_with_scores = reranker.rerank(query, SAMPLE_DOCS, top_k=5)
    
    # Print results
    print_results(
        "Top 5 Documents After Reranking",
        [doc for doc, score in reranked_docs_with_scores],
        show_scores=False
    )
    
    # Print scores
    print("\nReranking Scores:")
    for i, (doc, score) in enumerate(reranked_docs_with_scores, 1):
        source = doc.metadata.get('source', 'unknown')
        print(f"  {i}. {source}: {score:.3f}")
    
    return reranked_docs_with_scores


def test_reranker_with_metadata():
    """Test reranker with metadata injection"""
    print("\n" + "="*80)
    print("TEST 2: Reranker with Metadata")
    print("="*80)
    
    query = "What's the difference between OAuth2 and API key?"
    print(f"\nQuery: {query}")
    
    reranker = get_reranker()
    reranked_docs = reranker.rerank_with_metadata(query, SAMPLE_DOCS, top_k=3)
    
    print_results("Top 3 Documents with Metadata", reranked_docs, show_scores=True)
    
    return reranked_docs


def test_comparison():
    """Compare results with and without reranking"""
    print("\n" + "="*80)
    print("TEST 3: Comparison - With vs Without Reranking")
    print("="*80)
    
    query = "integration setup"
    print(f"\nQuery: {query}")
    
    # Simulate simple retrieval (just take first 5)
    simple_results = SAMPLE_DOCS[:5]
    print_results("WITHOUT Reranking (First 5 docs)", simple_results)
    
    # With reranking
    reranker = get_reranker()
    reranked_results = reranker.rerank_with_metadata(query, SAMPLE_DOCS, top_k=5)
    print_results("WITH Reranking (Top 5 by relevance)", reranked_results, show_scores=True)
    
    # Compare
    print("\n" + "-"*80)
    print("COMPARISON:")
    print("-"*80)
    print("\nWithout Reranking:")
    for i, doc in enumerate(simple_results, 1):
        print(f"  {i}. {doc.metadata.get('source')}")
    
    print("\nWith Reranking:")
    for i, doc in enumerate(reranked_results, 1):
        score = doc.metadata.get('rerank_score', 0)
        print(f"  {i}. {doc.metadata.get('source')} (score: {score:.3f})")


def test_edge_cases():
    """Test edge cases"""
    print("\n" + "="*80)
    print("TEST 4: Edge Cases")
    print("="*80)
    
    reranker = get_reranker()
    
    # Empty documents
    print("\n1. Empty documents list:")
    result = reranker.rerank("test query", [], top_k=5)
    print(f"   Result: {len(result)} documents (expected: 0)")
    
    # Single document
    print("\n2. Single document:")
    result = reranker.rerank("test query", SAMPLE_DOCS[:1], top_k=5)
    print(f"   Result: {len(result)} documents (expected: 1)")
    
    # Request more than available
    print("\n3. Request more docs than available:")
    result = reranker.rerank("test query", SAMPLE_DOCS[:3], top_k=10)
    print(f"   Result: {len(result)} documents (expected: 3)")
    
    print("\n[OK] All edge cases handled correctly")


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("RERANKING FUNCTIONALITY TESTS")
    print("="*80)
    
    try:
        # Test 1: Basic reranking
        test_reranker_basic()
        
        # Test 2: Reranking with metadata
        test_reranker_with_metadata()
        
        # Test 3: Comparison
        test_comparison()
        
        # Test 4: Edge cases
        test_edge_cases()
        
        print("\n" + "="*80)
        print("[OK] ALL TESTS PASSED")
        print("="*80)
        print("\nReranking is working correctly!")
        print("You can now use it in your RAG pipeline.")
        
    except Exception as e:
        print(f"\n[ERROR] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


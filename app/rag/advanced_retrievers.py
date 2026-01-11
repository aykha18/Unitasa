"""
Advanced RAG Retrievers - MultiQuery, Ensemble, Contextual Compression, and ReRanking
"""

import logging
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_community.retrievers import BM25Retriever
from langchain_core.vectorstores import VectorStore

from app.rag.vectorstore_manager import get_vector_store, get_vector_store_sync
from app.rag.reranker import get_reranker, CrossEncoderReranker
from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class MultiQueryRetriever(BaseRetriever):
    """Retriever that generates multiple queries and combines results"""

    def __init__(self, vectorstore: VectorStore, llm=None):
        super().__init__()
        self.vectorstore = vectorstore
        self.llm = llm

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        """Get relevant documents using multi-query approach"""

        # Generate multiple query variations
        query_variations = self._generate_query_variations(query)

        all_docs = []
        seen_content = set()

        # Retrieve documents for each query variation
        for q in query_variations:
            docs = self.vectorstore.similarity_search(q, k=3)
            for doc in docs:
                # Deduplicate based on content
                content_hash = hash(doc.page_content[:200])
                if content_hash not in seen_content:
                    seen_content.add(content_hash)
                    all_docs.append(doc)

        # Return top results
        return all_docs[:5]

    def _generate_query_variations(self, query: str) -> List[str]:
        """Generate multiple variations of the query"""
        # Simple query expansion for now
        variations = [query]

        # Add some basic variations
        if "how" in query.lower():
            variations.append(query.replace("how", "what is the process"))
        if "what" in query.lower():
            variations.append(query.replace("what", "explain"))

        # Add keyword-focused variations
        words = query.split()
        if len(words) > 3:
            variations.append(" ".join(words[:3]))  # First 3 words
            variations.append(" ".join(words[-3:]))  # Last 3 words

        return list(set(variations))  # Remove duplicates


class EnsembleRetriever(BaseRetriever):
    """Combines semantic search with BM25 keyword search"""

    def __init__(self, vectorstore: VectorStore):
        super().__init__()
        self.vectorstore = vectorstore
        self.bm25_retriever = None
        self.documents = []

    def add_documents(self, documents: List[Document]):
        """Add documents for BM25 indexing"""
        self.documents = documents
        self.bm25_retriever = BM25Retriever.from_documents(documents)

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        """Get relevant documents using ensemble approach"""

        # Semantic search results
        semantic_docs = self.vectorstore.similarity_search(query, k=5)

        # BM25 keyword search results
        bm25_docs = []
        if self.bm25_retriever:
            bm25_docs = self.bm25_retriever.get_relevant_documents(query)

        # Combine and deduplicate
        all_docs = semantic_docs + bm25_docs
        seen_content = set()
        unique_docs = []

        for doc in all_docs:
            content_hash = hash(doc.page_content[:200])
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_docs.append(doc)

        # Re-rank by relevance score (simple approach)
        return unique_docs[:5]


class ContextualCompressionRetriever(BaseRetriever):
    """Compresses retrieved documents to keep only relevant context"""

    def __init__(self, vectorstore: VectorStore, llm=None):
        super().__init__()
        self.vectorstore = vectorstore
        self.llm = llm

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        """Get and compress relevant documents"""

        # First, get more documents than needed
        raw_docs = self.vectorstore.similarity_search(query, k=10)

        # Compress each document
        compressed_docs = []
        for doc in raw_docs:
            compressed_content = self._compress_document(doc, query)
            if compressed_content and len(compressed_content) > 50:  # Minimum length
                compressed_doc = Document(
                    page_content=compressed_content,
                    metadata={**doc.metadata, "original_length": len(doc.page_content)}
                )
                compressed_docs.append(compressed_doc)

        return compressed_docs[:5]

    def _compress_document(self, document: Document, query: str) -> str:
        """Compress document to keep only relevant parts"""
        content = document.page_content

        # Simple compression: keep sentences containing query terms
        query_terms = set(query.lower().split())
        sentences = content.split('.')

        relevant_sentences = []
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(term in sentence_lower for term in query_terms):
                relevant_sentences.append(sentence.strip())

        # If no relevant sentences found, return original content
        if not relevant_sentences:
            return content

        return '. '.join(relevant_sentences)


class ReRankingRetriever(BaseRetriever):
    """
    Retriever with two-stage ranking: fast retrieval + precise reranking
    
    Stage 1: Retrieve more candidates using fast bi-encoder (recall-focused)
    Stage 2: Rerank with cross-encoder for precision
    """
    vectorstore: VectorStore
    reranker: Any = None
    initial_k: int = 20
    final_k: int = 5

    class Config:
        arbitrary_types_allowed = True
    
    def __init__(
        self, 
        vectorstore: VectorStore, 
        reranker: Optional[CrossEncoderReranker] = None,
        initial_k: int = 20,
        final_k: int = 5,
        **kwargs
    ):
        """
        Initialize reranking retriever
        """
        # Initialize Pydantic model with fields
        super().__init__(
            vectorstore=vectorstore,
            reranker=reranker or get_reranker(),
            initial_k=initial_k,
            final_k=final_k,
            **kwargs
        )
    
    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        """Retrieve and rerank documents"""
        
        try:
            # Stage 1: Fast retrieval (recall-focused)
            logger.info(f"Stage 1: Retrieving {self.initial_k} candidates")
            candidate_docs = self.vectorstore.similarity_search(query, k=self.initial_k)
            
            if not candidate_docs:
                logger.warning("No candidates retrieved")
                return []
            
            # Stage 2: Precise reranking (precision-focused)
            logger.info(f"Stage 2: Reranking to top {self.final_k}")
            reranked_docs = self.reranker.rerank_with_metadata(
                query, 
                candidate_docs, 
                top_k=self.final_k
            )
            
            logger.info(
                f"✅ Retrieved {len(candidate_docs)} → Reranked to {len(reranked_docs)}"
            )
            
            return reranked_docs
            
        except Exception as e:
            logger.error(f"❌ ReRankingRetriever failed: {e}")
            # Fallback to simple retrieval
            return self.vectorstore.similarity_search(query, k=self.final_k)


class HybridReRankingRetriever(BaseRetriever):
    """
    Combines ensemble retrieval (semantic + BM25) with reranking
    Best of all worlds: keyword matching + semantic search + precision reranking
    """
    vectorstore: VectorStore
    reranker: Any = None
    bm25_retriever: Any = None
    initial_k: int = 20
    final_k: int = 5

    class Config:
        arbitrary_types_allowed = True
    
    def __init__(
        self,
        vectorstore: VectorStore,
        reranker: Optional[CrossEncoderReranker] = None,
        initial_k: int = 20,
        final_k: int = 5,
        **kwargs
    ):
        super().__init__(
            vectorstore=vectorstore,
            reranker=reranker or get_reranker(),
            initial_k=initial_k,
            final_k=final_k,
            **kwargs
        )
        self.bm25_retriever = None
    
    def add_documents(self, documents: List[Document]):
        """Add documents for BM25 indexing"""
        self.bm25_retriever = BM25Retriever.from_documents(documents)
    
    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        """Retrieve using ensemble, then rerank"""
        
        try:
            # Stage 1: Ensemble retrieval (semantic + keyword)
            semantic_docs = self.vectorstore.similarity_search(query, k=self.initial_k // 2)
            
            bm25_docs = []
            if self.bm25_retriever:
                bm25_docs = self.bm25_retriever.get_relevant_documents(query)[:self.initial_k // 2]
            
            # Combine and deduplicate
            all_docs = semantic_docs + bm25_docs
            seen_content = set()
            unique_docs = []
            
            for doc in all_docs:
                content_hash = hash(doc.page_content[:200])
                if content_hash not in seen_content:
                    seen_content.add(content_hash)
                    unique_docs.append(doc)
            
            # Stage 2: Rerank combined results
            reranked_docs = self.reranker.rerank_with_metadata(
                query,
                unique_docs,
                top_k=self.final_k
            )
            
            logger.info(
                f"✅ Hybrid: {len(semantic_docs)} semantic + {len(bm25_docs)} BM25 "
                f"→ {len(unique_docs)} unique → {len(reranked_docs)} reranked"
            )
            
            return reranked_docs
            
        except Exception as e:
            logger.error(f"❌ HybridReRankingRetriever failed: {e}")
            return self.vectorstore.similarity_search(query, k=self.final_k)


# Global retriever instances
_multi_query_retriever = None
_ensemble_retriever = None
_contextual_retriever = None
_reranking_retriever = None
_hybrid_reranking_retriever = None


def get_multi_query_retriever() -> MultiQueryRetriever:
    """Get multi-query retriever instance"""
    global _multi_query_retriever
    if _multi_query_retriever is None:
        vectorstore = get_vector_store_sync()
        _multi_query_retriever = MultiQueryRetriever(vectorstore)
    return _multi_query_retriever


def get_ensemble_retriever() -> EnsembleRetriever:
    """Get ensemble retriever instance"""
    global _ensemble_retriever
    if _ensemble_retriever is None:
        vectorstore = get_vector_store_sync()
        _ensemble_retriever = EnsembleRetriever(vectorstore)
    return _ensemble_retriever


def get_contextual_compression_retriever() -> ContextualCompressionRetriever:
    """Get contextual compression retriever instance"""
    global _contextual_retriever
    if _contextual_retriever is None:
        vectorstore = get_vector_store_sync()
        _contextual_retriever = ContextualCompressionRetriever(vectorstore)
    return _contextual_retriever


def get_reranking_retriever(
    initial_k: int = 20,
    final_k: int = 5
) -> ReRankingRetriever:
    """Get reranking retriever instance"""
    global _reranking_retriever
    if _reranking_retriever is None:
        vectorstore = get_vector_store_sync()
        _reranking_retriever = ReRankingRetriever(
            vectorstore=vectorstore,
            initial_k=initial_k,
            final_k=final_k
        )
    return _reranking_retriever


def get_hybrid_reranking_retriever(
    initial_k: int = 20,
    final_k: int = 5
) -> HybridReRankingRetriever:
    """Get hybrid reranking retriever instance"""
    global _hybrid_reranking_retriever
    if _hybrid_reranking_retriever is None:
        vectorstore = get_vector_store_sync()
        _hybrid_reranking_retriever = HybridReRankingRetriever(
            vectorstore=vectorstore,
            initial_k=initial_k,
            final_k=final_k
        )
    return _hybrid_reranking_retriever


def get_advanced_retriever(strategy: str = "reranking") -> BaseRetriever:
    """
    Get advanced retriever based on strategy
    
    Args:
        strategy: Retrieval strategy
            - "reranking" (NEW DEFAULT): Semantic search + reranking
            - "hybrid_reranking": Ensemble + reranking (best quality)
            - "ensemble": Semantic + BM25 (no reranking)
            - "multi_query": Query expansion
            - "contextual": Contextual compression
    
    Returns:
        BaseRetriever instance
    """
    if strategy == "reranking":
        return get_reranking_retriever()
    elif strategy == "hybrid_reranking":
        return get_hybrid_reranking_retriever()
    elif strategy == "multi_query":
        return get_multi_query_retriever()
    elif strategy == "ensemble":
        return get_ensemble_retriever()
    elif strategy == "contextual":
        return get_contextual_compression_retriever()
    else:
        # Default to reranking (best balance of quality and speed)
        logger.info(f"Unknown strategy '{strategy}', defaulting to 'reranking'")
        return get_reranking_retriever()

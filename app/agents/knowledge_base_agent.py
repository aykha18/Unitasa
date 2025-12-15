"""
KnowledgeBaseAgent - RAG System with Vector Storage
Handles document chunking, embeddings, and semantic search
"""

import logging
from typing import Dict, Any, List, Optional
import uuid
import hashlib

from app.agents.base import CostOptimizedAgent

logger = logging.getLogger(__name__)


class KnowledgeBaseAgent(CostOptimizedAgent):
    """
    Agent responsible for managing the knowledge base with RAG capabilities
    """

    def __init__(self, name: str = "knowledge_base"):
        super().__init__(name)
        self.vector_store = None  # Will be initialized with Pinecone
        self._init_vector_store()

    def _init_vector_store(self):
        """Initialize vector store (Pinecone)"""
        try:
            import pinecone
            from pinecone import Pinecone

            # Initialize Pinecone (would use actual API key from config)
            # pc = Pinecone(api_key=settings.vector_db.api_key)
            # self.index = pc.Index(settings.vector_db.index_name)

            logger.info("Vector store initialized (mock for now)")
        except ImportError:
            logger.warning("Pinecone not available, using mock vector store")

    def get_system_prompt(self) -> str:
        return """You are a knowledge base management expert. Your role is to:

1. Analyze content and extract key concepts and topics
2. Generate meaningful tags and categories
3. Identify relationships between different pieces of information
4. Ensure content is properly categorized for retrieval

Focus on creating searchable, well-organized knowledge structures."""

    async def execute_task(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute knowledge base operations
        """
        operation = task_input.get("operation", "store")

        if operation == "store":
            return await self._store_content(task_input)
        elif operation == "search":
            return await self._search_content(task_input)
        elif operation == "retrieve":
            return await self._retrieve_content(task_input)
        else:
            return {
                "success": False,
                "error": f"Unsupported operation: {operation}"
            }

    async def _store_content(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store content in vector database
        """
        content = task_input.get("content", "")
        metadata = task_input.get("metadata", {})
        client_id = task_input.get("client_id", "default")

        if not content:
            return {"success": False, "error": "No content provided"}

        try:
            # Generate content chunks
            chunks = self._chunk_content(content)

            # Process each chunk
            stored_chunks = []
            for i, chunk in enumerate(chunks):
                # Generate embeddings (mock for now)
                embedding = self._generate_embedding(chunk)

                # Analyze chunk for metadata
                chunk_metadata = await self._analyze_chunk(chunk)

                # Create unique ID
                chunk_id = self._generate_chunk_id(client_id, metadata.get("source", "unknown"), i)

                # Store in vector database
                vector_metadata = {
                    "client_id": client_id,
                    "chunk_id": chunk_id,
                    "content": chunk,
                    "source": metadata.get("source", "unknown"),
                    "topic": chunk_metadata.get("topic", "general"),
                    "tags": chunk_metadata.get("tags", []),
                    **metadata
                }

                # Mock storage - would actually store in Pinecone
                stored_chunks.append({
                    "id": chunk_id,
                    "content": chunk,
                    "metadata": vector_metadata,
                    "embedding": embedding
                })

            return {
                "success": True,
                "operation": "store",
                "chunks_stored": len(stored_chunks),
                "client_id": client_id,
                "total_tokens": sum(len(chunk.split()) for chunk in chunks)
            }

        except Exception as e:
            logger.error(f"Content storage failed: {e}")
            return {"success": False, "error": str(e)}

    async def _search_content(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search content using semantic similarity
        """
        query = task_input.get("query", "")
        client_id = task_input.get("client_id", "default")
        limit = task_input.get("limit", 5)

        if not query:
            return {"success": False, "error": "No search query provided"}

        try:
            # Generate query embedding
            query_embedding = self._generate_embedding(query)

            # Perform vector search (mock implementation)
            results = self._mock_vector_search(query_embedding, client_id, limit)

            # Re-rank results based on relevance
            ranked_results = await self._rerank_results(query, results)

            return {
                "success": True,
                "operation": "search",
                "query": query,
                "results": ranked_results,
                "total_found": len(ranked_results)
            }

        except Exception as e:
            logger.error(f"Content search failed: {e}")
            return {"success": False, "error": str(e)}

    async def _retrieve_content(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retrieve specific content by ID or filters
        """
        content_id = task_input.get("content_id")
        filters = task_input.get("filters", {})

        try:
            if content_id:
                # Retrieve by ID
                result = self._mock_retrieve_by_id(content_id)
                return {
                    "success": True,
                    "operation": "retrieve",
                    "content": result
                }
            else:
                # Retrieve by filters
                results = self._mock_retrieve_by_filters(filters)
                return {
                    "success": True,
                    "operation": "retrieve",
                    "results": results,
                    "total_found": len(results)
                }

        except Exception as e:
            logger.error(f"Content retrieval failed: {e}")
            return {"success": False, "error": str(e)}

    def _chunk_content(self, content: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Split content into manageable chunks
        """
        words = content.split()
        chunks = []

        for i in range(0, len(words), chunk_size - overlap):
            chunk = words[i:i + chunk_size]
            if len(chunk) >= 50:  # Minimum chunk size
                chunks.append(' '.join(chunk))

        return chunks

    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embeddings for text (mock implementation)
        """
        # In real implementation, would use OpenAI embeddings or similar
        # For now, return a mock embedding vector
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        # Create a simple 384-dimensional mock embedding
        hash_bytes = hash_obj.digest()
        embedding = []
        for i in range(0, len(hash_bytes), 1):
            embedding.append((hash_bytes[i % len(hash_bytes)] / 255.0) * 2 - 1)
        return embedding[:384]  # Truncate to reasonable size

    async def _analyze_chunk(self, chunk: str) -> Dict[str, Any]:
        """
        Analyze content chunk to extract metadata
        """
        prompt = f"""
Analyze this content chunk and extract:

1. Primary topic/category
2. Key concepts mentioned
3. Relevant tags (3-5 tags)
4. Content type (factual, opinion, tutorial, etc.)

CONTENT:
{chunk[:1000]}

Return JSON format:
{{
    "topic": "primary topic",
    "concepts": ["concept1", "concept2"],
    "tags": ["tag1", "tag2", "tag3"],
    "content_type": "factual"
}}
"""

        try:
            response = await self.generate_response(
                user_prompt=prompt,
                task_description="content chunk analysis for knowledge base"
            )

            if response["success"]:
                import json
                try:
                    content = response["content"]
                    json_start = content.find('{')
                    json_end = content.rfind('}') + 1
                    if json_start >= 0 and json_end > json_start:
                        json_str = content[json_start:json_end]
                        return json.loads(json_str)
                except:
                    pass

            # Fallback
            return {
                "topic": "general",
                "concepts": [],
                "tags": ["content"],
                "content_type": "unknown"
            }

        except Exception as e:
            logger.error(f"Chunk analysis failed: {e}")
            return {
                "topic": "general",
                "concepts": [],
                "tags": ["content"],
                "content_type": "unknown"
            }

    def _generate_chunk_id(self, client_id: str, source: str, chunk_index: int) -> str:
        """Generate unique chunk identifier"""
        unique_string = f"{client_id}:{source}:{chunk_index}"
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, unique_string))

    def _mock_vector_search(self, query_embedding: List[float], client_id: str, limit: int) -> List[Dict]:
        """Mock vector search implementation"""
        # In real implementation, would query Pinecone
        return [
            {
                "id": f"mock_chunk_{i}",
                "content": f"Mock content chunk {i} related to query",
                "metadata": {
                    "client_id": client_id,
                    "topic": "business",
                    "score": 0.95 - (i * 0.1)
                },
                "score": 0.95 - (i * 0.1)
            }
            for i in range(min(limit, 3))
        ]

    async def _rerank_results(self, query: str, results: List[Dict]) -> List[Dict]:
        """Re-rank search results based on relevance"""
        # Simple re-ranking - in real implementation could use cross-encoders
        return sorted(results, key=lambda x: x.get("score", 0), reverse=True)

    def _mock_retrieve_by_id(self, content_id: str) -> Dict:
        """Mock retrieval by ID"""
        return {
            "id": content_id,
            "content": f"Mock content for ID {content_id}",
            "metadata": {"client_id": "default", "topic": "general"}
        }

    def _mock_retrieve_by_filters(self, filters: Dict) -> List[Dict]:
        """Mock retrieval by filters"""
        return [
            {
                "id": "filtered_chunk_1",
                "content": "Filtered content example",
                "metadata": filters
            }
        ]


# Convenience functions
async def store_content(content: str, client_id: str, metadata: Dict = None) -> Dict[str, Any]:
    """Store content in knowledge base"""
    agent = KnowledgeBaseAgent()
    return await agent.execute_task({
        "operation": "store",
        "content": content,
        "client_id": client_id,
        "metadata": metadata or {}
    })


async def search_content(query: str, client_id: str, limit: int = 5) -> Dict[str, Any]:
    """Search content in knowledge base"""
    agent = KnowledgeBaseAgent()
    return await agent.execute_task({
        "operation": "search",
        "query": query,
        "client_id": client_id,
        "limit": limit
    })


def get_knowledge_base_agent() -> KnowledgeBaseAgent:
    """Get knowledge base agent instance"""
    return KnowledgeBaseAgent()
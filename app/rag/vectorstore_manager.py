"""
Vector Store Manager for ChromaDB Integration
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

from app.core.config import get_settings
settings = get_settings()


class VectorStoreManager:
    """Manages ChromaDB vector store operations"""

    def __init__(self):
        self.collection_name = settings.chroma.collection_name or "marketing_knowledge"
        self.persist_directory = settings.chroma.persist_directory or "./chroma_db"
        self.embedding_function = self._get_embedding_function()
        self.vectorstore = None

    def _get_embedding_function(self) -> Embeddings:
        """Get the embedding function"""
        return OpenAIEmbeddings(
            model=settings.embeddings.model,
            openai_api_key=settings.embeddings.openai_api_key
        )

    async def initialize(self):
        """Initialize the vector store"""
        try:
            self.vectorstore = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embedding_function,
                persist_directory=self.persist_directory
            )
            print(f"✅ Vector store initialized: {self.collection_name}")
        except Exception as e:
            print(f"❌ Failed to initialize vector store: {e}")
            raise

    async def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to the vector store"""
        if not self.vectorstore:
            await self.initialize()

        try:
            # Add metadata
            for doc in documents:
                if not doc.metadata:
                    doc.metadata = {}
                doc.metadata["added_at"] = datetime.utcnow().isoformat()
                doc.metadata["source"] = doc.metadata.get("source", "unknown")

            ids = self.vectorstore.add_documents(documents)
            print(f"✅ Added {len(documents)} documents to vector store")
            return ids
        except Exception as e:
            print(f"❌ Failed to add documents: {e}")
            raise

    async def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """Perform similarity search"""
        if not self.vectorstore:
            await self.initialize()

        try:
            docs = self.vectorstore.similarity_search(query, k=k, filter=filter)
            print(f"✅ Found {len(docs)} similar documents for query: {query[:50]}...")
            return docs
        except Exception as e:
            print(f"❌ Similarity search failed: {e}")
            return []

    async def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[tuple]:
        """Perform similarity search with relevance scores"""
        if not self.vectorstore:
            await self.initialize()

        try:
            docs_with_scores = self.vectorstore.similarity_search_with_score(query, k=k, filter=filter)
            print(f"✅ Found {len(docs_with_scores)} documents with scores for query: {query[:50]}...")
            return docs_with_scores
        except Exception as e:
            print(f"❌ Similarity search with scores failed: {e}")
            return []


# Singleton instance
_vector_store_manager_instance = None

def get_vector_store_manager() -> VectorStoreManager:
    """Get singleton instance of VectorStoreManager"""
    global _vector_store_manager_instance
    if _vector_store_manager_instance is None:
        _vector_store_manager_instance = VectorStoreManager()
    return _vector_store_manager_instance

    async def delete_documents(self, ids: List[str]):
        """Delete documents by IDs"""
        if not self.vectorstore:
            await self.initialize()

        try:
            self.vectorstore.delete(ids)
            print(f"✅ Deleted {len(ids)} documents from vector store")
        except Exception as e:
            print(f"❌ Failed to delete documents: {e}")
            raise

    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        if not self.vectorstore:
            await self.initialize()

        try:
            # Get basic stats
            count = self.vectorstore._collection.count()
            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "persist_directory": self.persist_directory,
                "embedding_model": settings.embeddings.model
            }
        except Exception as e:
            print(f"❌ Failed to get collection stats: {e}")
            return {"error": str(e)}

    async def clear_collection(self):
        """Clear all documents from the collection"""
        if not self.vectorstore:
            await self.initialize()

        try:
            self.vectorstore.delete_collection()
            # Reinitialize
            await self.initialize()
            print("✅ Collection cleared and reinitialized")
        except Exception as e:
            print(f"❌ Failed to clear collection: {e}")
            raise

    def persist(self):
        """Persist the vector store to disk"""
        if self.vectorstore:
            try:
                self.vectorstore.persist()
                print("✅ Vector store persisted to disk")
            except Exception as e:
                print(f"❌ Failed to persist vector store: {e}")


# Global instance
_vector_store_manager = None


async def get_vector_store_manager() -> VectorStoreManager:
    """Get the global vector store manager instance"""
    global _vector_store_manager
    if _vector_store_manager is None:
        _vector_store_manager = VectorStoreManager()
        await _vector_store_manager.initialize()
    return _vector_store_manager


async def get_vector_store() -> Chroma:
    """Get the Chroma vector store instance"""
    manager = await get_vector_store_manager()
    return manager.vectorstore


# Convenience functions
async def add_documents_to_vectorstore(documents: List[Document]) -> List[str]:
    """Add documents to vector store"""
    manager = await get_vector_store_manager()
    return await manager.add_documents(documents)


async def search_vectorstore(query: str, k: int = 4) -> List[Document]:
    """Search the vector store"""
    manager = await get_vector_store_manager()
    return await manager.similarity_search(query, k=k)


async def get_vectorstore_stats() -> Dict[str, Any]:
    """Get vector store statistics"""
    manager = await get_vector_store_manager()
    return await manager.get_collection_stats()

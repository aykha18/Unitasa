"""
Document Ingestion Pipeline for RAG System
Handles processing and ingesting documents from various sources
"""

import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

try:
    try:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
    except ImportError:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        
    from langchain_core.documents import Document
    from langchain_community.document_loaders import (
        TextLoader,
        PyPDFLoader,
        UnstructuredMarkdownLoader,
        DirectoryLoader
    )
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    # Define dummy Document for type hinting if langchain is missing
    class Document:
        pass

from .vectorstore_manager import get_vector_store_manager

logger = logging.getLogger(__name__)


class DocumentIngestionPipeline:
    """Pipeline for processing and ingesting documents into vector store"""

    def __init__(self, collection_name: str = "marketing_knowledge"):
        if not LANGCHAIN_AVAILABLE:
            # We can log warning instead of raising error if we want to allow class init for other purposes
            # but methods will fail
            pass

        self.collection_name = collection_name
        self.vector_store_manager = None  # Will be initialized lazily or via async call

        # Initialize text splitter with optimized settings
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""],
            length_function=len
        )

        # Supported file extensions
        self.supported_extensions = {
            '.pdf': self._load_pdf,
            '.md': self._load_markdown,
            '.txt': self._load_text,
            '.html': self._load_html,
            '.json': self._load_json
        }

    async def ingest_file(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Ingest a single file"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            # Determine loader based on file extension
            extension = file_path.suffix.lower()
            if extension not in self.supported_extensions:
                raise ValueError(f"Unsupported file type: {extension}")

            # Load documents
            loader_func = self.supported_extensions[extension]
            documents = loader_func(file_path)

            if not documents:
                return {"status": "error", "message": "No documents loaded from file"}

            # Process and ingest
            result = await self.ingest_documents(documents, metadata or {})

            return {
                "status": "success",
                "file": str(file_path),
                "documents_loaded": len(documents),
                "chunks_created": result.get("chunks_created", 0)
            }

        except Exception as e:
            logger.error(f"Failed to ingest file {file_path}: {e}")
            return {"status": "error", "file": str(file_path), "error": str(e)}

    async def ingest_directory(self, directory_path: str, metadata: Optional[Dict[str, Any]] = None, recursive: bool = True) -> Dict[str, Any]:
        """Ingest all supported files from a directory"""
        try:
            directory = Path(directory_path)
            if not directory.exists() or not directory.is_dir():
                raise NotADirectoryError(f"Directory not found: {directory_path}")

            results = []
            total_files = 0
            total_documents = 0

            # Find all supported files
            pattern = "**/*" if recursive else "*"
            for extension in self.supported_extensions.keys():
                for file_path in directory.glob(f"{pattern}{extension}"):
                    total_files += 1
                    result = await self.ingest_file(str(file_path), metadata)
                    results.append(result)

                    if result["status"] == "success":
                        total_documents += result.get("documents_loaded", 0)

            return {
                "status": "success",
                "directory": str(directory_path),
                "files_processed": total_files,
                "total_documents": total_documents,
                "results": results
            }

        except Exception as e:
            logger.error(f"Failed to ingest directory {directory_path}: {e}")
            return {"status": "error", "directory": str(directory_path), "error": str(e)}

    async def ingest_documents(self, documents: List[Document], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process and ingest documents into vector store"""
        try:
            # Add metadata to documents
            if metadata:
                for doc in documents:
                    doc.metadata.update(metadata)

            # Split documents into chunks
            chunks = self.text_splitter.split_documents(documents)

            # Add chunk-specific metadata
            for i, chunk in enumerate(chunks):
                chunk.metadata.update({
                    "chunk_id": f"chunk_{i}",
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "ingestion_timestamp": datetime.utcnow().isoformat()
                })

            # Ingest into vector store
            manager = await get_vector_store_manager()
            # VectorStoreManager.add_documents does not accept collection_name
            await manager.add_documents(chunks)

            logger.info(f"Ingested {len(chunks)} chunks from {len(documents)} documents")

            return {
                "status": "success",
                "documents_processed": len(documents),
                "chunks_created": len(chunks),
                "collection": self.collection_name
            }

        except Exception as e:
            logger.error(f"Failed to ingest documents: {e}")
            return {"status": "error", "error": str(e)}

    async def ingest_from_urls(self, urls: List[str], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Ingest content from URLs"""
        try:
            from langchain_community.document_loaders import WebBaseLoader

            loader = WebBaseLoader(urls)
            documents = loader.load()

            if not documents:
                return {"status": "error", "message": "No documents loaded from URLs"}

            # Add URL metadata
            for doc in documents:
                doc.metadata.update({
                    "source_type": "web",
                    "urls": ",".join(urls) if isinstance(urls, list) else str(urls)
                })

            result = await self.ingest_documents(documents, metadata)

            return {
                "status": "success",
                "urls_processed": len(urls),
                "documents_loaded": len(documents),
                "chunks_created": result.get("chunks_created", 0)
            }

        except Exception as e:
            logger.error(f"Failed to ingest from URLs: {e}")
            return {"status": "error", "urls": urls, "error": str(e)}

    async def ingest_marketing_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Ingest structured marketing content"""
        try:
            # Create document from structured content
            doc_content = f"""
            Title: {content.get('title', 'Untitled')}
            Category: {content.get('category', 'General')}
            Platform: {content.get('platform', 'General')}

            Content:
            {content.get('content', '')}

            Key Points:
            {content.get('key_points', '')}

            Best Practices:
            {content.get('best_practices', '')}
            """

            document = Document(
                page_content=doc_content,
                metadata={
                    "title": content.get('title'),
                    "category": content.get('category'),
                    "platform": content.get('platform'),
                    "content_type": content.get('content_type', 'marketing_content'),
                    "source": content.get('source', 'manual_entry'),
                    "tags": ",".join(content.get('tags', [])) if isinstance(content.get('tags'), list) else str(content.get('tags', "")),
                    "author": content.get('author'),
                    "publish_date": content.get('publish_date'),
                    "client_id": content.get('client_id')
                }
            )

            result = await self.ingest_documents([document])

            return {
                "status": "success",
                "content_title": content.get('title'),
                "chunks_created": result.get("chunks_created", 0)
            }

        except Exception as e:
            logger.error(f"Failed to ingest marketing content: {e}")
            return {"status": "error", "error": str(e)}

    def _load_pdf(self, file_path: Path) -> List[Document]:
        """Load PDF documents"""
        try:
            loader = PyPDFLoader(str(file_path))
            return loader.load()
        except Exception as e:
            logger.error(f"Failed to load PDF {file_path}: {e}")
            return []

    def _load_markdown(self, file_path: Path) -> List[Document]:
        """Load Markdown documents"""
        try:
            loader = UnstructuredMarkdownLoader(str(file_path))
            return loader.load()
        except Exception as e:
            logger.error(f"Failed to load Markdown {file_path}: {e}")
            return []

    def _load_text(self, file_path: Path) -> List[Document]:
        """Load text documents"""
        try:
            loader = TextLoader(str(file_path))
            return loader.load()
        except Exception as e:
            logger.error(f"Failed to load text file {file_path}: {e}")
            return []

    def _load_html(self, file_path: Path) -> List[Document]:
        """Load HTML documents"""
        try:
            from langchain_community.document_loaders import BSHTMLLoader
            loader = BSHTMLLoader(str(file_path))
            return loader.load()
        except Exception as e:
            logger.error(f"Failed to load HTML {file_path}: {e}")
            return []

    def _load_json(self, file_path: Path) -> List[Document]:
        """Load JSON documents"""
        try:
            import json
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Handle different JSON structures
            if isinstance(data, list):
                documents = []
                for item in data:
                    if isinstance(item, dict):
                        content = json.dumps(item, indent=2)
                        doc = Document(
                            page_content=content,
                            metadata={"source": str(file_path), "type": "json_record"}
                        )
                        documents.append(doc)
                return documents
            elif isinstance(data, dict):
                content = json.dumps(data, indent=2)
                return [Document(
                    page_content=content,
                    metadata={"source": str(file_path), "type": "json_object"}
                )]
            else:
                return [Document(
                    page_content=str(data),
                    metadata={"source": str(file_path), "type": "json_value"}
                )]

        except Exception as e:
            logger.error(f"Failed to load JSON {file_path}: {e}")
            return []


# Convenience functions
def ingest_file(file_path: str, collection: str = "marketing_knowledge", metadata: Optional[Dict[str, Any]] = None):
    """Convenience function to ingest a single file"""
    pipeline = DocumentIngestionPipeline(collection)
    return pipeline.ingest_file(file_path, metadata)


def ingest_directory(directory_path: str, collection: str = "marketing_knowledge", metadata: Optional[Dict[str, Any]] = None):
    """Convenience function to ingest a directory"""
    pipeline = DocumentIngestionPipeline(collection)
    return pipeline.ingest_directory(directory_path, metadata)


def ingest_marketing_content(content: Dict[str, Any], collection: str = "marketing_knowledge"):
    """Convenience function to ingest marketing content"""
    pipeline = DocumentIngestionPipeline(collection)
    return pipeline.ingest_marketing_content(content)

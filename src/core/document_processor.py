"""
Document Processing Module
Handles document loading, parsing, and chunking
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
import hashlib

from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import Document as LlamaDocument, TextNode

from src.core.exceptions import DocumentNotFoundError, DocumentLoadError, DocumentParseError
from src.models.schemas import DocumentMetadata, Document
from src.utils.logging import get_logger, ContextLogger
from config.settings import ChunkingConfig

logger = get_logger(__name__)


class DocumentProcessor:
    """Handles document processing operations"""

    def __init__(self, chunking_config: Optional[ChunkingConfig] = None):
        """
        Initialize document processor

        Args:
            chunking_config: Configuration for chunking
        """
        self.chunking_config = chunking_config or ChunkingConfig()
        self.splitter = SentenceSplitter(
            chunk_size=self.chunking_config.chunk_size,
            chunk_overlap=self.chunking_config.chunk_overlap
        )

        logger.info(
            "DocumentProcessor initialized",
            extra={
                "chunk_size": self.chunking_config.chunk_size,
                "chunk_overlap": self.chunking_config.chunk_overlap
            }
        )

    def load_document(self, file_path: str) -> List[LlamaDocument]:
        """
        Load a single document

        Args:
            file_path: Path to the document

        Returns:
            List of LlamaIndex Document objects

        Raises:
            DocumentNotFoundError: If document doesn't exist
            DocumentLoadError: If document fails to load
        """
        path = Path(file_path)

        if not path.exists():
            raise DocumentNotFoundError(
                f"Document not found: {file_path}",
                details={"file_path": file_path}
            )

        with ContextLogger(logger, "load_document", file_path=file_path):
            try:
                documents = SimpleDirectoryReader(
                    input_files=[file_path]
                ).load_data()

                logger.info(
                    f"Loaded {len(documents)} page(s) from {path.name}",
                    extra={
                        "file_path": file_path,
                        "num_pages": len(documents)
                    }
                )

                return documents

            except Exception as e:
                raise DocumentLoadError(
                    f"Failed to load document: {file_path}",
                    details={"file_path": file_path},
                    original_error=e
                )

    def load_multiple_documents(
        self,
        file_paths: List[str]
    ) -> Dict[str, List[LlamaDocument]]:
        """
        Load multiple documents

        Args:
            file_paths: List of file paths

        Returns:
            Dictionary mapping file names to document lists
        """
        loaded_docs = {}

        for file_path in file_paths:
            try:
                docs = self.load_document(file_path)
                file_name = Path(file_path).stem
                loaded_docs[file_name] = docs
            except Exception as e:
                logger.error(
                    f"Failed to load {file_path}: {str(e)}",
                    extra={"file_path": file_path, "error": str(e)}
                )

        logger.info(
            f"Loaded {len(loaded_docs)} documents successfully",
            extra={"total_requested": len(file_paths), "successfully_loaded": len(loaded_docs)}
        )

        return loaded_docs

    def chunk_documents(
        self,
        documents: List[LlamaDocument]
    ) -> List[TextNode]:
        """
        Chunk documents into smaller pieces

        Args:
            documents: List of documents to chunk

        Returns:
            List of TextNode objects
        """
        with ContextLogger(logger, "chunk_documents", num_documents=len(documents)):
            try:
                nodes = self.splitter.get_nodes_from_documents(documents)

                logger.info(
                    f"Created {len(nodes)} chunks from {len(documents)} documents",
                    extra={
                        "num_documents": len(documents),
                        "num_chunks": len(nodes)
                    }
                )

                return nodes

            except Exception as e:
                raise DocumentParseError(
                    "Failed to chunk documents",
                    details={"num_documents": len(documents)},
                    original_error=e
                )

    def process_document(
        self,
        file_path: str
    ) -> tuple[List[TextNode], DocumentMetadata]:
        """
        Full document processing pipeline

        Args:
            file_path: Path to document

        Returns:
            Tuple of (nodes, metadata)
        """
        with ContextLogger(logger, "process_document", file_path=file_path):
            # Load document
            documents = self.load_document(file_path)

            # Create metadata
            path = Path(file_path)
            metadata = DocumentMetadata(
                file_name=path.name,
                file_path=str(path.absolute()),
                file_size=path.stat().st_size,
                file_type=path.suffix,
                num_pages=len(documents)
            )

            # Chunk documents
            nodes = self.chunk_documents(documents)
            metadata.num_chunks = len(nodes)

            logger.info(
                f"Processed {path.name}",
                extra={
                    "file_name": path.name,
                    "num_pages": len(documents),
                    "num_chunks": len(nodes)
                }
            )

            return nodes, metadata

    def process_multiple_documents(
        self,
        file_paths: List[str]
    ) -> Dict[str, tuple[List[TextNode], DocumentMetadata]]:
        """
        Process multiple documents

        Args:
            file_paths: List of file paths

        Returns:
            Dictionary mapping file names to (nodes, metadata) tuples
        """
        processed_docs = {}

        for file_path in file_paths:
            try:
                nodes, metadata = self.process_document(file_path)
                file_name = Path(file_path).stem
                processed_docs[file_name] = (nodes, metadata)
            except Exception as e:
                logger.error(
                    f"Failed to process {file_path}: {str(e)}",
                    extra={"file_path": file_path, "error": str(e)}
                )

        return processed_docs

    @staticmethod
    def compute_document_hash(content: str) -> str:
        """
        Compute hash of document content

        Args:
            content: Document content

        Returns:
            SHA256 hash
        """
        return hashlib.sha256(content.encode()).hexdigest()

    def get_document_stats(self, nodes: List[TextNode]) -> Dict[str, Any]:
        """
        Get statistics about document chunks

        Args:
            nodes: List of TextNode objects

        Returns:
            Dictionary of statistics
        """
        if not nodes:
            return {
                "num_chunks": 0,
                "avg_chunk_size": 0,
                "min_chunk_size": 0,
                "max_chunk_size": 0,
                "total_chars": 0
            }

        chunk_sizes = [len(node.text) for node in nodes]

        return {
            "num_chunks": len(nodes),
            "avg_chunk_size": sum(chunk_sizes) / len(chunk_sizes),
            "min_chunk_size": min(chunk_sizes),
            "max_chunk_size": max(chunk_sizes),
            "total_chars": sum(chunk_sizes)
        }

"""
Vector Store Management with Persistence
Supports ChromaDB and in-memory storage
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
from abc import ABC, abstractmethod

from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.schema import TextNode
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.vector_stores import SimpleVectorStore

from src.core.exceptions import IndexCreationError, IndexLoadError, IndexPersistError
from src.utils.logging import get_logger, ContextLogger
from config.settings import VectorStoreConfig

logger = get_logger(__name__)


class BaseVectorStore(ABC):
    """Abstract base class for vector stores"""

    @abstractmethod
    def create_index(self, nodes: List[TextNode]) -> VectorStoreIndex:
        """Create index from nodes"""
        pass

    @abstractmethod
    def load_index(self) -> Optional[VectorStoreIndex]:
        """Load existing index"""
        pass

    @abstractmethod
    def persist_index(self, index: VectorStoreIndex) -> bool:
        """Persist index to storage"""
        pass

    @abstractmethod
    def delete_index(self) -> bool:
        """Delete index from storage"""
        pass


class ChromaVectorStoreManager(BaseVectorStore):
    """ChromaDB vector store manager with persistence"""

    def __init__(self, config: VectorStoreConfig):
        """
        Initialize ChromaDB vector store

        Args:
            config: Vector store configuration
        """
        self.config = config
        self.persist_dir = Path(config.persist_directory)
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        self.collection_name = config.collection_name

        # Initialize ChromaDB
        try:
            import chromadb
            self.chroma_client = chromadb.PersistentClient(
                path=str(self.persist_dir)
            )

            logger.info(
                "ChromaDB vector store initialized",
                extra={
                    "persist_dir": str(self.persist_dir),
                    "collection_name": self.collection_name
                }
            )
        except ImportError:
            logger.error("chromadb package not installed. Install with: pip install chromadb")
            raise ImportError("chromadb package is required for persistent storage")

    def create_index(self, nodes: List[TextNode]) -> VectorStoreIndex:
        """
        Create vector index from nodes

        Args:
            nodes: List of TextNode objects

        Returns:
            VectorStoreIndex

        Raises:
            IndexCreationError: If index creation fails
        """
        with ContextLogger(logger, "create_chroma_index", num_nodes=len(nodes)):
            try:
                # Create or get collection
                chroma_collection = self.chroma_client.get_or_create_collection(
                    name=self.collection_name
                )

                # Create vector store
                vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

                # Create storage context
                storage_context = StorageContext.from_defaults(
                    vector_store=vector_store
                )

                # Create index
                index = VectorStoreIndex(
                    nodes=nodes,
                    storage_context=storage_context
                )

                logger.info(
                    f"Created ChromaDB index with {len(nodes)} nodes",
                    extra={
                        "num_nodes": len(nodes),
                        "collection": self.collection_name
                    }
                )

                return index

            except Exception as e:
                raise IndexCreationError(
                    "Failed to create ChromaDB index",
                    details={"num_nodes": len(nodes)},
                    original_error=e
                )

    def load_index(self) -> Optional[VectorStoreIndex]:
        """
        Load existing index

        Returns:
            VectorStoreIndex if exists, None otherwise

        Raises:
            IndexLoadError: If index loading fails
        """
        with ContextLogger(logger, "load_chroma_index"):
            try:
                # Try to get existing collection
                chroma_collection = self.chroma_client.get_collection(
                    name=self.collection_name
                )

                # Create vector store
                vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

                # Create storage context
                storage_context = StorageContext.from_defaults(
                    vector_store=vector_store
                )

                # Load index
                index = VectorStoreIndex.from_vector_store(
                    vector_store=vector_store,
                    storage_context=storage_context
                )

                logger.info(
                    f"Loaded ChromaDB index from {self.collection_name}",
                    extra={"collection": self.collection_name}
                )

                return index

            except ValueError:
                # Collection doesn't exist
                logger.info(
                    f"No existing collection found: {self.collection_name}",
                    extra={"collection": self.collection_name}
                )
                return None
            except Exception as e:
                raise IndexLoadError(
                    "Failed to load ChromaDB index",
                    details={"collection": self.collection_name},
                    original_error=e
                )

    def persist_index(self, index: VectorStoreIndex) -> bool:
        """
        Persist index (ChromaDB automatically persists)

        Args:
            index: Index to persist

        Returns:
            True if successful
        """
        logger.info(
            "ChromaDB automatically persists data",
            extra={"collection": self.collection_name}
        )
        return True

    def delete_index(self) -> bool:
        """
        Delete index

        Returns:
            True if successful
        """
        try:
            self.chroma_client.delete_collection(name=self.collection_name)
            logger.info(
                f"Deleted ChromaDB collection: {self.collection_name}",
                extra={"collection": self.collection_name}
            )
            return True
        except Exception as e:
            logger.error(
                f"Failed to delete collection: {str(e)}",
                extra={"collection": self.collection_name, "error": str(e)}
            )
            return False


class MemoryVectorStoreManager(BaseVectorStore):
    """In-memory vector store manager (no persistence)"""

    def __init__(self, config: VectorStoreConfig):
        """
        Initialize in-memory vector store

        Args:
            config: Vector store configuration
        """
        self.config = config
        self._index: Optional[VectorStoreIndex] = None

        logger.info("In-memory vector store initialized")

    def create_index(self, nodes: List[TextNode]) -> VectorStoreIndex:
        """
        Create vector index from nodes

        Args:
            nodes: List of TextNode objects

        Returns:
            VectorStoreIndex

        Raises:
            IndexCreationError: If index creation fails
        """
        with ContextLogger(logger, "create_memory_index", num_nodes=len(nodes)):
            try:
                self._index = VectorStoreIndex(nodes=nodes)

                logger.info(
                    f"Created in-memory index with {len(nodes)} nodes",
                    extra={"num_nodes": len(nodes)}
                )

                return self._index

            except Exception as e:
                raise IndexCreationError(
                    "Failed to create in-memory index",
                    details={"num_nodes": len(nodes)},
                    original_error=e
                )

    def load_index(self) -> Optional[VectorStoreIndex]:
        """
        Load existing index

        Returns:
            VectorStoreIndex if exists, None otherwise
        """
        return self._index

    def persist_index(self, index: VectorStoreIndex) -> bool:
        """
        Persist index (no-op for memory store)

        Args:
            index: Index to persist

        Returns:
            False (memory store doesn't persist)
        """
        logger.warning("Memory vector store does not support persistence")
        return False

    def delete_index(self) -> bool:
        """
        Delete index

        Returns:
            True if successful
        """
        self._index = None
        logger.info("Cleared in-memory index")
        return True


class VectorStoreFactory:
    """Factory for creating vector store managers"""

    @staticmethod
    def create(config: VectorStoreConfig) -> BaseVectorStore:
        """
        Create vector store manager based on configuration

        Args:
            config: Vector store configuration

        Returns:
            BaseVectorStore implementation

        Raises:
            ValueError: If store type is not supported
        """
        if config.type == "chroma":
            return ChromaVectorStoreManager(config)
        elif config.type in ["memory", "faiss"]:
            return MemoryVectorStoreManager(config)
        else:
            raise ValueError(f"Unsupported vector store type: {config.type}")


class VectorStoreManager:
    """High-level vector store manager"""

    def __init__(self, config: Optional[VectorStoreConfig] = None):
        """
        Initialize vector store manager

        Args:
            config: Vector store configuration
        """
        self.config = config or VectorStoreConfig()
        self.store = VectorStoreFactory.create(self.config)

        self.indices: Dict[str, VectorStoreIndex] = {}

        logger.info(
            "VectorStoreManager initialized",
            extra={"store_type": self.config.type}
        )

    def create_index(
        self,
        name: str,
        nodes: List[TextNode],
        force: bool = False
    ) -> VectorStoreIndex:
        """
        Create or retrieve index

        Args:
            name: Index name
            nodes: Nodes to index
            force: Force recreation if exists

        Returns:
            VectorStoreIndex
        """
        if name in self.indices and not force:
            logger.info(f"Returning existing index: {name}")
            return self.indices[name]

        index = self.store.create_index(nodes)
        self.indices[name] = index

        return index

    def get_index(self, name: str) -> Optional[VectorStoreIndex]:
        """
        Get index by name

        Args:
            name: Index name

        Returns:
            VectorStoreIndex if exists, None otherwise
        """
        return self.indices.get(name)

    def list_indices(self) -> List[str]:
        """
        List all index names

        Returns:
            List of index names
        """
        return list(self.indices.keys())

    def delete_index(self, name: str) -> bool:
        """
        Delete index

        Args:
            name: Index name

        Returns:
            True if successful
        """
        if name in self.indices:
            del self.indices[name]

        return self.store.delete_index()

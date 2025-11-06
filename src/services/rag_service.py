"""
Improved RAG Service - Industry Standard Implementation
Main business logic for RAG system with all best practices
"""

from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path
from uuid import uuid4
from datetime import datetime

from llama_index.core import Settings, SummaryIndex
from llama_index.core.agent import FunctionCallingAgentWorker, AgentRunner
from llama_index.core.objects import ObjectIndex
from llama_index.core.tools import FunctionTool, QueryEngineTool
from llama_index.core.vector_stores import MetadataFilters, FilterCondition
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from src.core.document_processor import DocumentProcessor
from src.core.vector_store import VectorStoreManager
from src.core.exceptions import (
    AgentNotInitializedError,
    DocumentError,
    QueryError,
    APIKeyError
)
from src.models.schemas import (
    QueryRequest,
    QueryResponse,
    RetrievedChunk,
    AgentState,
    DocumentMetadata
)
from src.utils.logging import get_logger, ContextLogger
from src.utils.cache import QueryCache
from src.utils.retry import retry_with_exponential_backoff
from config.settings import Settings as AppSettings, get_settings

logger = get_logger(__name__)


class RAGService:
    """
    Production-Ready RAG Service with Industry Best Practices

    Features:
    - Persistent vector store with ChromaDB
    - Structured logging and error handling
    - Query caching with LRU
    - Retry logic with exponential backoff
    - Configuration management with Pydantic
    - Comprehensive validation
    - Monitoring and metrics
    """

    def __init__(self, settings: Optional[AppSettings] = None):
        """
        Initialize RAG service

        Args:
            settings: Application settings (loads from env if None)

        Raises:
            APIKeyError: If API key is invalid
        """
        self.settings = settings or get_settings()

        with ContextLogger(logger, "initialize_rag_service"):
            # Validate API key
            if not self.settings.google_api_key:
                raise APIKeyError("Google API key not configured")

            # Initialize components
            self._initialize_llm()
            self._initialize_embeddings()
            self._initialize_global_settings()
            self._initialize_components()

            logger.info(
                "RAG Service initialized successfully",
                extra={
                    "llm_model": self.settings.llm.model_name,
                    "embedding_model": self.settings.embedding.model_name,
                    "vector_store": self.settings.vector_store.type,
                    "cache_enabled": self.settings.cache.enabled
                }
            )

    def _initialize_llm(self):
        """Initialize LLM"""
        try:
            self.llm = Gemini(
                model=self.settings.llm.model_name,
                api_key=self.settings.google_api_key,
                temperature=self.settings.llm.temperature,
                max_tokens=self.settings.llm.max_tokens,
                timeout=self.settings.llm.timeout
            )
            logger.info(f"LLM initialized: {self.settings.llm.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {str(e)}")
            raise

    def _initialize_embeddings(self):
        """Initialize embedding model"""
        try:
            self.embed_model = HuggingFaceEmbedding(
                model_name=self.settings.embedding.model_name,
                max_length=self.settings.embedding.max_length
            )
            logger.info(f"Embeddings initialized: {self.settings.embedding.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize embeddings: {str(e)}")
            raise

    def _initialize_global_settings(self):
        """Set global LlamaIndex settings"""
        Settings.llm = self.llm
        Settings.embed_model = self.embed_model
        Settings.chunk_size = self.settings.chunking.chunk_size
        Settings.chunk_overlap = self.settings.chunking.chunk_overlap

    def _initialize_components(self):
        """Initialize RAG components"""
        # Document processor
        self.document_processor = DocumentProcessor(
            chunking_config=self.settings.chunking
        )

        # Vector store manager
        self.vector_store_manager = VectorStoreManager(
            config=self.settings.vector_store
        )

        # Query cache
        self.query_cache = QueryCache(config=self.settings.cache)

        # State
        self.agent: Optional[AgentRunner] = None
        self.tools: Dict[str, List] = {}
        self.document_metadata: Dict[str, DocumentMetadata] = {}
        self.agent_state = AgentState(
            status="initializing",
            num_documents=0,
            num_chunks=0,
            mode="advanced"
        )

    def get_available_documents(self, docs_dir: Optional[str] = None) -> List[str]:
        """
        Get list of available PDF documents

        Args:
            docs_dir: Directory to search (uses settings if None)

        Returns:
            List of PDF filenames
        """
        directory = Path(docs_dir or self.settings.docs_dir)
        pdf_files = list(directory.glob("*.pdf"))
        return sorted([pdf.name for pdf in pdf_files])

    def _create_doc_tools(
        self,
        file_path: str,
        doc_name: str
    ) -> Tuple[FunctionTool, QueryEngineTool]:
        """
        Create vector and summary tools for a document

        Args:
            file_path: Path to document
            doc_name: Document name

        Returns:
            Tuple of (vector_tool, summary_tool)
        """
        # Process document
        nodes, metadata = self.document_processor.process_document(file_path)
        self.document_metadata[doc_name] = metadata

        # Create vector index
        vector_index = self.vector_store_manager.create_index(
            name=doc_name,
            nodes=nodes
        )

        # Create vector query tool
        def vector_query(
            query: str,
            page_numbers: Optional[List[str]] = None
        ) -> str:
            """
            Search over a specific document using semantic similarity.

            Args:
                query: The search query
                page_numbers: Optional page numbers to filter

            Returns:
                Retrieved context from the document
            """
            page_numbers = page_numbers or []
            metadata_dicts = [
                {"key": "page_label", "value": p} for p in page_numbers
            ]

            query_engine = vector_index.as_query_engine(
                similarity_top_k=self.settings.retrieval.similarity_top_k,
                filters=MetadataFilters.from_dicts(
                    metadata_dicts,
                    condition=FilterCondition.OR
                ) if metadata_dicts else None
            )

            response = query_engine.query(query)
            return str(response)

        vector_tool = FunctionTool.from_defaults(
            name=f"vector_tool_{doc_name}",
            fn=vector_query,
            description=f"Useful for answering specific questions about {doc_name}. "
                       f"Use this when you need detailed information from the document."
        )

        # Create summary index and tool
        summary_index = SummaryIndex(nodes)
        summary_query_engine = summary_index.as_query_engine(
            response_mode="tree_summarize",
            use_async=True
        )

        summary_tool = QueryEngineTool.from_defaults(
            name=f"summary_tool_{doc_name}",
            query_engine=summary_query_engine,
            description=f"Useful for getting a high-level summary of {doc_name}. "
                       f"Use this when you need an overview of the document."
        )

        return vector_tool, summary_tool

    @retry_with_exponential_backoff(max_retries=3)
    def create_agent(
        self,
        file_paths: List[str],
        mode: str = "advanced"
    ) -> AgentState:
        """
        Create RAG agent with documents

        Args:
            file_paths: List of document paths
            mode: Agent mode ("simple" or "advanced")

        Returns:
            AgentState

        Raises:
            DocumentError: If document loading fails
        """
        with ContextLogger(
            logger,
            "create_agent",
            num_files=len(file_paths),
            mode=mode
        ):
            self.agent_state.status = "initializing"
            self.agent_state.mode = mode

            # Create tools for each document
            all_tools = []
            for file_path in file_paths:
                doc_name = Path(file_path).stem
                try:
                    vector_tool, summary_tool = self._create_doc_tools(
                        file_path,
                        doc_name
                    )
                    self.tools[doc_name] = [vector_tool, summary_tool]
                    all_tools.extend([vector_tool, summary_tool])
                except Exception as e:
                    logger.error(
                        f"Failed to process {file_path}: {str(e)}",
                        extra={"file_path": file_path, "error": str(e)}
                    )
                    raise DocumentError(
                        f"Failed to process document: {file_path}",
                        details={"file_path": file_path},
                        original_error=e
                    )

            # Create agent
            if mode == "advanced" and len(all_tools) > 6:
                # Use tool retrieval for many documents
                obj_index = ObjectIndex.from_objects(
                    all_tools,
                    index_cls=lambda objects: self.vector_store_manager.create_index(
                        "tools",
                        objects,
                        force=True
                    )
                )

                obj_retriever = obj_index.as_retriever(
                    similarity_top_k=self.settings.retrieval.similarity_top_k
                )

                agent_worker = FunctionCallingAgentWorker.from_tools(
                    tool_retriever=obj_retriever,
                    llm=self.llm,
                    system_prompt=self.settings.agent.system_prompt,
                    verbose=self.settings.agent.verbose,
                    max_iterations=self.settings.agent.max_iterations
                )
            else:
                # Simple agent with all tools
                agent_worker = FunctionCallingAgentWorker.from_tools(
                    all_tools,
                    llm=self.llm,
                    system_prompt=self.settings.agent.system_prompt,
                    verbose=self.settings.agent.verbose,
                    max_iterations=self.settings.agent.max_iterations
                )

            self.agent = AgentRunner(agent_worker)

            # Update state
            self.agent_state.status = "ready"
            self.agent_state.num_documents = len(file_paths)
            self.agent_state.num_chunks = sum(
                meta.num_chunks or 0
                for meta in self.document_metadata.values()
            )

            logger.info(
                "Agent created successfully",
                extra={
                    "num_documents": self.agent_state.num_documents,
                    "num_chunks": self.agent_state.num_chunks,
                    "mode": mode
                }
            )

            return self.agent_state

    @retry_with_exponential_backoff(max_retries=3)
    def query(self, query_request: QueryRequest) -> QueryResponse:
        """
        Query the agent

        Args:
            query_request: Query request

        Returns:
            QueryResponse

        Raises:
            AgentNotInitializedError: If agent not initialized
            QueryError: If query fails
        """
        if self.agent is None:
            raise AgentNotInitializedError(
                "Agent not initialized. Call create_agent first."
            )

        query = query_request.query

        # Check cache
        cached_result = self.query_cache.get(query)
        if cached_result:
            logger.info("Returning cached result")
            return cached_result

        with ContextLogger(logger, "query", query=query[:100]):
            start_time = datetime.utcnow()

            try:
                # Execute query
                self.agent_state.status = "processing"
                response = self.agent.query(query)

                # Calculate latency
                latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

                # Create response
                query_response = QueryResponse(
                    query=query,
                    answer=str(response),
                    retrieved_chunks=[],  # TODO: Extract from response
                    sources=[],  # TODO: Extract from response
                    latency_ms=latency_ms,
                    metadata={
                        "model": self.settings.llm.model_name,
                        "cache_hit": False
                    }
                )

                # Update state
                self.agent_state.status = "ready"
                self.agent_state.last_query_at = datetime.utcnow()

                # Cache result
                self.query_cache.set(query, query_response)

                logger.info(
                    "Query completed",
                    extra={
                        "latency_ms": latency_ms,
                        "answer_length": len(str(response))
                    }
                )

                return query_response

            except Exception as e:
                self.agent_state.status = "error"
                logger.error(
                    f"Query failed: {str(e)}",
                    extra={"query": query, "error": str(e)}
                )
                raise QueryError(
                    "Query execution failed",
                    details={"query": query},
                    original_error=e
                )

    def get_agent_state(self) -> AgentState:
        """Get current agent state"""
        return self.agent_state

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self.query_cache.get_stats()

    def clear_cache(self) -> None:
        """Clear query cache"""
        self.query_cache.clear()
        logger.info("Query cache cleared")

    def reset(self) -> None:
        """Reset the service"""
        self.agent = None
        self.tools = {}
        self.document_metadata = {}
        self.agent_state = AgentState(
            status="initializing",
            num_documents=0,
            num_chunks=0,
            mode="advanced"
        )
        self.clear_cache()
        logger.info("RAG Service reset")

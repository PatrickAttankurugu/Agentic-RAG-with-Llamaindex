"""
Agentic RAG Backend
This module provides the core RAG functionality using Gemini 2.5 Flash and open-source embeddings.
"""

import os
from pathlib import Path
from typing import List, Optional, Tuple
from dotenv import load_dotenv
import nest_asyncio

# Apply nest_asyncio to handle async operations
nest_asyncio.apply()

# Load environment variables
load_dotenv()

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, SummaryIndex, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.agent import FunctionCallingAgentWorker, AgentRunner
from llama_index.core.objects import ObjectIndex
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from utils import get_doc_tools, get_router_query_engine


class RAGBackend:
    """Main RAG backend class for document processing and querying."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the RAG backend.

        Args:
            api_key: Google API key for Gemini. If None, will use GOOGLE_API_KEY env var.
        """
        # Set up API key
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("Google API key not found. Please set GOOGLE_API_KEY environment variable.")

        # Initialize LLM (Gemini 2.5 Flash)
        self.llm = Gemini(
            model="models/gemini-2.0-flash-exp",
            api_key=self.api_key,
            temperature=0.1
        )

        # Initialize open-source embeddings (HuggingFace)
        self.embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-small-en-v1.5"
        )

        # Set global settings
        Settings.llm = self.llm
        Settings.embed_model = self.embed_model
        Settings.chunk_size = 1024

        # Storage for documents and tools
        self.documents = {}
        self.tools = {}
        self.agent = None

    def get_available_documents(self, docs_dir: str = ".") -> List[str]:
        """
        Get list of available PDF documents.

        Args:
            docs_dir: Directory to search for PDFs

        Returns:
            List of PDF filenames
        """
        pdf_files = list(Path(docs_dir).glob("*.pdf"))
        return [pdf.name for pdf in pdf_files]

    def load_single_document(self, file_path: str) -> Tuple[str, List]:
        """
        Load a single document and create tools for it.

        Args:
            file_path: Path to PDF file

        Returns:
            Tuple of (document_name, [vector_tool, summary_tool])
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Document not found: {file_path}")

        doc_name = Path(file_path).stem
        print(f"Loading document: {doc_name}")

        # Create tools for the document
        vector_tool, summary_tool = get_doc_tools(file_path, doc_name)

        # Store the tools
        self.tools[doc_name] = [vector_tool, summary_tool]

        return doc_name, [vector_tool, summary_tool]

    def load_multiple_documents(self, file_paths: List[str]) -> dict:
        """
        Load multiple documents and create tools for each.

        Args:
            file_paths: List of paths to PDF files

        Returns:
            Dictionary mapping document names to their tools
        """
        loaded_docs = {}

        for file_path in file_paths:
            try:
                doc_name, tools = self.load_single_document(file_path)
                loaded_docs[doc_name] = tools
            except Exception as e:
                print(f"Error loading {file_path}: {str(e)}")

        return loaded_docs

    def create_simple_agent(self, file_paths: List[str]) -> AgentRunner:
        """
        Create a simple agent that works with multiple documents.

        Args:
            file_paths: List of PDF file paths

        Returns:
            AgentRunner instance
        """
        # Load documents
        self.load_multiple_documents(file_paths)

        # Flatten tools
        all_tools = [tool for tools_list in self.tools.values() for tool in tools_list]

        # Create agent
        agent_worker = FunctionCallingAgentWorker.from_tools(
            all_tools,
            llm=self.llm,
            verbose=True
        )
        self.agent = AgentRunner(agent_worker)

        return self.agent

    def create_advanced_agent(self, file_paths: List[str], top_k: int = 3) -> AgentRunner:
        """
        Create an advanced agent with tool retrieval for handling many documents.

        Args:
            file_paths: List of PDF file paths
            top_k: Number of tools to retrieve per query

        Returns:
            AgentRunner instance
        """
        # Load documents
        self.load_multiple_documents(file_paths)

        # Flatten tools
        all_tools = [tool for tools_list in self.tools.values() for tool in tools_list]

        # Create object index for tool retrieval
        obj_index = ObjectIndex.from_objects(
            all_tools,
            index_cls=VectorStoreIndex,
        )

        # Create retriever
        obj_retriever = obj_index.as_retriever(similarity_top_k=top_k)

        # Create agent with tool retrieval
        agent_worker = FunctionCallingAgentWorker.from_tools(
            tool_retriever=obj_retriever,
            llm=self.llm,
            system_prompt=(
                "You are an agent designed to answer queries over a set of research papers. "
                "Please always use the tools provided to answer a question. "
                "Do not rely on prior knowledge. Be thorough and provide detailed answers."
            ),
            verbose=True
        )
        self.agent = AgentRunner(agent_worker)

        return self.agent

    def create_router_engine(self, file_path: str):
        """
        Create a router query engine for a single document.

        Args:
            file_path: Path to PDF file

        Returns:
            RouterQueryEngine instance
        """
        return get_router_query_engine(file_path, llm=self.llm, embed_model=self.embed_model)

    def query(self, question: str) -> str:
        """
        Query the agent with a question.

        Args:
            question: The question to ask

        Returns:
            Response string
        """
        if self.agent is None:
            raise ValueError("Agent not initialized. Please create an agent first.")

        response = self.agent.query(question)
        return str(response)

    def chat(self, message: str) -> str:
        """
        Have a conversation with the agent.

        Args:
            message: The message to send

        Returns:
            Response string
        """
        if self.agent is None:
            raise ValueError("Agent not initialized. Please create an agent first.")

        response = self.agent.chat(message)
        return str(response)


# Convenience functions for quick setup
def create_rag_system(
    document_paths: List[str],
    api_key: Optional[str] = None,
    mode: str = "advanced"
) -> RAGBackend:
    """
    Quickly create a RAG system.

    Args:
        document_paths: List of PDF file paths
        api_key: Google API key (optional, uses env var if not provided)
        mode: Either "simple" or "advanced" (with tool retrieval)

    Returns:
        Configured RAGBackend instance
    """
    backend = RAGBackend(api_key=api_key)

    if mode == "advanced":
        backend.create_advanced_agent(document_paths)
    else:
        backend.create_simple_agent(document_paths)

    return backend


if __name__ == "__main__":
    # Example usage
    print("Initializing RAG Backend...")

    # Get available documents
    backend = RAGBackend()
    available_docs = backend.get_available_documents()

    print(f"\nAvailable documents: {len(available_docs)}")
    for doc in available_docs[:5]:  # Show first 5
        print(f"  - {doc}")

    # Example: Create agent with first 3 documents
    if len(available_docs) >= 3:
        print("\nCreating agent with first 3 documents...")
        doc_paths = available_docs[:3]
        backend.create_advanced_agent(doc_paths)

        # Test query
        print("\nTesting query...")
        response = backend.query("What are the main topics covered in these papers?")
        print(f"\nResponse: {response}")
    else:
        print("\nNot enough documents found for demo.")

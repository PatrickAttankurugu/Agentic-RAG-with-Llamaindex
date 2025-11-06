"""
Improved Streamlit Frontend - Industry Standard
Production-ready UI with proper error handling and monitoring
"""

import streamlit as st
import sys
from pathlib import Path
from typing import List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.settings import get_settings
from src.services.rag_service import RAGService
from src.models.schemas import QueryRequest, AgentState
from src.utils.logging import get_logger
from src.utils.validation import validate_query
from src.core.exceptions import RAGException

logger = get_logger(__name__)

# Page configuration
st.set_page_config(
    page_title="Agentic RAG v2.0 - Industry Standard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(120deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .metrics-card {
        padding: 1rem;
        border-radius: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin: 0.5rem 0;
    }
    .status-ready { color: #28a745; }
    .status-error { color: #dc3545; }
    .status-processing { color: #ffc107; }
    </style>
""", unsafe_allow_html=True)


# Initialize session state
if 'rag_service' not in st.session_state:
    st.session_state.rag_service = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'initialized' not in st.session_state:
    st.session_state.initialized = False


def initialize_service():
    """Initialize RAG service"""
    try:
        settings = get_settings()
        st.session_state.rag_service = RAGService(settings)
        return True
    except Exception as e:
        st.error(f"Failed to initialize service: {str(e)}")
        logger.error(f"Service initialization failed: {str(e)}")
        return False


def create_agent(file_paths: List[str], mode: str):
    """Create agent with documents"""
    try:
        with st.spinner(f"Creating {mode} agent with {len(file_paths)} documents..."):
            state = st.session_state.rag_service.create_agent(file_paths, mode)
            st.session_state.initialized = True
            st.success(f"✅ Agent created! Documents: {state.num_documents}, Chunks: {state.num_chunks}")
            return True
    except Exception as e:
        st.error(f"❌ Failed to create agent: {str(e)}")
        logger.error(f"Agent creation failed: {str(e)}")
        return False


def query_agent(query: str):
    """Query the agent"""
    try:
        # Validate query
        validated_query = validate_query(query)

        # Create query request
        query_request = QueryRequest(query=validated_query)

        # Execute query
        response = st.session_state.rag_service.query(query_request)

        return response
    except RAGException as e:
        st.error(f"Query failed: {e.message}")
        logger.error(f"Query failed: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        logger.error(f"Unexpected error: {str(e)}")
        return None


def main():
    """Main application"""

    # Header
    st.markdown('<p class="main-header">🚀 Agentic RAG v2.0 - Industry Standard</p>', unsafe_allow_html=True)
    st.markdown("**Production-Ready** | Persistent Storage | Caching | Monitoring | Testing")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Initialize service
        if st.session_state.rag_service is None:
            if st.button("🔧 Initialize Service", type="primary"):
                initialize_service()

        if st.session_state.rag_service:
            st.success("✅ Service Initialized")

            st.divider()

            # Document selection
            st.subheader("📚 Documents")
            available_docs = st.session_state.rag_service.get_available_documents()

            if not available_docs:
                st.warning("No PDFs found")
            else:
                st.write(f"Found {len(available_docs)} documents")

                selected_docs = st.multiselect(
                    "Select documents:",
                    options=available_docs,
                    default=available_docs[:3] if len(available_docs) >= 3 else available_docs
                )

                # Agent mode
                mode = st.radio(
                    "Agent Mode:",
                    options=["advanced", "simple"],
                    help="Advanced mode uses tool retrieval for better scalability"
                )

                if st.button("🚀 Create Agent", type="primary"):
                    if selected_docs:
                        create_agent(selected_docs, mode)
                    else:
                        st.error("Select at least one document")

            st.divider()

            # Metrics
            if st.session_state.initialized:
                st.subheader("📊 Metrics")

                cache_stats = st.session_state.rag_service.get_cache_stats()
                agent_state = st.session_state.rag_service.get_agent_state()

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Documents", agent_state.num_documents)
                    st.metric("Chunks", agent_state.num_chunks)
                with col2:
                    if 'hit_rate' in cache_stats:
                        st.metric("Cache Hit Rate", f"{cache_stats['hit_rate']:.2%}")
                    st.metric("Status", agent_state.status)

                if st.button("🔄 Clear Cache"):
                    st.session_state.rag_service.clear_cache()
                    st.success("Cache cleared")

    # Main content
    if not st.session_state.initialized:
        st.info("👈 Initialize the service and create an agent to get started!")

        # Features
        st.subheader("✨ New Industry-Standard Features")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            **🏗️ Architecture**
            - Modular design
            - Separation of concerns
            - Factory patterns
            - SOLID principles
            """)

        with col2:
            st.markdown("""
            **🔧 Infrastructure**
            - ChromaDB persistence
            - LRU caching
            - Structured logging
            - Error handling
            """)

        with col3:
            st.markdown("""
            **🧪 Quality**
            - Comprehensive tests
            - Type hints
            - Input validation
            - Metrics tracking
            """)

    else:
        # Chat interface
        st.subheader("💬 Chat Interface")

        # Display chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                if message["role"] == "assistant" and "latency" in message:
                    st.write(message["content"])
                    st.caption(f"⏱️ {message['latency']:.0f}ms")
                else:
                    st.write(message["content"])

        # Query input
        if query := st.chat_input("Ask a question..."):
            # Add user message
            st.session_state.chat_history.append({"role": "user", "content": query})

            with st.chat_message("user"):
                st.write(query)

            # Get response
            with st.chat_message("assistant"):
                with st.spinner("🤔 Thinking..."):
                    response = query_agent(query)

                    if response:
                        st.write(response.answer)
                        st.caption(f"⏱️ {response.latency_ms:.0f}ms")

                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": response.answer,
                            "latency": response.latency_ms
                        })

        # Quick actions
        st.divider()
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📝 Summarize Papers"):
                query = "Provide a comprehensive summary of all papers"
                st.session_state.chat_history.append({"role": "user", "content": query})
                st.rerun()

        with col2:
            if st.button("🔬 Compare Methods"):
                query = "Compare the methodologies across papers"
                st.session_state.chat_history.append({"role": "user", "content": query})
                st.rerun()

        with col3:
            if st.button("🗑️ Clear Chat"):
                st.session_state.chat_history = []
                st.rerun()


if __name__ == "__main__":
    main()

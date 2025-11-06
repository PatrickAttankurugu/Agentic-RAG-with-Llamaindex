"""
Agentic RAG with LlamaIndex - Streamlit Frontend
Multi-document intelligent research assistant powered by Gemini 2.5 Flash
"""

import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

# Import backend
from rag_backend import RAGBackend

# Page configuration
st.set_page_config(
    page_title="Agentic RAG Research Assistant",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    .doc-card {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)


# Initialize session state
if 'backend' not in st.session_state:
    st.session_state.backend = None
if 'agent_created' not in st.session_state:
    st.session_state.agent_created = False
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'selected_docs' not in st.session_state:
    st.session_state.selected_docs = []


def initialize_backend():
    """Initialize the RAG backend with API key."""
    api_key = os.getenv('GOOGLE_API_KEY')

    if not api_key:
        st.error("⚠️ Google API key not found! Please set GOOGLE_API_KEY in your .env file.")
        st.info("Get your API key from: https://makersuite.google.com/app/apikey")
        return None

    try:
        backend = RAGBackend(api_key=api_key)
        st.success("✅ Backend initialized successfully!")
        return backend
    except Exception as e:
        st.error(f"❌ Error initializing backend: {str(e)}")
        return None


def get_available_pdfs():
    """Get list of available PDF files."""
    pdf_files = list(Path(".").glob("*.pdf"))
    return sorted([pdf.name for pdf in pdf_files])


def create_agent(backend, selected_docs, mode):
    """Create the agent with selected documents."""
    try:
        with st.spinner(f"🔄 Creating {mode} agent with {len(selected_docs)} documents..."):
            if mode == "Advanced (Tool Retrieval)":
                backend.create_advanced_agent(selected_docs, top_k=3)
            else:
                backend.create_simple_agent(selected_docs)

            st.session_state.agent_created = True
            st.session_state.selected_docs = selected_docs
            st.success(f"✅ Agent created successfully with {len(selected_docs)} documents!")
            return True
    except Exception as e:
        st.error(f"❌ Error creating agent: {str(e)}")
        return False


def main():
    """Main application."""

    # Header
    st.markdown('<p class="main-header">🔍 Agentic RAG Research Assistant</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Powered by Gemini 2.5 Flash & LlamaIndex | Ask questions across multiple research papers</p>',
        unsafe_allow_html=True
    )

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")

        # API Key status
        api_key = os.getenv('GOOGLE_API_KEY')
        if api_key:
            st.success("🔑 API Key: Configured")
        else:
            st.error("🔑 API Key: Not Found")
            st.info("Set GOOGLE_API_KEY in .env file")

        st.divider()

        # Document selection
        st.subheader("📚 Document Selection")
        available_docs = get_available_pdfs()

        if not available_docs:
            st.warning("No PDF documents found in the current directory.")
            st.info("Add PDF files to get started!")
        else:
            st.write(f"Found {len(available_docs)} PDF documents")

            # Select documents
            selected_docs = st.multiselect(
                "Select documents to analyze:",
                options=available_docs,
                default=available_docs[:3] if len(available_docs) >= 3 else available_docs,
                help="Choose one or more documents for the agent to analyze"
            )

            # Agent mode
            st.subheader("🤖 Agent Mode")
            agent_mode = st.radio(
                "Select agent type:",
                options=["Advanced (Tool Retrieval)", "Simple"],
                help="Advanced mode is better for many documents (>5)"
            )

            st.divider()

            # Initialize/Reset button
            if st.button("🚀 Initialize Agent", type="primary", use_container_width=True):
                if not selected_docs:
                    st.error("Please select at least one document!")
                else:
                    # Initialize backend
                    st.session_state.backend = initialize_backend()

                    if st.session_state.backend:
                        # Create agent
                        create_agent(st.session_state.backend, selected_docs, agent_mode)

            if st.session_state.agent_created:
                if st.button("🔄 Reset Agent", use_container_width=True):
                    st.session_state.agent_created = False
                    st.session_state.backend = None
                    st.session_state.chat_history = []
                    st.rerun()

        st.divider()

        # Info
        st.subheader("ℹ️ About")
        st.write("""
        This application uses:
        - **LLM**: Gemini 2.5 Flash
        - **Embeddings**: BAAI/bge-small-en-v1.5
        - **Framework**: LlamaIndex

        Features:
        - Multi-document analysis
        - Intelligent routing
        - Source attribution
        - Tool retrieval for scalability
        """)

    # Main content area
    if not st.session_state.agent_created:
        # Welcome screen
        st.info("👈 Configure the agent in the sidebar to get started!")

        # Show available documents
        if available_docs:
            st.subheader("📄 Available Documents")
            cols = st.columns(3)
            for idx, doc in enumerate(available_docs):
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class="doc-card">
                        <strong>📄 {doc}</strong><br>
                        <small>{Path(doc).stat().st_size / 1024 / 1024:.2f} MB</small>
                    </div>
                    """, unsafe_allow_html=True)

        # Example queries
        st.subheader("💡 Example Queries")
        st.write("""
        Once initialized, try asking:
        - "Summarize the main findings across all papers"
        - "What evaluation datasets are used in these papers?"
        - "Compare the methodologies described in the papers"
        - "What are the key contributions of each paper?"
        - "Tell me about the experimental results"
        """)

    else:
        # Chat interface
        st.subheader(f"💬 Chat with {len(st.session_state.selected_docs)} Documents")

        # Display selected documents
        with st.expander("📚 Active Documents", expanded=False):
            for doc in st.session_state.selected_docs:
                st.write(f"• {doc}")

        # Chat history
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.write(message["content"])

        # Query input
        query = st.chat_input("Ask a question about your documents...")

        if query:
            # Add user message to chat
            st.session_state.chat_history.append({"role": "user", "content": query})

            # Display user message
            with st.chat_message("user"):
                st.write(query)

            # Get response
            with st.chat_message("assistant"):
                with st.spinner("🤔 Thinking..."):
                    try:
                        response = st.session_state.backend.query(query)
                        st.write(response)
                        st.session_state.chat_history.append({"role": "assistant", "content": response})
                    except Exception as e:
                        error_msg = f"❌ Error: {str(e)}"
                        st.error(error_msg)
                        st.session_state.chat_history.append({"role": "assistant", "content": error_msg})

        # Quick action buttons
        st.divider()
        st.subheader("🎯 Quick Actions")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📝 Summarize All Papers", use_container_width=True):
                query = "Provide a comprehensive summary of all the papers, highlighting the main contributions of each."
                st.session_state.chat_history.append({"role": "user", "content": query})
                with st.spinner("🤔 Thinking..."):
                    try:
                        response = st.session_state.backend.query(query)
                        st.session_state.chat_history.append({"role": "assistant", "content": response})
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

        with col2:
            if st.button("🔬 Compare Methodologies", use_container_width=True):
                query = "Compare and contrast the methodologies and approaches used across all papers."
                st.session_state.chat_history.append({"role": "user", "content": query})
                with st.spinner("🤔 Thinking..."):
                    try:
                        response = st.session_state.backend.query(query)
                        st.session_state.chat_history.append({"role": "assistant", "content": response})
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

        with col3:
            if st.button("📊 Key Results", use_container_width=True):
                query = "What are the key experimental results and findings from each paper?"
                st.session_state.chat_history.append({"role": "user", "content": query})
                with st.spinner("🤔 Thinking..."):
                    try:
                        response = st.session_state.backend.query(query)
                        st.session_state.chat_history.append({"role": "assistant", "content": response})
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

        # Clear chat button
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()


if __name__ == "__main__":
    main()

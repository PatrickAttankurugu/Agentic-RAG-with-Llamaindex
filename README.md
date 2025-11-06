# Agentic RAG with LlamaIndex

## Overview
Welcome to the Agentic RAG with LlamaIndex project! This is a production-ready application for building advanced research agents using the Agentic RAG (Retrieval-Augmented Generation) framework, powered by LlamaIndex and Google's Gemini 2.5 Flash.

**🎯 Key Highlights:**
- 🤖 Powered by **Gemini 2.5 Flash** (open-source friendly)
- 🔍 **HuggingFace embeddings** (completely open-source)
- 🎨 Beautiful **Streamlit** web interface
- 📚 Multi-document analysis with intelligent routing
- ⚡ Advanced tool retrieval for scalability
- 🔄 End-to-end working application

## What is Agentic RAG?
Agentic RAG is an innovative approach that combines the strengths of retrieval-based systems and generative models. This implementation enables intelligent agents that can:
- 📖 Retrieve relevant information from multiple research papers
- 💬 Generate coherent and contextually appropriate responses
- 🧠 Perform complex reasoning across documents
- 🎯 Intelligently route queries to appropriate tools

### Key Features
1. **Multi-Document Analysis**: Query across multiple research papers simultaneously
2. **Intelligent Routing**: Automatically chooses between summarization and detailed retrieval
3. **Tool Retrieval**: Scales efficiently with many documents (10+)
4. **Source Attribution**: Tracks which documents provide information
5. **Interactive UI**: User-friendly Streamlit interface
6. **Open Source**: Uses Gemini API and HuggingFace embeddings (no OpenAI required)

## Tech Stack

- **LLM**: Google Gemini 2.5 Flash (via API)
- **Embeddings**: BAAI/bge-small-en-v1.5 (HuggingFace)
- **Framework**: LlamaIndex 0.10.27
- **Frontend**: Streamlit 1.31.0
- **Language**: Python 3.9+

## Repository Structure

```
.
├── app.py                          # Streamlit frontend application
├── rag_backend.py                  # Core RAG backend logic
├── utils.py                        # Utility functions for document processing
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variable template
├── Multi-Document_Agent.ipynb      # Tutorial notebook
├── Router_Engine.ipynb             # Router tutorial notebook
└── *.pdf                           # Research papers
```

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/PatrickAttankurugu/Agentic-RAG-with-LlamaIndex.git
cd Agentic-RAG-with-LlamaIndex
```

### 2. Install Dependencies

```bash
# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Google API key
# Get your free API key from: https://makersuite.google.com/app/apikey
```

Your `.env` file should look like:
```
GOOGLE_API_KEY=your_actual_google_api_key_here
```

### 4. Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## Usage Guide

### Using the Web Interface

1. **Initialize the Agent**:
   - Select PDF documents from the sidebar
   - Choose agent mode (Advanced for 5+ documents, Simple for fewer)
   - Click "🚀 Initialize Agent"

2. **Ask Questions**:
   - Type your question in the chat input
   - Use quick action buttons for common queries
   - View responses with source attribution

3. **Example Queries**:
   - "Summarize the main findings across all papers"
   - "What evaluation datasets are used in these papers?"
   - "Compare the methodologies described in the papers"
   - "What are the key contributions of each paper?"

### Using the Backend Programmatically

```python
from rag_backend import RAGBackend

# Initialize backend
backend = RAGBackend()

# Create agent with documents
documents = ["metagpt.pdf", "longlora.pdf", "selfrag.pdf"]
backend.create_advanced_agent(documents)

# Query the agent
response = backend.query("What are the main contributions of these papers?")
print(response)
```

## Advanced Features

### Simple Agent Mode
- Best for: 3-5 documents
- Loads all tools upfront
- Faster initialization
- Direct tool access

### Advanced Agent Mode
- Best for: 5+ documents
- Uses tool retrieval
- Scales to many documents
- Intelligent tool selection

### Router Engine
For single-document analysis with automatic routing between summary and vector search:

```python
from rag_backend import RAGBackend

backend = RAGBackend()
router = backend.create_router_engine("metagpt.pdf")
response = router.query("What is the main contribution?")
```

## Jupyter Notebooks

Explore the learning materials:

```bash
jupyter notebook Multi-Document_Agent.ipynb
jupyter notebook Router_Engine.ipynb
```

## Configuration

### Customizing the LLM

Edit `rag_backend.py` to adjust LLM parameters:

```python
self.llm = Gemini(
    model="models/gemini-2.0-flash-exp",
    api_key=self.api_key,
    temperature=0.1  # Adjust for creativity vs consistency
)
```

### Customizing Embeddings

Change the embedding model in `rag_backend.py`:

```python
self.embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5"  # Or try other models
)
```

## Troubleshooting

### API Key Issues
- Ensure your `.env` file is in the project root
- Verify your Google API key is valid
- Check you haven't exceeded API quotas

### Installation Issues
- Use Python 3.9 or higher
- Try `pip install --upgrade pip` before installing requirements
- On Mac/Linux, you may need to install system dependencies for sentence-transformers

### Memory Issues
- For large PDFs, reduce chunk_size in Settings
- Use Advanced mode for many documents
- Process fewer documents at once

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Open a Pull Request

## License

This project is based on the DeepLearning.AI course materials and extended with additional features.

## Contact

For questions or inquiries, please email: [patricka.azuma@gmail.com]

## Acknowledgments

- DeepLearning.AI for the original course materials
- LlamaIndex team for the excellent framework
- Google for the Gemini API
- HuggingFace for open-source embeddings

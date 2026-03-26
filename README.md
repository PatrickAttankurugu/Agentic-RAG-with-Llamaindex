# Agentic RAG with LlamaIndex

[![CI](https://github.com/PatrickAttankurugu/Agentic-RAG-with-LlamaIndex/actions/workflows/ci.yml/badge.svg)](https://github.com/PatrickAttankurugu/Agentic-RAG-with-LlamaIndex/actions/workflows/ci.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A production-ready application for building advanced research agents using Agentic RAG (Retrieval-Augmented Generation), powered by LlamaIndex and Google Gemini 2.5 Flash.

## Key Highlights

- Gemini 2.5 Flash (free API key) + HuggingFace embeddings (open-source)
- Streamlit web interface and FastAPI REST API
- Multi-document analysis with intelligent routing
- Persistent storage with ChromaDB
- LRU caching, retry logic, circuit breaker patterns
- 111 unit tests, CI/CD with GitHub Actions

## What is Agentic RAG?

Agentic RAG combines retrieval-based systems with generative models and autonomous agents. This implementation enables agents that can:

- Retrieve relevant information from multiple research papers
- Generate coherent and contextually appropriate responses
- Perform complex reasoning across documents
- Intelligently route queries to appropriate tools

## Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | Google Gemini 2.5 Flash (via API) |
| Embeddings | BAAI/bge-small-en-v1.5 (HuggingFace) |
| Framework | LlamaIndex 0.10.27 |
| Frontend | Streamlit 1.31.0 |
| API | FastAPI |
| Vector Store | ChromaDB (persistent) |
| Language | Python 3.9+ |

## Repository Structure

```
.
├── app.py                          # Application entry point (Streamlit)
├── src/
│   ├── api/
│   │   ├── app_v2.py               # Streamlit frontend
│   │   └── fastapi_app.py          # FastAPI REST API
│   ├── core/
│   │   ├── document_processor.py   # Document loading and chunking
│   │   ├── exceptions.py           # Custom exception hierarchy
│   │   └── vector_store.py         # Vector store factory
│   ├── models/
│   │   └── schemas.py              # Pydantic data models
│   ├── services/
│   │   └── rag_service.py          # Main business logic
│   └── utils/                      # Cache, retry, logging, metrics, validation
├── config/
│   └── settings.py                 # Pydantic configuration management
├── tests/                          # Unit and integration tests
├── legacy/                         # Original v1 code (reference)
├── docs/                           # Architecture and development docs
├── Multi-Document_Agent.ipynb      # Tutorial notebook
└── Router_Engine.ipynb             # Router tutorial notebook
```

## Quick Start

### 1. Clone and Install

```bash
git clone https://github.com/PatrickAttankurugu/Agentic-RAG-with-LlamaIndex.git
cd Agentic-RAG-with-LlamaIndex

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -e .
# Or for development: pip install -e ".[dev]"
```

### 2. Set Up Environment Variables

```bash
cp .env.example .env
# Edit .env and add your Google API key
# Get your free key from: https://makersuite.google.com/app/apikey
```

### 3. Run the Application

```bash
# Streamlit UI
make run
# or: streamlit run app.py

# FastAPI REST API
make run-api
# or: uvicorn src.api.fastapi_app:app --reload
```

The Streamlit app opens at `http://localhost:8501`, the API at `http://localhost:8000/docs`.

## Usage

### Streamlit Interface

1. Click "Initialize Service" in the sidebar
2. Select PDF documents and choose agent mode (Advanced for 5+ docs, Simple for fewer)
3. Click "Create Agent" and start asking questions

### FastAPI Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/documents` | List available documents |
| POST | `/api/v1/agent` | Create agent from documents |
| POST | `/api/v1/query` | Query the agent |
| GET | `/api/v1/status` | Agent state and metrics |
| DELETE | `/api/v1/cache` | Clear query cache |

### Programmatic Usage

```python
from src.services.rag_service import RAGService
from src.models.schemas import QueryRequest

service = RAGService()
service.create_agent(["metagpt.pdf", "selfrag.pdf"], mode="advanced")

response = service.query(QueryRequest(query="Compare the methodologies"))
print(response.answer)
```

## Agent Modes

**Simple Mode** (3-5 documents): Loads all tools upfront for faster direct access.

**Advanced Mode** (5+ documents): Uses tool retrieval to scale efficiently with many documents.

## Configuration

All settings are managed via environment variables or `config/settings.py`:

```bash
# LLM
LLM_PROVIDER=gemini           # gemini, openai, anthropic
LLM_TEMPERATURE=0.1

# Chunking
CHUNKING_CHUNK_SIZE=1024
CHUNKING_CHUNK_OVERLAP=200

# Vector Store
VECTORSTORE_TYPE=chroma        # chroma, memory

# Cache
CACHE_ENABLED=true
CACHE_TTL=3600
```

## Development

```bash
# Install dev dependencies
make install-dev

# Run tests
make test

# Run with coverage
make test-cov

# Lint and format
make lint
make format
```

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for the full development guide.

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture documentation including design patterns, data flow, and extension points.

## Docker

```bash
docker compose up --build
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Quick start for contributors:
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Install dev dependencies: `make install-dev`
4. Make your changes and add tests
5. Run `make test` and `make lint`
6. Open a Pull Request

## License

MIT License. See [LICENSE](LICENSE) for details.

## Contact

For questions or inquiries: patricka.azuma@gmail.com

## Acknowledgments

- DeepLearning.AI for the original course materials
- LlamaIndex team for the excellent framework
- Google for the Gemini API
- HuggingFace for open-source embeddings

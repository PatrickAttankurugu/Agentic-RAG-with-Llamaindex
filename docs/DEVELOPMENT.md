# Development Guide

## Prerequisites

- Python 3.9+
- Git

## Setup

```bash
# Clone the repository
git clone https://github.com/PatrickAttankurugu/Agentic-RAG-with-LlamaIndex.git
cd Agentic-RAG-with-LlamaIndex

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dev dependencies
make install-dev
# Or manually:
pip install -e ".[dev]"
pre-commit install

# Set up environment variables
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

## Project Structure

```
.
├── app.py                      # Streamlit launcher (entry point)
├── src/
│   ├── api/
│   │   ├── app_v2.py           # Streamlit frontend (v2)
│   │   └── fastapi_app.py      # FastAPI REST API
│   ├── core/
│   │   ├── document_processor.py
│   │   ├── exceptions.py       # Custom exception hierarchy
│   │   └── vector_store.py     # Vector store with factory pattern
│   ├── models/
│   │   └── schemas.py          # Pydantic data models
│   ├── services/
│   │   └── rag_service.py      # Main business logic
│   └── utils/
│       ├── cache.py            # LRU cache with TTL
│       ├── logging.py          # Structured logging
│       ├── metrics.py          # Metrics collection
│       ├── retry.py            # Retry logic and circuit breaker
│       └── validation.py       # Input validation
├── config/
│   └── settings.py             # Pydantic configuration management
├── tests/
│   ├── unit/                   # Unit tests
│   └── integration/            # Integration tests
├── legacy/                     # Legacy v1 code (preserved for reference)
└── docs/                       # Documentation
```

## Running the Application

```bash
# Streamlit UI
make run
# or: streamlit run app.py

# FastAPI REST API
make run-api
# or: uvicorn src.api.fastapi_app:app --reload
```

## Running Tests

```bash
# All tests
make test

# With coverage
make test-cov

# Specific test file
pytest tests/unit/test_schemas.py -v
```

## Code Quality

```bash
# Lint
make lint

# Auto-format
make format
```

## Adding a New LLM Provider

1. Add the provider to `config/settings.py` `LLMConfig.provider` literal
2. Create the provider initialization in `src/core/llm_factory.py`
3. Add the provider's package to `pyproject.toml` optional dependencies
4. Add tests in `tests/unit/test_llm_factory.py`

## Adding a New Document Format

1. Add the extension to `config/settings.py` supported extensions
2. LlamaIndex's `SimpleDirectoryReader` handles most formats automatically
3. For custom formats, extend `src/core/document_processor.py`
4. Add tests with a fixture file in `tests/fixtures/`

## Architecture Overview

The system follows a layered architecture:

```
API Layer (Streamlit / FastAPI)
    ↓
Service Layer (RAGService)
    ↓
Core Layer (DocumentProcessor, VectorStore, Exceptions)
    ↓
Utilities (Cache, Retry, Logging, Metrics, Validation)
    ↓
Configuration (Pydantic Settings)
```

Key design patterns:
- **Factory Pattern**: Vector store creation
- **Singleton Pattern**: Settings, metrics collector
- **Strategy Pattern**: Agent mode selection (simple vs advanced)
- **Circuit Breaker**: Resilience for external API calls

# Contributing to Agentic RAG with LlamaIndex

Thanks for your interest in contributing! This document explains how to get started.

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git
- A Google API key (free from [Google AI Studio](https://makersuite.google.com/app/apikey))

### Getting Started

```bash
# Fork and clone
git clone https://github.com/<your-username>/Agentic-RAG-with-LlamaIndex.git
cd Agentic-RAG-with-LlamaIndex

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install with dev dependencies
pip install -e ".[dev]"

# Set up pre-commit hooks
pre-commit install

# Copy environment template
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# Download sample data
python scripts/download_sample_data.py
```

### Running the App

```bash
# Streamlit UI
streamlit run app.py

# Run tests
pytest

# Run linter
ruff check src/ tests/

# Run type checker
mypy src/
```

## How to Contribute

### Reporting Bugs

Use the [Bug Report](https://github.com/PatrickAttankurugu/Agentic-RAG-with-LlamaIndex/issues/new?template=bug_report.md) template. Include:

- Steps to reproduce
- Expected vs actual behavior
- Python version and OS
- Error messages / tracebacks

### Suggesting Features

Use the [Feature Request](https://github.com/PatrickAttankurugu/Agentic-RAG-with-LlamaIndex/issues/new?template=feature_request.md) template.

### Submitting Code

1. **Check existing issues** -- look for `good first issue` or `help wanted` labels
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Write your code** following the coding standards below
4. **Add tests** for any new functionality
5. **Run the full check suite**:
   ```bash
   ruff check src/ tests/
   mypy src/
   pytest
   ```
6. **Commit** with a clear message:
   ```bash
   git commit -m "feat: add support for Markdown documents"
   ```
7. **Push and open a PR** against `main`

## Coding Standards

### Style

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Use type hints for all function signatures
- Formatting and linting are enforced by `ruff` via pre-commit hooks

### Architecture

The project uses a layered architecture:

```
src/api/          # Frontend / API layer (Streamlit, FastAPI)
src/services/     # Business logic (RAGService)
src/core/         # Core infrastructure (document processing, vector store, exceptions)
src/models/       # Pydantic data models
src/utils/        # Cross-cutting utilities (cache, logging, retry, validation)
config/           # Configuration management
tests/            # Unit and integration tests
```

When adding new functionality:

- Put business logic in `src/services/`
- Put data models in `src/models/schemas.py`
- Put infrastructure in `src/core/`
- Add custom exceptions to `src/core/exceptions.py`
- Add tests in `tests/unit/` or `tests/integration/`

### Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` -- new feature
- `fix:` -- bug fix
- `docs:` -- documentation only
- `test:` -- adding or updating tests
- `refactor:` -- code change that neither fixes a bug nor adds a feature
- `chore:` -- build process, dependencies, or tooling

### Tests

- All new features must include tests
- Aim for 60%+ coverage on new code
- Use `pytest` with fixtures defined in `tests/conftest.py`
- Unit tests go in `tests/unit/`, integration tests in `tests/integration/`

## Project Structure

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for a detailed architecture overview.

## Questions?

Open a [Discussion](https://github.com/PatrickAttankurugu/Agentic-RAG-with-LlamaIndex/discussions) or email patricka.azuma@gmail.com.

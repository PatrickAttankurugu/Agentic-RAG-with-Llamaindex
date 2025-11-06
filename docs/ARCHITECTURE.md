# Architecture Documentation

## Overview

This is a production-ready, industry-standard implementation of an Agentic RAG (Retrieval-Augmented Generation) system using LlamaIndex and Google Gemini.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Streamlit)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Chat UI      │  │  Metrics     │  │ Config Panel │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Services Layer                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    RAG Service                            │  │
│  │  - Agent orchestration                                    │  │
│  │  - Query processing                                       │  │
│  │  - Response generation                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Core Layer                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Document    │  │   Vector     │  │    Agent     │         │
│  │  Processor   │  │   Store      │  │   Manager    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Infrastructure Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Logging    │  │    Cache     │  │   Metrics    │         │
│  │  (Loguru)    │  │    (LRU)     │  │  (Custom)    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Retry      │  │  Validation  │  │    Config    │         │
│  │  (Exp B/O)   │  │   (Input)    │  │  (Pydantic)  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      External Services                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │    Gemini    │  │   ChromaDB   │  │ HuggingFace  │         │
│  │     LLM      │  │ Vector Store │  │  Embeddings  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. Configuration Management (`config/settings.py`)
- **Purpose**: Centralized configuration using Pydantic
- **Features**:
  - Environment-based settings
  - Validation with Pydantic
  - Type safety
  - Nested configurations for each component
- **Best Practice**: Single source of truth for all configuration

### 2. Core Components (`src/core/`)

#### Document Processor
- **File**: `document_processor.py`
- **Responsibilities**:
  - Load PDF documents
  - Parse and chunk documents
  - Extract metadata
  - Compute document statistics

#### Vector Store Manager
- **File**: `vector_store.py`
- **Responsibilities**:
  - Persistent vector storage (ChromaDB)
  - Index creation and loading
  - Vector similarity search
  - Factory pattern for multiple backends

#### Exception Hierarchy
- **File**: `exceptions.py`
- **Features**:
  - Custom exception types
  - Error context preservation
  - Structured error information

### 3. Services Layer (`src/services/`)

#### RAG Service
- **File**: `rag_service.py`
- **Responsibilities**:
  - High-level RAG orchestration
  - Agent creation and management
  - Query processing with retry logic
  - Cache integration
  - State management

### 4. Utilities (`src/utils/`)

#### Logging
- **File**: `logging.py`
- **Features**:
  - Structured JSON logging
  - Multiple output handlers
  - Context managers
  - Function decorators

#### Caching
- **File**: `cache.py`
- **Features**:
  - LRU cache with TTL
  - Query result caching
  - Cache statistics
  - Automatic eviction

#### Retry Logic
- **File**: `retry.py`
- **Features**:
  - Exponential backoff
  - Circuit breaker pattern
  - Specialized retry strategies
  - Timeout handling

#### Validation
- **File**: `validation.py`
- **Features**:
  - Input sanitization
  - SQL injection prevention
  - Length validation

#### Metrics
- **File**: `metrics.py`
- **Features**:
  - Query latency tracking
  - Success/error rates
  - Cache hit rates
  - Percentile calculations

### 5. Data Models (`src/models/`)

#### Schemas
- **File**: `schemas.py`
- **Models**:
  - Document & DocumentMetadata
  - QueryRequest & QueryResponse
  - AgentState
  - EvaluationMetrics
  - SystemMetrics
  - CacheEntry
  - HealthCheck

## Design Patterns

### 1. Factory Pattern
- Used in `VectorStoreFactory` to create appropriate vector store implementations
- Allows easy switching between ChromaDB, FAISS, or in-memory stores

### 2. Singleton Pattern
- Used in `LoggerManager` and settings management
- Ensures single instance of global resources

### 3. Strategy Pattern
- Used for different agent modes (simple vs advanced)
- Different retrieval strategies

### 4. Repository Pattern
- Vector store abstraction
- Document storage abstraction

### 5. Decorator Pattern
- Retry decorators
- Caching decorators
- Logging decorators

## Data Flow

### Document Ingestion
```
PDF File → DocumentProcessor → Chunks → Embeddings → VectorStore
```

### Query Processing
```
User Query → Validation → Cache Check → Agent → Tools → LLM → Response
                                ↓
                          Cache Store
```

## Industry Best Practices Implemented

### 1. Configuration Management
- Pydantic settings with validation
- Environment-specific configs
- Type safety
- Nested configurations

### 2. Error Handling
- Custom exception hierarchy
- Retry logic with exponential backoff
- Circuit breaker pattern
- Graceful degradation

### 3. Logging & Observability
- Structured JSON logging
- Context managers
- Metrics collection
- Performance tracking

### 4. Caching
- LRU cache with TTL
- Query result caching
- Cache statistics

### 5. Testing
- Unit tests
- Integration tests
- Test fixtures
- Pytest configuration

### 6. Security
- Input validation
- SQL injection prevention
- API key protection

### 7. Performance
- Vector store persistence
- Query caching
- Lazy loading
- Batch processing

### 8. Data Validation
- Pydantic models
- Type hints
- Input sanitization

### 9. Monitoring
- Metrics collection
- Latency tracking
- Error rates
- Cache hit rates

### 10. Deployment
- Docker support
- Docker Compose
- Health checks
- Environment variables

## Comparison: Old vs New Implementation

| Feature | Old Implementation | New Implementation |
|---------|-------------------|-------------------|
| Architecture | Monolithic | Modular, layered |
| Configuration | Hard-coded | Pydantic settings |
| Error Handling | Basic try-catch | Exception hierarchy + retry |
| Logging | Print statements | Structured JSON logging |
| Caching | None | LRU cache with TTL |
| Testing | None | Comprehensive test suite |
| Vector Store | Memory only | Persistent ChromaDB |
| Validation | None | Pydantic + custom |
| Monitoring | None | Metrics + tracking |
| Documentation | Basic | Comprehensive |
| Type Safety | Partial | Full type hints |
| Deployment | Manual | Docker + compose |

## Performance Improvements

1. **Persistent Storage**: No need to reprocess documents on restart
2. **Query Caching**: Instant responses for repeated queries
3. **Retry Logic**: Resilient to transient failures
4. **Lazy Loading**: Components loaded on demand
5. **Batch Processing**: Efficient embedding generation

## Scalability

The architecture supports scaling through:

1. **Horizontal Scaling**: Multiple instances with shared ChromaDB
2. **Caching**: Reduces LLM calls
3. **Tool Retrieval**: Efficient for many documents
4. **Async Operations**: Non-blocking I/O

## Security Considerations

1. **Input Validation**: All user inputs validated
2. **SQL Injection**: Protection against dangerous patterns
3. **API Keys**: Environment variables only
4. **Rate Limiting**: Configurable limits
5. **Error Messages**: No sensitive data in errors

## Future Enhancements

1. **OpenTelemetry**: Distributed tracing
2. **Prometheus**: Metrics export
3. **RAG Evaluation**: Automated quality metrics
4. **A/B Testing**: Experiment framework
5. **Multi-tenancy**: User isolation
6. **Reranking**: Improved retrieval quality
7. **HyDE**: Hypothetical document embeddings
8. **Query Routing**: Intelligent query classification

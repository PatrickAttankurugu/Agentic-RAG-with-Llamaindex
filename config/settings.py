"""
Configuration Management using Pydantic Settings
Industry-standard approach for managing application configuration
"""

from typing import Optional, List, Literal
from pydantic import Field, field_validator, ConfigDict
from pydantic_settings import BaseSettings
from pathlib import Path


class LLMConfig(BaseSettings):
    """LLM Configuration"""

    model_config = ConfigDict(env_prefix='LLM_')

    provider: Literal["gemini", "openai", "anthropic"] = "gemini"
    model_name: str = "models/gemini-2.0-flash-exp"
    temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, ge=1)
    timeout: int = Field(default=60, ge=1)
    max_retries: int = Field(default=3, ge=0)


class EmbeddingConfig(BaseSettings):
    """Embedding Model Configuration"""

    model_config = ConfigDict(env_prefix='EMBEDDING_')

    provider: Literal["huggingface", "openai"] = "huggingface"
    model_name: str = "BAAI/bge-small-en-v1.5"
    batch_size: int = Field(default=32, ge=1)
    max_length: int = Field(default=512, ge=1)


class VectorStoreConfig(BaseSettings):
    """Vector Store Configuration"""

    model_config = ConfigDict(env_prefix='VECTORSTORE_')

    type: Literal["chroma", "faiss", "memory"] = "chroma"
    persist_directory: str = "./data/vector_store"
    collection_name: str = "documents"
    distance_metric: Literal["cosine", "l2", "ip"] = "cosine"


class ChunkingConfig(BaseSettings):
    """Document Chunking Configuration"""

    model_config = ConfigDict(env_prefix='CHUNKING_')

    chunk_size: int = Field(default=1024, ge=128)
    chunk_overlap: int = Field(default=200, ge=0)

    @field_validator('chunk_overlap')
    @classmethod
    def validate_overlap(cls, v: int, info) -> int:
        chunk_size = info.data.get('chunk_size', 1024)
        if v >= chunk_size:
            raise ValueError(f"chunk_overlap ({v}) must be less than chunk_size ({chunk_size})")
        return v


class RetrievalConfig(BaseSettings):
    """Retrieval Configuration"""

    model_config = ConfigDict(env_prefix='RETRIEVAL_')

    similarity_top_k: int = Field(default=3, ge=1)
    rerank: bool = False
    rerank_top_n: int = Field(default=10, ge=1)
    use_hyde: bool = False  # Hypothetical Document Embeddings


class AgentConfig(BaseSettings):
    """Agent Configuration"""

    model_config = ConfigDict(env_prefix='AGENT_')

    mode: Literal["simple", "advanced"] = "advanced"
    max_iterations: int = Field(default=10, ge=1)
    verbose: bool = True
    system_prompt: str = (
        "You are an expert research assistant designed to answer questions "
        "using retrieval-augmented generation. Always cite your sources and "
        "provide detailed, accurate answers based on the provided context."
    )


class CacheConfig(BaseSettings):
    """Caching Configuration"""

    model_config = ConfigDict(env_prefix='CACHE_')

    enabled: bool = True
    ttl: int = Field(default=3600, ge=0)  # Time to live in seconds
    max_size: int = Field(default=1000, ge=1)  # Max number of cached items


class LoggingConfig(BaseSettings):
    """Logging Configuration"""

    model_config = ConfigDict(env_prefix='LOG_')

    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    format: Literal["json", "text"] = "json"
    output_file: Optional[str] = "./logs/app.log"
    rotation: str = "500 MB"
    retention: str = "10 days"


class SecurityConfig(BaseSettings):
    """Security Configuration"""

    model_config = ConfigDict(env_prefix='SECURITY_')

    rate_limit_enabled: bool = True
    rate_limit_requests: int = Field(default=100, ge=1)
    rate_limit_period: int = Field(default=60, ge=1)  # seconds
    input_validation: bool = True
    max_input_length: int = Field(default=10000, ge=1)


class MonitoringConfig(BaseSettings):
    """Monitoring and Observability Configuration"""

    model_config = ConfigDict(env_prefix='MONITORING_')

    enabled: bool = True
    tracing_enabled: bool = True
    metrics_enabled: bool = True
    export_prometheus: bool = False
    prometheus_port: int = Field(default=9090, ge=1024, le=65535)


class Settings(BaseSettings):
    """Main Application Settings"""

    model_config = ConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )

    # API Keys
    google_api_key: str = Field(alias="GOOGLE_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    cohere_api_key: Optional[str] = Field(default=None, alias="COHERE_API_KEY")

    # Application
    app_name: str = "Agentic RAG"
    app_version: str = "2.0.0"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = False

    # Directories
    data_dir: Path = Path("./data")
    docs_dir: Path = Path(".")
    cache_dir: Path = Path("./data/cache")
    logs_dir: Path = Path("./logs")

    # Component Configs
    llm: LLMConfig = Field(default_factory=LLMConfig)
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    vector_store: VectorStoreConfig = Field(default_factory=VectorStoreConfig)
    chunking: ChunkingConfig = Field(default_factory=ChunkingConfig)
    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig)
    agent: AgentConfig = Field(default_factory=AgentConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._create_directories()

    def _create_directories(self):
        """Create necessary directories if they don't exist"""
        for directory in [self.data_dir, self.cache_dir, self.logs_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    @field_validator('google_api_key')
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        if not v or v == "your_google_api_key_here":
            raise ValueError(
                "GOOGLE_API_KEY must be set. Get your key from: "
                "https://makersuite.google.com/app/apikey"
            )
        return v

    class Config:
        validate_assignment = True


# Singleton instance
_settings: Optional[Settings] = None


def get_settings(reload: bool = False) -> Settings:
    """
    Get application settings (singleton pattern)

    Args:
        reload: Force reload settings from environment

    Returns:
        Settings instance
    """
    global _settings

    if _settings is None or reload:
        _settings = Settings()

    return _settings


# Convenience function for testing
def get_test_settings(**overrides) -> Settings:
    """
    Get settings for testing with overrides

    Args:
        **overrides: Settings to override

    Returns:
        Settings instance with overrides
    """
    return Settings(
        google_api_key=overrides.get('google_api_key', 'test_key'),
        environment='development',
        debug=True,
        **overrides
    )

"""Integration tests for RAG service"""

import pytest
from pathlib import Path
from config.settings import get_test_settings
from src.services.rag_service import RAGService
from src.models.schemas import QueryRequest


@pytest.fixture
def rag_service():
    """Create RAG service for testing"""
    settings = get_test_settings()
    return RAGService(settings)


@pytest.mark.skipif(
    not Path("metagpt.pdf").exists(),
    reason="Test document not available"
)
class TestRAGService:
    """Test RAG service integration"""

    def test_service_initialization(self, rag_service):
        """Test service initializes correctly"""
        assert rag_service is not None
        assert rag_service.llm is not None
        assert rag_service.embed_model is not None

    def test_get_available_documents(self, rag_service):
        """Test getting available documents"""
        docs = rag_service.get_available_documents()
        assert isinstance(docs, list)

    def test_cache_stats(self, rag_service):
        """Test cache statistics"""
        stats = rag_service.get_cache_stats()
        assert isinstance(stats, dict)

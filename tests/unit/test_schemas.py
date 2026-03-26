"""Unit tests for Pydantic schemas."""

import time
import pytest
from datetime import datetime

from src.models.schemas import (
    QueryRequest,
    QueryResponse,
    RetrievedChunk,
    AgentState,
    DocumentMetadata,
    CacheEntry,
)


class TestQueryRequest:
    def test_valid_query(self):
        req = QueryRequest(query="What is RAG?")
        assert req.query == "What is RAG?"

    def test_empty_query_rejected(self):
        with pytest.raises(Exception):
            QueryRequest(query="")

    def test_whitespace_only_not_empty(self):
        # min_length counts whitespace characters
        req = QueryRequest(query=" ")
        assert req.query == " "


class TestRetrievedChunk:
    def test_defaults(self):
        chunk = RetrievedChunk(text="hello")
        assert chunk.source == ""
        assert chunk.score == 0.0
        assert chunk.metadata == {}

    def test_full_construction(self):
        chunk = RetrievedChunk(
            text="content", source="paper.pdf", score=0.95, metadata={"page": 1}
        )
        assert chunk.score == 0.95
        assert chunk.metadata["page"] == 1


class TestQueryResponse:
    def test_minimal_construction(self):
        resp = QueryResponse(query="q", answer="a")
        assert resp.retrieved_chunks == []
        assert resp.sources == []
        assert resp.latency_ms == 0.0
        assert resp.metadata == {}

    def test_full_construction(self):
        resp = QueryResponse(
            query="q",
            answer="a",
            retrieved_chunks=[RetrievedChunk(text="t")],
            sources=["doc.pdf"],
            latency_ms=123.4,
            metadata={"model": "gemini"},
        )
        assert len(resp.retrieved_chunks) == 1
        assert resp.latency_ms == 123.4

    def test_serialization_roundtrip(self):
        resp = QueryResponse(query="q", answer="a", latency_ms=50.0)
        data = resp.model_dump()
        restored = QueryResponse(**data)
        assert restored.query == resp.query
        assert restored.latency_ms == resp.latency_ms


class TestAgentState:
    def test_defaults(self):
        state = AgentState()
        assert state.status == "initializing"
        assert state.num_documents == 0
        assert state.num_chunks == 0
        assert state.mode == "advanced"
        assert state.last_query_at is None

    def test_explicit_values(self):
        now = datetime.utcnow()
        state = AgentState(
            status="ready",
            num_documents=3,
            num_chunks=150,
            mode="simple",
            last_query_at=now,
        )
        assert state.status == "ready"
        assert state.last_query_at == now

    def test_mutable_update(self):
        state = AgentState()
        state.status = "processing"
        state.num_documents = 5
        assert state.status == "processing"


class TestDocumentMetadata:
    def test_construction(self):
        meta = DocumentMetadata(
            file_name="test.pdf",
            file_path="/tmp/test.pdf",
            file_size=2048,
            file_type=".pdf",
            num_pages=10,
        )
        assert meta.file_name == "test.pdf"
        assert meta.num_chunks is None

    def test_num_chunks_mutable(self):
        meta = DocumentMetadata(
            file_name="a.pdf",
            file_path="/a.pdf",
            file_size=100,
            file_type=".pdf",
        )
        meta.num_chunks = 42
        assert meta.num_chunks == 42


class TestCacheEntry:
    def test_construction_defaults(self):
        entry = CacheEntry(key="k", value="v", ttl=3600)
        assert entry.access_count == 0
        assert isinstance(entry.created_at, datetime)
        assert isinstance(entry.accessed_at, datetime)

    def test_not_expired(self):
        entry = CacheEntry(key="k", value="v", ttl=3600)
        assert not entry.is_expired()

    def test_expired(self):
        entry = CacheEntry(key="k", value="v", ttl=0)
        # TTL of 0 means it expires immediately
        time.sleep(0.01)
        assert entry.is_expired()

    def test_serialization(self):
        entry = CacheEntry(key="k", value={"nested": True}, ttl=60)
        data = entry.model_dump()
        assert data["key"] == "k"
        assert data["value"] == {"nested": True}

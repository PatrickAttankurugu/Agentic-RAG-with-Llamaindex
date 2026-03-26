"""
FastAPI REST API for the Agentic RAG system.

Run with: uvicorn src.api.fastapi_app:app --reload
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel, Field

from config.settings import get_settings
from src.core.exceptions import (
    AgentNotInitializedError,
    DocumentError,
    QueryError,
    RAGException,
)
from src.models.schemas import AgentState, QueryRequest, QueryResponse
from src.services.rag_service import RAGService
from src.utils.logging import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="Agentic RAG API",
    description="REST API for multi-document Agentic RAG powered by LlamaIndex",
    version="2.0.0",
)

# ---------------------------------------------------------------------------
# Service singleton
# ---------------------------------------------------------------------------
_service: Optional[RAGService] = None


def _get_service() -> RAGService:
    global _service
    if _service is None:
        _service = RAGService(get_settings())
    return _service


# ---------------------------------------------------------------------------
# Request / response models specific to the API
# ---------------------------------------------------------------------------

class CreateAgentRequest(BaseModel):
    file_names: List[str] = Field(..., description="PDF file names to load")
    mode: str = Field(default="advanced", description="Agent mode: simple or advanced")


class CreateAgentResponse(BaseModel):
    status: str
    num_documents: int
    num_chunks: int
    mode: str


class HealthResponse(BaseModel):
    status: str
    version: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/v1/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok", version="2.0.0")


@app.get("/api/v1/documents", response_model=List[str])
async def list_documents():
    """List available PDF documents."""
    service = _get_service()
    return service.get_available_documents()


@app.post("/api/v1/agent", response_model=CreateAgentResponse)
async def create_agent(request: CreateAgentRequest):
    """Create a RAG agent from the specified documents."""
    service = _get_service()
    try:
        state: AgentState = service.create_agent(request.file_names, request.mode)
        return CreateAgentResponse(
            status=state.status,
            num_documents=state.num_documents,
            num_chunks=state.num_chunks,
            mode=state.mode,
        )
    except DocumentError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RAGException as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/v1/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Query the RAG agent."""
    service = _get_service()
    try:
        return service.query(request)
    except AgentNotInitializedError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except QueryError as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/v1/status")
async def status():
    """Return agent state and cache metrics."""
    service = _get_service()
    return {
        "agent": service.get_agent_state().model_dump(),
        "cache": service.get_cache_stats(),
    }


@app.delete("/api/v1/cache")
async def clear_cache():
    """Clear the query cache."""
    service = _get_service()
    service.clear_cache()
    return {"status": "cache cleared"}

"""Offline Host Agentic RAG foundation.

Lite implementation of agentic_rag_functional_specification patterns
without Chroma, commercial LightRAG, live web, or 65k production ingest.
"""

from app.rag.service import AgenticRagService, get_rag_service

__all__ = ["AgenticRagService", "get_rag_service"]

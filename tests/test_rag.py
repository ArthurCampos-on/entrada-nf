"""tests/test_rag.py — Testes do pipeline RAG."""

import pytest
from unittest.mock import MagicMock, patch

from src.rag.pipeline import DocumentChunk, RAGPipeline
from src.utils.config import RAGConfig


@pytest.fixture
def rag_config(tmp_path):
    return RAGConfig(
        enabled=True,
        vector_store_path=str(tmp_path / "embeddings"),
        documents_path=str(tmp_path / "docs"),
        collection_name="test_collection",
        chunk_size=100,
        chunk_overlap=10,
        top_k=3,
    )


def test_chunk_text_basic(rag_config):
    rag = RAGPipeline(rag_config)
    text = "a" * 250
    chunks = rag._chunk_text(text, {"source": "test"})
    assert len(chunks) > 1
    assert all(isinstance(c, DocumentChunk) for c in chunks)
    assert all(len(c.text) <= rag_config.chunk_size for c in chunks)


def test_chunk_overlap(rag_config):
    rag = RAGPipeline(rag_config)
    text = "palavra " * 100
    chunks = rag._chunk_text(text, {"source": "test"})
    # Com overlap, chunks consecutivos devem ter conteúdo comum
    assert len(chunks) >= 2


def test_document_chunk_id_deterministic(rag_config):
    c1 = DocumentChunk("mesmo texto", {"source": "a"})
    c2 = DocumentChunk("mesmo texto", {"source": "b"})
    assert c1.id == c2.id  # ID baseado no conteúdo


def test_ingest_empty_directory(rag_config, tmp_path):
    """Ingestão em pasta vazia deve retornar 0 sem erros."""
    (tmp_path / "docs").mkdir()
    with patch.object(RAGPipeline, "setup", return_value=None):
        rag = RAGPipeline(rag_config)
        rag._collection = MagicMock()
        count = rag.ingest_directory()
    assert count == 0

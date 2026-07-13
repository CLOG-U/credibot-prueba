"""Ingesta de documentos RAG hacia Supabase o caché local."""
import hashlib
import json
from pathlib import Path
from typing import Any

from app.core.config import settings

DOCUMENTS_DIR = Path(__file__).parent / "documents"
CACHE_FILE = Path(__file__).parent / ".chunk_cache.json"


def _stable_chunk_id(source: str, index: int, content: str) -> str:
    digest = hashlib.sha256(f"{source}:{index}:{content}".encode()).hexdigest()
    return digest[:32]


def chunk_documents() -> list[dict[str, Any]]:
    """Trocea documentos markdown en fragmentos estables."""
    chunks: list[dict[str, Any]] = []
    for doc_path in sorted(DOCUMENTS_DIR.glob("*.md")):
        content = doc_path.read_text(encoding="utf-8")
        sections = [s.strip() for s in content.split("\n## ") if s.strip()]
        for i, section in enumerate(sections):
            if i > 0:
                section = "## " + section
            title = section.split("\n")[0].replace("#", "").strip()
            chunks.append(
                {
                    "id": _stable_chunk_id(doc_path.name, i, section),
                    "content": section,
                    "source": doc_path.name,
                    "title": title,
                    "metadata": {"section_index": i},
                }
            )
    return chunks


def _pseudo_embedding(text: str, dims: int = 64) -> list[float]:
    """Embedding determinista para entornos sin OpenAI."""
    vec = [0.0] * dims
    tokens = text.lower().split()
    for token in tokens:
        h = int(hashlib.md5(token.encode()).hexdigest(), 16)
        vec[h % dims] += 1.0
    norm = sum(v * v for v in vec) ** 0.5 or 1.0
    return [round(v / norm, 6) for v in vec]


def generate_embedding(text: str) -> list[float]:
    """Genera embedding con OpenAI o fallback pseudo."""
    if settings.openai_api_key and settings.llm_provider == "openai":
        try:
            from openai import OpenAI

            client = OpenAI(api_key=settings.openai_api_key, timeout=30)
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text[:8000],
            )
            return response.data[0].embedding
        except Exception:
            pass
    return _pseudo_embedding(text)


def save_local_cache(chunks: list[dict[str, Any]]) -> None:
    """Guarda chunks con embeddings en caché local."""
    CACHE_FILE.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")


def load_local_cache() -> list[dict[str, Any]]:
    """Carga caché local si existe."""
    if not CACHE_FILE.exists():
        return []
    return json.loads(CACHE_FILE.read_text(encoding="utf-8"))


def ingest_all(persist_remote: bool = False) -> int:
    """Ingesta documentos y genera embeddings."""
    chunks = chunk_documents()
    enriched = []
    for chunk in chunks:
        enriched.append({**chunk, "embedding": generate_embedding(chunk["content"])})

    save_local_cache(enriched)

    if persist_remote and settings.supabase_url and settings.openai_api_key:
        try:
            from app.repositories.supabase_client import get_supabase_client

            client = get_supabase_client()
            for chunk in enriched:
                embedding = chunk.get("embedding", [])
                if len(embedding) != 1536:
                    embedding = generate_embedding(chunk["content"])
                doc_lookup = (
                    client.table("rag_documents")
                    .select("id")
                    .eq("source_path", chunk["source"])
                    .limit(1)
                    .execute()
                )
                if doc_lookup.data:
                    doc_id = doc_lookup.data[0]["id"]
                else:
                    doc_id = (
                        client.table("rag_documents")
                        .insert({"title": chunk["title"], "source_path": chunk["source"]})
                        .execute()
                        .data[0]["id"]
                    )
                client.table("rag_chunks").delete().eq("document_id", doc_id).eq(
                    "metadata->>chunk_key", chunk["id"]
                ).execute()
                client.table("rag_chunks").insert(
                    {
                        "document_id": doc_id,
                        "content": chunk["content"],
                        "metadata": {**chunk["metadata"], "chunk_key": chunk["id"]},
                        "embedding": embedding,
                    }
                ).execute()
        except Exception:
            pass

    return len(enriched)

"""End-to-end ingestion: file → chunks → embeddings → DB."""
import json
from pathlib import Path
from typing import List, Tuple
from loguru import logger

from src.ingestion.loaders import load_document
from src.ingestion.chunking import build_chunks
from src.ingestion.embedding import embed_texts
from src.models.schemas import DocumentMetadata
from src.utils.db import get_connection


def ingest_document(file_path: Path, metadata: DocumentMetadata) -> int:
    logger.info(f"Ingesting {file_path.name} (v{metadata.version})")
    text = load_document(file_path)
    if not text.strip():
        logger.warning(f"Empty document: {file_path}")
        return 0

    chunks = build_chunks(text, metadata)
    contents = [c["content"] for c in chunks]
    embeddings = embed_texts(contents)

    conn = get_connection()
    cur = conn.cursor()
    for chunk, emb in zip(chunks, embeddings):
        cur.execute(
            """
            INSERT INTO documents (content, embedding, metadata)
            VALUES (%s, %s::vector, %s::jsonb)
            """,
            (
                chunk["content"],
                emb,
                json.dumps(chunk["metadata"]),
            ),
        )
    conn.commit()
    cur.close()
    conn.close()
    logger.success(f"Ingested {len(chunks)} chunks from {file_path.name}")
    return len(chunks)


def ingest_batch(items: List[Tuple[Path, DocumentMetadata]]) -> int:
    total = 0
    for path, meta in items:
        total += ingest_document(path, meta)
    return total
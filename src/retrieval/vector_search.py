"""Pre-filtered vector search using pgvector."""
from typing import List, Dict, Any
from src.ingestion.embedding import embed_query
from src.models.schemas import Chunk, DocumentMetadata
from src.utils.db import get_connection


SQL_TEMPLATE = """
SELECT
    id,
    content,
    metadata,
    1 - (embedding <=> %s::vector) AS similarity
FROM documents
WHERE
    metadata->>'access_level' = ANY(%s)
    AND metadata->>'product' = ANY(%s)
    AND metadata->>'region' = ANY(%s)
    AND (metadata->>'effective_date')::date <= %s
    AND (
        metadata->>'expiry_date' IS NULL
        OR metadata->>'expiry_date' = ''
        OR (metadata->>'expiry_date')::date > %s
    )
ORDER BY embedding <=> %s::vector
LIMIT %s;
"""


def search(
    query: str,
    filters: Dict[str, Any],
    top_k: int = 20,
    similarity_threshold: float = 0.7,
) -> List[Chunk]:
    qvec = embed_query(query)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        SQL_TEMPLATE,
        (
            qvec,
            filters["access_level"],
            filters["product"],
            filters["region"],
            filters["effective_before"],
            filters["expiry_after"],
            qvec,
            top_k,
        ),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    chunks: List[Chunk] = []
    for row_id, content, meta, sim in rows:
        if sim < similarity_threshold:
            continue
        chunks.append(
            Chunk(
                id=row_id,
                content=content,
                metadata=DocumentMetadata(**meta),
                similarity=sim,
            )
        )
    return chunks
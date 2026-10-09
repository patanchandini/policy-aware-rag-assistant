"""Semantic chunking that preserves metadata on every chunk."""
from typing import List
import tiktoken
from src.models.schemas import DocumentMetadata


ENCODER = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    return len(ENCODER.encode(text))


def chunk_text(text: str, max_tokens: int = 400, overlap: int = 50) -> List[str]:
    tokens = ENCODER.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + max_tokens, len(tokens))
        chunks.append(ENCODER.decode(tokens[start:end]))
        if end == len(tokens):
            break
        start = end - overlap
    return chunks


def build_chunks(text: str, metadata: DocumentMetadata) -> List[dict]:
    pieces = chunk_text(text)
    return [
        {"content": piece, "metadata": metadata.model_dump(mode="json")}
        for piece in pieces
    ]
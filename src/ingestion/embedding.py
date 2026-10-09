"""Embedding generation via Google Gemini."""
from typing import List
from google import genai
from tenacity import retry, stop_after_attempt, wait_exponential
from config.settings import get_settings

settings = get_settings()
client = genai.Client(api_key=settings.gemini_api_key)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def embed_texts(texts: List[str]) -> List[List[float]]:
    """Embed a list of texts into 768-dim vectors."""
    result = client.models.embed_content(
        model=settings.gemini_embedding_model,
        contents=texts,
        config={"output_dimensionality": 768},
    )
    return [emb.values for emb in result.embeddings]


def embed_query(query: str) -> List[float]:
    """Embed a single query string."""
    return embed_texts([query])[0]
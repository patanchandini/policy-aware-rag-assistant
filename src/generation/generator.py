"""Call Gemini LLM with strict grounding rules."""
from typing import List
from google import genai
from config.settings import get_settings
from src.models.schemas import Chunk
from src.generation.prompts import SYSTEM_PROMPT, USER_TEMPLATE
from src.security.sanitizer import wrap_context

settings = get_settings()
client = genai.Client(api_key=settings.gemini_api_key)


def generate_answer(query: str, chunks: List[Chunk]) -> str:
    context = wrap_context(chunks)
    prompt = f"{SYSTEM_PROMPT}\n\n{USER_TEMPLATE.format(context=context, query=query)}"
    response = client.models.generate_content(
        model=settings.gemini_llm_model,
        contents=prompt,
    )
    return response.text.strip()
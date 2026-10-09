"""Detect semantic conflicts across retrieved chunks (same product/region)."""
from collections import defaultdict
from typing import List, Dict
from google import genai
from src.models.schemas import Chunk
from config.settings import get_settings

settings = get_settings()
client = genai.Client(api_key=settings.gemini_api_key)


def _scope_key(chunk: Chunk) -> str:
    m = chunk.metadata
    return f"{m.product}|{m.region}|{m.source_type}"


def group_by_scope(chunks: List[Chunk]) -> Dict[str, List[Chunk]]:
    groups = defaultdict(list)
    for c in chunks:
        groups[_scope_key(c)].append(c)
    return groups


CONTRADICTION_PROMPT = """You are a strict contradiction detector.
Given two text excerpts, answer ONLY 'YES' or 'NO':
Do they make contradicting factual claims on the same topic?

Excerpt A:
{a}

Excerpt B:
{b}

Answer:"""


def are_contradictory(a: str, b: str) -> bool:
    prompt = CONTRADICTION_PROMPT.format(a=a, b=b)
    response = client.models.generate_content(
        model=settings.gemini_llm_model,
        contents=prompt,
    )
    text = response.text.strip().upper()
    return text.startswith("YES")


def detect_conflicts(chunks: List[Chunk]) -> List[List[Chunk]]:
    """Return groups of mutually conflicting chunks."""
    conflicts = []
    for scope, group in group_by_scope(chunks).items():
        if len(group) < 2:
            continue
        conflicting = []
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                if are_contradictory(group[i].content, group[j].content):
                    if group[i] not in conflicting:
                        conflicting.append(group[i])
                    if group[j] not in conflicting:
                        conflicting.append(group[j])
        if conflicting:
            conflicts.append(conflicting)
    return conflicts
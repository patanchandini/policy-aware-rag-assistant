"""Refusal gates and citation validation."""
import re
from typing import List, Tuple
from src.models.schemas import Chunk, Citation


CITATION_RE = re.compile(r"\[Source:\s*([^\]]+)\]")


def extract_citations(answer: str) -> List[str]:
    return [m.strip() for m in CITATION_RE.findall(answer)]


def validate_citations(answer: str, chunks: List[Chunk]) -> Tuple[bool, List[str]]:
    cited = extract_citations(answer)
    valid = {c.metadata.citation_label for c in chunks}
    bad = [c for c in cited if c not in valid]
    return (len(bad) == 0 and len(cited) > 0), bad


def map_citations(cited: List[str], chunks: List[Chunk]) -> List[Citation]:
    by_label = {c.metadata.citation_label: c for c in chunks}
    out = []
    for label in cited:
        c = by_label.get(label)
        if c:
            out.append(Citation(
                citation_label=label,
                doc_id=c.metadata.doc_id,
                version=c.metadata.version,
                effective_date=c.metadata.effective_date,
            ))
    return out


def should_refuse(answer: str, chunks: List[Chunk]) -> Tuple[bool, str | None]:
    if not chunks:
        return True, "no_evidence"
    if answer.startswith("NO_ANSWER"):
        reason = answer.split(":", 1)[-1].strip() if ":" in answer else "insufficient_evidence"
        return True, reason
    ok, bad = validate_citations(answer, chunks)
    if not ok:
        return True, "citation_invalid"
    return False, None
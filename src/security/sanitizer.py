"""Prompt-injection detection & neutralization for retrieved content."""
import re
from loguru import logger
from src.utils.db import get_connection


INJECTION_PATTERNS = [
    r"ignore (all )?(previous|prior|above) instructions",
    r"disregard (the )?(system|previous) prompt",
    r"you are now",
    r"new instructions?:",
    r"system prompt",
    r"reveal your (prompt|instructions)",
    r"print your (prompt|instructions)",
]


def contains_injection(text: str) -> bool:
    low = text.lower()
    return any(re.search(p, low) for p in INJECTION_PATTERNS)


def log_security_event(event_type: str, doc_id, details: dict):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO security_events (event_type, doc_id, details) VALUES (%s, %s, %s)",
        (event_type, doc_id, details),
    )
    conn.commit()
    cur.close()
    conn.close()


def sanitize_chunks(chunks):
    """Wrap each chunk in <document> tags; neutralize injection attempts."""
    safe = []
    for c in chunks:
        if contains_injection(c.content):
            logger.warning(f"Injection pattern in {c.metadata.doc_id}")
            log_security_event("injection_attempt", c.id, {"snippet": c.content[:200]})
            c.content = "[SUSPICIOUS CONTENT REMOVED]"
        safe.append(c)
    return safe


def wrap_context(chunks) -> str:
    return "\n\n".join(
        f"<document id='{c.metadata.doc_id}' version='{c.metadata.version}'>\n"
        f"{c.content}\n</document>"
        for c in chunks
    )
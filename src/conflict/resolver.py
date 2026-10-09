"""Resolve conflict by selecting the latest applicable policy."""
from typing import List, Optional
from loguru import logger
from src.models.schemas import Chunk


class AmbiguousConflictError(Exception):
    pass


def _version_key(version: str):
    """Turn '2.10' or 'v2.10' into comparable tuple."""
    cleaned = version.lower().lstrip("v")
    parts = []
    for p in cleaned.split("."):
        try:
            parts.append(int(p))
        except ValueError:
            parts.append(0)
    return tuple(parts)


def resolve_conflict(conflicting: List[Chunk]) -> Chunk:
    """
    Pick the latest applicable policy.
    Priority: effective_date DESC, then version DESC.
    If tie on effective_date with no supersedes link → ambiguity.
    """
    ordered = sorted(
        conflicting,
        key=lambda c: (c.metadata.effective_date, _version_key(c.metadata.version)),
        reverse=True,
    )
    winner = ordered[0]

    if len(ordered) > 1:
        second = ordered[1]
        same_date = second.metadata.effective_date == winner.metadata.effective_date
        explicit = second.metadata.doc_id in winner.metadata.supersedes
        if same_date and not explicit:
            logger.warning(
                f"Ambiguous conflict: {winner.metadata.doc_id} vs {second.metadata.doc_id}"
            )
            raise AmbiguousConflictError(
                f"Two policies effective on {winner.metadata.effective_date} "
                f"have conflicting content and no supersedes link."
            )
    return winner


def resolve_all(conflicts: List[List[Chunk]]) -> List[Chunk]:
    """Return winning chunks for each conflict group."""
    winners = []
    for group in conflicts:
        winners.append(resolve_conflict(group))
    return winners
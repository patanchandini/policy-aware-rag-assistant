"""The full RAG orchestration — the single entry point used by the API."""
from loguru import logger

from src.models.schemas import (
    QueryRequest, QueryResponse, UserContext,
)
from src.retrieval.query_analysis import parse_query
from src.retrieval.filters import build_filters
from src.retrieval.vector_search import search
from src.conflict.detector import detect_conflicts
from src.conflict.resolver import resolve_all, AmbiguousConflictError
from src.security.access_control import validate_user_scope
from src.security.sanitizer import sanitize_chunks
from src.generation.generator import generate_answer
from src.generation.refusal import (
    should_refuse, extract_citations, map_citations,
)
from config.settings import get_settings

settings = get_settings()


def run_rag(request: QueryRequest) -> QueryResponse:
    user = validate_user_scope(request.user_context)

    parsed = parse_query(request.query, request.historical_date)
    filters = build_filters(parsed, user)

    chunks = search(
        query=parsed.raw_query,
        filters=filters,
        top_k=settings.top_k,
        similarity_threshold=settings.similarity_threshold,
    )

    if not chunks:
        return QueryResponse(
            answer="I don't have enough information to answer that.",
            refused=True,
            refusal_reason="no_evidence",
        )

    chunks = sanitize_chunks(chunks)

    conflicts = detect_conflicts(chunks)
    if conflicts:
        try:
            winners = resolve_all(conflicts)
        except AmbiguousConflictError as e:
            logger.warning(f"Ambiguity: {e}")
            return QueryResponse(
                answer="I found conflicting information that cannot be resolved.",
                refused=True,
                clarification_needed=True,
                clarification_question=str(e),
            )
        winner_ids = {c.id for c in winners}
        conflicting_ids = {c.id for grp in conflicts for c in grp}
        chunks = [c for c in chunks if c.id not in conflicting_ids] + winners

    answer = generate_answer(request.query, chunks)

    refused, reason = should_refuse(answer, chunks)
    if refused:
        return QueryResponse(
            answer="I don't have enough information to answer that.",
            refused=True,
            refusal_reason=reason,
        )

    cites = map_citations(extract_citations(answer), chunks)
    return QueryResponse(answer=answer, citations=cites)
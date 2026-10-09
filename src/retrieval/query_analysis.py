"""Classify query as current or historical; extract temporal/product scope."""
import re
from datetime import date, datetime
from dateutil import parser as dateparser
from typing import Optional

from src.models.schemas import ParsedQuery, QueryType


HISTORICAL_MARKERS = [
    r"\bas of\b", r"\bon \d{4}-\d{2}-\d{2}\b",
    r"\bin (january|february|march|april|may|june|july|august|september|october|november|december)",
    r"\b(before|after|prior to|back in)\b",
    r"\b(19|20)\d{2}\b",
]


def extract_date(text: str) -> Optional[date]:
    """Try to extract a date from the query."""
    # ISO format
    iso = re.search(r"\d{4}-\d{2}-\d{2}", text)
    if iso:
        return datetime.strptime(iso.group(), "%Y-%m-%d").date()
    # Natural language
    try:
        # Only attempt on a short snippet around temporal markers
        return dateparser.parse(text, fuzzy=True).date()
    except (ValueError, OverflowError):
        return None


def parse_query(raw_query: str, historical_date: Optional[date] = None) -> ParsedQuery:
    q_lower = raw_query.lower()

    is_historical = any(re.search(p, q_lower) for p in HISTORICAL_MARKERS)
    target_date = historical_date or extract_date(raw_query)

    if is_historical and target_date:
        return ParsedQuery(
            raw_query=raw_query,
            query_type=QueryType.HISTORICAL,
            target_date=target_date,
        )

    return ParsedQuery(
        raw_query=raw_query,
        query_type=QueryType.CURRENT,
    )
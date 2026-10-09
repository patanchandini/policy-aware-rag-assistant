"""Build SQL metadata filters enforcing access + temporal scope."""
from datetime import date
from typing import Dict, Any
from src.models.schemas import ParsedQuery, QueryType, UserContext


def build_filters(
    parsed: ParsedQuery,
    user: UserContext,
) -> Dict[str, Any]:
    today = date.today()

    filters: Dict[str, Any] = {
        "access_level": [a.value for a in user.access_levels],
        "product": user.authorized_products,
        "region": user.authorized_regions,
    }

    if parsed.query_type == QueryType.CURRENT:
        filters["effective_before"] = today
        filters["expiry_after"] = today
    else:  # HISTORICAL
        filters["effective_before"] = parsed.target_date
        filters["expiry_after"] = parsed.target_date

    return filters
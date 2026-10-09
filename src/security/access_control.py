"""Server-side access control. Never trust client-supplied scope."""
from src.models.schemas import UserContext, AccessLevel


def validate_user_scope(user: UserContext) -> UserContext:
    """Sanitize and validate user context. Extend with real auth here."""
    if not user.access_levels:
        user.access_levels = [AccessLevel.PUBLIC]
    if not user.authorized_products:
        raise ValueError("User has no authorized products")
    if not user.authorized_regions:
        raise ValueError("User has no authorized regions")
    return user
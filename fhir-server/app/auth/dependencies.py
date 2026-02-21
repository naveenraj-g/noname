from typing import Any

from fastapi import Cookie, Depends, HTTPException, status
from keycloak.exceptions import KeycloakAuthenticationError

from app.core.config import settings
from app.core.keycloak import decode_token, get_keycloak_public_key, keycloak_openid
from app.core.logging import get_logger
from app.core.redis import redis_client
from app.core.session import SessionManager

logger = get_logger(__name__)


def get_session_manager() -> SessionManager:
    """Dependency to get a SessionManager backed by the app's Redis client."""
    return SessionManager(redis_client)


async def get_current_user(
    session_manager: SessionManager = Depends(get_session_manager),
    session_id: str | None = Cookie(None, alias=settings.SESSION_COOKIE_NAME),
) -> dict[str, Any]:
    """FastAPI dependency that extracts and validates the current user from the session.

    Flow:
    1. Read session_id from cookie
    2. Look up session data in Redis
    3. Decode & validate the access token
    4. If the access token is expired, attempt a transparent refresh using the refresh token
    5. Return user info dict

    Raises HTTPException 401 on any failure.
    """
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated — no session cookie found",
        )

    session_data = await session_manager.get_session(session_id)
    if session_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid — please log in again",
        )

    public_key = await get_keycloak_public_key()
    access_token = session_data["access_token"]

    try:
        decoded = decode_token(access_token, public_key)
        return decoded
    except KeycloakAuthenticationError:
        # Access token might be expired — try refreshing
        logger.info("Access token expired for session %s, attempting refresh", session_id[:8])

    # Attempt transparent token refresh
    refresh_token = session_data.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired and no refresh token available",
        )

    try:
        new_tokens = keycloak_openid.refresh_token(refresh_token)
        new_decoded = decode_token(new_tokens["access_token"], public_key)

        # Update the session with new tokens
        await session_manager.update_session(session_id, new_decoded, new_tokens)
        logger.info("Transparently refreshed tokens for session %s", session_id[:8])
        return new_decoded

    except Exception as e:
        logger.warning("Token refresh failed for session %s: %s", session_id[:8], str(e))
        # Clean up the stale session
        await session_manager.delete_session(session_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired — please log in again",
        )


async def get_current_user_optional(
    session_manager: SessionManager = Depends(get_session_manager),
    session_id: str | None = Cookie(None, alias=settings.SESSION_COOKIE_NAME),
) -> dict[str, Any] | None:
    """Same as get_current_user but returns None instead of raising on failure.

    Useful for endpoints that optionally use auth info.
    """
    if not session_id:
        return None

    try:
        return await get_current_user(
            session_manager=session_manager,
            session_id=session_id,
        )
    except HTTPException:
        return None

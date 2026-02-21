from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from pydantic import BaseModel

from app.auth.dependencies import get_current_user, get_session_manager
from app.core.config import settings
from app.core.keycloak import decode_token, get_keycloak_public_key, keycloak_openid
from app.core.logging import get_logger
from app.core.session import SessionManager

logger = get_logger(__name__)

router = APIRouter()


# ── Request / Response Schemas ────────────────────────────────────────────


class LoginRequest(BaseModel):
    username: str
    password: str


class UserInfo(BaseModel):
    sub: str | None = None
    username: str | None = None
    email: str | None = None
    name: str | None = None
    realm_roles: list[str] = []


class AuthResponse(BaseModel):
    message: str
    user: UserInfo | None = None


def _build_user_info(token_data: dict) -> UserInfo:
    """Extract a clean UserInfo from decoded token payload."""
    return UserInfo(
        sub=token_data.get("sub"),
        username=token_data.get("preferred_username"),
        email=token_data.get("email"),
        name=token_data.get("name"),
        realm_roles=token_data.get("realm_access", {}).get("roles", []),
    )


# ── Endpoints ─────────────────────────────────────────────────────────────


@router.post("/login", response_model=AuthResponse)
async def login(
    body: LoginRequest,
    response: Response,
    session_manager: SessionManager = Depends(get_session_manager),
):
    """Authenticate with Keycloak and create a server-side session.

    Exchanges username/password for Keycloak tokens, stores them in Redis,
    and sets a session cookie on the response.
    """
    try:
        tokens = keycloak_openid.token(
            username=body.username,
            password=body.password,
            grant_type="password",
        )
    except Exception as e:
        logger.warning("Login failed for user '%s': %s", body.username, str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    # Decode the access token to get user info
    public_key = await get_keycloak_public_key()
    try:
        user_info = decode_token(tokens["access_token"], public_key)
    except Exception as e:
        logger.error("Failed to decode token after successful login: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication succeeded but token validation failed",
        )

    # Create a server-side session
    session_id = await session_manager.create_session(user_info, tokens)

    # Set session cookie (httponly for security)
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=session_id,
        httponly=True,
        samesite="lax",
        secure=settings.ENVIRONMENT != "development",
        max_age=settings.SESSION_TTL_SECONDS,
        path="/",
    )

    logger.info("User '%s' logged in successfully", body.username)
    return AuthResponse(message="Login successful", user=_build_user_info(user_info))


@router.post("/logout", response_model=AuthResponse)
async def logout(
    response: Response,
    session_manager: SessionManager = Depends(get_session_manager),
    session_id: str | None = Cookie(None, alias=settings.SESSION_COOKIE_NAME),
):
    """Logout: delete the server-side session from Redis and clear the cookie."""
    if session_id:
        await session_manager.delete_session(session_id)

    response.delete_cookie(
        key=settings.SESSION_COOKIE_NAME,
        path="/",
        httponly=True,
        samesite="lax",
    )

    logger.info("Logout completed")
    return AuthResponse(message="Logged out successfully")


@router.post("/refresh", response_model=AuthResponse)
async def refresh_tokens(
    response: Response,
    session_manager: SessionManager = Depends(get_session_manager),
    session_id: str | None = Cookie(None, alias=settings.SESSION_COOKIE_NAME),
):
    """Explicitly refresh the Keycloak tokens and extend the session."""
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No session — please log in first",
        )

    session_data = await session_manager.get_session(session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired — please log in again",
        )

    refresh_token = session_data.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh token available",
        )

    try:
        new_tokens = keycloak_openid.refresh_token(refresh_token)
    except Exception as e:
        logger.warning("Explicit refresh failed: %s", str(e))
        await session_manager.delete_session(session_id)
        response.delete_cookie(key=settings.SESSION_COOKIE_NAME, path="/")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh failed — please log in again",
        )

    public_key = await get_keycloak_public_key()
    new_user_info = decode_token(new_tokens["access_token"], public_key)
    await session_manager.update_session(session_id, new_user_info, new_tokens)

    # Reset cookie TTL
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=session_id,
        httponly=True,
        samesite="lax",
        secure=settings.ENVIRONMENT != "development",
        max_age=settings.SESSION_TTL_SECONDS,
        path="/",
    )

    return AuthResponse(message="Session refreshed successfully", user=_build_user_info(new_user_info))


@router.get("/me", response_model=AuthResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Return the current authenticated user's info."""
    return AuthResponse(message="Authenticated", user=_build_user_info(current_user))

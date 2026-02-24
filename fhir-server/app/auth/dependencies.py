from fastapi import HTTPException, status, Request
from jwt import PyJWKClient
import jwt
from app.core.config import settings

JWKS_URL = f"{settings.KEYCLOAK_URL}/realms/{settings.KEYCLOAK_REALM_NAME}/protocol/openid-connect/certs"

jwks_client = PyJWKClient(JWKS_URL)


def decode_token(token: str):
    signing_key = jwks_client.get_signing_key_from_jwt(token)

    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        # audience=settings.KEYCLOAK_CLIENT_ID,
        issuer=f"{settings.KEYCLOAK_URL}/realms/{settings.KEYCLOAK_REALM_NAME}",
        options={"verify_aud": False},
    )


def get_current_principal(request: Request):
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
        )

    token = auth_header.split(" ")[1]

    try:
        payload = decode_token(token)
        if "preferred_username" in payload:
            payload["principal_type"] = "user"
        else:
            payload["principal_type"] = "service"

        # store in request state
        request.state.user = payload
        # return payload
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

from fastapi import HTTPException, status, Request, Depends
from jwt import PyJWKClient
import jwt
from app.core.config import settings
import requests

KEYCLOAK_TOKEN_URL = (
    f"{settings.KEYCLOAK_URL}/realms/"
    f"{settings.KEYCLOAK_REALM_NAME}/protocol/openid-connect/token"
)

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

        payload["principal_type"] = (
            "user" if "preferred_username" in payload else "service"
        )

        # store in request state
        request.state.user = payload
        request.state.token = token

        return payload
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


# Permission
#   Resource = Patient
#   Scope = read
def check_permission(token: str, resource: str, scope: str):
    response = requests.post(
        KEYCLOAK_TOKEN_URL,
        data={
            "grant_type": "urn:ietf:params:oauth:grant-type:uma-ticket",
            "audience": settings.KEYCLOAK_CLIENT_ID,
            "permission": f"{resource}#{scope}",
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )


def require_permission(resource: str, scope: str):
    def dependency(request: Request):
        token = request.state.token
        check_permission(token, resource, scope)

    return dependency

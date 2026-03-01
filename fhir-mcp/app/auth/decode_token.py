from jwt import PyJWKClient
import jwt
from app.core.config import settings

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
        issuer=f"{settings.KEYCLOAK_URL}/realms/{settings.KEYCLOAK_REALM_NAME}",
        options={"verify_aud": False},
    )

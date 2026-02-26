import httpx
import uvicorn
from contextlib import asynccontextmanager
from contextvars import ContextVar

from fastapi import FastAPI
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.config import settings

# ---------------------------------------------------------------------------
# 1. ContextVar for per-request auth token (concurrency-safe)
# ---------------------------------------------------------------------------
current_token: ContextVar[str | None] = ContextVar("current_token", default=None)


class BearerAuth(httpx.Auth):
    """Injects the Authorization header from the current request context."""

    def auth_flow(self, request: httpx.Request):
        token = current_token.get()
        if token:
            request.headers["Authorization"] = token
        yield request


# ---------------------------------------------------------------------------
# 2. httpx client pointed at the FHIR backend
# ---------------------------------------------------------------------------
client = httpx.AsyncClient(
    base_url=settings.HTTP_CLIENT,
    auth=BearerAuth(),
)

# ---------------------------------------------------------------------------
# 3. Load the OpenAPI spec and build the FastMCP server
# ---------------------------------------------------------------------------
openapi_spec = httpx.get(settings.OPENAPI_SPEC).json()

mcp = FastMCP.from_openapi(
    openapi_spec=openapi_spec,
    client=client,
    name="FHIR MCP",
)

# ---------------------------------------------------------------------------
# 4. Build the MCP Starlette sub-app (streamable-http at /mcp)
# ---------------------------------------------------------------------------
mcp_app = mcp.http_app(path="/", transport="streamable-http")


# ---------------------------------------------------------------------------
# 5. Middleware: extract Authorization header → ContextVar
# ---------------------------------------------------------------------------
class AuthForwardingMiddleware:
    """
    ASGI middleware that reads the incoming Authorization header and stores it
    in `current_token` so that BearerAuth can forward it to the FHIR backend.
    Returns 401 if the header is missing on MCP routes.
    """

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope)
        auth_header = request.headers.get("authorization")

        # Only enforce auth on the /mcp endpoint
        if request.url.path.startswith("/mcp"):
            if not auth_header:
                response = Response("Missing Authorization header", status_code=401)
                await response(scope, receive, send)
                return

        # Set the token for the duration of this request
        token = current_token.set(auth_header)

        try:
            await self.app(scope, receive, send)
        finally:
            current_token.reset(token)


# ---------------------------------------------------------------------------
# 6. FastAPI application wrapping the MCP server
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Propagate the MCP app lifespan (initializes StreamableHTTPSessionManager)."""
    async with mcp_app.lifespan(mcp_app):
        yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(AuthForwardingMiddleware)  # type: ignore[arg-type]
app.mount("/mcp", mcp_app)

# ---------------------------------------------------------------------------
# 7. Entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)

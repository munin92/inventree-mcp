from contextvars import ContextVar

from fastmcp import FastMCP
from fastmcp.server.dependencies import get_access_token
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from .config import settings
from .client import InvenTreeClient

# Per-request InvenTree token — set by TokenMiddleware from X-Inventree-Token header.
_request_token: ContextVar[str] = ContextVar("inventree_token", default="")


class TokenMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        _request_token.set(request.headers.get("x-inventree-token") or "")
        return await call_next(request)


def _build_auth():
    """Builds caller verification when it is configured.

    Without configuration the server stays unprotected as before — something
    else has to sit in front of it then (a gateway, a reverse proxy).
    """
    if not settings.identity_passthrough:
        return None

    from fastmcp.server.auth import RemoteAuthProvider
    from fastmcp.server.auth.providers.jwt import JWTVerifier
    from pydantic import AnyHttpUrl

    if not settings.mcp_base_url:
        raise ValueError("mcp_base_url is required when identity checking is enabled")

    # RemoteAuthProvider rather than a bare JWTVerifier: it also serves the
    # OAuth metadata through which a client discovers the issuer itself.
    return RemoteAuthProvider(
        token_verifier=JWTVerifier(
            jwks_uri=settings.oidc_jwks_uri,
            issuer=settings.oidc_issuer,
            audience=settings.oidc_audience,
        ),
        authorization_servers=[AnyHttpUrl(settings.oidc_issuer)],
        base_url=settings.mcp_base_url,
    )


mcp = FastMCP(
    name="InvenTree MCP",
    instructions="Tools for managing InvenTree inventory. Each tool uses an 'operation' parameter to select the action.",
    auth=_build_auth(),
)


class NotAuthenticated(RuntimeError):
    """The caller brought no usable identity."""


def get_client() -> InvenTreeClient:
    """Returns a client for the current request.

    Three ways to say who is calling, in this order of precedence:

    1. **X-Inventree-Token header** — the caller brings their own InvenTree
       token. Most specific, so it wins.
    2. **Verified JWT** (OIDC settings present) — the caller's identity claim is
       mapped onto an InvenTree user via remote login.
    3. **Shared token** from the environment — everyone sees the same data.

    Ways 1 and 2 both mean "act as this caller", so the header wins over the
    JWT: someone who explicitly hands over a token wants exactly that token.

    With identity checking on and no caller identity at all, the call FAILS — it
    does not quietly fall back to the shared token. A silent fallback would undo
    the data separation without anyone noticing.
    """
    per_request = _request_token.get()
    if per_request:
        return InvenTreeClient(base_url=settings.inventree_url, token=per_request)

    if settings.identity_passthrough:
        token = get_access_token()
        if token is None:
            raise NotAuthenticated("No valid token — please sign in.")

        username = token.claims.get(settings.oidc_username_claim)
        if not username:
            raise NotAuthenticated(
                f"The token is missing the '{settings.oidc_username_claim}' claim; "
                "without it you cannot be mapped to an InvenTree user."
            )

        return InvenTreeClient(
            base_url=settings.inventree_url,
            remote_user=username,
            remote_user_header=settings.inventree_remote_user_header,
        )

    return InvenTreeClient(base_url=settings.inventree_url, token=settings.inventree_token)


# Import tools (registers them on mcp via @mcp.tool decorator)
from .tools import *  # noqa: F401, E402


def main():
    import uvicorn

    app = mcp.http_app()
    app.add_middleware(TokenMiddleware)
    uvicorn.run(app, host=settings.mcp_host, port=settings.mcp_port)


if __name__ == "__main__":
    main()

from contextvars import ContextVar

from fastmcp import FastMCP
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from .config import settings
from .client import InvenTreeClient

# Per-request InvenTree token — set by TokenMiddleware from X-Inventree-Token header.
# Falls back to INVENTREE_TOKEN env var if header is absent.
_request_token: ContextVar[str] = ContextVar("inventree_token", default="")


class TokenMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        token = request.headers.get("x-inventree-token") or settings.inventree_token
        _request_token.set(token)
        return await call_next(request)


mcp = FastMCP(
    name="InvenTree MCP",
    instructions="Tools for managing InvenTree inventory. Each tool uses an 'operation' parameter to select the action.",
)


def get_client() -> InvenTreeClient:
    token = _request_token.get() or settings.inventree_token
    return InvenTreeClient(base_url=settings.inventree_url, token=token)


# Import tools (registers them on mcp via @mcp.tool decorator)
from .tools import *  # noqa: F401, E402


def main():
    import uvicorn

    app = mcp.http_app()
    app.add_middleware(TokenMiddleware)
    uvicorn.run(app, host=settings.mcp_host, port=settings.mcp_port)


if __name__ == "__main__":
    main()

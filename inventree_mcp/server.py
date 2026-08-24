from fastmcp import FastMCP
from fastmcp.server.dependencies import get_access_token

from .config import settings
from .client import InvenTreeClient


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

    verifier = JWTVerifier(
        jwks_uri=settings.oidc_jwks_uri,
        issuer=settings.oidc_issuer,
        audience=settings.oidc_audience,
    )
    if not settings.mcp_base_url:
        raise ValueError("mcp_base_url is required when identity checking is enabled")

    # RemoteAuthProvider rather than a bare JWTVerifier: it also serves the
    # OAuth metadata through which a client discovers the issuer itself.
    return RemoteAuthProvider(
        token_verifier=verifier,
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
    """Returns a client — shared or per-person, depending on the mode.

    With identity checking on, it NEVER falls back to the shared token: if the
    identity is missing, the call fails. A silent fallback would undo the data
    separation without anyone noticing.
    """
    if not settings.identity_passthrough:
        return InvenTreeClient(base_url=settings.inventree_url, token=settings.inventree_token)

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


# Import tools (registers them on mcp via @mcp.tool decorator)
from .tools import *  # noqa: F401, E402


def main():
    mcp.run(
        transport="http",
        host=settings.mcp_host,
        port=settings.mcp_port,
    )


if __name__ == "__main__":
    main()

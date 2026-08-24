from fastmcp import FastMCP
from fastmcp.server.dependencies import get_access_token

from .config import settings
from .client import InvenTreeClient


def _build_auth():
    """Baut die Aufrufer-Pruefung, wenn sie konfiguriert ist.

    Ohne Konfiguration bleibt der Server ungeschuetzt wie bisher — dann muss
    etwas davor stehen (bei uns das MCP-Gateway).
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
        raise ValueError("mcp_base_url ist Pflicht, wenn die Identitaetspruefung an ist")

    # RemoteAuthProvider statt nur JWTVerifier: es liefert zusaetzlich die
    # OAuth-Metadaten, ueber die ein Client den Aussteller selbst findet.
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
    """Der Aufrufer hat keine verwertbare Identitaet mitgebracht."""


def get_client() -> InvenTreeClient:
    """Liefert einen Client — je nach Betriebsart gemeinsam oder personenbezogen.

    Bei eingeschalteter Identitaetspruefung wird NIE auf den gemeinsamen Token
    zurueckgefallen: fehlt die Identitaet, bricht der Aufruf ab. Ein stiller
    Rueckfall wuerde die Datentrennung aufheben, ohne dass es jemand merkt.
    """
    if not settings.identity_passthrough:
        return InvenTreeClient(base_url=settings.inventree_url, token=settings.inventree_token)

    token = get_access_token()
    if token is None:
        raise NotAuthenticated("Kein gueltiges Token — bitte anmelden.")

    username = token.claims.get(settings.oidc_username_claim)
    if not username:
        raise NotAuthenticated(
            f"Im Token fehlt der Claim '{settings.oidc_username_claim}'; "
            "ohne ihn kann ich dich bei InvenTree nicht zuordnen."
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

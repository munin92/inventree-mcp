from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    inventree_url: str = "http://localhost:8000"
    inventree_token: str = ""
    mcp_port: int = 8001
    mcp_host: str = "0.0.0.0"

    # --- Caller identity (optional) ---------------------------------------
    # With these three set, the server verifies incoming JWTs itself and acts
    # AS THE CALLING PERSON against InvenTree instead of using one shared token
    # for everyone. Each person sees their own data, and no token has to be
    # stored anywhere.
    #
    # Left empty, nothing changes: one shared inventree_token as before.
    oidc_jwks_uri: str = ""
    oidc_issuer: str = ""
    oidc_audience: str = ""

    # Public address of this server. Needed so clients can discover the OAuth
    # metadata and authenticate against the issuer themselves.
    mcp_base_url: str = ""

    # Claim the InvenTree username is read from.
    oidc_username_claim: str = "preferred_username"

    # Header InvenTree takes the username from (INVENTREE_REMOTE_LOGIN_HEADER).
    #
    # The default is deliberately the header oauth2-proxy already emits for
    # browser SSO, so this server slots into an existing setup instead of
    # introducing a second mechanism.
    #
    # On the browser path a reverse proxy typically replaces this header, so it
    # cannot be injected there. This server, however, talks to InvenTree
    # directly, bypassing the proxy — here IT is the trusted component. Hence
    # the no-silent-fallback rule in server.py.
    inventree_remote_user_header: str = "X-Auth-Request-REMOTE_USER"

    @property
    def identity_passthrough(self) -> bool:
        return bool(self.oidc_jwks_uri and self.oidc_issuer and self.oidc_audience)


settings = Settings()

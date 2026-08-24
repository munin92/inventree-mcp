"""Identity passthrough: each person acts as themselves against InvenTree.

The case that matters is not "it works" but "it does not silently fall back" —
a quiet fallback to the shared token would be a data separation that does not
exist.
"""

import pytest

from inventree_mcp.client import InvenTreeClient
from inventree_mcp.config import Settings


def test_shared_token_when_identity_off():
    s = Settings(inventree_token="gemeinsam")
    assert not s.identity_passthrough


def test_identity_needs_all_three_settings():
    """Two out of three is not enough — the server would run half-protected."""
    assert not Settings(oidc_jwks_uri="https://k/jwks").identity_passthrough
    assert not Settings(oidc_jwks_uri="https://k/jwks", oidc_issuer="https://k").identity_passthrough
    assert Settings(
        oidc_jwks_uri="https://k/jwks",
        oidc_issuer="https://k",
        oidc_audience="inventree-mcp",
    ).identity_passthrough


def test_client_with_token_sends_authorization():
    c = InvenTreeClient(base_url="http://x", token="tok")
    assert c._headers["Authorization"] == "Token tok"
    assert "X-Auth-Request-REMOTE_USER" not in c._headers


def test_client_with_person_sends_user_header():
    c = InvenTreeClient(base_url="http://x", remote_user="nadine")
    assert c._headers["X-Auth-Request-REMOTE_USER"] == "nadine"


def test_person_replaces_token_not_accompanies_it():
    """If the token stayed alongside, InvenTree would use it and the separation
    would be void."""
    c = InvenTreeClient(base_url="http://x", token="gemeinsam", remote_user="nadine")
    assert c._headers["X-Auth-Request-REMOTE_USER"] == "nadine"
    assert "Authorization" not in c._headers


def test_default_is_the_existing_sso_header():
    """oauth2-proxy emits exactly this header — the server slots in rather than
    introducing a second mechanism."""
    c = InvenTreeClient(base_url="http://x", remote_user="marian")
    assert c._headers["X-Auth-Request-REMOTE_USER"] == "marian"


def test_header_name_stays_configurable():
    c = InvenTreeClient(base_url="http://x", remote_user="marian", remote_user_header="X-Remote-User")
    assert c._headers["X-Remote-User"] == "marian"


def test_client_without_any_identity_is_rejected():
    with pytest.raises(ValueError, match="token or remote_user"):
        InvenTreeClient(base_url="http://x")


def test_no_silent_fallback_without_token(monkeypatch):
    """Without a valid token the call fails — it does NOT keep using the shared
    token."""
    import inventree_mcp.server as srv

    monkeypatch.setattr(
        srv.settings, "oidc_jwks_uri", "https://keycloak/jwks", raising=False
    )
    monkeypatch.setattr(srv.settings, "oidc_issuer", "https://keycloak", raising=False)
    monkeypatch.setattr(srv.settings, "oidc_audience", "inventree-mcp", raising=False)
    monkeypatch.setattr(srv.settings, "inventree_token", "gemeinsam", raising=False)
    monkeypatch.setattr(srv, "get_access_token", lambda: None)

    with pytest.raises(srv.NotAuthenticated, match="sign in"):
        srv.get_client()


def test_missing_claim_fails(monkeypatch):
    import inventree_mcp.server as srv

    class Token:
        claims = {"sub": "abc-123"}  # no preferred_username

    monkeypatch.setattr(srv.settings, "oidc_jwks_uri", "https://keycloak/jwks", raising=False)
    monkeypatch.setattr(srv.settings, "oidc_issuer", "https://keycloak", raising=False)
    monkeypatch.setattr(srv.settings, "oidc_audience", "inventree-mcp", raising=False)
    monkeypatch.setattr(srv, "get_access_token", lambda: Token())

    with pytest.raises(srv.NotAuthenticated, match="preferred_username"):
        srv.get_client()


def test_valid_token_acts_as_that_person(monkeypatch):
    import inventree_mcp.server as srv

    class Token:
        claims = {"preferred_username": "nadine"}

    monkeypatch.setattr(srv.settings, "oidc_jwks_uri", "https://keycloak/jwks", raising=False)
    monkeypatch.setattr(srv.settings, "oidc_issuer", "https://keycloak", raising=False)
    monkeypatch.setattr(srv.settings, "oidc_audience", "inventree-mcp", raising=False)
    monkeypatch.setattr(srv.settings, "inventree_token", "gemeinsam", raising=False)
    monkeypatch.setattr(srv, "get_access_token", lambda: Token())

    c = srv.get_client()
    assert c._headers["X-Auth-Request-REMOTE_USER"] == "nadine"
    assert "Authorization" not in c._headers


def test_without_identity_checking_nothing_changes(monkeypatch):
    """Control case: the change must not touch the previous mode."""
    import inventree_mcp.server as srv

    monkeypatch.setattr(srv.settings, "oidc_jwks_uri", "", raising=False)
    monkeypatch.setattr(srv.settings, "inventree_token", "gemeinsam", raising=False)

    c = srv.get_client()
    assert c._headers["Authorization"] == "Token gemeinsam"

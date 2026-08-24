"""Identitaetsdurchreichung: jede Person handelt bei InvenTree als sie selbst.

Der Kernfall ist nicht "es funktioniert", sondern "es faellt nicht heimlich
zurueck" — ein stiller Rueckfall auf den gemeinsamen Token waere eine
Datentrennung, die es nicht gibt.
"""

import pytest

from inventree_mcp.client import InvenTreeClient
from inventree_mcp.config import Settings


def test_gemeinsamer_token_wenn_identitaet_aus():
    s = Settings(inventree_token="gemeinsam")
    assert not s.identity_passthrough


def test_identitaet_braucht_alle_drei_angaben():
    """Zwei von drei reichen nicht — sonst liefe der Server halb geschuetzt."""
    assert not Settings(oidc_jwks_uri="https://k/jwks").identity_passthrough
    assert not Settings(oidc_jwks_uri="https://k/jwks", oidc_issuer="https://k").identity_passthrough
    assert Settings(
        oidc_jwks_uri="https://k/jwks",
        oidc_issuer="https://k",
        oidc_audience="inventree-mcp",
    ).identity_passthrough


def test_client_mit_token_schickt_authorization():
    c = InvenTreeClient(base_url="http://x", token="tok")
    assert c._headers["Authorization"] == "Token tok"
    assert "X-Auth-Request-REMOTE_USER" not in c._headers


def test_client_mit_person_schickt_den_benutzerkopf():
    c = InvenTreeClient(base_url="http://x", remote_user="nadine")
    assert c._headers["X-Auth-Request-REMOTE_USER"] == "nadine"


def test_person_ersetzt_den_token_und_ergaenzt_ihn_nicht():
    """Bliebe der Token daneben stehen, wuerde InvenTree ihn nehmen und die
    Trennung waere wirkungslos."""
    c = InvenTreeClient(base_url="http://x", token="gemeinsam", remote_user="nadine")
    assert c._headers["X-Auth-Request-REMOTE_USER"] == "nadine"
    assert "Authorization" not in c._headers


def test_vorgabe_ist_der_kopf_des_vorhandenen_sso():
    """oauth2-proxy liefert genau diesen Kopf — der Server reiht sich ein,
    statt einen zweiten Mechanismus danebenzustellen."""
    c = InvenTreeClient(base_url="http://x", remote_user="marian")
    assert c._headers["X-Auth-Request-REMOTE_USER"] == "marian"


def test_kopfname_bleibt_einstellbar():
    c = InvenTreeClient(base_url="http://x", remote_user="marian", remote_user_header="X-Remote-User")
    assert c._headers["X-Remote-User"] == "marian"


def test_client_ohne_jede_identitaet_wird_abgelehnt():
    with pytest.raises(ValueError, match="token oder remote_user"):
        InvenTreeClient(base_url="http://x")


def test_kein_stiller_rueckfall_ohne_token(monkeypatch):
    """Ohne gueltiges Token bricht der Aufruf ab — er nutzt NICHT den
    gemeinsamen Token weiter."""
    import inventree_mcp.server as srv

    monkeypatch.setattr(
        srv.settings, "oidc_jwks_uri", "https://keycloak/jwks", raising=False
    )
    monkeypatch.setattr(srv.settings, "oidc_issuer", "https://keycloak", raising=False)
    monkeypatch.setattr(srv.settings, "oidc_audience", "inventree-mcp", raising=False)
    monkeypatch.setattr(srv.settings, "inventree_token", "gemeinsam", raising=False)
    monkeypatch.setattr(srv, "get_access_token", lambda: None)

    with pytest.raises(srv.NotAuthenticated, match="anmelden"):
        srv.get_client()


def test_fehlender_claim_bricht_ab(monkeypatch):
    import inventree_mcp.server as srv

    class Token:
        claims = {"sub": "abc-123"}  # kein preferred_username

    monkeypatch.setattr(srv.settings, "oidc_jwks_uri", "https://keycloak/jwks", raising=False)
    monkeypatch.setattr(srv.settings, "oidc_issuer", "https://keycloak", raising=False)
    monkeypatch.setattr(srv.settings, "oidc_audience", "inventree-mcp", raising=False)
    monkeypatch.setattr(srv, "get_access_token", lambda: Token())

    with pytest.raises(srv.NotAuthenticated, match="preferred_username"):
        srv.get_client()


def test_gueltiges_token_handelt_als_diese_person(monkeypatch):
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


def test_ohne_identitaetspruefung_bleibt_alles_beim_alten(monkeypatch):
    """Kontrollfall: die Aenderung darf den bisherigen Betrieb nicht anfassen."""
    import inventree_mcp.server as srv

    monkeypatch.setattr(srv.settings, "oidc_jwks_uri", "", raising=False)
    monkeypatch.setattr(srv.settings, "inventree_token", "gemeinsam", raising=False)

    c = srv.get_client()
    assert c._headers["Authorization"] == "Token gemeinsam"

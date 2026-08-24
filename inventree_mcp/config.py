from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    inventree_url: str = "http://localhost:8000"
    inventree_token: str = ""
    mcp_port: int = 8001
    mcp_host: str = "0.0.0.0"
    mcp_bearer_token: str = ""

    # --- Identität des Aufrufers (optional) -------------------------------
    # Sind diese drei gesetzt, prüft der Server eingehende JWTs selbst und
    # handelt bei InvenTree ALS DIE AUFRUFENDE PERSON, statt für alle denselben
    # Token zu benutzen. Jede Person sieht damit ihre eigenen Daten, und es
    # muss nirgends ein Token abgelegt werden.
    #
    # Leer gelassen bleibt alles wie bisher: ein gemeinsamer inventree_token.
    oidc_jwks_uri: str = ""
    oidc_issuer: str = ""
    oidc_audience: str = ""

    # Öffentliche Adresse dieses Servers. Nötig, damit Clients die
    # OAuth-Metadaten finden und sich selbst beim Aussteller anmelden können.
    mcp_base_url: str = ""

    # Claim, aus dem der InvenTree-Benutzername gelesen wird.
    oidc_username_claim: str = "preferred_username"

    # Kopf, über den InvenTree den Benutzer entgegennimmt
    # (INVENTREE_REMOTE_LOGIN_HEADER, üblich HTTP_REMOTE_USER -> Remote-User).
    #
    # ACHTUNG, Betriebsbedingung: InvenTree darf dann NUR über einen
    # vertrauenswürdigen Proxy erreichbar sein, der diesen Kopf immer selbst
    # setzt und einen mitgebrachten überschreibt. Wer InvenTree direkt
    # erreicht, ist sonst, wen er will.
    inventree_remote_user_header: str = "Remote-User"

    @property
    def identity_passthrough(self) -> bool:
        return bool(self.oidc_jwks_uri and self.oidc_issuer and self.oidc_audience)


settings = Settings()

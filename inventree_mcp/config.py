from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    inventree_url: str = "http://localhost:8000"
    inventree_token: str = ""
    mcp_port: int = 8001
    mcp_host: str = "0.0.0.0"
    mcp_bearer_token: str = ""


settings = Settings()

"""Application settings loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings. Defaults keep local ``uvicorn`` runs working."""

    DATABASE_URL: str = "sqlite:///./secondbrain.db"
    SECRET_KEY: str = "dev-only-change-me"
    ENVIRONMENT: str = "development"
    # Switch bridge (see app.switch.client for the contract / assumptions)
    SWITCH_BRIDGE_URL: str = ""
    SWITCH_API_KEY: str = ""
    SWITCH_AGENT_ID: str = ""
    API_PREFIX: str = "/api"
    CORS_ORIGINS: str = "*"
    APP_VERSION: str = "0.1.0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

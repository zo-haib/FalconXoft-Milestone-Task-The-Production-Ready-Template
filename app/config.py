"""
Application configuration.

All configuration is loaded from environment variables, which in local
development are populated from a `.env` file via python-dotenv /
pydantic-settings. In production, real environment variables (e.g. injected
by Docker Compose, Kubernetes, or your platform's secret manager) take
precedence -- nothing sensitive is ever hard-coded here.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- App ---
    app_name: str = "Production Ready Template"
    environment: str = "development"
    secret_key: str = "change-me"

    # --- Database ---
    db_host: str = "db"
    db_port: int = 5432
    db_name: str = "app_db"
    db_user: str = "app_user"
    db_password: str = "app_password"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()

import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Bump this when you ship a new Docker image so you can confirm the UI is updated.
APP_VERSION = "0.0.2"


def llm_base_url_from_env() -> str | None:
    """When set (e.g. in Docker Compose), overrides DB `llm_base_url` for LLM HTTP calls."""
    v = os.environ.get("GPM_LLM_BASE_URL", "").strip()
    return v or None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="GPM_", env_file=".env", extra="ignore")

    data_dir: Path = Path("./data")
    database_url: str | None = None
    """If unset, uses sqlite+aiosqlite under data_dir."""

    @property
    def sqlite_path(self) -> Path:
        return self.data_dir / "app.db"

    @property
    def runs_csv_dir(self) -> Path:
        d = self.data_dir / "runs"
        d.mkdir(parents=True, exist_ok=True)
        return d


settings = Settings()

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSettings(BaseModel):
    provider: str = Field(default="openai_compatible")
    model: str = Field(default="gpt-4o-mini")
    api_key: str | None = Field(default=None)
    base_url: str | None = Field(default=None)
    temperature: float = Field(default=0.1)


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = Field(default="local")
    app_verbose: bool = Field(default=False)
    app_log_level: str = Field(default="INFO")

    data_raw_dir: Path = Field(default=Path("data/raw"))
    data_duckdb_dir: Path = Field(default=Path("data/duckdb"))
    data_exports_dir: Path = Field(default=Path("data/exports"))
    duckdb_path: Path = Field(default=Path("data/duckdb/protheus_analytics.duckdb"))
    config_path: Path = Field(default=Path("config/bootstrap_config.yml"))

    llm_provider: str = Field(default="openai_compatible")
    llm_model: str = Field(default="gpt-4o-mini")
    llm_api_key: str | None = Field(default=None)
    llm_base_url: str | None = Field(default=None)
    llm_temperature: float = Field(default=0.1)

    @property
    def llm(self) -> LLMSettings:
        return LLMSettings(
            provider=self.llm_provider,
            model=self.llm_model,
            api_key=self.llm_api_key,
            base_url=self.llm_base_url,
            temperature=self.llm_temperature,
        )

    def ensure_directories(self) -> None:
        self.data_raw_dir.mkdir(parents=True, exist_ok=True)
        self.data_duckdb_dir.mkdir(parents=True, exist_ok=True)
        self.data_exports_dir.mkdir(parents=True, exist_ok=True)
        self.duckdb_path.parent.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    settings = AppSettings()
    settings.ensure_directories()
    return settings


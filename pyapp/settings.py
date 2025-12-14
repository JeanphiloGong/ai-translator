from functools import lru_cache
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load environment variables from .env if present
load_dotenv()

class Settings(BaseSettings):
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    openai_base_url: str = Field(default="https://api.chatanywhere.tech/v1", alias="OPENAI_BASE_URL")
    openai_model: str = Field(default="gpt-4o-2024-08-06", alias="OPENAI_MODEL")
    database_path: Path = Field(default=Path("translations.db"), alias="DB_PATH")

    model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            case_sensitive=False,
            )

@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()


from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    gemini_api_key: str = ""
    gemini_model: str = "gemini-3-flash-preview"
    auth_bridge_secret: str = "insecure-dev-secret"
    cors_origins: str = "http://localhost:3000"

    # Full JSON contents of a Firebase Admin service account key. Falls back to
    # GOOGLE_APPLICATION_CREDENTIALS / Application Default Credentials if unset.
    firebase_service_account_json: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

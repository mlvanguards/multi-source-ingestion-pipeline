from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / '.env'),
        env_file_encoding='utf-8',
        extra='ignore'
    )

    ATLASSIAN_DOMAIN: str
    ATLASSIAN_EMAIL: str
    ATLASSIAN_API_TOKEN: str
    ATLASSIAN_CLIENT_ID: str
    ATLASSIAN_CLIENT_SECRET: str


settings = Settings()

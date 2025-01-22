from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    ATLASSIAN_DOMAIN: str | None = None
    ATLASSIAN_EMAIL: str | None = None
    ATLASSIAN_API_KEY: str | None = None


settings = Settings()

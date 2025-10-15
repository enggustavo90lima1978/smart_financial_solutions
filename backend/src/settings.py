from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv('.env', encoding='utf-8')


class Settings(BaseSettings):
    groq_api_key: str | None = None
    gemini_api_key: str | None = None
    database_uri: str

    model_config = SettingsConfigDict(
        env_file='.env',
        extra='ignore',
        env_file_encoding='utf-8',
        env_ignore_empty=True,
    )


settings = Settings()

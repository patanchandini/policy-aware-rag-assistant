from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "knowledge_assistant"
    postgres_user: str = "rag_user"
    postgres_password: str = "rag_password"

    # OpenAI (kept for compatibility, not required if using Gemini)
    openai_api_key: str = "placeholder"
    embedding_model: str = "text-embedding-3-small"
    embedding_dim: int = 1536
    llm_model: str = "gpt-4o-mini"

    # Gemini (free alternative)
    gemini_api_key: str = ""
    gemini_embedding_model: str = "gemini-embedding-001"
    gemini_llm_model: str = "gemini-2.5-flash"

    # Retrieval
    top_k: int = 20
    similarity_threshold: float = 0.7
    faithfulness_threshold: float = 0.8

    # App
    log_level: str = "INFO"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"          # ← CRITICAL: ignore extra .env vars


@lru_cache
def get_settings() -> Settings:
    return Settings()
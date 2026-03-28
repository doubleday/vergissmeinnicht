from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from memory_api.services.embedding import DEFAULT_SENTENCE_TRANSFORMER_DEVICE, DEFAULT_SENTENCE_TRANSFORMER_MODEL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    postgres_db: str = Field(default="memory")
    postgres_user: str = Field(default="memory")
    postgres_password: str = Field(default="memory")
    postgres_host: str = Field(default="localhost")
    postgres_port: int = Field(default=5432)

    qdrant_host: str = Field(default="localhost")
    qdrant_port: int = Field(default=6333)
    memory_qdrant_collection: str = Field(default="memories")

    memory_api_host: str = Field(default="0.0.0.0")
    memory_api_port: int = Field(default=8000)
    memory_api_log_level: str = Field(default="info")

    embedding_provider: str = Field(default="deterministic-local")
    embedding_dimensions: int = Field(default=32)
    embedding_model_name: str = Field(default=DEFAULT_SENTENCE_TRANSFORMER_MODEL)
    embedding_device: str = Field(default=DEFAULT_SENTENCE_TRANSFORMER_DEVICE)

    @property
    def postgres_dsn(self) -> str:
        return (
            f"dbname={self.postgres_db} user={self.postgres_user} "
            f"password={self.postgres_password} host={self.postgres_host} port={self.postgres_port}"
        )

    @property
    def qdrant_url(self) -> str:
        return f"http://{self.qdrant_host}:{self.qdrant_port}"


settings = Settings()

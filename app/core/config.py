from pydantic import ConfigDict, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "FastAPI AI API"
    debug: bool = False
    environment: str = "development"

    # LLM
    openai_api_key: str = ""
    google_gemini_api_key: str = ""
    llama_api_key: str = ""

    # API
    api_v1_prefix: str = "/api/v1"
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Database - PostgreSQL
    postgres_server: str = "localhost"
    postgres_user: str = "postgres"
    postgres_password: str = "password"
    postgres_db: str = "fastapi_db"
    postgres_port: int = 5432

    # Database - MongoDB
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_database: str = "fastapi_mongo"

    # Database - Chroma
    chroma_api_key: str = ""
    chroma_tenant: str = ""
    chroma_database: str = ""

    # Redis (for caching/sessions)
    redis_url: str = "redis://localhost:6379"

    # CORS
    backend_cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8080"]

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            # Handle both comma-separated strings and JSON strings
            if v.startswith("[") and v.endswith("]"):
                import json

                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    pass
            return [origin.strip() for origin in v.split(",")]
        return v

    # Security
    algorithm: str = "HS256"

    @property
    def postgres_url(self) -> str:
        """Construct PostgreSQL connection URL."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:"
            f"{self.postgres_password}@{self.postgres_server}:"
            f"{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def mongodb_connection_url(self) -> str:
        """Construct MongoDB connection URL."""
        return f"{self.mongodb_url}/{self.mongodb_database}"

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
    )


# Global settings instance
settings = Settings()

"""Application settings and configuration."""

import os
from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="agentic-ai-platform")
    app_version: str = Field(default="1.0.0")
    environment: str = Field(default="development")
    log_level: str = Field(default="INFO")

    # API
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_workers: int = Field(default=4)

    # LLM Provider - Support multiple providers
    llm_provider: str = Field(default="openai", description="LLM provider: openai, anthropic, groq, etc.")
    openai_api_key: Optional[str] = Field(default="", alias="OPENAI_API_KEY")
    nebius_api_key: Optional[str] = Field(default="", alias="NEBIUS_API_KEY")

    # Couchbase
    cb_connection_string: Optional[str] = Field(default="", alias="CB_CONNECTION_STRING")
    cb_username: Optional[str] = Field(default="", alias="CB_USERNAME")
    cb_password: Optional[str] = Field(default="", alias="CB_PASSWORD")
    cb_bucket_name: str = Field(alias="CB_BUCKET_NAME", default="travel-sample")

    # MCP Server
    mcp_server_path: Optional[str] = Field(default="/app/mcp-server-couchbase", alias="MCP_SERVER_PATH")

    # Redis
    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379)
    redis_db: int = Field(default=0)
    redis_password: Optional[str] = Field(default=None)

    # Cache
    cache_ttl_seconds: int = Field(default=3600)
    cache_enabled: bool = Field(default=True)

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True)
    rate_limit_requests_per_minute: int = Field(default=60)

    # Monitoring
    metrics_enabled: bool = Field(default=True)
    tracing_enabled: bool = Field(default=False)

    # LLM
    llm_model: str = Field(default="gpt-4o-mini", description="Model name (e.g., gpt-4o-mini, gpt-4, claude-3-5-sonnet-20241022)")
    
    @property
    def effective_model(self) -> str:
        """Get effective model name based on provider."""
        if self.llm_provider.lower() == "openai" and not self.llm_model.startswith("gpt"):
            # Auto-fix model name for OpenAI
            return "gpt-4o-mini"
        return self.llm_model
    llm_temperature: float = Field(default=0.7)
    llm_max_tokens: int = Field(default=2000)

    @property
    def couchbase_env(self) -> dict[str, str]:
        """Get Couchbase environment variables for MCP server."""
        env = {
            "CB_CONNECTION_STRING": self.cb_connection_string or "",
            "CB_USERNAME": self.cb_username or "",
            "CB_PASSWORD": self.cb_password or "",
            "CB_BUCKET_NAME": self.cb_bucket_name,
        }
        # Add connection timeout settings for Couchbase
        env["CB_CONNECTION_TIMEOUT"] = "30"  # 30 seconds connection timeout
        env["CB_KV_TIMEOUT"] = "10"  # 10 seconds KV timeout
        env["CB_QUERY_TIMEOUT"] = "75"  # 75 seconds query timeout
        return env

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment.lower() == "development"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


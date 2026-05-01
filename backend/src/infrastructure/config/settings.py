from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMMode(str, Enum):
    LOCAL = "local"       # Ollama only — no external API calls
    HYBRID = "hybrid"     # Claude for complex, Ollama for simple
    CLOUD = "cloud"       # Full cloud: Claude + Groq + Gemini


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Application
    app_name: str = "PM Copilot"
    debug: bool = False
    secret_key: str = "change-me-in-production"
    allowed_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/pmcopilot"

    # LLM
    llm_mode: LLMMode = LLMMode.LOCAL
    anthropic_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    ollama_base_url: str = "http://localhost:11434"
    ollama_llm_model: str = "llama3"

    # ChromaDB
    chromadb_host: str = "localhost"
    chromadb_port: int = 8001

    # Confluence
    confluence_base_url: Optional[str] = None
    confluence_email: Optional[str] = None
    confluence_api_token: Optional[str] = None
    confluence_space_key: str = "PBPMIA"

    # Jira
    jira_base_url: Optional[str] = None
    jira_email: Optional[str] = None
    jira_api_token: Optional[str] = None

    # GitHub
    github_token: Optional[str] = None


settings = Settings()

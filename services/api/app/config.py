"""AcoustiStruct API — Application configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class DatabaseConfig:
    url: str = "sqlite+aiosqlite:///./acoustistruct.db"
    echo: bool = False


@dataclass(frozen=True)
class AuthConfig:
    secret_key: str = "change-me"
    algorithm: str = "HS256"
    expiration_minutes: int = 1440


@dataclass(frozen=True)
class StorageConfig:
    upload_dir: Path = field(default_factory=lambda: Path("./uploads"))
    max_upload_size_mb: int = 50
    document_output_dir: Path = field(default_factory=lambda: Path("./generated_docs"))


@dataclass(frozen=True)
class ProviderConfig:
    asr_provider: str = "mock"
    semantic_provider: str = "mock"
    language_provider: str = "mock"
    sarvam_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None


@dataclass(frozen=True)
class AppConfig:
    env: str = "development"
    debug: bool = True
    secret_key: str = "change-me"
    host: str = "0.0.0.0"
    port: int = 8000
    frontend_url: str = "http://localhost:5173"
    demo_mode: bool = True
    log_level: str = "INFO"
    log_sensitive_data: bool = False

    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    auth: AuthConfig = field(default_factory=AuthConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    providers: ProviderConfig = field(default_factory=ProviderConfig)

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Build configuration from environment variables."""
        return cls(
            env=os.getenv("APP_ENV", "development"),
            debug=os.getenv("APP_DEBUG", "true").lower() == "true",
            secret_key=os.getenv("APP_SECRET_KEY", "change-me"),
            host=os.getenv("APP_HOST", "0.0.0.0"),
            port=int(os.getenv("APP_PORT", "8000")),
            frontend_url=os.getenv("FRONTEND_URL", "http://localhost:5173"),
            demo_mode=os.getenv("DEMO_MODE", "true").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_sensitive_data=os.getenv("LOG_SENSITIVE_DATA", "false").lower() == "true",
            database=DatabaseConfig(
                url=os.getenv(
                    "DATABASE_URL",
                    "sqlite+aiosqlite:///./acoustistruct.db",
                ),
                echo=os.getenv("DATABASE_ECHO", "false").lower() == "true",
            ),
            auth=AuthConfig(
                secret_key=os.getenv("JWT_SECRET_KEY", "change-me"),
                algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
                expiration_minutes=int(os.getenv("JWT_EXPIRATION_MINUTES", "1440")),
            ),
            storage=StorageConfig(
                upload_dir=Path(os.getenv("UPLOAD_DIR", "./uploads")),
                max_upload_size_mb=int(os.getenv("MAX_UPLOAD_SIZE_MB", "50")),
                document_output_dir=Path(os.getenv("DOCUMENT_OUTPUT_DIR", "./generated_docs")),
            ),
            providers=ProviderConfig(
                asr_provider=os.getenv("ASR_PROVIDER", "mock"),
                semantic_provider=os.getenv("SEMANTIC_PROVIDER", "mock"),
                language_provider=os.getenv("LANGUAGE_PROVIDER", "mock"),
                sarvam_api_key=os.getenv("SARVAM_API_KEY"),
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                gemini_api_key=os.getenv("GEMINI_API_KEY"),
            ),
        )


# Singleton — created once at import time
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    global _config
    if _config is None:
        _config = AppConfig.from_env()
    return _config

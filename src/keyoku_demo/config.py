"""Configuration management for Keyoku Demo."""

import os
from dataclasses import dataclass, field
from typing import Optional

from dotenv import load_dotenv


@dataclass
class Config:
    """Demo configuration with sensible defaults."""

    # Keyoku settings
    keyoku_api_key: str = field(default_factory=lambda: os.getenv("KEYOKU_API_KEY", ""))
    keyoku_base_url: str = field(
        default_factory=lambda: os.getenv("KEYOKU_BASE_URL", "http://localhost:8000")
    )

    # LLM settings
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    llm_model: str = field(default_factory=lambda: os.getenv("LLM_MODEL", "gpt-4o"))
    llm_temperature: float = 0.7

    # Demo settings
    agent_id: str = field(default_factory=lambda: os.getenv("AGENT_ID", "demo-assistant"))
    session_id: Optional[str] = None

    # Memory settings
    memory_search_limit: int = 5
    memory_search_mode: str = "hybrid"

    def validate(self) -> list[str]:
        """Validate configuration, return list of errors."""
        errors = []
        if not self.keyoku_api_key:
            errors.append("KEYOKU_API_KEY is required")
        if not self.openai_api_key:
            errors.append("OPENAI_API_KEY is required")
        return errors

    @classmethod
    def load(cls) -> "Config":
        """Load configuration from environment."""
        load_dotenv()
        return cls()


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global config instance."""
    global _config
    if _config is None:
        _config = Config.load()
    return _config

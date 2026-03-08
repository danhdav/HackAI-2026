"""Centralized application configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-backed settings for the backend."""

    app_name: str = "TaxMaxx Backend"
    app_env: str = "development"
    app_debug: bool = True

    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "hackai_tax_assistant"
    mongodb_collection_sessions: str = "tax_sessions"
    mongodb_collection_boxdata: str = "box_data"

    use_mock_parser_by_default: bool = True
    parser_timeout_seconds: int = 120

    azure_key: str = ""
    azure_endpoint: str = ""

    gemini_enabled: bool = False
    gemini_api_key: str = ""
    gemini_model_name: str = "gemini-1.5-flash"

    # TODO: Confirm deduction amount based on target tax year.
    standard_deduction_single: float = 14600.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()

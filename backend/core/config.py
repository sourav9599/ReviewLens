import os
os.environ["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"

from pydantic_settings import BaseSettings
from typing import Optional, Literal

class Settings(BaseSettings):
    # LLM Provider Configuration
    LLM_PROVIDER: Literal["gemini", "litellm", "googleADC"] = "gemini"

    # Gemini-specific settings (API key auth)
    GOOGLE_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash-lite"
    GEMINI_EMBEDDING_MODEL: str = "models/gemini-embedding-2"

    # Google ADC settings (Vertex AI with Application Default Credentials)
    GCP_PROJECT: str = "code-fest"
    GCP_LOCATION: str = "us-central1"
    GOOGLE_ADC_MODEL: str = "gemini-2.5-flash"
    GOOGLE_ADC_EMBEDDING_MODEL: str = "text-embedding-005"

    # LiteLLM settings (supports 100+ providers via unified interface)
    LITELLM_MODEL: str = "gemini/gemini-2.5-flash-lite"
    LITELLM_EMBEDDING_MODEL: str = "gemini/gemini-embedding-2"
    LITELLM_API_KEY: str = ""
    LITELLM_API_BASE: Optional[str] = None
    LITELLM_TEMPERATURE: float = 0.0
    LITELLM_MAX_TOKENS: int = 4096

    # Pipeline settings
    MAX_REVIEWS_PER_BATCH: int = 500
    DEDUP_SIMILARITY_THRESHOLD: float = 0.85
    BOT_DETECTION_THRESHOLD: float = 0.65
    TREND_WINDOW_SIZE: int = 50
    ANOMALY_Z_SCORE_THRESHOLD: float = 2.0
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]

    # Agentic AI settings
    MIN_CONFIDENCE_THRESHOLD: float = 0.45
    FEEDBACK_LOOP_MAX_RETRIES: int = 2
    EMOJI_CONFIDENCE_BOOST: float = 0.15
    BOT_HIGH_THRESHOLD: float = 0.75
    BOT_CRITICAL_THRESHOLD: float = 0.90
    MIN_CROSS_COMPARE_CATEGORIES: int = 2
    ORCHESTRATOR_BOT_REQUEUE_THRESHOLD: float = 0.40

    class Config:
        env_file = ".env"

settings = Settings()

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    GOOGLE_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash-lite"
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

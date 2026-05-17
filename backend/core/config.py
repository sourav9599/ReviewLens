from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1:8b"
    MAX_REVIEWS_PER_BATCH: int = 500
    DEDUP_SIMILARITY_THRESHOLD: float = 0.85
    BOT_DETECTION_THRESHOLD: float = 0.65
    TREND_WINDOW_SIZE: int = 50
    ANOMALY_Z_SCORE_THRESHOLD: float = 2.0
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]

    # Agentic AI settings
    MIN_CONFIDENCE_THRESHOLD: float = 0.45      # below this triggers feedback loop
    FEEDBACK_LOOP_MAX_RETRIES: int = 2           # max re-runs per feedback loop
    EMOJI_CONFIDENCE_BOOST: float = 0.15         # boost when emoji matches sentiment
    BOT_HIGH_THRESHOLD: float = 0.75             # high risk bot
    BOT_CRITICAL_THRESHOLD: float = 0.90         # critical risk bot
    MIN_CROSS_COMPARE_CATEGORIES: int = 2        # minimum categories for cross-comparison
    ORCHESTRATOR_BOT_REQUEUE_THRESHOLD: float = 0.40  # if >40% bots → re-run dedup
    
    class Config:
        env_file = ".env"

settings = Settings()

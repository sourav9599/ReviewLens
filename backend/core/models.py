from typing import TypedDict, List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class SentimentLabel(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"
    SARCASTIC = "sarcastic"
    AMBIGUOUS = "ambiguous"


class ReviewStatus(str, Enum):
    CLEAN = "clean"
    DUPLICATE = "duplicate"
    NEAR_DUPLICATE = "near_duplicate"
    BOT_SUSPECTED = "bot_suspected"
    FLAGGED = "flagged"


class BotRiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FeatureSentiment(BaseModel):
    feature: str
    sentiment: SentimentLabel
    confidence: float = Field(ge=0.0, le=1.0)
    excerpts: List[str] = []


class EmojiSignal(BaseModel):
    emoji: str
    description: str
    sentiment: SentimentLabel
    count: int = 1
    confidence_boost: float = 0.0


class AgentMessage(BaseModel):
    """Inter-agent communication message for the AgentBus."""
    msg_id: str
    sender: str
    event_type: str  # "bot_detected", "low_confidence", "alert_raised", "emoji_found", "quality_check"
    payload: Dict[str, Any] = {}
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class OrchestratorDecision(BaseModel):
    """Decision made by the Orchestrator Agent."""
    decision_id: str
    phase: str          # pipeline phase when decision was made
    decision: str       # what was decided
    reason: str         # why
    action: str         # what action was taken: "route", "retry", "skip", "escalate"
    affected_agents: List[str] = []
    metadata: Dict[str, Any] = {}
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class ProcessedReview(BaseModel):
    id: str
    original_text: str
    cleaned_text: str
    language: str = "en"
    detected_languages: List[str] = []
    status: ReviewStatus = ReviewStatus.CLEAN
    duplicate_of: Optional[str] = None
    overall_sentiment: SentimentLabel = SentimentLabel.NEUTRAL
    overall_confidence: float = 0.0
    feature_sentiments: List[FeatureSentiment] = []
    product_category: str = ""
    product_name: str = ""
    rating: Optional[float] = None
    review_date: Optional[str] = None
    helpful_votes: int = 0
    verified_purchase: bool = False
    bot_score: float = 0.0
    bot_risk_level: BotRiskLevel = BotRiskLevel.LOW
    bot_signals: List[str] = []
    emoji_signals: List[EmojiSignal] = []
    emoji_count: int = 0
    flags: List[str] = []
    processed_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class TrendPoint(BaseModel):
    window_index: int
    window_start: int
    window_end: int
    feature: str
    sentiment_distribution: Dict[str, float]
    complaint_rate: float
    praise_rate: float
    review_count: int


class TrendAlert(BaseModel):
    alert_id: str
    severity: str  # "critical", "warning", "info"
    feature: str
    alert_type: str  # "emerging_complaint", "emerging_praise", "anomaly_drop", "systemic_issue"
    description: str
    current_rate: float
    previous_rate: float
    change_percent: float
    z_score: float = 0.0
    affected_reviews: List[str] = []
    first_detected_at: str
    is_systemic: bool = False


class ActionableRecommendation(BaseModel):
    priority: int  # 1=critical, 2=high, 3=medium, 4=low
    category: str  # "product", "marketing", "operations", "quality"
    title: str
    description: str
    supporting_data: str
    suggested_action: str
    estimated_impact: str
    affected_feature: str
    triggered_by: str = "analysis"  # "analysis", "feedback_loop", "orchestrator", "emoji_signal"


class EmojiAnalysisSummary(BaseModel):
    total_emojis_found: int = 0
    unique_emojis: int = 0
    emoji_frequency: Dict[str, int] = {}        # emoji → count
    emoji_sentiment_map: Dict[str, str] = {}    # emoji → sentiment label
    top_positive_emojis: List[str] = []
    top_negative_emojis: List[str] = []
    reviews_with_emojis: int = 0
    emoji_confidence_boosts_applied: int = 0
    emoji_sentiment_distribution: Dict[str, float] = {}


class CrossProductComparison(BaseModel):
    categories: List[str] = []
    sentiment_by_category: Dict[str, Dict[str, float]] = {}   # cat → {positive:%, negative:%...}
    feature_by_category: Dict[str, Dict[str, float]] = {}     # cat → {feature: complaint_rate}
    best_category: str = ""
    worst_category: str = ""
    bot_rate_by_category: Dict[str, float] = {}
    review_count_by_category: Dict[str, int] = {}


class AnalysisReport(BaseModel):
    report_id: str
    created_at: str
    total_reviews: int
    clean_reviews: int
    duplicate_count: int
    bot_suspected_count: int
    flagged_count: int
    languages_detected: List[str]
    product_categories: List[str]
    overall_sentiment_distribution: Dict[str, float]
    feature_summary: Dict[str, Dict[str, Any]]
    trend_alerts: List[TrendAlert]
    trend_data: List[TrendPoint]
    recommendations: List[ActionableRecommendation]
    processed_reviews: List[ProcessedReview]
    processing_time_seconds: float
    agent_trace: List[Dict[str, Any]] = []
    orchestrator_decisions: List[OrchestratorDecision] = []
    emoji_analysis: Optional[EmojiAnalysisSummary] = None
    cross_product_comparison: Optional[CrossProductComparison] = None
    feedback_loops_triggered: int = 0
    pipeline_version: str = "2.0-agentic"


# LangGraph State
class ReviewPipelineState(TypedDict):
    raw_reviews: List[Dict[str, Any]]
    preprocessed_reviews: List[ProcessedReview]
    deduplicated_reviews: List[ProcessedReview]
    analyzed_reviews: List[ProcessedReview]
    trend_data: List[TrendPoint]
    trend_alerts: List[TrendAlert]
    recommendations: List[ActionableRecommendation]
    report: Optional[AnalysisReport]
    errors: List[str]
    progress: Dict[str, Any]
    pipeline_config: Dict[str, Any]
    # Agentic extensions
    agent_messages: List[AgentMessage]
    orchestrator_decisions: List[OrchestratorDecision]
    emoji_analysis: Optional[EmojiAnalysisSummary]
    cross_product_comparison: Optional[CrossProductComparison]
    feedback_loop_count: int
    orchestrator_route: str   # current routing decision

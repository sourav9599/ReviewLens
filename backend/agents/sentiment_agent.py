"""
Agent 3: Enhanced Hybrid Sentiment Agent
- Batch processing (fast + stable)
- Rule-based feature extraction
- Per-feature confidence scores (not binary 0.5/0.7)
- Emoji signal confidence boosting
- Emits low_confidence events to AgentBus for feedback loop
"""

import logging
from typing import List
from langchain_ollama import OllamaLLM
from core.models import (
    ReviewPipelineState, SentimentLabel, ReviewStatus,
    FeatureSentiment, EmojiSignal
)
from core.config import settings

logger = logging.getLogger(__name__)


# Feature keyword extractor (expanded)
def extract_features(text: str):
    text = text.lower()
    features = []
    if "battery" in text or "charge" in text or "charging" in text:
        features.append("battery")
    if "packaging" in text or "box" in text or "seal" in text or "pack" in text:
        features.append("packaging")
    if "sound" in text or "audio" in text or "speaker" in text or "volume" in text or "bass" in text:
        features.append("sound")
    if "price" in text or "cost" in text or "value" in text or "worth" in text or "expensive" in text or "cheap" in text:
        features.append("price")
    if "quality" in text or "build" in text or "material" in text or "durability" in text or "durable" in text:
        features.append("quality")
    if "delivery" in text or "shipping" in text or "arrived" in text or "dispatch" in text:
        features.append("delivery")
    if "screen" in text or "display" in text or "brightness" in text or "resolution" in text:
        features.append("screen")
    if "size" in text or "fit" in text or "weight" in text or "compact" in text or "portable" in text:
        features.append("size")
    if "color" in text or "colour" in text or "look" in text or "design" in text or "style" in text:
        features.append("design")
    if "performance" in text or "fast" in text or "slow" in text or "lag" in text or "smooth" in text:
        features.append("performance")
    return features


def compute_feature_confidence(
    base_confidence: float,
    emoji_signals: List[EmojiSignal],
    feature: str,
    text_sentiment: SentimentLabel
) -> float:
    """
    Per-feature confidence = base + emoji alignment boost - emoji conflict penalty.
    """
    boost = 0.0
    for sig in emoji_signals:
        if sig.sentiment == text_sentiment:
            boost += sig.confidence_boost * 0.5  # half boost for feature-level
        elif sig.sentiment != SentimentLabel.NEUTRAL and sig.sentiment != text_sentiment:
            boost -= sig.confidence_boost * 0.2

    return round(min(1.0, max(0.0, base_confidence + boost)), 3)


def sentiment_analysis_agent(state: ReviewPipelineState) -> ReviewPipelineState:
    reviews = state["deduplicated_reviews"]
    errors = list(state.get("errors", []))
    agent_messages = list(state.get("agent_messages", []))

    llm = OllamaLLM(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.OLLAMA_MODEL,
        temperature=0.0,
        num_predict=128,
    )

    analyzable_statuses = {ReviewStatus.CLEAN, ReviewStatus.NEAR_DUPLICATE}
    to_analyze = [r for r in reviews if r.status in analyzable_statuses]

    logger.info(f"[SentimentAgent] Processing {len(to_analyze)} reviews")

    BATCH_SIZE = 20
    low_confidence_count = 0

    try:
        for i in range(0, len(to_analyze), BATCH_SIZE):
            batch = to_analyze[i:i + BATCH_SIZE]
            texts = [r.cleaned_text[:200] for r in batch]

            prompt = f"""You are a sentiment analysis expert.

Classify each review into ONE of:
positive, negative, or neutral

Rules:
- Positive → good, excellent, satisfied
- Negative → bad, poor, broken, issue
- Neutral → average, okay, mixed

Return ONLY one word per review.
No explanation.

Reviews:
{chr(10).join(texts)}
"""

            response = llm.invoke(prompt)
            results = response.strip().split("\n")

            # Handle mismatch safely
            if len(results) != len(batch):
                logger.warning(f"[SentimentAgent] Batch mismatch ({len(results)} vs {len(batch)}), using rating fallback")
                for review in batch:
                    if review.rating is not None:
                        if review.rating >= 4:
                            sentiment = SentimentLabel.POSITIVE
                            base_conf = 0.55
                        elif review.rating <= 2:
                            sentiment = SentimentLabel.NEGATIVE
                            base_conf = 0.55
                        else:
                            sentiment = SentimentLabel.NEUTRAL
                            base_conf = 0.45
                    else:
                        sentiment = SentimentLabel.NEUTRAL
                        base_conf = 0.40

                    # Apply emoji boost to overall confidence
                    emoji_boost = sum(
                        s.confidence_boost for s in review.emoji_signals
                        if s.sentiment == sentiment
                    )
                    final_conf = round(min(1.0, base_conf + emoji_boost), 3)

                    review.overall_sentiment = sentiment
                    review.overall_confidence = final_conf

                    if final_conf < settings.MIN_CONFIDENCE_THRESHOLD:
                        low_confidence_count += 1
                        agent_messages.append({
                            "sender": "SentimentAgent",
                            "event_type": "low_confidence",
                            "payload": {"review_id": review.id, "confidence": final_conf}
                        })

                    features = extract_features(review.cleaned_text)
                    review.feature_sentiments = [
                        FeatureSentiment(
                            feature=f,
                            sentiment=sentiment,
                            confidence=compute_feature_confidence(final_conf, review.emoji_signals, f, sentiment),
                            excerpts=[]
                        )
                        for f in features
                    ]
                continue

            # Normal case
            for review, result in zip(batch, results):
                label = result.lower().strip()

                if "positive" in label:
                    sentiment = SentimentLabel.POSITIVE
                    base_conf = 0.72
                elif "negative" in label:
                    sentiment = SentimentLabel.NEGATIVE
                    base_conf = 0.72
                else:
                    sentiment = SentimentLabel.NEUTRAL
                    base_conf = 0.60

                # Apply emoji confidence boosting
                emoji_boost = sum(
                    s.confidence_boost for s in review.emoji_signals
                    if s.sentiment == sentiment
                )
                emoji_conflict = sum(
                    s.confidence_boost * 0.3 for s in review.emoji_signals
                    if s.sentiment != sentiment and s.sentiment != SentimentLabel.NEUTRAL
                )
                final_conf = round(min(1.0, max(0.0, base_conf + emoji_boost - emoji_conflict)), 3)

                review.overall_sentiment = sentiment
                review.overall_confidence = final_conf

                # Track low-confidence for feedback loop
                if final_conf < settings.MIN_CONFIDENCE_THRESHOLD:
                    low_confidence_count += 1
                    agent_messages.append({
                        "sender": "SentimentAgent",
                        "event_type": "low_confidence",
                        "payload": {"review_id": review.id, "confidence": final_conf}
                    })

                # Per-feature analysis with individual confidence
                features = extract_features(review.cleaned_text)
                review.feature_sentiments = [
                    FeatureSentiment(
                        feature=f,
                        sentiment=sentiment,
                        confidence=compute_feature_confidence(final_conf, review.emoji_signals, f, sentiment),
                        excerpts=[]
                    )
                    for f in features
                ]

    except Exception as e:
        logger.error(f"[SentimentAgent] Critical Error: {e}")
        errors.append(str(e))

    logger.info(f"[SentimentAgent] Completed | {low_confidence_count} low-confidence reviews")

    state["analyzed_reviews"] = reviews
    state["errors"] = errors
    state["agent_messages"] = agent_messages
    state["progress"] = {
        **state.get("progress", {}),
        "sentiment_analysis": "complete",
        "mode": "hybrid_emoji_boosted",
        "low_confidence_count": low_confidence_count,
    }

    return state
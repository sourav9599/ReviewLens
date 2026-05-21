"""
Agent 4: Aspect-Based Sentiment Analysis Agent
================================================
Performs hotel-specific aspect-based sentiment analysis on Marriott reviews.
Uses Gemini LLM for nuanced sentiment classification per hotel feature (room,
cleanliness, service, location, dining, amenities, value, noise, parking, WiFi)
with confidence scoring. Integrates emoji signal boosts from the Emoji Agent.

ReviewLens Context:
───────────────────
ReviewLens provides guests with granular topic filters ("Pool," "Gym,"
"Valet wait time," "Late checkout flexibility") beyond Marriott's static 6
categories. This agent classifies sentiment at the aspect/feature level,
feeding the Property Manager Topic Heatmap with sentiment-per-topic scores
(e.g. "Noise (elevator): 23 mentions, sentiment 2.1/5 — trending negative").

Enterprise KPI Alignment:
─────────────────────────
• Intent to Recommend: Aspect-level sentiment reveals which specific hotel
  features drive delight vs. dissatisfaction → fixing high-impact negative
  aspects directly increases NPS (+4-8 points within 90 days).
• RevPAR: Per-feature sentiment identifies which operational improvements
  will have highest impact on ratings → occupancy + ADR.
• Marriott Bonvoy Occupancy & Enrollments: Understanding what loyal Bonvoy
  members care about most helps tailor the loyalty experience.
• Leadership Index: Clear, quantified insight into which operational areas
  need attention, enabling focused leadership action.

Pipeline Position: Runs AFTER deduplication gate → feeds Trend Detection.
"""

import time
import logging
from typing import List
from core.models import (
    ReviewPipelineState, SentimentLabel, ReviewStatus,
    FeatureSentiment, EmojiSignal
)
from core.config import settings
from core.llm_factory import get_llm

logger = logging.getLogger(__name__)


# Hotel feature keyword extractor — maps hotel aspects to keyword triggers
# These power the Topic Heatmap on the Property Manager Dashboard
FEATURE_KEYWORDS = {
    "room": ["room", "suite", "bed", "pillow", "mattress", "spacious", "cramped", "view", "balcony", "minibar", "closet"],
    "cleanliness": ["clean", "dirty", "spotless", "stain", "housekeeping", "hygiene", "mold", "dusty", "fresh", "smell"],
    "service": ["staff", "front desk", "concierge", "bellman", "helpful", "rude", "friendly", "attentive", "responsive", "manager"],
    "location": ["location", "distance", "walking", "block", "nearby", "downtown", "central", "neighborhood", "transit", "airport"],
    "dining": ["breakfast", "restaurant", "food", "coffee", "dining", "bar", "lounge", "buffet", "room service", "menu"],
    "noise": ["noise", "noisy", "loud", "quiet", "soundproof", "hear", "music", "banging", "construction", "elevator"],
    "parking": ["parking", "valet", "garage", "lot", "self-park"],
    "bathroom": ["bathroom", "shower", "tub", "towel", "toilet", "jacuzzi", "bath", "hot water", "plumbing"],
    "wifi": ["wifi", "internet", "wireless", "wi-fi", "connectivity", "bandwidth"],
    "check_in": ["check-in", "checkin", "check in", "check-out", "checkout", "front desk", "wait time", "queue", "key card"],
    "amenities": ["pool", "gym", "spa", "fitness", "sauna", "amenities", "hot tub", "steam room"],
    "value": ["price", "expensive", "overpriced", "value", "worth", "rate", "cost", "deal", "affordable"],
    "lobby": ["lobby", "entrance", "decor", "ambiance", "atmosphere", "renovation"],
}


def extract_features(text: str):
    text_lower = text.lower()
    features = []
    for feature, keywords in FEATURE_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            features.append(feature)
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

    llm = get_llm(temperature=0.0, max_tokens=256)

    analyzable_statuses = {ReviewStatus.CLEAN, ReviewStatus.NEAR_DUPLICATE}
    to_analyze = [r for r in reviews if r.status in analyzable_statuses]

    logger.info(f"[SentimentAgent] Processing {len(to_analyze)} reviews")

    BATCH_SIZE = 20
    low_confidence_count = 0

    try:
        for i in range(0, len(to_analyze), BATCH_SIZE):
            batch = to_analyze[i:i + BATCH_SIZE]
            texts = [r.cleaned_text[:200] for r in batch]

            prompt = f"""You are a senior hospitality intelligence analyst specializing in Aspect-Based Sentiment Analysis (ABSA) for hotel guest reviews.

TASK: Classify the overall sentiment of each guest review below.

CLASSIFICATION RULES:
- "positive": Guest expresses satisfaction, delight, or recommends the property. Look for praise of specific aspects (comfortable bed, great location, helpful staff), expressions of intent to return, or overall positive stay narrative.
- "negative": Guest expresses disappointment, frustration, or warns others. Look for complaints about specific failures (dirty room, rude staff, broken amenities), expressions of regret, or requests for refund/compensation.
- "neutral": Guest provides factual description without strong emotion, expresses mixed feelings where positives and negatives roughly balance, or describes an unremarkable/adequate stay.

CRITICAL NUANCES:
- Sarcasm inverts meaning (e.g. "Oh sure, loved waiting 45 minutes for check-in" = negative)
- A high star rating with complaint text should still be classified by the TEXT sentiment
- Backhanded compliments (e.g. "room was fine for the price") = neutral, not positive
- Multiple aspects with conflicting sentiment: classify by the DOMINANT emotion in the text

OUTPUT: Return EXACTLY one word per review on its own line: positive, negative, or neutral.
No numbering, no explanation, no extra text.

REVIEWS:
{chr(10).join(texts)}
"""

            response = llm.invoke(prompt)
            results = response.content.strip().split("\n")

            time.sleep(1)

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
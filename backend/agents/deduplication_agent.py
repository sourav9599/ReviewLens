"""
Agent 3: Deduplication & Bot Detection Agent
==============================================
Protects the integrity of Marriott hotel review analytics by removing exact
duplicates, near-duplicate reviews (fuzzy matching), and detecting bot/spam
reviews using multi-signal heuristic scoring with risk level classification.

ReviewLens Context:
───────────────────
ReviewLens surfaces dynamic topic clusters on Marriott.com where guests filter
reviews by "Pool," "Gym," "Valet," etc. Fake or duplicate reviews poison topic
frequency counts and sentiment scores. This agent ensures the Popular Mentions
feature and Property Manager Topic Heatmap reflect genuine guest experiences.

Enterprise KPI Alignment:
─────────────────────────
• Intent to Recommend: Removing fake reviews ensures the guest-facing review
  page reflects genuine experiences, maintaining trust and credibility.
• RevPAR: Fake positive reviews mask operational issues; removing them
  surfaces true problems that, when fixed, improve actual satisfaction.
• EBITDA Growth: Automated bot detection eliminates manual moderation.
• Digital Direct Share: Trustworthy reviews on Marriott.com differentiate
  it from third-party sites with known spam issues.
• Non-RevPAR Affiliation Fees: Clean review data strengthens the Marriott
  brand proposition for franchise owners considering affiliation.

Pipeline Position: Runs AFTER orchestrator_pre → feeds orchestrator_post_dedup.
"""
import re
import hashlib
from typing import List, Dict, Tuple
from collections import Counter
from rapidfuzz import fuzz
from core.models import (
    ReviewPipelineState, ProcessedReview, ReviewStatus,
    BotRiskLevel, AgentMessage
)
from core.config import settings
import logging
import uuid

logger = logging.getLogger(__name__)


def compute_fingerprint(text: str) -> str:
    """Compute a normalized fingerprint for exact duplicate detection."""
    normalized = re.sub(r'\s+', ' ', text.lower().strip())
    return hashlib.md5(normalized.encode()).hexdigest()


def compute_similarity(text1: str, text2: str) -> float:
    """Compute fuzzy similarity between two texts."""
    if not text1 or not text2:
        return 0.0
    return fuzz.token_sort_ratio(text1.lower(), text2.lower()) / 100.0


def compute_bot_score(review: ProcessedReview, all_reviews: List[ProcessedReview]) -> Tuple[float, List[str]]:
    """
    Enhanced heuristic bot detection.
    Returns (score 0.0-1.0, list of triggered signal names).
    """
    score = 0.0
    signals = []
    text = review.cleaned_text.lower()
    words = text.split()
    word_count = len(words)

    # Signal 0: Spam keywords (hotel-specific)
    spam_keywords = ["buy now", "limited offer", "best hotel ever", "hurry", "click here", "discount code", "free stay", "promo"]
    if any(k in text for k in spam_keywords):
        score += 0.4
        signals.append("spam_keywords")

    # Signal 1: Too short / too long (outlier length)
    if word_count < 5:
        score += 0.3
        signals.append("too_short")
    elif word_count > 300:
        score += 0.15
        signals.append("suspiciously_long")

    # Signal 2: Unnatural word repetition
    word_counter = Counter(words)
    if words:
        max_repeat_ratio = max(word_counter.values()) / max(word_count, 1)
        if max_repeat_ratio > 0.3:
            score += 0.25
            signals.append("word_repetition")

    # Signal 3: Generic template phrases (hotel context)
    generic_phrases = [
        "good hotel", "nice hotel", "best hotel", "worst hotel",
        "highly recommend", "do not recommend", "great value", "waste of money",
        "five stars", "one star", "amazing stay", "terrible stay",
        "perfect location", "worst experience"
    ]
    generic_matches = sum(1 for phrase in generic_phrases if phrase in text)
    if generic_matches >= 2 and word_count < 15:
        score += 0.25
        signals.append("generic_template")

    # Signal 4: All caps
    if "all_caps" in review.flags:
        score += 0.1
        signals.append("all_caps")

    # Signal 5: Excessive punctuation
    if text.count("!") >= 3:
        score += 0.2
        signals.append("excessive_exclamation")
    if text.count("?") >= 4:
        score += 0.1
        signals.append("excessive_question")

    # Signal 6: Near-duplicate flooding (same rating + similar text)
    if review.rating is not None:
        same_rating_similar = [
            r for r in all_reviews
            if r.id != review.id
            and r.rating == review.rating
            and compute_similarity(r.cleaned_text, review.cleaned_text) > 0.7
        ]
        if len(same_rating_similar) >= 2:
            score += 0.3
            signals.append("near_duplicate_flood")

    # Signal 7: No hotel feature mention (overly vague)
    feature_words = [
        "room", "bed", "clean", "staff", "breakfast", "pool", "wifi",
        "location", "parking", "check-in", "noise", "view", "bathroom",
        "service", "restaurant", "lobby", "spa", "gym", "elevator"
    ]
    if word_count >= 10 and not any(fw in text for fw in feature_words):
        if generic_matches >= 1:
            score += 0.1
            signals.append("vague_no_features")

    # Signal 8: Suspicious punctuation ratio
    punct_count = sum(1 for c in text if c in "!?.,;:")
    if word_count > 0 and punct_count / max(word_count, 1) > 0.5:
        score += 0.1
        signals.append("punctuation_abuse")

    return round(min(1.0, score), 3), signals


def classify_bot_risk(score: float) -> BotRiskLevel:
    if score >= settings.BOT_CRITICAL_THRESHOLD:
        return BotRiskLevel.CRITICAL
    elif score >= settings.BOT_HIGH_THRESHOLD:
        return BotRiskLevel.HIGH
    elif score >= settings.BOT_DETECTION_THRESHOLD:
        return BotRiskLevel.MEDIUM
    else:
        return BotRiskLevel.LOW


def deduplication_agent(state: ReviewPipelineState) -> ReviewPipelineState:
    reviews = state["preprocessed_reviews"]
    errors = list(state.get("errors", []))
    threshold = state["pipeline_config"].get("dedup_threshold", 0.85)
    bot_threshold = state["pipeline_config"].get("bot_threshold", settings.BOT_DETECTION_THRESHOLD)
    agent_messages = list(state.get("agent_messages", []))

    logger.info(f"[DeduplicationAgent] Processing {len(reviews)} reviews | threshold={threshold:.2f} bot_threshold={bot_threshold:.2f}")

    # Step 1: Exact duplicate detection
    seen_fingerprints: Dict[str, str] = {}
    for review in reviews:
        fp = compute_fingerprint(review.cleaned_text)
        if fp in seen_fingerprints:
            review.status = ReviewStatus.DUPLICATE
            review.duplicate_of = seen_fingerprints[fp]
        else:
            seen_fingerprints[fp] = review.id

    # Step 2: Near-duplicate detection
    clean_reviews = [r for r in reviews if r.status == ReviewStatus.CLEAN]

    for i, review_a in enumerate(clean_reviews):
        if review_a.status != ReviewStatus.CLEAN:
            continue
        for review_b in clean_reviews[i + 1:]:
            if review_b.status != ReviewStatus.CLEAN:
                continue
            sim = compute_similarity(review_a.cleaned_text, review_b.cleaned_text)
            if sim >= threshold:
                if len(review_b.cleaned_text) <= len(review_a.cleaned_text):
                    review_b.status = ReviewStatus.NEAR_DUPLICATE
                    review_b.duplicate_of = review_a.id
                else:
                    review_a.status = ReviewStatus.NEAR_DUPLICATE
                    review_a.duplicate_of = review_b.id
                    break

    # Step 3: Enhanced bot detection
    for review in reviews:
        bs, signals = compute_bot_score(review, reviews)
        review.bot_score = bs
        review.bot_signals = signals
        review.bot_risk_level = classify_bot_risk(bs)

        if bs >= bot_threshold:
            review.status = ReviewStatus.BOT_SUSPECTED
            if "bot_suspected" not in review.flags:
                review.flags.append("bot_suspected")

            # Emit to AgentBus
            agent_messages.append({
                "sender": "DeduplicationAgent",
                "event_type": "bot_detected",
                "payload": {
                    "review_id": review.id,
                    "score": bs,
                    "risk_level": review.bot_risk_level.value,
                    "signals": signals,
                }
            })

    # Step 4: Final stats
    deduplicated = reviews
    stats = Counter(r.status.value for r in deduplicated)
    bot_count = stats.get("bot_suspected", 0)
    dup_count = stats.get("duplicate", 0) + stats.get("near_duplicate", 0)

    logger.info(f"[DeduplicationAgent] Stats: {dict(stats)} | {bot_count} bots, {dup_count} duplicates")

    state["deduplicated_reviews"] = deduplicated
    state["errors"] = errors
    state["agent_messages"] = agent_messages
    state["progress"] = {
        **state.get("progress", {}),
        "deduplication": "complete",
        "duplicate_count": dup_count,
        "bot_count": bot_count,
        "bot_risk_breakdown": {
            "critical": sum(1 for r in reviews if r.bot_risk_level == BotRiskLevel.CRITICAL),
            "high": sum(1 for r in reviews if r.bot_risk_level == BotRiskLevel.HIGH),
            "medium": sum(1 for r in reviews if r.bot_risk_level == BotRiskLevel.MEDIUM),
            "low": sum(1 for r in reviews if r.bot_risk_level == BotRiskLevel.LOW),
        }
    }

    return state
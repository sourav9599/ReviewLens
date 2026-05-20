"""
Agent 2: Emoji Analysis Agent
===============================
Extracts emoji signals from raw Marriott hotel review text (before cleaning),
maps emojis to sentiment signals with confidence boosts, and enriches reviews.
Particularly relevant for reviews from younger demographics, social media
cross-posts, and international travelers where emoji usage conveys strong
sentiment that text analysis alone might miss.

ReviewLens Context:
───────────────────
Marriott serves a global guest base where emoji communication patterns vary.
A business traveler from Japan may use 🙇‍♂️ to indicate respect, while a
leisure traveler uses 😍 to express delight. Emoji signals boost sentiment
confidence, making the Property Manager Topic Heatmap more accurate.

Enterprise KPI Alignment:
─────────────────────────
• Intent to Recommend: Emoji-enriched sentiment scoring produces more accurate
  guest satisfaction signals (e.g. 😍 vs 😡), helping identify truly delighted
  guests who are likely to recommend.
• Marriott Bonvoy Occupancy & Enrollments: Younger Bonvoy members use emojis
  heavily; analyzing these signals ensures their feedback isn't lost.
• RevPAR: More accurate sentiment confidence means better prioritization of
  issues that actually impact bookings.

Pipeline Position: Runs AFTER preprocessing → feeds Orchestrator Pre-Analysis.
"""
import logging
from typing import List, Dict, Tuple
from collections import Counter
from core.models import (
    ReviewPipelineState, ProcessedReview,
    EmojiSignal, EmojiAnalysisSummary, SentimentLabel
)
from core.config import settings

logger = logging.getLogger(__name__)

# ─── Emoji → Sentiment Mapping ─────────────────────────────────────────────
# Maps emoji character → (sentiment, description, confidence_boost)
EMOJI_SENTIMENT_MAP: Dict[str, Tuple[SentimentLabel, str, float]] = {
    # Positive
    "😊": (SentimentLabel.POSITIVE, "smiling face", 0.15),
    "😍": (SentimentLabel.POSITIVE, "heart eyes / love", 0.20),
    "🥰": (SentimentLabel.POSITIVE, "loving face", 0.20),
    "😄": (SentimentLabel.POSITIVE, "happy / satisfied", 0.15),
    "😁": (SentimentLabel.POSITIVE, "big smile", 0.15),
    "👍": (SentimentLabel.POSITIVE, "thumbs up / approval", 0.20),
    "❤️": (SentimentLabel.POSITIVE, "love / strong positive", 0.20),
    "🧡": (SentimentLabel.POSITIVE, "positive warmth", 0.15),
    "💛": (SentimentLabel.POSITIVE, "positive warmth", 0.15),
    "💚": (SentimentLabel.POSITIVE, "approval / green light", 0.15),
    "💙": (SentimentLabel.POSITIVE, "calm positive", 0.12),
    "💜": (SentimentLabel.POSITIVE, "appreciation", 0.12),
    "⭐": (SentimentLabel.POSITIVE, "star rating / quality", 0.18),
    "🌟": (SentimentLabel.POSITIVE, "excellent", 0.18),
    "✨": (SentimentLabel.POSITIVE, "sparkle / impressive", 0.15),
    "🔥": (SentimentLabel.POSITIVE, "intense positive / amazing", 0.15),
    "💯": (SentimentLabel.POSITIVE, "perfect score", 0.25),
    "🎉": (SentimentLabel.POSITIVE, "celebration / delight", 0.18),
    "🎊": (SentimentLabel.POSITIVE, "celebration", 0.15),
    "🙌": (SentimentLabel.POSITIVE, "praise / excellent", 0.18),
    "👏": (SentimentLabel.POSITIVE, "applause / great job", 0.18),
    "😎": (SentimentLabel.POSITIVE, "cool / impressive", 0.12),
    "🤩": (SentimentLabel.POSITIVE, "amazed / super impressed", 0.22),
    "😻": (SentimentLabel.POSITIVE, "love it", 0.20),
    "💪": (SentimentLabel.POSITIVE, "strong / powerful product", 0.12),
    "✅": (SentimentLabel.POSITIVE, "confirmed positive", 0.20),
    "🏆": (SentimentLabel.POSITIVE, "best / winner", 0.22),
    "🌈": (SentimentLabel.POSITIVE, "wonderful variety", 0.10),
    "😀": (SentimentLabel.POSITIVE, "happy", 0.13),
    "😃": (SentimentLabel.POSITIVE, "very happy", 0.15),

    # Negative
    "😡": (SentimentLabel.NEGATIVE, "angry / very dissatisfied", 0.25),
    "🤬": (SentimentLabel.NEGATIVE, "furious / outraged", 0.28),
    "😤": (SentimentLabel.NEGATIVE, "frustrated", 0.20),
    "😠": (SentimentLabel.NEGATIVE, "angry", 0.22),
    "👎": (SentimentLabel.NEGATIVE, "thumbs down / disapproval", 0.25),
    "💔": (SentimentLabel.NEGATIVE, "heartbreak / disappointment", 0.22),
    "😞": (SentimentLabel.NEGATIVE, "disappointed", 0.18),
    "😟": (SentimentLabel.NEGATIVE, "worried / concerned", 0.15),
    "😩": (SentimentLabel.NEGATIVE, "exhausted / fed up", 0.18),
    "😭": (SentimentLabel.NEGATIVE, "crying / extremely unhappy", 0.20),
    "🤮": (SentimentLabel.NEGATIVE, "disgusted / terrible quality", 0.30),
    "🤢": (SentimentLabel.NEGATIVE, "disgusted / nauseating", 0.25),
    "💀": (SentimentLabel.NEGATIVE, "deadly bad / worst ever", 0.25),
    "🗑️": (SentimentLabel.NEGATIVE, "garbage / worthless", 0.28),
    "❌": (SentimentLabel.NEGATIVE, "wrong / failed", 0.22),
    "🚫": (SentimentLabel.NEGATIVE, "do not buy / prohibited", 0.25),
    "⚠️": (SentimentLabel.NEGATIVE, "warning / caution needed", 0.18),
    "😢": (SentimentLabel.NEGATIVE, "sad / unhappy", 0.18),
    "😿": (SentimentLabel.NEGATIVE, "sad cat / unhappy", 0.15),
    "🤦": (SentimentLabel.NEGATIVE, "facepalm / disbelief", 0.20),
    "🤦‍♀️": (SentimentLabel.NEGATIVE, "facepalm", 0.20),
    "🤦‍♂️": (SentimentLabel.NEGATIVE, "facepalm", 0.20),

    # Neutral / Mixed
    "🤔": (SentimentLabel.NEUTRAL, "thinking / uncertain", 0.05),
    "😐": (SentimentLabel.NEUTRAL, "neutral / indifferent", 0.08),
    "😑": (SentimentLabel.NEUTRAL, "expressionless / meh", 0.08),
    "🤷": (SentimentLabel.NEUTRAL, "unsure / mixed feelings", 0.05),
    "🤷‍♀️": (SentimentLabel.NEUTRAL, "unsure", 0.05),
    "🤷‍♂️": (SentimentLabel.NEUTRAL, "unsure", 0.05),
    "😶": (SentimentLabel.NEUTRAL, "silent / no opinion", 0.05),
    "💭": (SentimentLabel.NEUTRAL, "thinking / contemplating", 0.05),
    "📦": (SentimentLabel.NEUTRAL, "packaging mention", 0.05),
    "📱": (SentimentLabel.NEUTRAL, "device mention", 0.05),
    "⚡": (SentimentLabel.NEUTRAL, "fast / energetic", 0.05),
    "🔋": (SentimentLabel.NEUTRAL, "battery mention", 0.05),
}


def extract_emoji_signals(text: str) -> List[EmojiSignal]:
    """Extract and analyze emojis from review text."""
    signals = []
    seen = {}

    for char in text:
        if char in EMOJI_SENTIMENT_MAP:
            if char in seen:
                seen[char].count += 1
            else:
                sentiment, description, boost = EMOJI_SENTIMENT_MAP[char]
                signal = EmojiSignal(
                    emoji=char,
                    description=description,
                    sentiment=sentiment,
                    count=1,
                    confidence_boost=boost,
                )
                seen[char] = signal
                signals.append(signal)

    return signals


def compute_emoji_confidence_boost(
    signals: List[EmojiSignal],
    text_sentiment: SentimentLabel
) -> float:
    """
    Compute net confidence boost from emoji signals.
    Emojis that agree with text sentiment provide a boost.
    Emojis that conflict reduce the boost.
    """
    if not signals:
        return 0.0

    aligned_boost = 0.0
    conflict_penalty = 0.0

    for sig in signals:
        if sig.sentiment == text_sentiment:
            aligned_boost += sig.confidence_boost * sig.count
        elif sig.sentiment != SentimentLabel.NEUTRAL and sig.sentiment != text_sentiment:
            conflict_penalty += sig.confidence_boost * 0.5 * sig.count

    net = aligned_boost - conflict_penalty
    return round(max(0.0, min(settings.EMOJI_CONFIDENCE_BOOST * 2, net)), 3)


def emoji_analysis_agent(state: ReviewPipelineState) -> ReviewPipelineState:
    """
    Emoji Analysis Agent: Extracts emoji signals and enriches reviews.
    Runs AFTER preprocessing, BEFORE deduplication.
    """
    reviews = state["preprocessed_reviews"]
    errors = list(state.get("errors", []))
    agent_messages = list(state.get("agent_messages", []))

    logger.info(f"[EmojiAgent] Analyzing emojis in {len(reviews)} reviews")

    # ── Per-review emoji extraction ──────────────────────────────────────
    global_emoji_freq: Counter = Counter()
    total_emojis = 0
    reviews_with_emojis = 0
    boosts_applied = 0

    for review in reviews:
        signals = extract_emoji_signals(review.original_text)
        if signals:
            review.emoji_signals = signals
            review.emoji_count = sum(s.count for s in signals)
            reviews_with_emojis += 1
            total_emojis += review.emoji_count

            for sig in signals:
                global_emoji_freq[sig.emoji] += sig.count

            # Compute confidence boost (applied later by sentiment agent if sentiment known)
            # For now, tag the review with emoji data; SentimentAgent will use it
            net_boost = sum(s.confidence_boost for s in signals if s.sentiment != SentimentLabel.NEUTRAL)
            if net_boost > 0:
                boosts_applied += 1

            # Emit to bus
            agent_messages.append({
                "sender": "EmojiAgent",
                "event_type": "emoji_found",
                "payload": {
                    "review_id": review.id,
                    "emojis": [s.emoji for s in signals],
                    "count": review.emoji_count,
                    "net_boost": net_boost,
                }
            })

    # ── Build EmojiAnalysisSummary ────────────────────────────────────────
    emoji_sentiment_dist: Dict[str, int] = Counter()
    emoji_sentiment_map = {}

    for emoji_char, count in global_emoji_freq.items():
        if emoji_char in EMOJI_SENTIMENT_MAP:
            sentiment, _, _ = EMOJI_SENTIMENT_MAP[emoji_char]
            emoji_sentiment_dist[sentiment.value] += count
            emoji_sentiment_map[emoji_char] = sentiment.value

    total_emoji_count = sum(emoji_sentiment_dist.values()) or 1
    emoji_sentiment_pct = {k: round(v / total_emoji_count, 3) for k, v in emoji_sentiment_dist.items()}

    top_positive = [
        e for e, _ in global_emoji_freq.most_common(20)
        if EMOJI_SENTIMENT_MAP.get(e, (SentimentLabel.NEUTRAL,))[0] == SentimentLabel.POSITIVE
    ][:5]

    top_negative = [
        e for e, _ in global_emoji_freq.most_common(20)
        if EMOJI_SENTIMENT_MAP.get(e, (SentimentLabel.NEUTRAL,))[0] == SentimentLabel.NEGATIVE
    ][:5]

    emoji_summary = EmojiAnalysisSummary(
        total_emojis_found=total_emojis,
        unique_emojis=len(global_emoji_freq),
        emoji_frequency=dict(global_emoji_freq.most_common(30)),
        emoji_sentiment_map=emoji_sentiment_map,
        top_positive_emojis=top_positive,
        top_negative_emojis=top_negative,
        reviews_with_emojis=reviews_with_emojis,
        emoji_confidence_boosts_applied=boosts_applied,
        emoji_sentiment_distribution=emoji_sentiment_pct,
    )

    logger.info(
        f"[EmojiAgent] Done: {total_emojis} emojis in {reviews_with_emojis} reviews, "
        f"{len(global_emoji_freq)} unique, {boosts_applied} confidence boosts queued"
    )

    state["emoji_analysis"] = emoji_summary
    state["preprocessed_reviews"] = reviews
    state["agent_messages"] = agent_messages
    state["errors"] = errors
    state["progress"] = {
        **state.get("progress", {}),
        "emoji_analysis": "complete",
        "emojis_found": total_emojis,
        "reviews_with_emojis": reviews_with_emojis,
    }

    return state

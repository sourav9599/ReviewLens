"""
Agent 10: Incremental Summary Agent (Map-Reduce)
==================================================
Generates scalable hotel review summaries using a two-phase approach:

Phase 1 (Map): After each ingestion batch, produces a lightweight "batch digest"
— a compressed statistical + qualitative snapshot of that batch (~500 tokens).
This avoids re-processing all reviews on every summary request.

Phase 2 (Reduce): When a summary is requested, aggregates all batch digests for
the hotel into a final narrative summary using a single LLM call. For hotels with
many digests (>20), uses hierarchical reduction.

ReviewLens Context:
───────────────────
The Architecture Guide specifies: "Once you have calculated the master JSON for a
specific hotel, cache that payload. You can then invalidate or update this cache
periodically via a cron job as new reviews come in."

This agent implements exactly that — each pipeline run adds one digest, and the
summary endpoint serves from cache until new digests arrive.

Enterprise KPI Alignment:
─────────────────────────
• Digital Direct Share: Instant narrative summaries on Marriott.com match the
  browsing experience of OTAs like TripAdvisor, keeping guests on direct channel.
• Intent to Recommend: Summaries surface highlights/lowlights that set accurate
  expectations, reducing post-stay disappointment.
• EBITDA Growth: Incremental digests avoid expensive full-dataset LLM calls;
  cost per summary read is zero (served from cache).

Pipeline Position: Runs AFTER hotel_json_export → END.
"""
import json
import os
import uuid
import time
import logging
from typing import List, Dict, Any
from collections import Counter
from datetime import datetime

from langchain_core.messages import HumanMessage

from core.config import settings
from core.models import ReviewPipelineState, ReviewStatus, SentimentLabel
from core.llm_factory import get_llm

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DIGESTS_FILE = os.path.join(DATA_DIR, "batch_digests.json")
SUMMARY_CACHE_FILE = os.path.join(DATA_DIR, "summary_cache.json")


# ─── Storage Helpers ──────────────────────────────────────────────────────────

def _load_digests() -> List[Dict[str, Any]]:
    if not os.path.exists(DIGESTS_FILE):
        return []
    try:
        with open(DIGESTS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def _save_digests(digests: List[Dict[str, Any]]):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(DIGESTS_FILE, "w") as f:
        json.dump(digests, f, indent=2, default=str)


def _load_summary_cache() -> Dict[str, Any]:
    if not os.path.exists(SUMMARY_CACHE_FILE):
        return {}
    try:
        with open(SUMMARY_CACHE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def _save_summary_cache(cache: Dict[str, Any]):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(SUMMARY_CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2, default=str)


def invalidate_summary_cache(hotel_id: str):
    """Mark a hotel's cached summary as stale. Called after new reviews are exported."""
    cache = _load_summary_cache()
    if hotel_id in cache:
        cache[hotel_id]["is_stale"] = True
        cache[hotel_id]["stale_since"] = datetime.utcnow().isoformat()
        _save_summary_cache(cache)
        logger.info(f"[SummaryAgent] Cache invalidated for hotel '{hotel_id}'")


# ─── Phase 1: Batch Digest Generation (Map) ──────────────────────────────────

def generate_batch_digest(state: ReviewPipelineState) -> ReviewPipelineState:
    """
    Map Phase: Generates a compact statistical digest of the current batch.
    Runs as a pipeline node AFTER export. Uses the already-analyzed reviews
    (sentiment, mentions, categories) to build the digest without extra LLM calls
    for statistics. One LLM call extracts representative excerpts.
    """
    reviews = state["analyzed_reviews"]
    hotel_id = state["pipeline_config"].get("hotel_id", "hotel_default")

    analyzable = [
        r for r in reviews
        if r.status not in {ReviewStatus.DUPLICATE, ReviewStatus.BOT_SUSPECTED}
    ]

    if not analyzable:
        logger.warning("[SummaryAgent] No analyzable reviews for digest generation")
        state["progress"] = {**state.get("progress", {}), "summary_digest": "skipped"}
        return state

    logger.info(f"[SummaryAgent] Generating batch digest for {len(analyzable)} reviews")

    # Compute statistics from already-processed data
    sentiment_counts = Counter(r.overall_sentiment.value for r in analyzable)
    total = len(analyzable)
    sentiment_distribution = {k: round(v / total, 3) for k, v in sentiment_counts.items()}

    ratings = [r.rating for r in analyzable if r.rating is not None]
    avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else None

    # Aggregate sub-ratings
    sub_rating_sums: Dict[str, float] = {}
    sub_rating_counts: Dict[str, int] = {}
    for r in analyzable:
        for key, val in r.sub_ratings.items():
            sub_rating_sums[key] = sub_rating_sums.get(key, 0) + val
            sub_rating_counts[key] = sub_rating_counts.get(key, 0) + 1
    sub_ratings_avg = {
        k: round(sub_rating_sums[k] / sub_rating_counts[k], 2)
        for k in sub_rating_sums
    }

    # Aggregate mentions
    mention_counter: Counter = Counter()
    for r in analyzable:
        for f in r.flags:
            if f.startswith("mention:"):
                mention_counter[f[8:]] += 1
    top_mentions = [{"mention": m, "count": c} for m, c in mention_counter.most_common(15)]

    # Category sentiments (majority vote per category)
    cat_sentiments: Dict[str, Counter] = {}
    for r in analyzable:
        for fs in r.feature_sentiments:
            if fs.feature not in cat_sentiments:
                cat_sentiments[fs.feature] = Counter()
            cat_sentiments[fs.feature][fs.sentiment.value] += 1
    category_sentiments = {
        cat: counts.most_common(1)[0][0]
        for cat, counts in cat_sentiments.items()
        if counts
    }

    # Collect sample excerpts (positive and negative)
    positive_excerpts = []
    negative_excerpts = []
    for r in analyzable:
        text_snippet = r.cleaned_text[:120]
        if r.overall_sentiment == SentimentLabel.POSITIVE and len(positive_excerpts) < 3:
            positive_excerpts.append(text_snippet)
        elif r.overall_sentiment == SentimentLabel.NEGATIVE and len(negative_excerpts) < 3:
            negative_excerpts.append(text_snippet)

    # Determine top complaints and praises from mentions + sentiment
    complaints = []
    praises = []
    for r in analyzable:
        review_mentions = [f[8:] for f in r.flags if f.startswith("mention:")]
        if r.overall_sentiment == SentimentLabel.NEGATIVE:
            complaints.extend(review_mentions[:2])
        elif r.overall_sentiment == SentimentLabel.POSITIVE:
            praises.extend(review_mentions[:2])
    top_complaints = [m for m, _ in Counter(complaints).most_common(5)]
    top_praises = [m for m, _ in Counter(praises).most_common(5)]

    # Date range
    dates = [r.review_date for r in analyzable if r.review_date]
    date_range = {}
    if dates:
        sorted_dates = sorted(dates)
        date_range = {"earliest": sorted_dates[0][:10], "latest": sorted_dates[-1][:10]}

    # Hotel name from first review
    hotel_name = analyzable[0].product_name if analyzable else "Unknown Hotel"

    digest = {
        "digest_id": f"batch_{uuid.uuid4().hex[:8]}",
        "hotel_id": hotel_id,
        "hotel_name": hotel_name,
        "created_at": datetime.utcnow().isoformat(),
        "review_count": total,
        "sentiment_distribution": sentiment_distribution,
        "avg_rating": avg_rating,
        "sub_ratings_avg": sub_ratings_avg,
        "top_mentions": top_mentions,
        "top_complaints": top_complaints,
        "top_praises": top_praises,
        "category_sentiments": category_sentiments,
        "sample_positive_excerpts": positive_excerpts,
        "sample_negative_excerpts": negative_excerpts,
        "date_range": date_range,
    }

    # Persist digest
    all_digests = _load_digests()
    all_digests.append(digest)
    _save_digests(all_digests)

    # Invalidate cached summary for this hotel
    invalidate_summary_cache(hotel_id)

    logger.info(f"[SummaryAgent] Digest '{digest['digest_id']}' saved ({total} reviews)")

    state["progress"] = {
        **state.get("progress", {}),
        "summary_digest": "complete",
        "digest_id": digest["digest_id"],
    }
    return state


# ─── Phase 2: Summary Aggregation (Reduce) ───────────────────────────────────

REDUCE_PROMPT = """You are a senior editorial writer for a premium hotel review platform (similar to TripAdvisor's AI Review Summary).
Your job is to synthesize guest review data into a polished, publication-ready hotel summary that reads naturally — as if written by an experienced travel editor who has personally read hundreds of guest reviews.

WRITING RULES:
- Write in a warm, authoritative third-person editorial voice.
- NEVER quote raw data phrases in quotation marks (e.g. never write "friendly staff" — instead write: Guests consistently praise the attentive, welcoming service team.)
- NEVER reference percentages, statistics, or numerical counts (e.g. never write "50% positive" or "mentioned 12 times").
- DO weave specific details naturally into flowing prose (mention actual amenities, room features, neighborhood landmarks).
- DO acknowledge both strengths and weaknesses with balanced, professional tone.
- The narrative should feel like reading a polished TripAdvisor summary panel — concise, insightful, and immediately useful for someone deciding whether to book.
- Each category descriptor should be exactly 1-2 evocative words (e.g. "Spotless", "Walkable", "Outdated", "Warm & Attentive").

Hotel: {hotel_name}
Total guest reviews analyzed: {total_reviews}

AGGREGATED REVIEW DATA:
{digests_text}

Generate a JSON response with this EXACT structure (return ONLY valid JSON, no markdown, no backticks):
{{
    "narrative_summary": "A 2-paragraph editorial summary. Paragraph 1: What guests love — weave together the property's strongest attributes into flowing prose that paints a picture of the stay experience. Paragraph 2: Where the property falls short — acknowledge shortcomings honestly but constructively, noting any patterns. Keep total length to 80-120 words.",
    "categories": {{
        "Location": "1-2 word descriptor",
        "Rooms": "1-2 word descriptor",
        "Cleanliness": "1-2 word descriptor",
        "Service": "1-2 word descriptor",
        "Dining": "1-2 word descriptor",
        "Value": "1-2 word descriptor"
    }},
    "highlights": ["strength 1 as natural phrase", "strength 2", "strength 3"],
    "lowlights": ["concern 1 as natural phrase", "concern 2", "concern 3"],
    "verdict": "One compelling sentence a traveler would find useful when deciding whether to book — specific to this property's character."
}}"""


def aggregate_hotel_summary(hotel_id: str, force_refresh: bool = False) -> Dict[str, Any]:
    """
    Reduce Phase: Aggregates all batch digests for a hotel into a final summary.
    Returns cached result if available and fresh.
    """
    cache = _load_summary_cache()

    # Check cache freshness
    if not force_refresh and hotel_id in cache:
        cached = cache[hotel_id]
        if not cached.get("is_stale", True):
            logger.info(f"[SummaryAgent] Serving cached summary for '{hotel_id}'")
            return cached

    # Load all digests for this hotel
    all_digests = _load_digests()
    hotel_digests = [d for d in all_digests if d.get("hotel_id") == hotel_id]

    if not hotel_digests:
        return {
            "hotel_id": hotel_id,
            "error": "No review data available for this hotel. Ingest reviews first.",
            "total_reviews_summarized": 0,
        }

    total_reviews = sum(d.get("review_count", 0) for d in hotel_digests)
    hotel_name = hotel_digests[-1].get("hotel_name", "Unknown Hotel")

    # Compute aggregate sub-ratings and avg rating across all digests
    all_ratings = [d["avg_rating"] for d in hotel_digests if d.get("avg_rating") is not None]
    overall_avg_rating = round(sum(all_ratings) / len(all_ratings), 2) if all_ratings else None

    sub_rating_totals: Dict[str, List[float]] = {}
    for d in hotel_digests:
        for key, val in d.get("sub_ratings_avg", {}).items():
            if key not in sub_rating_totals:
                sub_rating_totals[key] = []
            sub_rating_totals[key].append(val)
    overall_sub_ratings = {
        k: round(sum(v) / len(v), 2) for k, v in sub_rating_totals.items()
    }

    # Format digests for LLM (exclude embeddings/large fields)
    digests_for_prompt = []
    for d in hotel_digests:
        compact = {
            "batch": d["digest_id"],
            "reviews": d["review_count"],
            "sentiment": d["sentiment_distribution"],
            "avg_rating": d["avg_rating"],
            "top_mentions": [m["mention"] for m in d.get("top_mentions", [])[:8]],
            "complaints": d.get("top_complaints", []),
            "praises": d.get("top_praises", []),
            "categories": d.get("category_sentiments", {}),
            "positive_samples": d.get("sample_positive_excerpts", []),
            "negative_samples": d.get("sample_negative_excerpts", []),
        }
        digests_for_prompt.append(compact)

    # Hierarchical reduction if too many digests
    if len(digests_for_prompt) > 20:
        digests_for_prompt = _hierarchical_reduce(digests_for_prompt, hotel_name, hotel_id)

    digests_text = json.dumps(digests_for_prompt, indent=2)

    try:
        llm = get_llm(temperature=0.3, max_tokens=1024)

        prompt = REDUCE_PROMPT.format(
            hotel_name=hotel_name,
            total_reviews=total_reviews,
            digests_text=digests_text,
        )

        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content.strip()
        content = content.lstrip("```json").lstrip("```").rstrip("```").strip()
        summary_data = json.loads(content)

        time.sleep(1)

    except Exception as e:
        logger.error(f"[SummaryAgent] LLM aggregation failed: {e}")
        summary_data = _fallback_summary(hotel_digests)

    # Build final summary object
    final_summary = {
        "hotel_id": hotel_id,
        "hotel_name": hotel_name,
        "generated_at": datetime.utcnow().isoformat(),
        "total_reviews_summarized": total_reviews,
        "digest_count": len(hotel_digests),
        "narrative_summary": summary_data.get("narrative_summary", ""),
        "categories": summary_data.get("categories", {}),
        "highlights": summary_data.get("highlights", []),
        "lowlights": summary_data.get("lowlights", []),
        "avg_rating": overall_avg_rating,
        "sub_ratings_avg": overall_sub_ratings,
        "verdict": summary_data.get("verdict", ""),
        "is_stale": False,
        "last_digest_id": hotel_digests[-1]["digest_id"],
    }

    # Cache the result
    cache[hotel_id] = final_summary
    _save_summary_cache(cache)

    logger.info(f"[SummaryAgent] Generated fresh summary for '{hotel_id}' ({total_reviews} reviews, {len(hotel_digests)} digests)")
    return final_summary


def _hierarchical_reduce(digests: List[Dict], hotel_name: str, hotel_id: str) -> List[Dict]:
    """For large numbers of digests, merge groups of 10 into intermediate summaries."""
    _ = hotel_name, hotel_id  # reserved for future hierarchical LLM calls
    GROUP_SIZE = 10
    merged = []

    for i in range(0, len(digests), GROUP_SIZE):
        group = digests[i:i + GROUP_SIZE]
        total_reviews = sum(d.get("reviews", 0) for d in group)
        all_mentions = []
        all_complaints = []
        all_praises = []
        sentiment_agg: Counter = Counter()

        for d in group:
            all_mentions.extend(d.get("top_mentions", []))
            all_complaints.extend(d.get("complaints", []))
            all_praises.extend(d.get("praises", []))
            for sent, pct in d.get("sentiment", {}).items():
                sentiment_agg[sent] += pct

        total_pct = sum(sentiment_agg.values()) or 1
        merged_sentiment = {k: round(v / total_pct, 3) for k, v in sentiment_agg.items()}

        merged.append({
            "batch": f"merged_group_{i // GROUP_SIZE}",
            "reviews": total_reviews,
            "sentiment": merged_sentiment,
            "top_mentions": [m for m, _ in Counter(all_mentions).most_common(8)],
            "complaints": [m for m, _ in Counter(all_complaints).most_common(5)],
            "praises": [m for m, _ in Counter(all_praises).most_common(5)],
            "positive_samples": group[-1].get("positive_samples", []),
            "negative_samples": group[-1].get("negative_samples", []),
        })

    return merged


def _fallback_summary(digests: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Rule-based fallback when LLM fails."""
    all_mentions = Counter()
    all_complaints = []
    all_praises = []
    sentiment_agg: Counter = Counter()

    for d in digests:
        for m in d.get("top_mentions", []):
            all_mentions[m["mention"]] += m["count"]
        all_complaints.extend(d.get("top_complaints", []))
        all_praises.extend(d.get("top_praises", []))
        for sent, pct in d.get("sentiment_distribution", {}).items():
            sentiment_agg[sent] += pct

    top_praise_list = [m for m, _ in Counter(all_praises).most_common(3)]
    top_complaint_list = [m for m, _ in Counter(all_complaints).most_common(3)]

    total_pct = sum(sentiment_agg.values()) or 1
    pos_pct = sentiment_agg.get("positive", 0) / total_pct

    if pos_pct > 0.6:
        tone = "overwhelmingly positive"
    elif pos_pct > 0.4:
        tone = "generally favorable with some notable concerns"
    else:
        tone = "mixed, with significant areas for improvement"

    praise_prose = ", ".join(top_praise_list[:3]) if top_praise_list else "the overall experience"
    complaint_prose = ", ".join(top_complaint_list[:3]) if top_complaint_list else "minor operational issues"

    narrative = (
        f"Guest feedback is {tone}. Travelers particularly appreciate {praise_prose}, "
        f"which contribute to the property's appeal. "
        f"However, some guests note concerns around {complaint_prose} that may affect the stay experience."
    )

    return {
        "narrative_summary": narrative,
        "categories": {},
        "highlights": top_praise_list,
        "lowlights": top_complaint_list,
        "verdict": "Consider this property if the highlights align with your travel priorities.",
    }

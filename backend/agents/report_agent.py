"""
Agent 6: Report Synthesis Agent (Enhanced)
- Aggregates all agent outputs into a unified AnalysisReport
- Includes emoji_analysis, orchestrator_decisions, cross_product_comparison
- Computes final statistics and feature summaries
"""
import uuid
import time
from typing import List, Dict, Any
from collections import defaultdict, Counter
from core.models import (
    ReviewPipelineState, AnalysisReport, ProcessedReview,
    SentimentLabel, ReviewStatus, OrchestratorDecision
)
import logging

logger = logging.getLogger(__name__)


def build_feature_summary(reviews: List[ProcessedReview]) -> Dict[str, Dict[str, Any]]:
    """Build per-feature summary statistics with confidence scores."""
    feature_data: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
        "total_mentions": 0,
        "positive": 0,
        "negative": 0,
        "neutral": 0,
        "mixed": 0,
        "sarcastic": 0,
        "ambiguous": 0,
        "avg_confidence": 0.0,
        "complaint_rate": 0.0,
        "praise_rate": 0.0,
        "top_excerpts": [],
        "representative_reviews": []
    })

    feature_confidences: Dict[str, List[float]] = defaultdict(list)
    feature_excerpts: Dict[str, List[str]] = defaultdict(list)

    for review in reviews:
        if review.status in {ReviewStatus.DUPLICATE, ReviewStatus.BOT_SUSPECTED}:
            continue
        for fs in review.feature_sentiments:
            feat = fs.feature
            feature_data[feat]["total_mentions"] += 1
            sentiment_key = fs.sentiment.value
            if sentiment_key in feature_data[feat]:
                feature_data[feat][sentiment_key] += 1
            feature_confidences[feat].append(fs.confidence)
            feature_excerpts[feat].extend(fs.excerpts[:2])

            if len(feature_data[feat]["representative_reviews"]) < 3:
                feature_data[feat]["representative_reviews"].append({
                    "review_id": review.id,
                    "sentiment": sentiment_key,
                    "excerpt": review.cleaned_text[:100],
                    "confidence": fs.confidence,
                    "emoji_count": review.emoji_count,
                })

    # Compute rates and avg confidence
    for feat, data in feature_data.items():
        total = max(data["total_mentions"], 1)
        data["complaint_rate"] = round(data["negative"] / total, 3)
        data["praise_rate"] = round(data["positive"] / total, 3)
        data["avg_confidence"] = round(
            sum(feature_confidences[feat]) / max(len(feature_confidences[feat]), 1), 3
        )
        seen = set()
        unique_excerpts = []
        for ex in feature_excerpts[feat]:
            if ex.lower() not in seen and ex.strip():
                seen.add(ex.lower())
                unique_excerpts.append(ex)
        data["top_excerpts"] = unique_excerpts[:5]

    return dict(feature_data)


def report_synthesis_agent(state: ReviewPipelineState) -> ReviewPipelineState:
    """
    Report Synthesis Agent: Assembles the final AnalysisReport from all agent outputs.
    """
    start_time = state["pipeline_config"].get("start_time", time.time())
    reviews = state["analyzed_reviews"]
    trend_data = state["trend_data"]
    alerts = state["trend_alerts"]
    recommendations = state["recommendations"]
    orchestrator_decisions = state.get("orchestrator_decisions", [])
    emoji_analysis = state.get("emoji_analysis")
    cross_comparison = state.get("cross_product_comparison")
    agent_messages = state.get("agent_messages", [])

    logger.info("[ReportAgent] Synthesizing final report...")

    total = len(reviews)
    status_counts = Counter(r.status.value for r in reviews)
    clean_reviews = [
        r for r in reviews
        if r.status not in {ReviewStatus.DUPLICATE, ReviewStatus.BOT_SUSPECTED}
    ]

    sentiment_dist = Counter(r.overall_sentiment.value for r in clean_reviews)
    total_clean = max(len(clean_reviews), 1)
    overall_sentiment_distribution = {
        k: round(v / total_clean, 3) for k, v in sentiment_dist.items()
    }

    all_langs = set()
    for r in reviews:
        all_langs.update(r.detected_languages)

    categories = list(set(r.product_category for r in reviews if r.product_category and r.product_category != "Unknown"))
    feature_summary = build_feature_summary(reviews)

    # Build enhanced agent trace
    progress = state.get("progress", {})
    agent_trace = [
        {"agent": "PreprocessingAgent", "output": progress.get("preprocessing", "unknown"), "count": progress.get("preprocessed_count", 0)},
        {"agent": "EmojiAgent", "output": progress.get("emoji_analysis", "unknown"), "emojis": progress.get("emojis_found", 0), "reviews_with_emojis": progress.get("reviews_with_emojis", 0)},
        {"agent": "OrchestratorAgent (Pre)", "output": progress.get("orchestrator_pre", "unknown"), "decisions": len([d for d in orchestrator_decisions if d.phase == "pre_analysis"])},
        {"agent": "DeduplicationAgent", "output": progress.get("deduplication", "unknown"), "duplicates": progress.get("duplicate_count", 0), "bots": progress.get("bot_count", 0)},
        {"agent": "OrchestratorAgent (Post-Dedup)", "output": progress.get("orchestrator_post_dedup", "unknown"), "route": progress.get("route", "proceed")},
        {"agent": "SentimentAgent", "output": progress.get("sentiment_analysis", "unknown"), "low_confidence": progress.get("low_confidence_count", 0)},
        {"agent": "OrchestratorAgent (Post-Sentiment)", "output": progress.get("orchestrator_post_sentiment", "unknown"), "avg_confidence": progress.get("avg_confidence", 0)},
        {"agent": "TrendAgent", "output": progress.get("trend_detection", "unknown"), "alerts": progress.get("alert_count", 0)},
        {"agent": "OrchestratorAgent (Post-Trend)", "output": progress.get("orchestrator_post_trend", "unknown")},
        {"agent": "RecommendationAgent", "output": progress.get("recommendations", "unknown"), "recommendations": progress.get("recommendation_count", 0)},
        {"agent": "CrossComparisonAgent", "output": progress.get("cross_comparison", "unknown"), "categories": progress.get("categories_compared", 0)},
        {"agent": "ReportAgent", "output": "complete"},
    ]

    report = AnalysisReport(
        report_id=str(uuid.uuid4())[:12],
        created_at=__import__("datetime").datetime.utcnow().isoformat(),
        total_reviews=total,
        clean_reviews=len(clean_reviews),
        duplicate_count=status_counts.get("duplicate", 0) + status_counts.get("near_duplicate", 0),
        bot_suspected_count=status_counts.get("bot_suspected", 0),
        flagged_count=status_counts.get("flagged", 0),
        languages_detected=sorted(all_langs),
        product_categories=categories,
        overall_sentiment_distribution=overall_sentiment_distribution,
        feature_summary=feature_summary,
        trend_alerts=alerts,
        trend_data=trend_data,
        recommendations=recommendations,
        processed_reviews=reviews,
        processing_time_seconds=round(time.time() - start_time, 2),
        agent_trace=agent_trace,
        orchestrator_decisions=orchestrator_decisions,
        emoji_analysis=emoji_analysis,
        cross_product_comparison=cross_comparison,
        feedback_loops_triggered=state.get("feedback_loop_count", 0),
        pipeline_version="2.0-agentic",
    )

    logger.info(
        f"[ReportAgent] Report {report.report_id} | {total} reviews | "
        f"{len(alerts)} alerts | {len(recommendations)} recs | "
        f"{len(orchestrator_decisions)} orchestrator decisions | "
        f"feedback loops: {report.feedback_loops_triggered}"
    )

    state["report"] = report
    state["progress"] = {**progress, "report": "complete"}

    return state

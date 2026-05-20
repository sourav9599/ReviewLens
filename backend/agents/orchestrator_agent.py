"""
Orchestrator / Controller Agent — Pipeline Intelligence Hub
=============================================================
Dynamic decision-making agent that acts as the operational brain of the
ReviewLens hotel review pipeline. Assesses data quality at key pipeline
junctions and routes processing dynamically based on real-time signals
from upstream agents.

ReviewLens Context:
───────────────────
At Marriott's scale (~10M reviews/month across 9,000 properties), not every
review batch needs the same processing depth. This agent optimizes compute
costs by dynamically routing: small batches skip trend detection, high bot-rate
batches trigger feedback loops, and low-confidence datasets get flagged before
expensive recommendation generation. This keeps inference costs within the
~$0.003/1K tokens budget at scale.

Dynamic Decision Making:
  - Assesses data quality after each pipeline phase
  - Routes pipeline dynamically (feedback loops, skips, escalations)
  - Tracks all decisions in OrchestratorDecision log
  - Communicates with other agents via AgentBus

Inter-Agent Communication:
  - Subscribes to bot_detected, low_confidence, alert_raised events
  - Emits quality_check events for downstream agents

Enterprise KPI Alignment:
─────────────────────────
• EBITDA Growth: Intelligent routing optimizes compute costs and reduces
  API spend on LLM calls (skip unnecessary processing at scale).
• RevPAR: Quality gates ensure only high-confidence insights reach the
  Property Manager Dashboard, preventing false signals.
• Leadership Index: Full decision auditability (OrchestratorDecision log)
  provides transparency into AI reasoning, building leadership trust in
  automated operational intelligence.

Pipeline Position: Operates at 4 checkpoints across the pipeline flow.
"""
import uuid
import logging
from typing import Dict, Any, List
from collections import Counter
from core.models import (
    ReviewPipelineState, OrchestratorDecision, ProcessedReview,
    ReviewStatus, SentimentLabel
)
from core.config import settings

logger = logging.getLogger(__name__)


def _make_decision(
    phase: str, decision: str, reason: str, action: str,
    affected_agents: List[str] = None, metadata: Dict = None
) -> OrchestratorDecision:
    return OrchestratorDecision(
        decision_id=str(uuid.uuid4())[:8],
        phase=phase,
        decision=decision,
        reason=reason,
        action=action,
        affected_agents=affected_agents or [],
        metadata=metadata or {},
    )


def assess_data_quality(reviews: List[ProcessedReview]) -> Dict[str, Any]:
    """Compute quality metrics from the current review set."""
    if not reviews:
        return {"total": 0, "bot_rate": 0.0, "avg_confidence": 0.0, "clean_rate": 0.0}

    total = len(reviews)
    bot_count = sum(1 for r in reviews if r.status == ReviewStatus.BOT_SUSPECTED)
    clean_count = sum(1 for r in reviews if r.status == ReviewStatus.CLEAN)

    analyzable = [r for r in reviews if r.status not in {ReviewStatus.DUPLICATE, ReviewStatus.BOT_SUSPECTED}]
    avg_confidence = (
        sum(r.overall_confidence for r in analyzable) / len(analyzable)
        if analyzable else 0.0
    )

    return {
        "total": total,
        "bot_rate": round(bot_count / total, 3),
        "clean_rate": round(clean_count / total, 3),
        "avg_confidence": round(avg_confidence, 3),
        "analyzable": len(analyzable),
        "bot_count": bot_count,
    }


def orchestrator_pre_analysis(state: ReviewPipelineState) -> ReviewPipelineState:
    """
    Phase 1: Orchestrator runs AFTER preprocessing.
    Decides: Should we tighten dedup threshold? Skip if data is too noisy?
    """
    reviews = state["preprocessed_reviews"]
    decisions = list(state.get("orchestrator_decisions", []))
    messages = list(state.get("agent_messages", []))
    config = dict(state["pipeline_config"])
    errors = list(state.get("errors", []))

    logger.info(f"[Orchestrator] PRE-ANALYSIS phase — evaluating {len(reviews)} preprocessed reviews")

    # Assess raw quality
    quality = assess_data_quality(reviews)

    # Check language diversity
    lang_counts = Counter(r.language for r in reviews)
    dominant_lang = lang_counts.most_common(1)[0][0] if lang_counts else "en"
    multilang = len(lang_counts) > 1

    # DECISION 1: Too few reviews → skip trend detection
    if len(reviews) < 10:
        decisions.append(_make_decision(
            phase="pre_analysis",
            decision="skip_trend_detection",
            reason=f"Only {len(reviews)} reviews — insufficient for trend windows",
            action="route",
            affected_agents=["TrendAgent"],
            metadata={"review_count": len(reviews)}
        ))
        config["skip_trend"] = True
        logger.info("[Orchestrator] DECISION: skip trend detection (too few reviews)")

    # DECISION 2: Multilingual dataset → set language-aware mode
    if multilang:
        decisions.append(_make_decision(
            phase="pre_analysis",
            decision="enable_multilingual_mode",
            reason=f"Detected {len(lang_counts)} languages: {list(lang_counts.keys())}",
            action="route",
            affected_agents=["SentimentAgent"],
            metadata={"languages": dict(lang_counts)}
        ))
        config["multilingual_mode"] = True
        logger.info(f"[Orchestrator] DECISION: multilingual mode enabled for {list(lang_counts.keys())}")

    # DECISION 3: Large dataset → enable cross-comparison
    category_counts = Counter(r.product_category for r in reviews if r.product_category and r.product_category != "Unknown")
    if len(category_counts) >= settings.MIN_CROSS_COMPARE_CATEGORIES:
        decisions.append(_make_decision(
            phase="pre_analysis",
            decision="enable_cross_comparison",
            reason=f"Found {len(category_counts)} product categories: {list(category_counts.keys())}",
            action="route",
            affected_agents=["CrossComparisonAgent"],
            metadata={"categories": dict(category_counts)}
        ))
        config["run_cross_comparison"] = True
        logger.info(f"[Orchestrator] DECISION: cross-comparison enabled for {len(category_counts)} categories")
    else:
        config["run_cross_comparison"] = False

    state["orchestrator_decisions"] = decisions
    state["agent_messages"] = messages
    state["pipeline_config"] = config
    state["errors"] = errors
    state["progress"] = {
        **state.get("progress", {}),
        "orchestrator_pre": "complete",
        "data_quality": quality,
        "orchestrator_decisions_count": len(decisions),
    }

    logger.info(f"[Orchestrator] PRE-ANALYSIS done. {len(decisions)} decisions made.")
    return state


def orchestrator_post_dedup(state: ReviewPipelineState) -> ReviewPipelineState:
    """
    Phase 2: Orchestrator runs AFTER deduplication.
    Decides: Should we re-run dedup with stricter threshold (feedback loop)?
    """
    reviews = state["deduplicated_reviews"]
    decisions = list(state.get("orchestrator_decisions", []))
    messages = list(state.get("agent_messages", []))
    config = dict(state["pipeline_config"])
    loop_count = state.get("feedback_loop_count", 0)

    quality = assess_data_quality(reviews)
    logger.info(f"[Orchestrator] POST-DEDUP: bot_rate={quality['bot_rate']:.1%}, clean_rate={quality['clean_rate']:.1%}")

    # Emit quality check to bus (captured in messages)
    messages.append({
        "sender": "Orchestrator",
        "event_type": "quality_check",
        "payload": {"phase": "post_dedup", **quality}
    })

    # DECISION: High bot rate → feedback loop — re-run dedup with stricter threshold
    if (quality["bot_rate"] > settings.ORCHESTRATOR_BOT_REQUEUE_THRESHOLD
            and loop_count < settings.FEEDBACK_LOOP_MAX_RETRIES):
        new_threshold = min(0.95, config.get("dedup_threshold", 0.85) + 0.05)
        decisions.append(_make_decision(
            phase="post_dedup",
            decision="requeue_dedup_feedback_loop",
            reason=(
                f"Bot rate {quality['bot_rate']:.1%} exceeds threshold "
                f"{settings.ORCHESTRATOR_BOT_REQUEUE_THRESHOLD:.1%}. "
                f"Retry #{loop_count + 1} with threshold={new_threshold:.2f}"
            ),
            action="retry",
            affected_agents=["DeduplicationAgent"],
            metadata={"old_threshold": config.get("dedup_threshold"), "new_threshold": new_threshold, "bot_rate": quality["bot_rate"]}
        ))
        config["dedup_threshold"] = new_threshold
        config["bot_threshold"] = min(0.90, config.get("bot_threshold", 0.65) - 0.05)
        state["feedback_loop_count"] = loop_count + 1
        state["orchestrator_route"] = "requeue_dedup"
        logger.warning(f"[Orchestrator] FEEDBACK LOOP #{loop_count + 1}: re-queuing dedup, threshold→{new_threshold:.2f}")
    else:
        state["orchestrator_route"] = "proceed_to_sentiment"
        if quality["bot_rate"] > settings.ORCHESTRATOR_BOT_REQUEUE_THRESHOLD:
            decisions.append(_make_decision(
                phase="post_dedup",
                decision="accept_high_bot_rate",
                reason=f"Max retries ({settings.FEEDBACK_LOOP_MAX_RETRIES}) reached. Proceeding with {quality['bot_rate']:.1%} bot rate.",
                action="escalate",
                affected_agents=[],
                metadata={"bot_rate": quality["bot_rate"]}
            ))

    state["orchestrator_decisions"] = decisions
    state["agent_messages"] = messages
    state["pipeline_config"] = config
    state["progress"] = {
        **state.get("progress", {}),
        "orchestrator_post_dedup": "complete",
        "route": state["orchestrator_route"],
    }
    return state


def orchestrator_post_sentiment(state: ReviewPipelineState) -> ReviewPipelineState:
    """
    Phase 3: Orchestrator runs AFTER sentiment analysis.
    Decides: Is confidence high enough? Trigger recommendation boost?
    """
    reviews = state["analyzed_reviews"]
    decisions = list(state.get("orchestrator_decisions", []))
    messages = list(state.get("agent_messages", []))
    config = dict(state["pipeline_config"])

    quality = assess_data_quality(reviews)
    avg_conf = quality["avg_confidence"]

    logger.info(f"[Orchestrator] POST-SENTIMENT: avg_confidence={avg_conf:.2f}")

    # DECISION: Low overall confidence → flag for enhanced recommendations
    if avg_conf < settings.MIN_CONFIDENCE_THRESHOLD:
        decisions.append(_make_decision(
            phase="post_sentiment",
            decision="flag_low_confidence_dataset",
            reason=f"Average confidence {avg_conf:.2f} below threshold {settings.MIN_CONFIDENCE_THRESHOLD}",
            action="escalate",
            affected_agents=["RecommendationAgent"],
            metadata={"avg_confidence": avg_conf, "threshold": settings.MIN_CONFIDENCE_THRESHOLD}
        ))
        config["low_confidence_mode"] = True
        logger.warning(f"[Orchestrator] Low confidence dataset flagged: {avg_conf:.2f}")
    else:
        config["low_confidence_mode"] = False
        decisions.append(_make_decision(
            phase="post_sentiment",
            decision="confidence_acceptable",
            reason=f"Average confidence {avg_conf:.2f} meets threshold {settings.MIN_CONFIDENCE_THRESHOLD}",
            action="route",
            affected_agents=["TrendAgent", "RecommendationAgent"],
            metadata={"avg_confidence": avg_conf}
        ))

    # DECISION: Check emoji signals for consistency validation
    emoji_boosted = sum(1 for r in reviews if r.emoji_count > 0 and r.overall_confidence > 0.7)
    if emoji_boosted > 0:
        decisions.append(_make_decision(
            phase="post_sentiment",
            decision="emoji_confidence_validated",
            reason=f"{emoji_boosted} reviews had emoji-boosted confidence scores",
            action="route",
            affected_agents=["ReportAgent"],
            metadata={"emoji_boosted_count": emoji_boosted}
        ))

    state["orchestrator_decisions"] = decisions
    state["agent_messages"] = messages
    state["pipeline_config"] = config
    state["orchestrator_route"] = "proceed_to_trend"
    state["progress"] = {
        **state.get("progress", {}),
        "orchestrator_post_sentiment": "complete",
        "avg_confidence": avg_conf,
    }
    return state


def orchestrator_post_trend(state: ReviewPipelineState) -> ReviewPipelineState:
    """
    Phase 4: Orchestrator runs AFTER trend detection.
    Decides: Escalate critical alerts? Trigger targeted recommendation loop?
    """
    alerts = state.get("trend_alerts", [])
    decisions = list(state.get("orchestrator_decisions", []))
    config = dict(state["pipeline_config"])

    critical_alerts = [a for a in alerts if a.severity == "critical"]
    systemic_alerts = [a for a in alerts if a.is_systemic]

    logger.info(f"[Orchestrator] POST-TREND: {len(alerts)} alerts, {len(critical_alerts)} critical, {len(systemic_alerts)} systemic")

    if critical_alerts:
        decisions.append(_make_decision(
            phase="post_trend",
            decision="escalate_critical_alerts",
            reason=f"{len(critical_alerts)} critical alerts require prioritized recommendations",
            action="escalate",
            affected_agents=["RecommendationAgent"],
            metadata={
                "critical_features": [a.feature for a in critical_alerts],
                "systemic_count": len(systemic_alerts),
            }
        ))
        config["priority_features"] = [a.feature for a in critical_alerts]
        logger.warning(f"[Orchestrator] ESCALATE: critical alerts on features: {[a.feature for a in critical_alerts]}")

    if systemic_alerts:
        decisions.append(_make_decision(
            phase="post_trend",
            decision="systemic_issue_detected",
            reason=f"{len(systemic_alerts)} systemic issues need immediate business action",
            action="escalate",
            affected_agents=["RecommendationAgent", "ReportAgent"],
            metadata={"systemic_features": [a.feature for a in systemic_alerts]}
        ))

    state["orchestrator_decisions"] = decisions
    state["pipeline_config"] = config
    state["orchestrator_route"] = "proceed_to_recommendations"
    state["progress"] = {
        **state.get("progress", {}),
        "orchestrator_post_trend": "complete",
    }
    return state


# ─── Routing Functions (used as conditional edges in LangGraph) ────────────

def should_requeue_dedup(state: ReviewPipelineState) -> str:
    """LangGraph conditional edge: re-dedup or proceed?"""
    route = state.get("orchestrator_route", "proceed_to_sentiment")
    if route == "requeue_dedup":
        logger.info("[Orchestrator Router] → requeue deduplication (feedback loop)")
        return "requeue_dedup"
    return "proceed"


def should_run_cross_comparison(state: ReviewPipelineState) -> str:
    """LangGraph conditional edge: run cross-comparison or skip?"""
    if state["pipeline_config"].get("run_cross_comparison", False):
        return "run"
    return "skip"

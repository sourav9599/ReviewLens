"""
ReviewIQ LangGraph Pipeline v2.0 — Agentic Architecture
========================================================
Non-linear pipeline with:
  - Orchestrator/Controller Agent at key decision points
  - Conditional edges for dynamic routing (feedback loops, skips)
  - 9 agents total: Preprocessing → Emoji → Orchestrator(Pre) →
    Dedup → Orchestrator(PostDedup) → [feedback loop] →
    Sentiment → Orchestrator(PostSentiment) → Trend →
    Orchestrator(PostTrend) → Recommendations → CrossComparison → Report
"""
import time
import logging
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END

from core.models import ReviewPipelineState
from agents.preprocessing_agent import preprocessing_agent
from agents.emoji_agent import emoji_analysis_agent
from agents.orchestrator_agent import (
    orchestrator_pre_analysis,
    orchestrator_post_dedup,
    orchestrator_post_sentiment,
    orchestrator_post_trend,
    should_requeue_dedup,
    should_run_cross_comparison,
)
from agents.deduplication_agent import deduplication_agent
from agents.sentiment_agent import sentiment_analysis_agent
from agents.trend_agent import trend_detection_agent
from agents.recommendations_agent import recommendations_agent
from agents.cross_comparison_agent import cross_comparison_agent
from agents.report_agent import report_synthesis_agent

logger = logging.getLogger(__name__)


def build_pipeline() -> StateGraph:
    """Build the agentic ReviewIQ pipeline with dynamic routing."""

    workflow = StateGraph(ReviewPipelineState)

    # ── Register all nodes ─────────────────────────────────────────────
    workflow.add_node("preprocessing", preprocessing_agent)
    workflow.add_node("emoji_agent", emoji_analysis_agent)
    workflow.add_node("orchestrator_pre", orchestrator_pre_analysis)
    workflow.add_node("deduplication", deduplication_agent)
    workflow.add_node("orchestrator_post_dedup", orchestrator_post_dedup)
    workflow.add_node("sentiment_analysis", sentiment_analysis_agent)
    workflow.add_node("orchestrator_post_sentiment", orchestrator_post_sentiment)
    workflow.add_node("trend_detection", trend_detection_agent)
    workflow.add_node("orchestrator_post_trend", orchestrator_post_trend)
    workflow.add_node("recommendations_node", recommendations_agent)
    workflow.add_node("cross_compare_node", cross_comparison_agent)
    workflow.add_node("report_synthesis", report_synthesis_agent)

    # ── Entry point ────────────────────────────────────────────────────
    workflow.set_entry_point("preprocessing")

    # ── Linear edges (always run) ──────────────────────────────────────
    workflow.add_edge("preprocessing", "emoji_agent")
    workflow.add_edge("emoji_agent", "orchestrator_pre")
    workflow.add_edge("orchestrator_pre", "deduplication")
    workflow.add_edge("deduplication", "orchestrator_post_dedup")

    # ── CONDITIONAL EDGE 1: Post-dedup routing ─────────────────────────
    # If bot rate is too high → re-run dedup (feedback loop)
    # Otherwise → proceed to sentiment
    workflow.add_conditional_edges(
        "orchestrator_post_dedup",
        should_requeue_dedup,
        {
            "requeue_dedup": "deduplication",   # feedback loop
            "proceed": "sentiment_analysis",
        }
    )

    # ── Continue after sentiment ────────────────────────────────────────
    workflow.add_edge("sentiment_analysis", "orchestrator_post_sentiment")
    workflow.add_edge("orchestrator_post_sentiment", "trend_detection")
    workflow.add_edge("trend_detection", "orchestrator_post_trend")
    workflow.add_edge("orchestrator_post_trend", "recommendations_node")
    workflow.add_edge("recommendations_node", "orchestrator_cross_check")

    # ── CONDITIONAL EDGE 2: Cross-comparison routing ────────────────────
    workflow.add_node("orchestrator_cross_check", _pass_through)
    workflow.add_conditional_edges(
        "orchestrator_cross_check",
        should_run_cross_comparison,
        {
            "run": "cross_compare_node",    # run cross-product comparison
            "skip": "report_synthesis",      # skip if not enough categories
        }
    )

    workflow.add_edge("cross_compare_node", "report_synthesis")
    workflow.add_edge("report_synthesis", END)

    return workflow.compile()


def _pass_through(state: ReviewPipelineState) -> ReviewPipelineState:
    """No-op passthrough node for conditional branching."""
    return state


# Singleton compiled pipeline
_pipeline = None


def get_pipeline():
    global _pipeline
    if _pipeline is None:
        _pipeline = build_pipeline()
    return _pipeline


async def run_pipeline(
    raw_reviews: List[Dict[str, Any]],
    config: Dict[str, Any] = None
) -> ReviewPipelineState:
    """
    Run the full agentic pipeline on a list of raw reviews.
    Returns the final pipeline state containing the AnalysisReport.
    """
    pipeline = get_pipeline()

    initial_state: ReviewPipelineState = {
        "raw_reviews": raw_reviews,
        "preprocessed_reviews": [],
        "deduplicated_reviews": [],
        "analyzed_reviews": [],
        "trend_data": [],
        "trend_alerts": [],
        "recommendations": [],
        "report": None,
        "errors": [],
        "progress": {},
        "pipeline_config": {
            "start_time": time.time(),
            "dedup_threshold": 0.85,
            "bot_threshold": 0.65,
            "trend_window_size": 50,
            "run_cross_comparison": False,
            "feedback_loop_max_retries": 2,
            **(config or {}),
        },
        # Agentic extensions
        "agent_messages": [],
        "orchestrator_decisions": [],
        "emoji_analysis": None,
        "cross_product_comparison": None,
        "feedback_loop_count": 0,
        "orchestrator_route": "proceed",
    }

    logger.info(f"[Pipeline v2] Starting agentic ReviewIQ pipeline with {len(raw_reviews)} reviews")

    final_state = pipeline.invoke(initial_state)

    report = final_state.get("report")
    logger.info(
        f"[Pipeline v2] Complete. Report: {report.report_id if report else 'None'} | "
        f"Decisions: {len(final_state.get('orchestrator_decisions', []))} | "
        f"Feedback loops: {final_state.get('feedback_loop_count', 0)}"
    )

    return final_state

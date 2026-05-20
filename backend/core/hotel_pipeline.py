"""
ReviewLens Hotel Reviews LangGraph Pipeline
=============================================
Multi-agent pipeline for processing Marriott hotel reviews through 9 specialized
agents. Reuses the core ReviewIQ agents and extends with hotel-specific stages
for mentions extraction, vector embedding generation, and MongoDB export.

Pipeline Stages:
  1. Preprocessing Agent — Cleans and normalizes raw review text
  2. Emoji Analysis Agent — Extracts emoji-based sentiment signals
  3. Orchestrator (Pre) — Assesses data quality and routes pipeline
  4. Deduplication Agent — Removes duplicates and detects bot reviews
  5. Orchestrator (Post-Dedup) — Feedback loop if bot rate too high
  6. Sentiment Analysis Agent — Aspect-based sentiment for hotel features
  7. Trend Detection Agent — Sliding window anomaly detection
  8. Recommendations Agent — LLM-powered actionable insights
  9. Report Synthesis Agent — Aggregates all outputs
  10. Mentions Extraction Agent — Gemini keyphrase extraction
  11. Embedding Generation Agent — gemini-embedding-2 vectors
  12. Hotel Export Agent — Writes MongoDB-ready JSON documents

Enterprise KPI Alignment:
  • RevPAR — Faster insight-to-action improves guest satisfaction → occupancy
  • Intent to Recommend — Rich review categorization builds guest trust
  • Digital Direct Share — AI-powered search keeps guests on Marriott.com
  • EBITDA Growth — Automated processing reduces manual operational costs
  • Marriott Bonvoy Occupancy — Personalized review UX drives loyalty
"""
import os
import time
import logging
from typing import List, Dict, Any

from langgraph.graph import StateGraph, END

from core.config import settings
from core.models import ReviewPipelineState

from agents.preprocessing_agent import preprocessing_agent
from agents.emoji_agent import emoji_analysis_agent
from agents.deduplication_agent import deduplication_agent
from agents.sentiment_agent import sentiment_analysis_agent
from agents.trend_agent import trend_detection_agent
from agents.recommendations_agent import recommendations_agent
from agents.report_agent import report_synthesis_agent
from agents.cross_comparison_agent import cross_comparison_agent
from agents.orchestrator_agent import (
    orchestrator_pre_analysis,
    orchestrator_post_dedup,
    orchestrator_post_sentiment,
    orchestrator_post_trend,
    should_requeue_dedup,
    should_run_cross_comparison,
)
from agents.mentions_agent import mentions_extraction_agent
from agents.embedding_agent import embedding_generation_agent
from agents.export_agent import hotel_json_export_agent, OUTPUT_FILE
from agents.summary_agent import generate_batch_digest

logger = logging.getLogger(__name__)


# ─── Build the Hotel Pipeline ────────────────────────────────────────────────

def _pass_through(state: ReviewPipelineState) -> ReviewPipelineState:
    """No-op passthrough for conditional branching."""
    return state


def build_hotel_pipeline() -> StateGraph:
    workflow = StateGraph(ReviewPipelineState)

    # Core agents (shared with generic pipeline)
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
    workflow.add_node("orchestrator_cross_check", _pass_through)
    workflow.add_node("cross_compare_node", cross_comparison_agent)
    workflow.add_node("report_synthesis", report_synthesis_agent)

    # Hotel-specific agents
    workflow.add_node("mentions_extraction", mentions_extraction_agent)
    workflow.add_node("embedding_generation", embedding_generation_agent)
    workflow.add_node("hotel_json_export", hotel_json_export_agent)
    workflow.add_node("summary_digest", generate_batch_digest)

    # Entry
    workflow.set_entry_point("preprocessing")

    # Core flow
    workflow.add_edge("preprocessing", "emoji_agent")
    workflow.add_edge("emoji_agent", "orchestrator_pre")
    workflow.add_edge("orchestrator_pre", "deduplication")
    workflow.add_edge("deduplication", "orchestrator_post_dedup")

    workflow.add_conditional_edges(
        "orchestrator_post_dedup",
        should_requeue_dedup,
        {
            "requeue_dedup": "deduplication",
            "proceed": "sentiment_analysis",
        }
    )

    workflow.add_edge("sentiment_analysis", "orchestrator_post_sentiment")
    workflow.add_edge("orchestrator_post_sentiment", "trend_detection")
    workflow.add_edge("trend_detection", "orchestrator_post_trend")
    workflow.add_edge("orchestrator_post_trend", "recommendations_node")
    workflow.add_edge("recommendations_node", "orchestrator_cross_check")

    workflow.add_conditional_edges(
        "orchestrator_cross_check",
        should_run_cross_comparison,
        {
            "run": "cross_compare_node",
            "skip": "report_synthesis",
        }
    )

    workflow.add_edge("cross_compare_node", "report_synthesis")

    # After standard report → hotel-specific stages
    workflow.add_edge("report_synthesis", "mentions_extraction")
    workflow.add_edge("mentions_extraction", "embedding_generation")
    workflow.add_edge("embedding_generation", "hotel_json_export")
    workflow.add_edge("hotel_json_export", "summary_digest")
    workflow.add_edge("summary_digest", END)

    return workflow.compile()


_hotel_pipeline = None


def get_hotel_pipeline() -> StateGraph:
    global _hotel_pipeline
    if _hotel_pipeline is None:
        _hotel_pipeline = build_hotel_pipeline()
    return _hotel_pipeline


async def run_hotel_pipeline(
    raw_reviews: List[Dict[str, Any]],
    hotel_id: str = "hotel_default",
) -> ReviewPipelineState:
    """
    Run the full hotel reviews pipeline.
    Uses all existing agents + mentions extraction + embeddings + JSON export.
    """
    pipeline = get_hotel_pipeline()

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
            "hotel_id": hotel_id,
        },
        "agent_messages": [],
        "orchestrator_decisions": [],
        "emoji_analysis": None,
        "cross_product_comparison": None,
        "feedback_loop_count": 0,
        "orchestrator_route": "proceed",
    }

    logger.info(f"[Hotel-Pipeline] Starting with {len(raw_reviews)} reviews for hotel '{hotel_id}'")
    final_state = pipeline.invoke(initial_state)

    elapsed = time.time() - initial_state["pipeline_config"]["start_time"]
    final_state["progress"]["elapsed_seconds"] = round(elapsed, 2)
    logger.info(f"[Hotel-Pipeline] Complete in {elapsed:.1f}s")

    return final_state

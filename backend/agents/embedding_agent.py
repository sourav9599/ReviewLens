"""
Agent 8: Embedding Generation Agent
=====================================
Generates high-dimensional vector embeddings for each Marriott hotel review
using Google's gemini-embedding-2 model (3072 dimensions). These embeddings
power semantic search on the guest-facing review page, enabling natural
language queries like "hotel near Times Square with great breakfast."

ReviewLens Context:
───────────────────
ReviewLens offers two discovery modes for guests:
1. **Topic Filters** (from Mentions Agent) — click "Pool" to see all pool reviews
2. **Semantic Search** (from this agent) — type "quiet room away from elevator"
   and find reviews that discuss that concept even if they don't use those words

This is a key differentiator vs. OTAs which only offer keyword search. A guest
searching "Is the gym actually open at 5 AM?" finds semantically relevant reviews
even if no review contains that exact phrase.

Enterprise KPI Alignment:
─────────────────────────
• Digital Direct Share: Semantic search on Marriott.com provides a superior
  discovery experience vs. keyword-only search on OTAs → keeps guests on
  the direct booking channel.
• RevPAR: Guests who can semantically search find relevant properties faster
  → higher booking conversion → increased occupancy.
• Intent to Recommend: AI-powered search helps guests set accurate expectations,
  reducing post-stay disappointment.
• Marriott Bonvoy Occupancy & Enrollments: Enhanced search experience
  differentiates the Bonvoy platform, driving enrollment.

Pipeline Position: Runs AFTER mentions_extraction → feeds Hotel Export.
"""
import time
import logging
from typing import List, Dict

from core.config import settings
from core.models import ReviewPipelineState, ReviewStatus
from core.llm_factory import get_embeddings

logger = logging.getLogger(__name__)


def embedding_generation_agent(state: ReviewPipelineState) -> ReviewPipelineState:
    """
    Embedding Generation Agent: Produces 3072-dimensional vector embeddings
    for each hotel review using Google gemini-embedding-2. Embeddings are stored
    in the pipeline state and later persisted to MongoDB Atlas Vector Search
    for powering semantic review queries on Marriott properties.
    """
    reviews = state["analyzed_reviews"]
    errors = list(state.get("errors", []))

    analyzable = [
        r for r in reviews
        if r.status not in {ReviewStatus.DUPLICATE, ReviewStatus.BOT_SUSPECTED}
    ]

    logger.info(f"[EmbeddingAgent] Generating embeddings for {len(analyzable)} reviews")

    embeddings_model = get_embeddings()

    embedding_map: Dict[str, List[float]] = state["pipeline_config"].get("_embedding_map", {})

    BATCH_SIZE = 50

    for i in range(0, len(analyzable), BATCH_SIZE):
        batch = analyzable[i:i + BATCH_SIZE]
        texts = [r.cleaned_text[:500] for r in batch]

        try:
            vectors = embeddings_model.embed_documents(texts)
            for review, vec in zip(batch, vectors):
                embedding_map[review.id] = vec
        except Exception as e:
            logger.warning(f"[EmbeddingAgent] Batch {i//BATCH_SIZE} failed: {e}")
            errors.append(f"Embedding batch error: {str(e)}")

        time.sleep(1)

    state["pipeline_config"]["_embedding_map"] = embedding_map
    state["errors"] = errors
    state["progress"] = {**state.get("progress", {}), "embedding_generation": "complete"}
    return state

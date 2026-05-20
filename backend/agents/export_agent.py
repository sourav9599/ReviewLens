"""
Agent 9: Hotel Review Export Agent
====================================
Final pipeline stage that assembles MongoDB-ready documents from all upstream
agent outputs (sentiment, dynamic topic mentions, embeddings, sub-ratings)
and persists them to storage. Each document follows the ReviewLens schema
optimized for Atlas Vector Search and aggregation queries.

ReviewLens Context:
───────────────────
This agent produces the documents that power both guest and manager experiences:
• Guest-facing: MongoDB aggregation on "mentions" field enables topic filtering;
  vector field enables semantic search via Atlas Vector Search.
• Manager-facing: Aggregation pipelines on sentiment, sub_ratings, and
  categories fields power the Property Manager Topic Heatmap and trend charts.

The schema is designed so that when a guest clicks "valet parking" on Marriott.com,
a simple MongoDB query {mentions: "valet parking"} returns all relevant reviews
with pre-computed sentiment — no re-processing needed at query time.

Enterprise KPI Alignment:
─────────────────────────
• RevPAR: Structured output enables the dashboard to identify bottlenecks that
  impact guest satisfaction → fixes increase positive reviews → higher occupancy.
• EBITDA Growth: Automated processing replaces manual review triage, reducing
  operational costs while increasing speed of insight delivery.
• Intent to Recommend: Persisted sub-ratings power the guest-facing category
  breakdown UI, helping guests make informed decisions.
• Non-RevPAR Affiliation Fees: Structured review intelligence as a value-add
  for franchise owners strengthens the Marriott affiliation proposition.
• Net Rooms Growth: Data-driven property insights help franchise prospects see
  the operational intelligence advantage of the Marriott brand.

Pipeline Position: Final stage → END.
"""
import json
import os
import logging
from typing import List, Dict, Any

from core.config import settings
from core.models import ReviewPipelineState, ReviewStatus

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
OUTPUT_FILE = os.path.join(DATA_DIR, "hotel_reviews_processed.json")


def _invalidate_summary_for_hotel(hotel_id: str):
    """Mark the summary cache as stale when new reviews are written."""
    from agents.summary_agent import invalidate_summary_cache
    try:
        invalidate_summary_cache(hotel_id)
    except Exception:
        pass


def hotel_json_export_agent(state: ReviewPipelineState) -> ReviewPipelineState:
    """
    Hotel Export Agent: Compiles all upstream analysis into MongoDB-ready
    documents and persists them to the data store. Each document includes
    the original text, title, reviewer name, submission timestamp, overall
    rating, sub-ratings, sentiment, confidence, aspect categories, popular
    mentions, locale, and vector embedding.

    Output schema per document:
    {
        "_id": "rev_xxxxx",
        "hotel_id": "NYCES",
        "hotel_name": "Courtyard New York Manhattan/Fifth Avenue",
        "text": "...",
        "title": "Great staff room and bathroom was mediocre",
        "user_name": "Scouting Family",
        "locale": "en_US",
        "submission_time": "2026-05-19T22:52:45.000+00:00",
        "rating": 4,
        "sub_ratings": {"cleanliness": 4.0, "location": 4.0, ...},
        "sentiment": "positive",
        "confidence": 0.87,
        "categories": {"room": "positive", "service": "negative"},
        "mentions": ["valet parking", "rooftop pool"],
        "embedding": [0.015, -0.024, ...],
        "language": "en",
        "is_processed": true
    }
    """
    reviews = state["analyzed_reviews"]
    hotel_id = state["pipeline_config"].get("hotel_id", "hotel_default")
    embedding_map = state["pipeline_config"].get("_embedding_map", {})

    analyzable = [
        r for r in reviews
        if r.status not in {ReviewStatus.DUPLICATE, ReviewStatus.BOT_SUSPECTED}
    ]

    logger.info(f"[HotelExportAgent] Exporting {len(analyzable)} reviews for hotel '{hotel_id}'")

    final_docs = []
    for review in analyzable:
        mentions = [
            f.replace("mention:", "")
            for f in review.flags if f.startswith("mention:")
        ]

        # Extract metadata stored in flags by preprocessing agent
        title = ""
        user_name = ""
        review_hotel_id = hotel_id
        locale = ""
        for f in review.flags:
            if f.startswith("title:"):
                title = f[6:]
            elif f.startswith("user:"):
                user_name = f[5:]
            elif f.startswith("hotel_id:"):
                review_hotel_id = f[9:]
            elif f.startswith("locale:"):
                locale = f[7:]

        embedding = embedding_map.get(review.id, [])

        categories = {}
        for fs in review.feature_sentiments:
            categories[fs.feature] = fs.sentiment.value

        doc = {
            "_id": review.id,
            "hotel_id": review_hotel_id,
            "hotel_name": review.product_name,
            "text": review.original_text,
            "title": title,
            "user_name": user_name,
            "locale": locale,
            "submission_time": review.review_date,
            "rating": review.rating,
            "sub_ratings": review.sub_ratings,
            "sentiment": review.overall_sentiment.value,
            "confidence": review.overall_confidence,
            "categories": categories,
            "mentions": mentions,
            "embedding": embedding,
            "language": review.language,
            "is_processed": True,
        }
        final_docs.append(doc)

    os.makedirs(DATA_DIR, exist_ok=True)

    existing_docs = []
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r") as f:
                existing_docs = json.load(f)
        except (json.JSONDecodeError, IOError):
            existing_docs = []

    existing_ids = {d["_id"] for d in existing_docs}
    new_docs = [d for d in final_docs if d["_id"] not in existing_ids]
    all_docs = existing_docs + new_docs

    with open(OUTPUT_FILE, "w") as f:
        json.dump(all_docs, f, indent=2, default=str)

    logger.info(f"[HotelExportAgent] Saved {len(new_docs)} new docs (total: {len(all_docs)}) to {OUTPUT_FILE}")

    # Invalidate summary cache so next summary request triggers re-aggregation
    if new_docs:
        _invalidate_summary_for_hotel(hotel_id)

    state["progress"] = {
        **state.get("progress", {}),
        "hotel_export": "complete",
        "total_exported": len(final_docs),
        "new_saved": len(new_docs),
        "output_file": OUTPUT_FILE,
    }
    return state

"""
Agent 7: Dynamic Topic / Mentions Extraction Agent
====================================================
The core differentiator of ReviewLens. Uses Gemini LLM to extract fine-grained,
dynamic topic tags from hotel review sentences — going far beyond Marriott's
static 6 categories (Cleanliness, Service, Location, Room, F&B, Check-in).

ReviewLens Context:
───────────────────
This agent solves the primary problem in the ReviewLens hypothesis:
"Marriott currently surfaces guest reviews with a fixed, coarse set of
categories... These six buckets were designed for star-rating aggregation,
not discovery."

Output powers:
• **Guest Portal**: Topic filter chips (dynamic, not hardcoded) — guests filter
  by "Pool," "Gym equipment," "Pillow quality," "Valet wait time," "Late
  checkout flexibility" — topics that emerge organically from real reviews.
• **Property Manager Dashboard**: Topic heatmap ranked by mention volume and
  sentiment trend — "Noise (elevator): 23 mentions, 2.1/5, trending negative."
• **Semantic Search**: Mentions are indexed in MongoDB for aggregation queries
  when a guest selects a topic chip.

Enterprise KPI Alignment:
─────────────────────────
• Digital Direct Share: Dynamic topic filters on Marriott.com provide a
  superior review browsing experience vs. TripAdvisor/Booking.com (which still
  rely on static category filters), keeping guests on the direct channel.
• Intent to Recommend: Surfacing what guests frequently praise (e.g. "rooftop
  pool", "concierge service") drives informed booking decisions and increases
  recommendation likelihood.
• RevPAR: Mention-based filtering helps potential guests find reviews relevant
  to their priorities → reduced bounce rates → higher conversion → occupancy.
• Marriott Bonvoy Occupancy & Enrollments: Personalized mention tags help
  Bonvoy members quickly validate property fit, increasing repeat bookings.

Pipeline Position: Runs AFTER report_synthesis → feeds Embedding Generation.
"""
import json
import re
import logging
from typing import List

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

from core.config import settings
from core.models import ReviewPipelineState, ReviewStatus

logger = logging.getLogger(__name__)

MENTIONS_PROMPT = """You are an Aspect-Based Key Point Extraction engine for a hotel review intelligence platform.

PURPOSE: Extract fine-grained, searchable topic tags from hotel guest reviews. These tags power:
1. "Popular Mentions" filter chips on the booking page (guests click to filter reviews)
2. Operational dashboards where property managers track topic frequency over time
3. Semantic clustering for competitive benchmarking across properties

EXTRACTION TAXONOMY (extract the SPECIFIC sub-topics, NOT these parent categories):
- Physical Space: room features, bathroom details, bed quality, view, noise sources, temperature, odors
- Service Touchpoints: specific staff interactions, response times, process friction, personalization moments
- F&B Specifics: individual menu items, restaurant names, breakfast variety, bar atmosphere, dietary accommodations
- Location Context: nearby landmarks, transport options, walkability, neighborhood character, safety perception
- Technology: wifi speed, app experience, keyless entry, TV/entertainment, charging availability
- Emotional Moments: surprise-and-delight experiences, frustration triggers, loyalty-building interactions

RULES:
- Output 3-8 tags per review as SHORT lowercase phrases (2-4 words each)
- Be maximally specific: "shower water pressure" not "bathroom"; "breakfast omelette station" not "food"
- Capture WHAT guests say, not your interpretation — if they say "thin walls" extract "thin walls"
- Include proper nouns when mentioned (restaurant names, landmark names, staff names)
- Distinguish closely related topics: "pool temperature" vs "pool cleanliness" vs "pool crowding"
- Tags must be suitable as UI filter labels — concise, human-readable, no sentence fragments
- When a review mentions nothing specific (e.g. "Nice hotel"), return ["general positive"] or ["general negative"]

OUTPUT FORMAT: Return ONLY a valid JSON array of arrays. No markdown fences, no commentary.
Each inner array corresponds to one review in the same order as input.
Example: [["rooftop infinity pool", "late checkout policy", "pike place market"], ["elevator noise", "valet wait time", "king bed comfort"]]

Reviews:
{reviews}"""


def mentions_extraction_agent(state: ReviewPipelineState) -> ReviewPipelineState:
    """
    Mentions Extraction Agent: Extracts guest-experience keyphrases from each
    hotel review using Gemini to power the Popular Mentions UI and mention-based
    review filtering for Marriott properties.

    Outputs are stored as flags on ProcessedReview (format: "mention:<phrase>")
    and later extracted during the export stage for MongoDB indexing.
    """
    reviews = state["analyzed_reviews"]
    errors = list(state.get("errors", []))

    analyzable = [
        r for r in reviews
        if r.status not in {ReviewStatus.DUPLICATE, ReviewStatus.BOT_SUSPECTED}
    ]

    logger.info(f"[MentionsAgent] Extracting mentions from {len(analyzable)} reviews")

    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0.0,
        max_output_tokens=4096,
    )

    BATCH_SIZE = 20

    for i in range(0, len(analyzable), BATCH_SIZE):
        batch = analyzable[i:i + BATCH_SIZE]
        texts = "\n".join([f"{idx+1}. {r.cleaned_text[:250]}" for idx, r in enumerate(batch)])

        try:
            response = llm.invoke([
                HumanMessage(content=MENTIONS_PROMPT.format(reviews=texts))
            ])
            content = response.content.strip()
            content = re.sub(r'^```json\s*', '', content)
            content = re.sub(r'\s*```$', '', content)
            results = json.loads(content)

            for review, mentions in zip(batch, results):
                if isinstance(mentions, list):
                    review.flags = list(set(review.flags) | {
                        f"mention:{m.lower().strip()}"
                        for m in mentions
                        if isinstance(m, str) and len(m.strip()) > 1
                    })
        except Exception as e:
            logger.warning(f"[MentionsAgent] Batch {i//BATCH_SIZE} failed: {e}")
            errors.append(f"Mentions batch error: {str(e)}")

    state["analyzed_reviews"] = reviews
    state["errors"] = errors
    state["progress"] = {**state.get("progress", {}), "mentions_extraction": "complete"}
    return state

"""
ReviewIQ FastAPI Backend v2.0
Main application with all REST endpoints + SSE streaming + PDF download
"""
import csv
import io
import json
import os
import time
import uuid
import asyncio
import logging
from typing import List, Optional, Dict, Any
from collections import Counter
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from core.config import settings
from core.models import AnalysisReport
from core.pipeline import run_pipeline
from data.synthetic_generator import generate_synthetic_dataset
from core.llm_factory import get_llm, get_embeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, HumanMessage

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ReviewIQ — Agentic Customer Review Intelligence Platform",
    description="Multi-agent AI system: Orchestrator + 8 specialized agents powered by LangGraph + Gemini",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def verify_llm_connection():
    """Validate LLM and embedding provider connectivity on application startup."""
    provider = settings.LLM_PROVIDER

    if provider == "gemini" and not settings.GOOGLE_API_KEY:
        logger.error("[Startup] LLM_PROVIDER=gemini but GOOGLE_API_KEY is not set.")
        return
    if provider == "litellm" and not settings.LITELLM_API_KEY:
        logger.warning("[Startup] LLM_PROVIDER=litellm but LITELLM_API_KEY is empty.")
    if provider == "googleADC" and not settings.GCP_PROJECT:
        logger.error("[Startup] LLM_PROVIDER=googleADC but GCP_PROJECT is not set.")
        return

    try:
        llm = get_llm(max_tokens=10)
        response = await asyncio.to_thread(llm.invoke, "Say OK")
        content = response.content if hasattr(response, "content") else str(response)
        logger.info(f"[Startup] LLM provider '{provider}' connected. Response: {content[:50].strip()}")
    except Exception as e:
        logger.error(f"[Startup] LLM connection FAILED ({provider}): {e}")
        logger.error("[Startup] Check credentials and model settings in .env")

    try:
        from core.llm_factory import get_embeddings
        emb = get_embeddings()
        vectors = await asyncio.to_thread(emb.embed_query, "test")
        dim = len(vectors) if vectors else 0
        logger.info(f"[Startup] Embedding model connected. Dimensions: {dim}")
    except Exception as e:
        logger.error(f"[Startup] Embedding connection FAILED ({provider}): {e}")
        logger.error("[Startup] Semantic search will not work until this is resolved.")


# ─── In-Memory Vector Store ──────────────────────────────────────────────────
_vector_store: Optional[InMemoryVectorStore] = None
_vector_store_metadata: Dict[str, Any] = {}


def _load_vector_store():
    """Load pre-computed embeddings from hotel_reviews_processed.json into InMemoryVectorStore."""
    global _vector_store, _vector_store_metadata
    from core.hotel_pipeline import OUTPUT_FILE

    if not os.path.exists(OUTPUT_FILE):
        logger.warning("[VectorStore] No processed reviews file found. Semantic search unavailable.")
        return

    with open(OUTPUT_FILE, "r") as f:
        docs = json.load(f)

    docs_with_embeddings = [d for d in docs if d.get("embedding")]
    if not docs_with_embeddings:
        logger.warning("[VectorStore] No embeddings found in processed reviews.")
        return

    embeddings_model = get_embeddings()
    _vector_store = InMemoryVectorStore(embedding=embeddings_model)

    for doc in docs_with_embeddings:
        doc_id = doc["_id"]
        _vector_store.store[doc_id] = {
            "id": doc_id,
            "vector": doc["embedding"],
            "text": doc.get("text", ""),
            "metadata": {
                "_id": doc_id,
                "hotel_id": doc.get("hotel_id", ""),
                "hotel_name": doc.get("hotel_name", ""),
                "title": doc.get("title", ""),
                "user_name": doc.get("user_name", ""),
                "submission_time": doc.get("submission_time", ""),
                "rating": doc.get("rating"),
                "sentiment": doc.get("sentiment", ""),
                "confidence": doc.get("confidence"),
                "mentions": doc.get("mentions", []),
                "categories": doc.get("categories", {}),
                "sub_ratings": doc.get("sub_ratings", {}),
                "locale": doc.get("locale", ""),
                "language": doc.get("language", ""),
            },
        }

    _vector_store_metadata["total_docs"] = len(docs_with_embeddings)
    _vector_store_metadata["loaded_at"] = time.time()
    logger.info(f"[VectorStore] Loaded {len(docs_with_embeddings)} documents with pre-computed embeddings (no re-embedding).")


@app.on_event("startup")
async def load_vector_store_on_startup():
    """Load the InMemoryVectorStore with pre-computed embeddings at application start."""
    await asyncio.to_thread(_load_vector_store)


# In-memory job store (in production: use Redis)
_jobs: Dict[str, Dict[str, Any]] = {}
# SSE progress streams: job_id → list of progress events
_job_progress: Dict[str, List[Dict]] = {}


class PasteReviewsRequest(BaseModel):
    reviews: List[Dict[str, Any]]
    config: Optional[Dict[str, Any]] = None


class AnalyzeTextRequest(BaseModel):
    text: str  # newline-separated reviews
    category: str = "General"
    product_name: str = "Unknown Product"
    config: Optional[Dict[str, Any]] = None


class ChatRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None


class ScrapeRequest(BaseModel):
    url: str
    max_reviews: int = 50


class BriefRequest(BaseModel):
    report: Dict[str, Any]


def parse_csv_reviews(content: bytes) -> List[Dict[str, Any]]:
    """Parse CSV file into review dicts."""
    text = content.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    reviews = []

    field_aliases = {
        "review_text": ["ReviewText", "review_text", "text", "review", "body", "content", "comment", "Review Text", "Review"],
        "rating": ["rating", "stars", "score", "Rating", "Stars"],
        "category": ["category", "product_category", "Category", "type"],
        "product_name": ["HotelName", "hotel_name", "property_name", "product_name", "product", "name", "Product", "Product Name"],
        "review_date": ["SubmissionTime", "review_date", "date", "Date", "created_at"],
        "hotel_id": ["HotelId", "hotel_id", "property_id"],
        "title": ["Title", "title", "review_title", "headline"],
        "user_name": ["UserName", "user_name", "reviewer", "author"],
        "locale": ["ContentLocale", "locale", "language_code", "lang"],
        "cleanliness": ["Cleanliness", "cleanliness"],
        "location": ["Location", "location"],
        "amenities": ["Amenities", "amenities"],
        "dining": ["Dining", "dining"],
        "service": ["Service", "service", "Service & Staff"],
        "value": ["Value", "value", "Value for Money"],
    }

    for row in reader:
        mapped = {}
        for field, aliases in field_aliases.items():
            for alias in aliases:
                if alias in row and row[alias]:
                    mapped[field] = row[alias]
                    break

        if not mapped.get("review_text"):
            for key, val in row.items():
                if val and len(str(val)) > 20:
                    mapped["review_text"] = str(val)
                    break

        if mapped.get("review_text"):
            reviews.append({**row, **mapped})

    return reviews


def parse_json_reviews(content: bytes) -> List[Dict[str, Any]]:
    """Parse JSON file into review dicts."""
    data = json.loads(content.decode("utf-8"))
    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and "reviews" in data:
        return data["reviews"]
    return [data]


def _push_progress(job_id: str, stage: str, message: str, extra: Dict = None):
    """Push a progress event for SSE streaming."""
    if job_id not in _job_progress:
        _job_progress[job_id] = []
    _job_progress[job_id].append({
        "stage": stage,
        "message": message,
        "timestamp": time.time(),
        **(extra or {}),
    })


async def run_analysis_job(job_id: str, reviews: List[Dict[str, Any]], config: Dict = None):
    """Run pipeline in background and store result."""
    try:
        _jobs[job_id]["status"] = "running"
        _jobs[job_id]["started_at"] = time.time()
        _push_progress(job_id, "started", f"Pipeline starting with {len(reviews)} reviews")

        # Simulate stage progress pushes (real pipeline uses Gemini)
        stages = [
            ("preprocessing", "Preprocessing & cleaning reviews..."),
            ("emoji_analysis", "Analyzing emoji signals..."),
            ("orchestrator_pre", "Orchestrator assessing data quality..."),
            ("deduplication", "Detecting duplicates and bots..."),
            ("sentiment", "Running sentiment analysis..."),
            ("trend_detection", "Detecting trends & anomalies..."),
            ("recommendations", "Generating recommendations..."),
            ("cross_comparison", "Running cross-product comparison..."),
            ("report", "Synthesizing final report..."),
        ]

        async def push_stage(idx):
            await asyncio.sleep(0.1)
            stage, msg = stages[idx]
            _push_progress(job_id, stage, msg, {"stage_index": idx, "total_stages": len(stages)})

        # Push first couple stages immediately
        await push_stage(0)
        await push_stage(1)

        final_state = await asyncio.to_thread(
            lambda: __import__("asyncio").run(run_pipeline(reviews, config))
        )

        # Fallback: if asyncio.run doesn't work, use event loop directly
        if not final_state:
            loop = asyncio.get_event_loop()
            final_state = await loop.run_in_executor(None, lambda: _sync_run(reviews, config))

        _push_progress(job_id, "complete", "Analysis complete!")

        report = final_state.get("report")
        if report:
            _jobs[job_id]["status"] = "complete"
            _jobs[job_id]["report"] = report.model_dump()
            _jobs[job_id]["errors"] = final_state.get("errors", [])
        else:
            _jobs[job_id]["status"] = "failed"
            _jobs[job_id]["error"] = "Pipeline produced no report"

    except Exception as e:
        logger.error(f"[Job {job_id}] Pipeline failed: {e}", exc_info=True)
        _jobs[job_id]["status"] = "failed"
        _jobs[job_id]["error"] = str(e)
        _push_progress(job_id, "error", str(e))


def _sync_run(reviews, config):
    """Synchronous wrapper for the async pipeline."""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, run_pipeline(reviews, config))
                return future.result()
        return loop.run_until_complete(run_pipeline(reviews, config))
    except RuntimeError:
        return asyncio.run(run_pipeline(reviews, config))


async def run_analysis_job_safe(job_id: str, reviews: List[Dict[str, Any]], config: Dict = None):
    """Safe wrapper that handles the async pipeline correctly."""
    try:
        _jobs[job_id]["status"] = "running"
        _jobs[job_id]["started_at"] = time.time()
        _push_progress(job_id, "started", f"Pipeline starting with {len(reviews)} reviews")

        final_state = await run_pipeline(reviews, config)

        _push_progress(job_id, "complete", "Analysis complete!")

        report = final_state.get("report")
        if report:
            _jobs[job_id]["status"] = "complete"
            _jobs[job_id]["report"] = report.model_dump()
            _jobs[job_id]["errors"] = final_state.get("errors", [])
        else:
            _jobs[job_id]["status"] = "failed"
            _jobs[job_id]["error"] = "Pipeline produced no report"

    except Exception as e:
        logger.error(f"[Job {job_id}] Pipeline failed: {e}", exc_info=True)
        _jobs[job_id]["status"] = "failed"
        _jobs[job_id]["error"] = str(e)
        _push_progress(job_id, "error", str(e))


# ─── Routes ─────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "message": "ReviewIQ Agentic API is running",
        "version": "2.0.0",
        "agents": 9,
        "features": ["orchestrator", "emoji_analysis", "cross_comparison", "feedback_loops", "bot_risk_levels"],
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "model": settings.GEMINI_MODEL, "pipeline_version": "2.0-agentic"}


@app.post("/api/analyze/upload")
async def analyze_uploaded_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    category: str = "General",
    product_name: str = "Unknown Product"
):
    """Upload CSV or JSON file for analysis."""
    content = await file.read()

    if file.filename.endswith(".csv"):
        reviews = parse_csv_reviews(content)
    elif file.filename.endswith(".json"):
        reviews = parse_json_reviews(content)
    else:
        raise HTTPException(400, "Only CSV and JSON files are supported")

    if not reviews:
        raise HTTPException(400, "No valid reviews found in the file")

    for r in reviews:
        if not r.get("category"):
            r["category"] = category
        if not r.get("product_name"):
            r["product_name"] = product_name

    job_id = f"job_{int(time.time() * 1000)}"
    _jobs[job_id] = {"status": "queued", "review_count": len(reviews)}
    _job_progress[job_id] = []

    background_tasks.add_task(run_analysis_job_safe, job_id, reviews)

    return {"job_id": job_id, "review_count": len(reviews), "message": "Analysis started"}


@app.post("/api/analyze/paste")
async def analyze_pasted_reviews(
    background_tasks: BackgroundTasks,
    request: PasteReviewsRequest
):
    """Analyze reviews provided directly as JSON."""
    if not request.reviews:
        raise HTTPException(400, "No reviews provided")

    job_id = f"job_{int(time.time() * 1000)}"
    _jobs[job_id] = {"status": "queued", "review_count": len(request.reviews)}
    _job_progress[job_id] = []

    background_tasks.add_task(run_analysis_job_safe, job_id, request.reviews, request.config)

    return {"job_id": job_id, "review_count": len(request.reviews), "message": "Analysis started"}


@app.post("/api/analyze/text")
async def analyze_text_reviews(
    background_tasks: BackgroundTasks,
    request: AnalyzeTextRequest
):
    """Analyze plain text (one review per line)."""
    lines = [l.strip() for l in request.text.split("\n") if l.strip() and len(l.strip()) > 5]

    if not lines:
        raise HTTPException(400, "No valid review text found")

    reviews = [
        {
            "review_text": line,
            "category": request.category,
            "product_name": request.product_name,
        }
        for line in lines
    ]

    job_id = f"job_{int(time.time() * 1000)}"
    _jobs[job_id] = {"status": "queued", "review_count": len(reviews)}
    _job_progress[job_id] = []

    background_tasks.add_task(run_analysis_job_safe, job_id, reviews, request.config)

    return {"job_id": job_id, "review_count": len(reviews), "message": "Analysis started"}


@app.post("/api/analyze/demo")
async def analyze_demo_dataset(background_tasks: BackgroundTasks):
    """
    Run analysis on hotel reviews from hotel_reviews_processed.json.
    Builds an AnalysisReport from pre-processed data grouped by property.
    """
    from core.hotel_pipeline import OUTPUT_FILE as HOTEL_OUTPUT

    if not os.path.exists(HOTEL_OUTPUT):
        reviews = generate_synthetic_dataset()
        job_id = f"job_demo_{int(time.time() * 1000)}"
        _jobs[job_id] = {"status": "queued", "review_count": len(reviews), "is_demo": True}
        _job_progress[job_id] = []
        background_tasks.add_task(run_analysis_job_safe, job_id, reviews)
        return {"job_id": job_id, "review_count": len(reviews), "message": "Demo analysis started (synthetic)"}

    with open(HOTEL_OUTPUT, "r") as f:
        docs = json.load(f)

    if not docs:
        raise HTTPException(400, "No processed reviews found in hotel_reviews_processed.json")

    reviews = []
    for doc in docs:
        sub_ratings = doc.get("sub_ratings", {})
        rating = doc.get("rating")
        if not rating and sub_ratings:
            rating = round(sum(sub_ratings.values()) / len(sub_ratings), 1)
        review = {
            "review_text": doc.get("text", ""),
            "rating": rating or 3.0,
            "category": doc.get("hotel_name") or "Hotel",
            "product_name": doc.get("hotel_name") or "Marriott Property",
            "review_date": doc.get("submission_time", ""),
            "verified_purchase": True,
        }
        for key, val in sub_ratings.items():
            review[key] = val
        reviews.append(review)

    job_id = f"job_hotel_{int(time.time() * 1000)}"
    _jobs[job_id] = {"status": "queued", "review_count": len(reviews), "is_demo": True}
    _job_progress[job_id] = []

    background_tasks.add_task(run_analysis_job_safe, job_id, reviews)

    return {"job_id": job_id, "review_count": len(reviews), "message": "Hotel review analysis started"}


# ─── Per-Property Analysis with Cache ─────────────────────────────────────────
PROPERTY_ANALYSIS_CACHE = os.path.join(os.path.dirname(__file__), "data", "property_analysis_cache.json")


def _load_property_cache() -> Dict[str, Any]:
    if os.path.exists(PROPERTY_ANALYSIS_CACHE):
        with open(PROPERTY_ANALYSIS_CACHE, "r") as f:
            return json.load(f)
    return {}


def _save_property_cache(cache: Dict[str, Any]):
    with open(PROPERTY_ANALYSIS_CACHE, "w") as f:
        json.dump(cache, f, indent=2, default=str)


@app.get("/api/analyze/property/{property_code}")
async def get_property_analysis(property_code: str):
    """
    Get cached analysis for a property. Returns the report if it exists in cache.
    If not cached, returns 404 — use POST to trigger analysis.
    """
    cache = _load_property_cache()
    if property_code in cache:
        return {
            "status": "complete",
            "property_code": property_code,
            "report": cache[property_code]["report"],
            "cached_at": cache[property_code].get("cached_at"),
            "review_count": cache[property_code].get("review_count", 0),
        }
    raise HTTPException(404, f"No cached analysis for property '{property_code}'. POST to trigger analysis.")


@app.post("/api/analyze/property/{property_code}")
async def trigger_property_analysis(
    property_code: str,
    background_tasks: BackgroundTasks,
    force_refresh: bool = False,
):
    """
    Trigger analysis pipeline for a specific property from hotel_reviews_processed.json.
    Results are cached in property_analysis_cache.json. Use force_refresh=true to re-run.
    """
    cache = _load_property_cache()
    if not force_refresh and property_code in cache:
        return {
            "status": "complete",
            "property_code": property_code,
            "report": cache[property_code]["report"],
            "cached_at": cache[property_code].get("cached_at"),
            "review_count": cache[property_code].get("review_count", 0),
            "from_cache": True,
        }

    from core.hotel_pipeline import OUTPUT_FILE as HOTEL_OUTPUT
    if not os.path.exists(HOTEL_OUTPUT):
        raise HTTPException(404, "No processed reviews file found. Run ingestion first.")

    with open(HOTEL_OUTPUT, "r") as f:
        docs = json.load(f)

    property_docs = [d for d in docs if d.get("hotel_id") == property_code]
    if not property_docs:
        raise HTTPException(404, f"No reviews found for property '{property_code}'")

    reviews = []
    for doc in property_docs:
        sub_ratings = doc.get("sub_ratings", {})
        rating = doc.get("rating")
        if not rating and sub_ratings:
            rating = round(sum(sub_ratings.values()) / len(sub_ratings), 1)
        review = {
            "review_text": doc.get("text", ""),
            "rating": rating or 3.0,
            "category": doc.get("hotel_name") or "Hotel",
            "product_name": doc.get("hotel_name") or property_code,
            "review_date": doc.get("submission_time", ""),
            "title": doc.get("title", ""),
            "user_name": doc.get("user_name", ""),
            "hotel_id": property_code,
            "verified_purchase": True,
        }
        for key, val in sub_ratings.items():
            review[key] = val
        reviews.append(review)

    job_id = f"job_property_{property_code}_{int(time.time() * 1000)}"
    _jobs[job_id] = {"status": "queued", "review_count": len(reviews), "is_demo": True, "property_code": property_code}
    _job_progress[job_id] = []

    async def _run_and_cache():
        await run_analysis_job_safe(job_id, reviews)
        job = _jobs.get(job_id, {})
        if job.get("status") == "complete" and job.get("report"):
            cache = _load_property_cache()
            cache[property_code] = {
                "report": job["report"],
                "cached_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "review_count": len(reviews),
                "hotel_name": property_docs[0].get("hotel_name", property_code),
            }
            _save_property_cache(cache)

    background_tasks.add_task(_run_and_cache)

    return {
        "job_id": job_id,
        "property_code": property_code,
        "review_count": len(reviews),
        "message": f"Analysis triggered for property '{property_code}'",
        "from_cache": False,
    }


@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Poll job status and result."""
    if job_id not in _jobs:
        raise HTTPException(404, f"Job {job_id} not found")

    job = _jobs[job_id]
    response = {
        "job_id": job_id,
        "status": job["status"],
        "review_count": job.get("review_count", 0),
    }

    if job["status"] == "complete":
        response["report"] = job["report"]
        response["errors"] = job.get("errors", [])
    elif job["status"] == "failed":
        response["error"] = job.get("error", "Unknown error")
    elif job["status"] == "running":
        elapsed = time.time() - job.get("started_at", time.time())
        response["elapsed_seconds"] = round(elapsed, 1)
        response["progress_events"] = _job_progress.get(job_id, [])

    return response


@app.get("/api/jobs/{job_id}/stream")
async def stream_job_progress(job_id: str, request: Request):
    """
    SSE endpoint for real-time pipeline progress streaming.
    Client connects here and receives live stage updates.
    """
    if job_id not in _jobs:
        raise HTTPException(404, f"Job {job_id} not found")

    async def event_generator():
        sent_count = 0
        while True:
            if await request.is_disconnected():
                break

            events = _job_progress.get(job_id, [])
            # Send any new events
            new_events = events[sent_count:]
            for ev in new_events:
                data = json.dumps(ev)
                yield f"data: {data}\n\n"
                sent_count += 1

            job_status = _jobs.get(job_id, {}).get("status", "unknown")
            if job_status in ("complete", "failed"):
                # Send final status
                yield f"data: {json.dumps({'stage': job_status, 'message': 'Pipeline finished', 'done': True})}\n\n"
                break

            await asyncio.sleep(0.5)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


@app.get("/api/jobs/{job_id}/report")
async def get_report(job_id: str):
    """Get just the report from a completed job."""
    if job_id not in _jobs:
        raise HTTPException(404, "Job not found")

    job = _jobs[job_id]
    if job["status"] != "complete":
        raise HTTPException(400, f"Job is not complete (status: {job['status']})")

    return job["report"]


@app.get("/api/jobs/{job_id}/pdf")
async def download_pdf_report(job_id: str):
    """
    Generate and download a PDF report for a completed job.
    Uses reportlab for server-side PDF generation.
    """
    if job_id not in _jobs:
        raise HTTPException(404, "Job not found")

    job = _jobs[job_id]
    if job["status"] != "complete":
        raise HTTPException(400, f"Job is not complete (status: {job['status']})")

    report_data = job["report"]

    try:
        pdf_bytes = _generate_pdf(report_data)
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=reviewiq_report_{job_id}.pdf"
            }
        )
    except ImportError:
        # reportlab not installed — return JSON fallback
        raise HTTPException(
            501,
            "PDF generation requires 'reportlab'. Install with: pip install reportlab"
        )
    except Exception as e:
        logger.error(f"PDF generation failed: {e}", exc_info=True)
        raise HTTPException(500, f"PDF generation failed: {str(e)}")


def _generate_pdf(report_data: Dict) -> bytes:
    """Generate a professional white-background PDF report using reportlab."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, KeepTogether
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from collections import Counter

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2.2 * cm, leftMargin=2.2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
        title="ReviewIQ Intelligence Report",
        author="ReviewIQ Agentic AI v2.0",
    )

    # ── Palette (professional white-background) ─────────────────────────
    ORANGE   = colors.HexColor("#FF7A00")
    DARK     = colors.HexColor("#1E293B")
    SLATE    = colors.HexColor("#475569")
    MUTED    = colors.HexColor("#94A3B8")
    GREEN    = colors.HexColor("#28C76F")
    YELLOW   = colors.HexColor("#FFB547")
    RED      = colors.HexColor("#EA5455")
    VIOLET   = colors.HexColor("#A78BFA")
    BLUE     = colors.HexColor("#60A5FA")
    BG_LIGHT = colors.HexColor("#F8FAFC")
    BG_CARD  = colors.HexColor("#FFFFFF")
    BORDER   = colors.HexColor("#E5E7EB")
    HDR_BG   = colors.HexColor("#1E293B")
    HDR_ALT  = colors.HexColor("#F1F5F9")

    SENTIMENT_COLORS = {
        "positive":  GREEN,
        "negative":  RED,
        "neutral":   YELLOW,
        "mixed":     colors.HexColor("#F7936F"),
        "sarcastic": VIOLET,
        "ambiguous": BLUE,
    }

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("RTitle",
        parent=styles["Title"], fontSize=26, textColor=DARK,
        spaceAfter=4, alignment=TA_LEFT, fontName="Helvetica-Bold")
    subtitle_style = ParagraphStyle("RSub",
        parent=styles["Normal"], fontSize=10, textColor=MUTED,
        spaceAfter=0, alignment=TA_LEFT)
    h2_style = ParagraphStyle("RH2",
        parent=styles["Heading2"], fontSize=13, textColor=DARK,
        spaceBefore=16, spaceAfter=8, fontName="Helvetica-Bold",
        borderPad=4)
    body_style = ParagraphStyle("RBody",
        parent=styles["Normal"], fontSize=9, textColor=SLATE, spaceAfter=4, leading=14)
    small_style = ParagraphStyle("RSmall",
        parent=styles["Normal"], fontSize=8, textColor=MUTED, spaceAfter=2, leading=12)
    footer_style = ParagraphStyle("RFooter",
        parent=styles["Normal"], fontSize=8, textColor=MUTED, alignment=TA_CENTER)
    kv_left = ParagraphStyle("KVL",
        parent=styles["Normal"], fontSize=9, textColor=SLATE, fontName="Helvetica")
    kv_right = ParagraphStyle("KVR",
        parent=styles["Normal"], fontSize=9, textColor=DARK, fontName="Helvetica-Bold", alignment=TA_RIGHT)

    story = []

    # ── Cover Banner ────────────────────────────────────────────────────
    header_data = [[
        Paragraph("ReviewIQ", ParagraphStyle("Logo", parent=styles["Normal"],
            fontSize=28, textColor=colors.white, fontName="Helvetica-Bold")),
        Paragraph(
            f"Intelligence Report<br/>"
            f"<font size=9 color='#94A3B8'>ID: {report_data.get('report_id','N/A')}  |  "
            f"Generated: {report_data.get('created_at','')[:10]}  |  "
            f"Pipeline v{report_data.get('pipeline_version','2.0')}</font>",
            ParagraphStyle("HdrRight", parent=styles["Normal"],
                fontSize=13, textColor=colors.white, fontName="Helvetica-Bold", alignment=TA_RIGHT)
        ),
    ]]
    hdr_table = Table(header_data, colWidths=[8*cm, 9*cm])
    hdr_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), HDR_BG),
        ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING",  (0,0), (0,0), 16),
        ("RIGHTPADDING", (-1,0), (-1,0), 16),
        ("TOPPADDING",   (0,0), (-1,-1), 14),
        ("BOTTOMPADDING",(0,0), (-1,-1), 14),
        ("LINEBELOW",    (0,0), (-1,-1), 3, ORANGE),
    ]))
    story.append(hdr_table)
    story.append(Spacer(1, 0.5*cm))

    # ── Helper: section header ─────────────────────────────────────────
    def section_header(title, color=ORANGE):
        return [
            Paragraph(title, h2_style),
            HRFlowable(width="100%", color=color, thickness=1.5, spaceAfter=6),
        ]

    def kv_table(rows, col_w=(10*cm, 7*cm)):
        """2-column key-value table."""
        data = [["Metric", "Value"]] + rows
        t = Table(data, colWidths=list(col_w))
        t.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,0), HDR_BG),
            ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
            ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",      (0,0), (-1,-1), 9),
            ("BACKGROUND",    (0,1), (-1,-1), BG_CARD),
            ("ROWBACKGROUNDS",(0,1), (-1,-1), [BG_CARD, BG_LIGHT]),
            ("TEXTCOLOR",     (0,1), (0,-1), SLATE),
            ("TEXTCOLOR",     (1,1), (1,-1), DARK),
            ("FONTNAME",      (1,1), (1,-1), "Helvetica-Bold"),
            ("GRID",          (0,0), (-1,-1), 0.5, BORDER),
            ("TOPPADDING",    (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ]))
        return t

    # ── Executive Summary ──────────────────────────────────────────────
    story.extend(section_header("Executive Summary"))
    story.append(kv_table([
        ["Total Reviews",           str(report_data.get("total_reviews", 0))],
        ["Clean Reviews",           str(report_data.get("clean_reviews", 0))],
        ["Duplicates Removed",      str(report_data.get("duplicate_count", 0))],
        ["Bot Reviews Flagged",     str(report_data.get("bot_suspected_count", 0))],
        ["Trend Alerts",            str(len(report_data.get("trend_alerts", [])))],
        ["Recommendations",         str(len(report_data.get("recommendations", [])))],
        ["Feedback Loops",          str(report_data.get("feedback_loops_triggered", 0))],
        ["Processing Time",         f"{report_data.get('processing_time_seconds', 0):.1f}s"],
        ["Languages Detected",      ", ".join(report_data.get("languages_detected", ["en"]))],
        ["Product Categories",      str(len(report_data.get("product_categories", [])))],
    ]))
    story.append(Spacer(1, 0.5*cm))

    # ── Sentiment Distribution ─────────────────────────────────────────
    story.extend(section_header("Sentiment Distribution"))
    sentiment = report_data.get("overall_sentiment_distribution", {})

    SENTIMENT_EMOJI = {
        "positive": "✅ Positive",   "negative": "❌ Negative",
        "neutral":  "➖ Neutral",    "mixed":    "🔀 Mixed",
        "sarcastic":"😏 Sarcastic",  "ambiguous":"❓ Ambiguous",
    }
    sent_rows = []
    for label, pct in sorted(sentiment.items(), key=lambda x: x[1], reverse=True):
        bar_pct = int(pct * 100)
        sent_rows.append([SENTIMENT_EMOJI.get(label, label.capitalize()), f"{pct * 100:.1f}%"])

    t2 = Table([["Sentiment Type", "Share"]] + sent_rows, colWidths=[10*cm, 7*cm])
    sent_bg_map = {"positive": colors.HexColor("#DCFCE7"), "negative": colors.HexColor("#FEE2E2"),
                   "neutral": colors.HexColor("#FEF3C7"),  "mixed": colors.HexColor("#FFF1E6"),
                   "sarcastic": colors.HexColor("#EDE9FE"), "ambiguous": colors.HexColor("#DBEAFE")}
    sent_txt_map = {k: SENTIMENT_COLORS[k] for k in SENTIMENT_COLORS}

    t2_style = [
        ("BACKGROUND",    (0,0), (-1,0), HDR_BG),
        ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 9),
        ("GRID",          (0,0), (-1,-1), 0.5, BORDER),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
    ]
    for i, (label, _) in enumerate(sorted(sentiment.items(), key=lambda x: x[1], reverse=True), start=1):
        bg = sent_bg_map.get(label, BG_LIGHT)
        fg = sent_txt_map.get(label, DARK)
        t2_style.append(("BACKGROUND", (0, i), (-1, i), bg))
        t2_style.append(("TEXTCOLOR",  (1, i), (1,  i), fg))
        t2_style.append(("FONTNAME",   (1, i), (1,  i), "Helvetica-Bold"))

    t2.setStyle(TableStyle(t2_style))
    story.append(t2)
    story.append(Spacer(1, 0.5*cm))

    # ── Product Satisfaction Summary ───────────────────────────────────
    processed = report_data.get("processed_reviews", [])
    if processed:
        story.extend(section_header("Product Satisfaction Summary"))
        story.append(Paragraph(
            "Satisfied = Positive + Neutral reviews. Unsatisfied = Negative + Mixed + Sarcastic + Ambiguous.",
            small_style
        ))
        story.append(Spacer(1, 0.2*cm))

        SATISFIED   = {"positive", "neutral"}
        UNSATISFIED = {"negative", "mixed", "sarcastic", "ambiguous"}
        by_product  = {}

        for r in processed:
            status = r.get("status", "clean")
            if status in ("bot_suspected", "duplicate"): continue
            name = r.get("product_name") or "Unknown"
            s    = r.get("overall_sentiment", "neutral")
            if name not in by_product:
                by_product[name] = {"total": 0, "satisfied": 0, "unsatisfied": 0}
            by_product[name]["total"] += 1
            if s in SATISFIED:   by_product[name]["satisfied"]   += 1
            if s in UNSATISFIED: by_product[name]["unsatisfied"] += 1

        # Top 8 by volume
        top_products = sorted(by_product.items(), key=lambda x: x[1]["total"], reverse=True)[:8]

        prod_rows = [["Product", "Total", "Satisfied", "Unsatisfied", "Sat. Rate"]]
        for name, d in top_products:
            rate = round(d["satisfied"] / max(d["total"], 1) * 100)
            prod_rows.append([
                name[:30], str(d["total"]),
                str(d["satisfied"]), str(d["unsatisfied"]),
                f"{rate}%",
            ])

        t_prod = Table(prod_rows, colWidths=[7*cm, 2*cm, 2.5*cm, 2.5*cm, 2.5*cm])
        t_prod_style = [
            ("BACKGROUND",    (0,0), (-1,0), HDR_BG),
            ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
            ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",      (0,0), (-1,-1), 8.5),
            ("GRID",          (0,0), (-1,-1), 0.5, BORDER),
            ("TOPPADDING",    (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            ("LEFTPADDING",   (0,0), (-1,-1), 8),
            ("ALIGN",         (1,0), (-1,-1), "CENTER"),
            ("ROWBACKGROUNDS",(0,1), (-1,-1), [BG_CARD, BG_LIGHT]),
        ]
        for i, (name, d) in enumerate(top_products, start=1):
            rate = round(d["satisfied"] / max(d["total"], 1) * 100)
            rate_color = GREEN if rate >= 60 else (YELLOW if rate >= 40 else RED)
            t_prod_style.append(("TEXTCOLOR", (2, i), (2, i), GREEN))
            t_prod_style.append(("TEXTCOLOR", (3, i), (3, i), RED))
            t_prod_style.append(("TEXTCOLOR", (4, i), (4, i), rate_color))
            t_prod_style.append(("FONTNAME",  (4, i), (4, i), "Helvetica-Bold"))

        t_prod.setStyle(TableStyle(t_prod_style))
        story.append(t_prod)
        story.append(Spacer(1, 0.5*cm))

    # ── Trend Alerts ───────────────────────────────────────────────────
    alerts = report_data.get("trend_alerts", [])
    if alerts:
        story.extend(section_header("Trend Alerts", color=RED))
        alert_rows = [["Severity", "Feature", "Type", "Rate", "Change"]]
        for a in alerts[:10]:
            alert_rows.append([
                a.get("severity", "").upper(),
                a.get("feature", ""),
                a.get("alert_type", "").replace("_", " "),
                f"{a.get('current_rate', 0) * 100:.0f}%",
                f"+{a.get('change_percent', 0):.0f}%",
            ])
        t3 = Table(alert_rows, colWidths=[2.5*cm, 4*cm, 5*cm, 2*cm, 2.5*cm])
        t3.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,0), colors.HexColor("#1E293B")),
            ("TEXTCOLOR",     (0,0), (-1,0), RED),
            ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",      (0,0), (-1,-1), 8.5),
            ("GRID",          (0,0), (-1,-1), 0.5, BORDER),
            ("ROWBACKGROUNDS",(0,1), (-1,-1), [colors.HexColor("#FFF5F5"), BG_CARD]),
            ("TEXTCOLOR",     (0,1), (-1,-1), SLATE),
            ("TEXTCOLOR",     (0,1), (0,-1), RED),
            ("FONTNAME",      (0,1), (0,-1), "Helvetica-Bold"),
            ("TOPPADDING",    (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ]))
        story.append(t3)
        story.append(Spacer(1, 0.5*cm))

    # ── Recommendations ────────────────────────────────────────────────
    recs = report_data.get("recommendations", [])
    if recs:
        story.extend(section_header("Actionable Recommendations"))
        for i, rec in enumerate(recs[:8]):
            p_num = rec.get("priority", 3)
            p_color = RED if p_num == 1 else (YELLOW if p_num == 2 else GREEN)
            badge_bg = colors.HexColor("#FEE2E2") if p_num == 1 else (colors.HexColor("#FEF3C7") if p_num == 2 else colors.HexColor("#DCFCE7"))
            rec_block = [
                [
                    Paragraph(f"P{p_num} · {rec.get('category','').upper()}",
                        ParagraphStyle("RecBadge", parent=styles["Normal"],
                            fontSize=8, textColor=p_color, fontName="Helvetica-Bold")),
                    Paragraph(f"<b>{rec.get('title','')}</b>",
                        ParagraphStyle("RecTitle", parent=styles["Normal"],
                            fontSize=10, textColor=DARK, fontName="Helvetica-Bold")),
                ],
                [
                    "",
                    Paragraph(rec.get("description", ""), body_style),
                ],
                [
                    "",
                    Paragraph(f"→ Action: {rec.get('suggested_action', '')}", small_style),
                ],
            ]
            rec_t = Table(rec_block, colWidths=[2.5*cm, 14*cm])
            rec_t.setStyle(TableStyle([
                ("BACKGROUND",    (0,0), (0,-1), badge_bg),
                ("BACKGROUND",    (1,0), (1,-1), BG_CARD),
                ("VALIGN",        (0,0), (-1,-1), "TOP"),
                ("TOPPADDING",    (0,0), (-1,-1), 5),
                ("BOTTOMPADDING", (0,0), (-1,-1), 5),
                ("LEFTPADDING",   (0,0), (-1,-1), 8),
                ("GRID",          (0,0), (-1,-1), 0.5, BORDER),
            ]))
            story.append(rec_t)
            story.append(Spacer(1, 0.2*cm))
        story.append(Spacer(1, 0.3*cm))

    # ── Orchestrator Decisions ─────────────────────────────────────────
    decisions = report_data.get("orchestrator_decisions", [])
    if decisions:
        story.extend(section_header("Orchestrator Decisions Log", color=colors.HexColor("#7C3AED")))
        dec_rows = [["Phase", "Decision", "Action"]]
        for d in decisions[:10]:
            dec_rows.append([
                d.get("phase", ""),
                d.get("decision", "").replace("_", " ")[:50],
                d.get("action", ""),
            ])
        t4 = Table(dec_rows, colWidths=[3.5*cm, 9*cm, 4*cm])
        t4.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,0), HDR_BG),
            ("TEXTCOLOR",     (0,0), (-1,0), colors.HexColor("#A78BFA")),
            ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",      (0,0), (-1,-1), 8.5),
            ("GRID",          (0,0), (-1,-1), 0.5, BORDER),
            ("ROWBACKGROUNDS",(0,1), (-1,-1), [BG_CARD, BG_LIGHT]),
            ("TEXTCOLOR",     (0,1), (-1,-1), SLATE),
            ("TOPPADDING",    (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ]))
        story.append(t4)

    # ── Footer ────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.6*cm))
    story.append(HRFlowable(width="100%", color=BORDER, thickness=0.8))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        f"Generated by ReviewIQ Agentic AI v2.0 — Powered by LangGraph + Gemini  |  "
        f"Report ID: {report_data.get('report_id','N/A')}  |  "
        f"{report_data.get('created_at','')[:19]} UTC",
        footer_style
    ))

    doc.build(story)
    return buffer.getvalue()


@app.get("/api/demo/dataset")
async def get_demo_dataset():
    """Get the synthetic demo dataset."""
    reviews = generate_synthetic_dataset()
    return {"reviews": reviews, "count": len(reviews)}


@app.get("/api/jobs")
async def list_jobs():
    """List all jobs."""
    return [
        {"job_id": k, "status": v["status"], "review_count": v.get("review_count")}
        for k, v in _jobs.items()
    ]


# ─── Scrape Endpoint ─────────────────────────────────────────────────────────

@app.post("/api/scrape")
async def scrape_reviews(request: ScrapeRequest):
    """
    Scrape product reviews from Amazon.in or Flipkart.
    Always returns data — uses realistic mock fallback if scraping is blocked.
    """
    url = request.url.strip()
    max_reviews = max(10, min(100, request.max_reviews))

    if not url:
        raise HTTPException(400, "URL must not be empty")

    url_lower = url.lower()
    if "amazon.in" in url_lower or "amazon.com" in url_lower or "amzn" in url_lower:
        platform = "amazon"
    elif "flipkart.com" in url_lower:
        platform = "flipkart"
    else:
        raise HTTPException(400, "Only Amazon.in and Flipkart URLs are supported")

    try:
        if platform == "amazon":
            from scrapers.amazon_scraper import scrape_amazon
            result = scrape_amazon(url, max_reviews)
        else:
            from scrapers.flipkart_scraper import scrape_flipkart
            result = scrape_flipkart(url, max_reviews)

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Scrape] Unexpected error: {e}", exc_info=True)
        # Ultimate fallback — never let the endpoint crash
        from scrapers.mock_data import get_mock_reviews
        return get_mock_reviews(url, max_reviews=max_reviews, platform=platform)


# ─── Executive Brief Endpoint ─────────────────────────────────────────────────

@app.post("/api/brief")
async def generate_executive_brief(request: BriefRequest):
    """
    Generate an executive brief from a report using LLM.
    Returns structured JSON with situation, business_impact, recommended_actions.
    """
    report = request.report

    total = report.get("total_reviews", 0)
    clean = report.get("clean_reviews", 0)
    bots  = report.get("bot_suspected_count", 0)
    sentiment_dist = report.get("overall_sentiment_distribution", {})
    recs  = report.get("recommendations", [])[:5]
    alerts = report.get("trend_alerts", [])[:3]
    product = report.get("product_name") or report.get("hotel_name")
    if not product:
        reviews_list = report.get("processed_reviews", [])
        for r in reviews_list:
            name = r.get("product_name", "")
            if name and name != "Hotel" and not name.startswith("job_"):
                product = name
                break
    if not product:
        cats = report.get("product_categories", [])
        product = cats[0] if cats else report.get("report_id", "Unknown Property")
    avg_rating = report.get("average_rating", None)

    context_summary = {
        "product_name": product,
        "total_reviews": total,
        "clean_reviews": clean,
        "bot_suspected": bots,
        "average_rating": avg_rating,
        "sentiment_distribution": {k: round(v * 100, 1) for k, v in sentiment_dist.items() if v > 0},
        "top_recommendations": [
            {"priority": r.get("priority"), "title": r.get("title"), "category": r.get("category")}
            for r in recs
        ],
        "trend_alerts": [
            {"severity": a.get("severity"), "alert_type": a.get("alert_type"), "feature": a.get("feature")}
            for a in alerts
        ],
        "feedback_loops_triggered": report.get("feedback_loops_triggered", 0),
    }

    system_prompt = (
        "You are a senior business analyst writing an executive brief for C-suite stakeholders.\n"
        "Write in formal, concise business language. No technical jargon.\n"
        "Use ONLY the data provided. Do not hallucinate.\n"
        "Return ONLY valid JSON, no markdown, no backticks:\n"
        "{\n"
        '  "situation": "2-3 sentence paragraph describing what the data shows",\n'
        '  "business_impact": "2-3 sentence paragraph on what this means for the business",\n'
        '  "recommended_actions": [\n'
        '    { "priority": "CRITICAL|HIGH|MEDIUM", "action": "specific actionable step" }\n'
        "  ],\n"
        '  "confidence_score": <integer 0-100>,\n'
        '  "product_name": "<product name>",\n'
        '  "summary_headline": "<one line compelling headline summarizing the situation>"\n'
        "}"
    )

    user_message = (
        f"Generate an executive brief based on this review analysis data:\n"
        f"{json.dumps(context_summary, indent=2)}"
    )

    try:
        llm = get_llm(temperature=0.3, max_tokens=1024)

        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message),
        ])

        content = response.content.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        parsed = json.loads(content)

        return {
            "situation":           str(parsed.get("situation", "")).strip(),
            "business_impact":     str(parsed.get("business_impact", "")).strip(),
            "recommended_actions": parsed.get("recommended_actions", []),
            "confidence_score":    int(parsed.get("confidence_score", 75)),
            "product_name":        str(parsed.get("product_name", product)).strip(),
            "summary_headline":    str(parsed.get("summary_headline", "")).strip(),
            "generated_at":        time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

    except json.JSONDecodeError as e:
        logger.warning(f"[Brief] JSON parse error: {e}")
        pos_pct = round(sentiment_dist.get("positive", 0) * 100)
        neg_pct = round(sentiment_dist.get("negative", 0) * 100)
        return {
            "situation": (
                f"Analysis of {total} customer reviews for {product} reveals a {pos_pct}% positive sentiment rate "
                f"with {neg_pct}% negative responses. {bots} suspected bot reviews were identified and excluded from analysis. "
                f"The pipeline processed {clean} authentic reviews to derive these insights."
            ),
            "business_impact": (
                f"Customer satisfaction levels indicate {'strong' if pos_pct > 60 else 'moderate'} product-market fit. "
                f"The {neg_pct}% negative sentiment requires attention to prevent churn. "
                f"Bot activity at {round(bots/max(total,1)*100)}% suggests the need for review authenticity measures."
            ),
            "recommended_actions": [
                {"priority": "HIGH",   "action": r.get("title", r.get("description", "")) }
                for r in recs[:3]
            ],
            "confidence_score": 70,
            "product_name": product,
            "summary_headline": f"{product} — {pos_pct}% Positive Sentiment Across {total} Reviews",
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
    except Exception as e:
        logger.error(f"[Brief] Unexpected error: {e}", exc_info=True)
        raise HTTPException(500, f"Brief generation error: {str(e)}")


@app.get("/api/brief/download/pdf")
async def download_brief_pdf(
    situation: str = "",
    business_impact: str = "",
    headline: str = "",
    product_name: str = "",
    confidence_score: int = 75,
):
    """Download executive brief as PDF."""
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    ORANGE = colors.HexColor("#FF7A00")
    DARK   = colors.HexColor("#1E293B")
    SLATE  = colors.HexColor("#475569")

    story = []
    story.append(Paragraph("EXECUTIVE BRIEF", ParagraphStyle("H",
        parent=styles["Normal"], fontSize=10, textColor=ORANGE,
        fontName="Helvetica-Bold", spaceAfter=4)))
    story.append(Paragraph(headline or f"Review Intelligence Report — {product_name}",
        ParagraphStyle("Title", parent=styles["Normal"], fontSize=18,
            textColor=DARK, fontName="Helvetica-Bold", spaceAfter=6)))
    story.append(Paragraph(f"Confidence Score: {confidence_score}/100",
        ParagraphStyle("Sub", parent=styles["Normal"], fontSize=9,
            textColor=SLATE, spaceAfter=12)))
    story.append(HRFlowable(width="100%", color=ORANGE, thickness=1.5))
    story.append(Spacer(1, 0.4*cm))

    for title, body in [("SITUATION", situation), ("BUSINESS IMPACT", business_impact)]:
        if body:
            story.append(Paragraph(title, ParagraphStyle("SH",
                parent=styles["Normal"], fontSize=9, textColor=ORANGE,
                fontName="Helvetica-Bold", spaceAfter=4)))
            story.append(Paragraph(body, ParagraphStyle("Body",
                parent=styles["Normal"], fontSize=10, textColor=SLATE,
                leading=16, spaceAfter=14)))

    story.append(Paragraph(
        f"Generated by ReviewIQ Agentic AI | {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}",
        ParagraphStyle("Footer", parent=styles["Normal"], fontSize=8, textColor=colors.HexColor("#94A3B8"))
    ))

    doc.build(story)
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=executive_brief_{int(time.time())}.pdf"}
    )


# ─── AI Chat Assistant ────────────────────────────────────────────────────────

@app.post("/chat")
async def chat_with_dashboard(request: ChatRequest):
    """
    AI Chat Assistant endpoint.
    Answers user queries strictly based on the provided dashboard context.
    Returns { answer, keywords }.
    """
    query = request.query.strip()
    context = request.context or {}

    if not query:
        raise HTTPException(400, "Query must not be empty")

    system_prompt = (
        "You are an AI assistant embedded inside a review analytics dashboard called ReviewIQ.\n\n"
        "STRICT RULES:\n"
        "1. Answer ONLY using the provided dashboard context JSON.\n"
        "2. DO NOT hallucinate, invent, or assume any data not present in the context.\n"
        "3. If the requested information is not in the context, respond EXACTLY:\n"
        '   "This information is not available in the current dashboard data."\n'
        "4. Keep answers concise (2-4 sentences max) and insight-focused.\n"
        "5. After the answer, extract keywords that satisfy ALL of these:\n"
        "   - The keyword appears in the user query OR is directly relevant to the answer.\n"
        "   - The keyword refers to data actually present in the context (features, sentiments, sections, metrics).\n"
        "   - Do NOT include generic words like 'the', 'is', 'data', 'review'.\n"
        "   - Do NOT use predefined or hardcoded keyword lists.\n"
        "6. Return ONLY valid JSON in this exact shape:\n"
        '   {"answer": "...", "keywords": ["keyword1", "keyword2"]}\n'
        "   No markdown, no backticks, no extra fields."
    )

    user_message = (
        f"Dashboard context:\n{json.dumps(context, indent=2)}\n\n"
        f"User question: {query}"
    )

    try:
        llm = get_llm(temperature=0.2, max_tokens=512)

        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message),
        ])

        content = response.content.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        parsed = json.loads(content)
        answer = str(parsed.get("answer", "")).strip() or "No answer returned."
        keywords = [str(k).strip().lower() for k in parsed.get("keywords", []) if str(k).strip()]
        return {"answer": answer, "keywords": keywords}

    except json.JSONDecodeError as e:
        logger.warning(f"[Chat] JSON parse error: {e}")
        return {
            "answer": "I had trouble parsing the AI response. Please try rephrasing your question.",
            "keywords": [],
        }
    except Exception as e:
        logger.error(f"[Chat] Unexpected error: {e}", exc_info=True)
        raise HTTPException(500, f"Chat error: {str(e)}")


# ─── Hotel Reviews Endpoints ──────────────────────────────────────────────────

from core.hotel_pipeline import run_hotel_pipeline, OUTPUT_FILE
from agents.summary_agent import aggregate_hotel_summary

_hotel_jobs: Dict[str, Dict[str, Any]] = {}


@app.post("/api/hotel-reviews/ingest")
async def ingest_hotel_reviews(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    hotel_id: str = "hotel_default",
    max_rows: Optional[int] = None,
):
    """
    Ingest a hotel reviews CSV through the 6-stage LangGraph pipeline.
    Generates sentiment, mentions, embeddings and stores in local JSON.
    Use max_rows to limit how many rows are read from the CSV.
    """
    content = await file.read()

    if not file.filename.endswith(".csv"):
        raise HTTPException(400, "Only CSV files are supported")

    reviews = parse_csv_reviews(content)
    if not reviews:
        raise HTTPException(400, "No valid reviews found in the CSV")

    if max_rows and max_rows < len(reviews):
        reviews = reviews[:max_rows]

    for r in reviews:
        if not r.get("category"):
            r["category"] = "Hotel"
        if not r.get("product_name"):
            r["product_name"] = r.get("hotel_name") or r.get("HotelName") or hotel_id
        if not r.get("hotel_id"):
            r["hotel_id"] = r.get("HotelId") or hotel_id

    job_id = f"hotel_job_{int(time.time() * 1000)}"
    _hotel_jobs[job_id] = {
        "status": "queued",
        "review_count": len(reviews),
        "hotel_id": hotel_id,
    }

    async def _run_hotel_job():
        try:
            _hotel_jobs[job_id]["status"] = "running"
            _hotel_jobs[job_id]["started_at"] = time.time()

            BATCH_SIZE = 100
            total_exported = 0
            all_errors = []
            batches = [reviews[i:i + BATCH_SIZE] for i in range(0, len(reviews), BATCH_SIZE)]
            _hotel_jobs[job_id]["total_batches"] = len(batches)
            _hotel_jobs[job_id]["completed_batches"] = 0

            for batch_idx, batch in enumerate(batches):
                logger.info(f"[HotelJob {job_id}] Processing batch {batch_idx + 1}/{len(batches)} ({len(batch)} reviews)")
                _hotel_jobs[job_id]["current_batch"] = batch_idx + 1

                final_state = await run_hotel_pipeline(
                    raw_reviews=batch,
                    hotel_id=hotel_id,
                )

                total_exported += final_state.get("progress", {}).get("total_exported", 0)
                all_errors.extend(final_state.get("errors", []))
                _hotel_jobs[job_id]["completed_batches"] = batch_idx + 1

                if batch_idx < len(batches) - 1:
                    await asyncio.sleep(2)

            _hotel_jobs[job_id]["status"] = "complete"
            _hotel_jobs[job_id]["doc_count"] = total_exported
            _hotel_jobs[job_id]["errors"] = all_errors
            _hotel_jobs[job_id]["progress"] = {"total_exported": total_exported}
        except Exception as e:
            logger.error(f"[HotelJob {job_id}] Failed: {e}", exc_info=True)
            _hotel_jobs[job_id]["status"] = "failed"
            _hotel_jobs[job_id]["error"] = str(e)

    background_tasks.add_task(_run_hotel_job)

    return {
        "job_id": job_id,
        "review_count": len(reviews),
        "hotel_id": hotel_id,
        "max_rows": max_rows,
        "message": "Hotel review ingestion started",
    }


@app.get("/api/hotel-reviews/jobs/{job_id}")
async def get_hotel_job_status(job_id: str):
    """Poll hotel ingestion job status."""
    if job_id not in _hotel_jobs:
        raise HTTPException(404, f"Job {job_id} not found")
    return _hotel_jobs[job_id]


@app.get("/api/hotel-reviews/mentions/popular")
async def get_popular_mentions(hotel_id: str = "hotel_default", limit: int = 20):
    """
    Get the most popular mentions across all processed hotel reviews.
    Equivalent to MongoDB: $unwind mentions → $group → $sort → $limit
    """
    if not os.path.exists(OUTPUT_FILE):
        return {"mentions": [], "total_reviews": 0}

    with open(OUTPUT_FILE, "r") as f:
        docs = json.load(f)

    filtered = [d for d in docs if d.get("hotel_id") == hotel_id]

    mention_counter: Counter = Counter()
    for doc in filtered:
        for mention in doc.get("mentions", []):
            mention_counter[mention] += 1

    top_mentions = [
        {"mention": m, "count": c}
        for m, c in mention_counter.most_common(limit)
    ]

    return {
        "hotel_id": hotel_id,
        "mentions": top_mentions,
        "total_reviews": len(filtered),
    }


@app.get("/api/hotel-reviews/search")
async def search_hotel_reviews(
    hotel_id: str = "hotel_default",
    tag: Optional[str] = None,
    sentiment: Optional[str] = None,
    min_rating: Optional[float] = None,
    page: int = 0,
    page_size: int = 20,
):
    """
    Filter and paginate hotel reviews by mention tag, sentiment, or rating.
    """
    if not os.path.exists(OUTPUT_FILE):
        return {"reviews": [], "total": 0, "page": page}

    with open(OUTPUT_FILE, "r") as f:
        docs = json.load(f)

    filtered = [d for d in docs if d.get("hotel_id") == hotel_id]

    if tag:
        tag_lower = tag.lower()
        filtered = [d for d in filtered if tag_lower in d.get("mentions", [])]

    if sentiment:
        filtered = [d for d in filtered if d.get("sentiment") == sentiment.lower()]

    if min_rating is not None:
        filtered = [d for d in filtered if (d.get("rating") or 0) >= min_rating]

    total = len(filtered)
    start = page * page_size
    page_docs = filtered[start:start + page_size]

    results = []
    for doc in page_docs:
        results.append({
            "_id": doc["_id"],
            "hotel_id": doc.get("hotel_id"),
            "hotel_name": doc.get("hotel_name"),
            "text": doc["text"],
            "title": doc.get("title", ""),
            "user_name": doc.get("user_name", ""),
            "submission_time": doc.get("submission_time", ""),
            "rating": doc.get("rating"),
            "sub_ratings": doc.get("sub_ratings", {}),
            "sentiment": doc.get("sentiment"),
            "categories": doc.get("categories", {}),
            "mentions": doc.get("mentions", []),
        })

    return {
        "hotel_id": hotel_id,
        "reviews": results,
        "total": total,
        "page": page,
        "page_size": page_size,
        "filters_applied": {
            "tag": tag,
            "sentiment": sentiment,
            "min_rating": min_rating,
        },
    }


@app.get("/api/hotel-reviews/semantic-search")
async def semantic_search_hotel_reviews(
    q: str,
    hotel_id: str = "hotel_default",
    top_k: int = 10,
    min_score: float = 0.3,
    sentiment: Optional[str] = None,
    tag: Optional[str] = None,
):
    """
    Semantic search over hotel reviews using LangChain InMemoryVectorStore
    with cosine similarity. Pre-loaded at startup from hotel_reviews_processed.json.

    The store uses cosine_similarity from langchain_community to rank results.
    Supports metadata-based filtering for hotel_id, sentiment, and mention tags.

    Args:
        q: Natural language search query (e.g. "quiet room away from elevator")
        hotel_id: Filter to a specific hotel
        top_k: Number of top results to return
        min_score: Minimum cosine similarity threshold (0-1)
        sentiment: Optional filter by sentiment (positive/negative/neutral)
        tag: Optional filter by mention tag
    """
    if not q.strip():
        raise HTTPException(400, "Query parameter 'q' is required")

    if _vector_store is None:
        raise HTTPException(503, "Vector store not loaded. Run ingestion first or restart server.")

    def _metadata_filter(doc: Document) -> bool:
        meta = doc.metadata
        if meta.get("hotel_id") != hotel_id:
            return False
        if sentiment and meta.get("sentiment") != sentiment.lower():
            return False
        if tag and tag.lower() not in [m.lower() for m in meta.get("mentions", [])]:
            return False
        return True

    def _run_search():
        return _vector_store._similarity_search_with_score_by_vector(
            embedding=_vector_store.embedding.embed_query(q),
            k=top_k,
            filter=_metadata_filter,
        )

    results_with_scores = await asyncio.to_thread(_run_search)

    results = []
    for doc, score, _ in results_with_scores:
        if score < min_score:
            continue
        results.append({
            "_id": doc.metadata.get("_id"),
            "score": round(float(score), 4),
            "hotel_id": doc.metadata.get("hotel_id"),
            "hotel_name": doc.metadata.get("hotel_name"),
            "text": doc.page_content,
            "title": doc.metadata.get("title", ""),
            "user_name": doc.metadata.get("user_name", ""),
            "submission_time": doc.metadata.get("submission_time", ""),
            "rating": doc.metadata.get("rating"),
            "sub_ratings": doc.metadata.get("sub_ratings", {}),
            "sentiment": doc.metadata.get("sentiment"),
            "categories": doc.metadata.get("categories", {}),
            "mentions": doc.metadata.get("mentions", []),
        })

    return {
        "query": q,
        "hotel_id": hotel_id,
        "results": results,
        "total_matches": len(results),
        "top_k": top_k,
        "min_score": min_score,
        "similarity_metric": "cosine",
        "filters_applied": {
            "sentiment": sentiment,
            "tag": tag,
        },
    }


@app.post("/api/hotel-reviews/vector-store/reload")
async def reload_vector_store():
    """Reload the in-memory vector store from disk (call after new ingestion)."""
    await asyncio.to_thread(_load_vector_store)
    return {
        "status": "reloaded",
        "total_docs": _vector_store_metadata.get("total_docs", 0),
    }


@app.get("/api/hotel-reviews/stats")
async def get_hotel_review_stats(hotel_id: str = "hotel_default"):
    """Get summary statistics for processed hotel reviews."""
    if not os.path.exists(OUTPUT_FILE):
        return {"total": 0, "message": "No processed reviews yet"}

    with open(OUTPUT_FILE, "r") as f:
        docs = json.load(f)

    filtered = [d for d in docs if d.get("hotel_id") == hotel_id]

    if not filtered:
        return {"total": 0, "hotel_id": hotel_id, "message": "No reviews for this hotel"}

    sentiment_dist = Counter(d.get("sentiment", "neutral") for d in filtered)
    ratings = [d["rating"] for d in filtered if d.get("rating") is not None]
    avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else None

    mention_counter: Counter = Counter()
    for doc in filtered:
        for m in doc.get("mentions", []):
            mention_counter[m] += 1

    return {
        "hotel_id": hotel_id,
        "total_reviews": len(filtered),
        "average_rating": avg_rating,
        "sentiment_distribution": dict(sentiment_dist),
        "top_mentions": [{"mention": m, "count": c} for m, c in mention_counter.most_common(10)],
        "has_embeddings": any(len(d.get("embedding", [])) > 0 for d in filtered),
    }


@app.get("/api/hotel-reviews/{hotel_id}/summary")
async def get_hotel_summary(hotel_id: str, force_refresh: bool = False):
    """
    Get an AI-generated narrative summary for a hotel.
    Uses incremental Map-Reduce: batch digests are generated at ingestion time,
    and aggregated into a cached summary on first request.
    Pass force_refresh=true to regenerate even if cache is fresh.
    """
    summary = await asyncio.to_thread(aggregate_hotel_summary, hotel_id, force_refresh)

    if "error" in summary:
        raise HTTPException(404, summary["error"])

    return summary


@app.get("/api/hotel-reviews/graph")
async def get_pipeline_graph():
    """Return the LangGraph pipeline as an HTML page with Mermaid rendered client-side."""
    from core.hotel_pipeline import get_hotel_pipeline
    from fastapi.responses import HTMLResponse

    pipeline = get_hotel_pipeline()
    mermaid_code = pipeline.get_graph().draw_mermaid()

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>ReviewLens Pipeline Graph</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
    <style>
        body {{ font-family: system-ui, sans-serif; margin: 0; padding: 2rem; background: #1a1a2e; color: #eee; display: flex; flex-direction: column; align-items: center; }}
        h1 {{ margin-bottom: 1rem; }}
        .mermaid {{ background: #fff; padding: 2rem; border-radius: 12px; max-width: 100%; overflow-x: auto; }}
    </style>
</head>
<body>
    <h1>ReviewLens - Hotel Pipeline Graph</h1>
    <div class="mermaid">
{mermaid_code}
    </div>
    <script>mermaid.initialize({{ startOnLoad: true, theme: 'default' }});</script>
</body>
</html>"""
    return HTMLResponse(content=html)


@app.get("/api/hotel-reviews/data")
async def get_hotel_reviews_data(
    hotel_id: Optional[str] = None,
    page: int = 0,
    page_size: int = 50,
):
    """
    Return all processed hotel reviews from the JSON store.
    Supports optional hotel_id filter and pagination.
    """
    if not os.path.exists(OUTPUT_FILE):
        return {"reviews": [], "total": 0, "page": page, "page_size": page_size}

    with open(OUTPUT_FILE, "r") as f:
        docs = json.load(f)

    if hotel_id:
        docs = [d for d in docs if d.get("hotel_id") == hotel_id]

    total = len(docs)
    start = page * page_size
    page_docs = docs[start:start + page_size]

    results = []
    for doc in page_docs:
        results.append({
            "_id": doc.get("_id"),
            "hotel_id": doc.get("hotel_id"),
            "hotel_name": doc.get("hotel_name"),
            "text": doc.get("text"),
            "title": doc.get("title", ""),
            "user_name": doc.get("user_name", ""),
            "locale": doc.get("locale", ""),
            "submission_time": doc.get("submission_time", ""),
            "rating": doc.get("rating"),
            "sub_ratings": doc.get("sub_ratings", {}),
            "sentiment": doc.get("sentiment"),
            "confidence": doc.get("confidence"),
            "categories": doc.get("categories", {}),
            "mentions": doc.get("mentions", []),
            "language": doc.get("language", ""),
        })

    return {
        "reviews": results,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@app.get("/api/hotel-reviews/properties")
async def list_properties():
    """Return distinct properties available in the processed reviews store."""
    if not os.path.exists(OUTPUT_FILE):
        return {"properties": []}

    with open(OUTPUT_FILE, "r") as f:
        docs = json.load(f)

    props: Dict[str, Any] = {}
    for doc in docs:
        hid = doc.get("hotel_id")
        if hid and hid not in props:
            sub_ratings = doc.get("sub_ratings", {})
            rating = doc.get("rating")
            if not rating and sub_ratings:
                rating = round(sum(sub_ratings.values()) / len(sub_ratings), 1)
            props[hid] = {
                "property_code": hid,
                "hotel_name": doc.get("hotel_name", hid),
                "review_count": 0,
            }
        if hid:
            props[hid]["review_count"] += 1

    return {"properties": list(props.values())}


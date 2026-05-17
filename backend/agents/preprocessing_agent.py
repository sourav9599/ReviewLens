"""
Agent 1: Ingestion & Preprocessing Agent
- Handles CSV/JSON/text input
- Cleans noise: typos, emojis, mixed language
- Language detection
- Normalizes review structure
"""
import re
import uuid
import emoji
from typing import List, Dict, Any
from langdetect import detect, detect_langs, LangDetectException
from core.models import ReviewPipelineState, ProcessedReview, ReviewStatus
import logging

logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """Clean review text while preserving semantic meaning."""
    if not text or not isinstance(text, str):
        return ""
    
    # Convert emojis to text descriptions
    text = emoji.demojize(text, delimiters=(" :", ": "))
    
    # Remove URLs
    text = re.sub(r'http[s]?://\S+', '', text)
    
    # Remove excessive punctuation but keep sentence boundaries
    text = re.sub(r'[!]{2,}', '!', text)
    text = re.sub(r'[?]{2,}', '?', text)
    text = re.sub(r'\.{4,}', '...', text)
    
    # Remove special characters but keep Hindi/Devanagari unicode range and basic punctuation
    text = re.sub(r'[^\w\s\u0900-\u097F\u0980-\u09FF.,!?\'"\-:;()\u2013\u2014]', ' ', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def detect_language(text: str) -> tuple[str, List[str]]:
    """Detect primary language and all detected languages."""
    try:
        primary = detect(text)
        langs = detect_langs(text)
        all_langs = [str(l).split(':')[0] for l in langs if float(str(l).split(':')[1]) > 0.1]
        return primary, all_langs
    except (LangDetectException, Exception):
        return "en", ["en"]


def extract_rating_from_text(text: str) -> float | None:
    """Try to extract implicit rating signals from text."""
    patterns = [
        r'(\d+)\s*/\s*5',
        r'(\d+)\s*stars?',
        r'(\d+)\s*out\s*of\s*5',
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            val = float(m.group(1))
            return min(5.0, max(1.0, val))
    return None


def flag_review(review: ProcessedReview, raw: Dict[str, Any]) -> ProcessedReview:
    """Apply initial flags based on heuristics."""
    flags = []
    text = review.cleaned_text.lower()
    
    # Very short review
    if len(review.cleaned_text.split()) < 3:
        flags.append("very_short")
    
    # All caps
    if review.original_text.isupper() and len(review.original_text) > 10:
        flags.append("all_caps")
    
    # Mixed language
    if len(review.detected_languages) > 1:
        flags.append("multilingual")
    
    # Contains Hindi
    if any(l in review.detected_languages for l in ["hi", "mr", "bn", "ta", "te", "kn"]):
        flags.append("indian_language")
    
    review.flags = flags
    return review


def preprocessing_agent(state: ReviewPipelineState) -> ReviewPipelineState:
    """
    Preprocessing Agent: Ingests raw reviews and produces clean, structured ProcessedReview objects.
    """
    raw_reviews = state["raw_reviews"]
    preprocessed = []
    errors = list(state.get("errors", []))
    
    logger.info(f"[PreprocessingAgent] Processing {len(raw_reviews)} raw reviews")
    
    for i, raw in enumerate(raw_reviews):
        try:
            review_id = raw.get("id") or str(uuid.uuid4())[:8]
            original_text = str(raw.get("review_text") or raw.get("text") or raw.get("body") or "")
            
            if not original_text.strip():
                continue
            
            cleaned = clean_text(original_text)
            primary_lang, all_langs = detect_language(original_text)
            
            # Extract rating
            rating = raw.get("rating") or raw.get("stars") or raw.get("score")
            if rating:
                try:
                    rating = float(rating)
                except:
                    rating = extract_rating_from_text(original_text)
            
            review = ProcessedReview(
                id=review_id,
                original_text=original_text,
                cleaned_text=cleaned,
                language=primary_lang,
                detected_languages=all_langs,
                product_category=str(raw.get("category") or raw.get("product_category") or "Unknown"),
                product_name=str(raw.get("product_name") or raw.get("product") or "Unknown Product"),
                rating=rating,
                review_date=str(raw.get("date") or raw.get("review_date") or ""),
                helpful_votes=int(raw.get("helpful_votes") or 0),
                verified_purchase=bool(raw.get("verified_purchase") or False),
                status=ReviewStatus.CLEAN,
            )
            
            review = flag_review(review, raw)
            preprocessed.append(review)
            
        except Exception as e:
            errors.append(f"Preprocessing error on review {i}: {str(e)}")
            logger.warning(f"[PreprocessingAgent] Error on review {i}: {e}")
    
    logger.info(f"[PreprocessingAgent] Completed: {len(preprocessed)} reviews preprocessed")
    
    state["preprocessed_reviews"] = preprocessed
    state["errors"] = errors
    state["progress"] = {**state.get("progress", {}), "preprocessing": "complete", "preprocessed_count": len(preprocessed)}
    
    return state

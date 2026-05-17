"""
Cross-Product Comparison Agent
================================
- Groups reviews by product_category
- Computes per-category sentiment distributions
- Feature-level complaint/praise rates per category
- Identifies best/worst performing categories
- Outputs CrossProductComparison to pipeline state
"""
import logging
from typing import Dict, List
from collections import defaultdict, Counter
from core.models import (
    ReviewPipelineState, ProcessedReview,
    SentimentLabel, ReviewStatus, CrossProductComparison
)

logger = logging.getLogger(__name__)


def cross_comparison_agent(state: ReviewPipelineState) -> ReviewPipelineState:
    """
    Cross-Product Comparison Agent: Analyzes reviews grouped by product category.
    """
    reviews = state["analyzed_reviews"]
    errors = list(state.get("errors", []))

    # Filter to analyzable reviews
    analyzable = [
        r for r in reviews
        if r.status not in {ReviewStatus.DUPLICATE, ReviewStatus.BOT_SUSPECTED}
    ]

    # Group by category
    by_category: Dict[str, List[ProcessedReview]] = defaultdict(list)
    for r in analyzable:
        cat = r.product_category if r.product_category and r.product_category != "Unknown" else "General"
        by_category[cat].append(r)

    if len(by_category) < 2:
        logger.info("[CrossComparisonAgent] Not enough categories for comparison")
        state["cross_product_comparison"] = CrossProductComparison(
            categories=list(by_category.keys()),
            sentiment_by_category={},
            feature_by_category={},
            review_count_by_category={cat: len(revs) for cat, revs in by_category.items()},
        )
        state["progress"] = {**state.get("progress", {}), "cross_comparison": "skipped"}
        return state

    logger.info(f"[CrossComparisonAgent] Comparing {len(by_category)} categories: {list(by_category.keys())}")

    sentiment_by_cat: Dict[str, Dict[str, float]] = {}
    feature_by_cat: Dict[str, Dict[str, float]] = {}
    bot_rate_by_cat: Dict[str, float] = {}
    review_count_by_cat: Dict[str, int] = {}

    category_scores: Dict[str, float] = {}    # composite positive score for ranking

    for cat, cat_reviews in by_category.items():
        total = len(cat_reviews)
        review_count_by_cat[cat] = total

        # Sentiment distribution
        sentiment_counts = Counter(r.overall_sentiment.value for r in cat_reviews)
        sentiment_by_cat[cat] = {
            k: round(v / total, 3) for k, v in sentiment_counts.items()
        }

        # Bot rate
        all_cat_reviews_incl_bots = [r for r in reviews if (r.product_category or "General") == cat or (r.product_category == "Unknown" and cat == "General")]
        bot_count = sum(1 for r in all_cat_reviews_incl_bots if r.status == ReviewStatus.BOT_SUSPECTED)
        bot_rate_by_cat[cat] = round(bot_count / max(len(all_cat_reviews_incl_bots), 1), 3)

        # Feature complaint rates
        feature_complaints: Dict[str, int] = defaultdict(int)
        feature_praises: Dict[str, int] = defaultdict(int)
        feature_total: Dict[str, int] = defaultdict(int)

        for r in cat_reviews:
            for fs in r.feature_sentiments:
                feature_total[fs.feature] += 1
                if fs.sentiment == SentimentLabel.NEGATIVE:
                    feature_complaints[fs.feature] += 1
                elif fs.sentiment == SentimentLabel.POSITIVE:
                    feature_praises[fs.feature] += 1

        feature_by_cat[cat] = {
            f: round(feature_complaints[f] / max(feature_total[f], 1), 3)
            for f in feature_total
        }

        # Composite positive score (higher = better category)
        pos_rate = sentiment_by_cat[cat].get("positive", 0.0)
        neg_rate = sentiment_by_cat[cat].get("negative", 0.0)
        category_scores[cat] = pos_rate - neg_rate

    # Rank categories
    ranked = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
    best_category = ranked[0][0] if ranked else ""
    worst_category = ranked[-1][0] if ranked else ""

    comparison = CrossProductComparison(
        categories=list(by_category.keys()),
        sentiment_by_category=sentiment_by_cat,
        feature_by_category=feature_by_cat,
        best_category=best_category,
        worst_category=worst_category,
        bot_rate_by_category=bot_rate_by_cat,
        review_count_by_category=review_count_by_cat,
    )

    logger.info(f"[CrossComparisonAgent] Best: {best_category}, Worst: {worst_category}")

    state["cross_product_comparison"] = comparison
    state["errors"] = errors
    state["progress"] = {
        **state.get("progress", {}),
        "cross_comparison": "complete",
        "categories_compared": len(by_category),
        "best_category": best_category,
        "worst_category": worst_category,
    }

    return state

"""
Agent 5: Actionable Recommendations Agent
- Synthesizes all analysis into prioritized, business-ready recommendations
- Uses LLM to generate contextual, specific actions
- Categorizes by product/marketing/operations/quality
"""
import json
import re
from typing import List, Dict, Any
from collections import defaultdict, Counter
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from core.models import (
    ReviewPipelineState, ProcessedReview, TrendAlert,
    ActionableRecommendation, SentimentLabel, ReviewStatus
)
from core.config import settings
import logging

logger = logging.getLogger(__name__)


RECOMMENDATION_PROMPT = PromptTemplate(
    input_variables=["analysis_summary", "top_issues", "top_praises", "alerts"],
    template="""You are a senior product strategy consultant. Based on the following customer review analysis, generate 5-8 prioritized, actionable recommendations for the product and marketing teams.

ANALYSIS SUMMARY:
{analysis_summary}

TOP ISSUES (Features with most complaints):
{top_issues}

TOP PRAISES (Features with most positive feedback):
{top_praises}

TREND ALERTS:
{alerts}

Generate recommendations as a JSON array. Return ONLY valid JSON, no markdown.

Each recommendation must follow this structure:
{{
  "priority": 1,
  "category": "product|marketing|operations|quality",
  "title": "Short action title",
  "description": "What the data shows",
  "supporting_data": "Specific numbers/percentages from the analysis",
  "suggested_action": "Concrete step to take",
  "estimated_impact": "Expected business outcome",
  "affected_feature": "battery life"
}}

Priority 1=critical, 2=high, 3=medium, 4=low.
Be specific, data-driven, and actionable. Do not be generic."""
)


def build_analysis_summary(
    reviews: List[ProcessedReview],
    alerts: List[TrendAlert]
) -> tuple[str, str, str, str]:
    """Build summary strings for the LLM prompt."""
    
    analyzable = [
        r for r in reviews
        if r.status not in {ReviewStatus.DUPLICATE, ReviewStatus.BOT_SUSPECTED}
    ]
    
    total = len(analyzable)
    if total == 0:
        return "No data", "None", "None", "None"
    
    # Overall sentiment distribution
    sentiment_counts = Counter(r.overall_sentiment.value for r in analyzable)
    
    # Feature-level aggregation
    feature_complaints: Dict[str, int] = defaultdict(int)
    feature_praises: Dict[str, int] = defaultdict(int)
    feature_total: Dict[str, int] = defaultdict(int)
    
    for review in analyzable:
        for fs in review.feature_sentiments:
            feature_total[fs.feature] += 1
            if fs.sentiment == SentimentLabel.NEGATIVE:
                feature_complaints[fs.feature] += 1
            elif fs.sentiment == SentimentLabel.POSITIVE:
                feature_praises[fs.feature] += 1
    
    summary = (
        f"Total reviews analyzed: {total}. "
        f"Sentiment breakdown: "
        f"{sentiment_counts.get('positive', 0)} positive ({sentiment_counts.get('positive', 0)/total:.0%}), "
        f"{sentiment_counts.get('negative', 0)} negative ({sentiment_counts.get('negative', 0)/total:.0%}), "
        f"{sentiment_counts.get('neutral', 0)} neutral ({sentiment_counts.get('neutral', 0)/total:.0%}), "
        f"{sentiment_counts.get('mixed', 0)} mixed. "
        f"Features analyzed: {len(feature_total)}. "
        f"Active trend alerts: {len(alerts)}."
    )
    
    # Top issues
    top_issues_list = sorted(
        [(f, c, feature_total[f]) for f, c in feature_complaints.items() if feature_total[f] >= 3],
        key=lambda x: x[1] / x[2],
        reverse=True
    )[:5]
    top_issues = "; ".join(
        f"{f}: {c}/{t} reviews ({c/t:.0%} complaint rate)"
        for f, c, t in top_issues_list
    ) or "None identified"
    
    # Top praises
    top_praises_list = sorted(
        [(f, p, feature_total[f]) for f, p in feature_praises.items() if feature_total[f] >= 3],
        key=lambda x: x[1] / x[2],
        reverse=True
    )[:5]
    top_praises = "; ".join(
        f"{f}: {p}/{t} reviews ({p/t:.0%} praise rate)"
        for f, p, t in top_praises_list
    ) or "None identified"
    
    # Alerts
    alerts_str = "; ".join(
        f"[{a.severity.upper()}] {a.feature}: {a.alert_type} ({a.current_rate:.0%} rate, +{a.change_percent:.0f}%)"
        for a in alerts[:5]
    ) or "No alerts"
    
    return summary, top_issues, top_praises, alerts_str


def parse_recommendations(response: str) -> List[ActionableRecommendation]:
    """Parse LLM response into ActionableRecommendation objects."""
    try:
        # Extract JSON array
        match = re.search(r'\[.*\]', response, re.DOTALL)
        if match:
            data = json.loads(match.group())
        else:
            data = json.loads(response.strip())
        
        recs = []
        for item in data:
            rec = ActionableRecommendation(
                priority=int(item.get("priority", 3)),
                category=str(item.get("category", "product")),
                title=str(item.get("title", "Recommendation")),
                description=str(item.get("description", "")),
                supporting_data=str(item.get("supporting_data", "")),
                suggested_action=str(item.get("suggested_action", "")),
                estimated_impact=str(item.get("estimated_impact", "")),
                affected_feature=str(item.get("affected_feature", ""))
            )
            recs.append(rec)
        
        return sorted(recs, key=lambda r: r.priority)
    
    except Exception as e:
        logger.warning(f"[RecommendationAgent] Failed to parse recommendations: {e}")
        return []


def fallback_recommendations(
    reviews: List[ProcessedReview],
    alerts: List[TrendAlert]
) -> List[ActionableRecommendation]:
    """Rule-based fallback recommendations when LLM fails."""
    recs = []
    
    feature_complaints: Dict[str, int] = defaultdict(int)
    feature_total: Dict[str, int] = defaultdict(int)
    
    for r in reviews:
        for fs in r.feature_sentiments:
            feature_total[fs.feature] += 1
            if fs.sentiment == SentimentLabel.NEGATIVE:
                feature_complaints[fs.feature] += 1
    
    # Top complaint features
    for feature, count in sorted(feature_complaints.items(), key=lambda x: x[1], reverse=True)[:3]:
        total = feature_total[feature]
        rate = count / max(total, 1)
        if rate >= 0.25:
            recs.append(ActionableRecommendation(
                priority=1 if rate >= 0.4 else 2,
                category="product",
                title=f"Address {feature.title()} Issues",
                description=f"{rate:.0%} of reviews mention negative {feature}",
                supporting_data=f"{count} complaints out of {total} mentions",
                suggested_action=f"Conduct root cause analysis on {feature} and prioritize fix in next sprint",
                estimated_impact="Estimated improvement in overall rating",
                affected_feature=feature
            ))
    
    # Alert-based recommendations
    for alert in alerts[:3]:
        if alert.severity in {"critical", "warning"}:
            recs.append(ActionableRecommendation(
                priority=1 if alert.severity == "critical" else 2,
                category="quality",
                title=f"Investigate {alert.feature.title()} Trend",
                description=alert.description,
                supporting_data=f"Rate: {alert.current_rate:.0%}, Change: +{alert.change_percent:.0f}%",
                suggested_action="Immediate quality control review recommended",
                estimated_impact="Prevent customer churn and negative word-of-mouth",
                affected_feature=alert.feature
            ))
    
    return sorted(recs, key=lambda r: r.priority)


def recommendations_agent(state: ReviewPipelineState) -> ReviewPipelineState:
    """
    Recommendations Agent: Synthesizes analysis into actionable business recommendations.
    """
    reviews = state["analyzed_reviews"]
    alerts = state["trend_alerts"]
    errors = list(state.get("errors", []))
    
    logger.info(f"[RecommendationAgent] Generating recommendations from {len(reviews)} reviews and {len(alerts)} alerts")
    
    summary, top_issues, top_praises, alerts_str = build_analysis_summary(reviews, alerts)
    
    try:
        llm = OllamaLLM(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            temperature=0.0,
            num_predict=400,
        )
        
        prompt = RECOMMENDATION_PROMPT.format(
            analysis_summary=summary,
            top_issues=top_issues,
            top_praises=top_praises,
            alerts=alerts_str
        )
        
        response = llm.invoke(prompt)
        recommendations = parse_recommendations(response)
        
        if not recommendations:
            raise ValueError("No recommendations parsed from LLM")
        
        logger.info(f"[RecommendationAgent] Generated {len(recommendations)} recommendations via LLM")
        
    except Exception as e:
        logger.warning(f"[RecommendationAgent] LLM failed, using fallback: {e}")
        recommendations = fallback_recommendations(reviews, alerts)
        errors.append(f"Recommendations fallback used: {str(e)}")
    
    state["recommendations"] = recommendations
    state["errors"] = errors
    state["progress"] = {
        **state.get("progress", {}),
        "recommendations": "complete",
        "recommendation_count": len(recommendations)
    }
    
    return state

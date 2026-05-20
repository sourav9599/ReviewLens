"""
Agent 6: Actionable Recommendations Agent
===========================================
Synthesizes all upstream analysis (sentiment, trends, anomalies) into
prioritized, business-ready recommendations for Marriott property General
Managers and operations teams. Uses Gemini LLM to generate contextual,
hotel-specific actions categorized by operations, service, marketing, and
quality improvement.

ReviewLens Context:
───────────────────
ReviewLens replaces the 45-minute daily manual review scan with automated
topic intelligence. This agent is the "action layer" — converting statistical
signals (topic heatmaps, trend alerts, sentiment shifts) into concrete steps:
"Increase housekeeping staff on floors 4-8 during weekend peak" or
"Noise: install sound-dampening panels near elevator bank — 23 complaints."

Enterprise KPI Alignment:
─────────────────────────
• RevPAR: Prioritized operational recommendations directly target issues
  suppressing occupancy and ADR (e.g. "Address cleanliness at 35% negative").
• EBITDA Growth: Replaces expensive consulting; automated insight delivery
  at scale reduces cost-per-insight across 9,000+ properties.
• Intent to Recommend: Recommendations that fix guest pain points directly
  improve NPS (+4-8 points within 90 days per Cornell Hospitality study).
• Leadership Index: Structured action plan prioritized by impact enables
  focused, measurable leadership execution.
• Non-RevPAR Affiliation Fees: AI-driven operational intelligence adds
  value to the franchise relationship.

Pipeline Position: Runs AFTER trend detection → feeds Cross-Comparison/Report.
"""
import json
import re
from typing import List, Dict, Any
from collections import defaultdict, Counter
from langchain_google_genai import ChatGoogleGenerativeAI
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
    template="""You are a hospitality operations strategist with 15 years of experience advising luxury and full-service hotel properties on service recovery, operational efficiency, and revenue optimization.

CONTEXT: You are reviewing guest feedback analytics for a Marriott property. Your recommendations will be presented to the General Manager and Department Heads in their weekly operations meeting.

ANALYSIS DATA:
{analysis_summary}

GUEST PAIN POINTS (ranked by frequency):
{top_issues}

GUEST DELIGHT DRIVERS (ranked by frequency):
{top_praises}

ACTIVE ALERTS:
{alerts}

TASK: Generate 5-8 prioritized recommendations that follow the SMART framework (Specific, Measurable, Achievable, Relevant, Time-bound).

RECOMMENDATION PRINCIPLES:
- Each recommendation must tie to a measurable business outcome (NPS, RevPAR, CSAT, or cost reduction)
- Distinguish between quick wins (< 48 hours, no budget) vs. strategic investments (require capex/staffing changes)
- For negative trends: prescribe BOTH immediate containment AND root cause resolution
- For positive trends: prescribe amplification strategies (marketing, upsell, staff recognition)
- Never recommend "monitor the situation" — every recommendation must have a concrete action verb
- Consider the guest lifecycle: pre-arrival, check-in, in-stay, check-out, post-stay

OUTPUT: Return ONLY a valid JSON array. No markdown, no backticks, no explanation.

Each object in the array:
{{
  "priority": 1,
  "category": "operations|service|marketing|quality",
  "title": "Action-verb title (e.g. 'Deploy additional housekeeping staff on weekends')",
  "description": "What the guest feedback reveals — written as an insight, not a data dump",
  "supporting_data": "The specific metric or pattern that triggered this recommendation",
  "suggested_action": "Concrete next step with owner, timeline, and success metric",
  "estimated_impact": "Projected business outcome (e.g. '+3 NPS points within 30 days', 'Reduce complaint rate from 35% to 15%')",
  "affected_feature": "cleanliness"
}}

Priority scale: 1 = Critical (revenue/reputation at immediate risk), 2 = High (address this week), 3 = Medium (this month), 4 = Low (next quarter planning)."""
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
    
    for feature, count in sorted(feature_complaints.items(), key=lambda x: x[1], reverse=True)[:3]:
        total = feature_total[feature]
        rate = count / max(total, 1)
        if rate >= 0.25:
            recs.append(ActionableRecommendation(
                priority=1 if rate >= 0.4 else 2,
                category="operations",
                title=f"Address {feature.replace('_', ' ').title()} Complaints",
                description=f"{rate:.0%} of guest reviews mention negative {feature.replace('_', ' ')} experience",
                supporting_data=f"{count} complaints out of {total} mentions",
                suggested_action=f"Investigate root cause of {feature.replace('_', ' ')} issues; consider staffing/maintenance review",
                estimated_impact="Expected improvement in guest satisfaction scores and NPS",
                affected_feature=feature
            ))
    
    for alert in alerts[:3]:
        if alert.severity in {"critical", "warning"}:
            recs.append(ActionableRecommendation(
                priority=1 if alert.severity == "critical" else 2,
                category="quality",
                title=f"Investigate {alert.feature.replace('_', ' ').title()} Trend",
                description=alert.description,
                supporting_data=f"Rate: {alert.current_rate:.0%}, Change: +{alert.change_percent:.0f}%",
                suggested_action="Immediate operational review and guest recovery protocol",
                estimated_impact="Prevent NPS decline and negative review accumulation",
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
        llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.0,
            max_output_tokens=1024,
        )
        
        prompt = RECOMMENDATION_PROMPT.format(
            analysis_summary=summary,
            top_issues=top_issues,
            top_praises=top_praises,
            alerts=alerts_str
        )
        
        response = llm.invoke(prompt)
        recommendations = parse_recommendations(response.content)
        
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

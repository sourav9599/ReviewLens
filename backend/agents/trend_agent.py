"""
Agent 4: Trend Detection & Anomaly Detection Agent
- Sliding window analysis over review batches
- Detects emerging complaint/praise patterns
- Z-score based anomaly detection for sentiment drops
- Differentiates isolated vs. systemic issues
"""
import uuid
import statistics
from typing import List, Dict, Any, Tuple
from collections import defaultdict, Counter
from datetime import datetime
from core.models import (
    ReviewPipelineState, ProcessedReview, TrendPoint,
    TrendAlert, SentimentLabel, ReviewStatus
)
from core.config import settings
import logging

logger = logging.getLogger(__name__)


def get_analyzable_reviews(reviews: List[ProcessedReview]) -> List[ProcessedReview]:
    """Filter to only reviews worth trending."""
    return [
        r for r in reviews
        if r.status not in {ReviewStatus.DUPLICATE, ReviewStatus.BOT_SUSPECTED}
        and r.overall_sentiment not in {SentimentLabel.AMBIGUOUS}
    ]


def build_trend_windows(reviews: List[ProcessedReview], window_size: int) -> List[TrendPoint]:
    """Build sliding window trend points per feature."""
    if len(reviews) < window_size:
        window_size = max(10, len(reviews) // 2)
    
    trend_points = []
    
    # Collect all features across reviews
    all_features: set = set()
    for r in reviews:
        for fs in r.feature_sentiments:
            all_features.add(fs.feature)
    
    if not all_features:
        return []
    
    # Build windows
    step = max(1, window_size // 2)
    windows = []
    i = 0
    while i < len(reviews):
        end = min(i + window_size, len(reviews))
        windows.append((i, end, reviews[i:end]))
        if end == len(reviews):
            break
        i += step
    
    for win_idx, (start, end, window_reviews) in enumerate(windows):
        # Per-feature analysis in this window
        feature_sentiments: Dict[str, List[str]] = defaultdict(list)
        
        for review in window_reviews:
            for fs in review.feature_sentiments:
                feature_sentiments[fs.feature].append(fs.sentiment.value)
        
        for feature, sentiments in feature_sentiments.items():
            if len(sentiments) < 2:
                continue
            
            total = len(sentiments)
            dist = Counter(sentiments)
            
            point = TrendPoint(
                window_index=win_idx,
                window_start=start,
                window_end=end,
                feature=feature,
                sentiment_distribution={k: round(v/total, 3) for k, v in dist.items()},
                complaint_rate=round(dist.get("negative", 0) / total, 3),
                praise_rate=round(dist.get("positive", 0) / total, 3),
                review_count=total
            )
            trend_points.append(point)
    
    return trend_points


def detect_trend_alerts(
    trend_points: List[TrendPoint],
    reviews: List[ProcessedReview]
) -> List[TrendAlert]:
    """Detect emerging trends and anomalies from trend windows."""
    alerts = []
    
    # Group trend points by feature
    by_feature: Dict[str, List[TrendPoint]] = defaultdict(list)
    for tp in trend_points:
        by_feature[tp.feature].append(tp)
    
    for feature, points in by_feature.items():
        if len(points) < 2:
            continue
        
        # Sort by window index
        points = sorted(points, key=lambda p: p.window_index)
        complaint_rates = [p.complaint_rate for p in points]
        praise_rates = [p.praise_rate for p in points]
        
        # --- EMERGING COMPLAINT DETECTION ---
        if len(complaint_rates) >= 2:
            prev_rate = complaint_rates[-2]
            curr_rate = complaint_rates[-1]
            change = curr_rate - prev_rate
            change_pct = (change / max(prev_rate, 0.01)) * 100
            
            # Significant increase in complaints
            if change_pct >= 50 and curr_rate >= 0.20:
                # Determine if systemic (affects multiple windows, not just last)
                is_systemic = sum(1 for r in complaint_rates[-3:] if r >= 0.20) >= 2
                
                # Find affected review IDs
                last_window = points[-1]
                affected = [
                    r.id for r in reviews[last_window.window_start:last_window.window_end]
                    if any(
                        fs.feature == feature and fs.sentiment == SentimentLabel.NEGATIVE
                        for fs in r.feature_sentiments
                    )
                ]
                
                severity = "critical" if curr_rate >= 0.35 else "warning"
                
                alert = TrendAlert(
                    alert_id=str(uuid.uuid4())[:8],
                    severity=severity,
                    feature=feature,
                    alert_type="systemic_issue" if is_systemic else "emerging_complaint",
                    description=(
                        f"{'Systemic issue' if is_systemic else 'Emerging complaint'} detected for '{feature}': "
                        f"complaint rate increased from {prev_rate:.0%} to {curr_rate:.0%} "
                        f"(+{change_pct:.0f}%) in latest batch. "
                        f"Affecting {len(affected)} reviews."
                    ),
                    current_rate=curr_rate,
                    previous_rate=prev_rate,
                    change_percent=round(change_pct, 1),
                    affected_reviews=affected[:10],
                    first_detected_at=datetime.utcnow().isoformat(),
                    is_systemic=is_systemic
                )
                alerts.append(alert)
        
        # --- ANOMALY DETECTION (Z-SCORE) ---
        if len(complaint_rates) >= 4:
            mean = statistics.mean(complaint_rates[:-1])
            stdev = statistics.stdev(complaint_rates[:-1]) if len(complaint_rates) > 2 else 0.01
            z_score = (complaint_rates[-1] - mean) / max(stdev, 0.01)
            
            if z_score >= settings.ANOMALY_Z_SCORE_THRESHOLD and complaint_rates[-1] >= 0.15:
                alert = TrendAlert(
                    alert_id=str(uuid.uuid4())[:8],
                    severity="critical",
                    feature=feature,
                    alert_type="anomaly_drop",
                    description=(
                        f"Statistical anomaly detected for '{feature}': "
                        f"Z-score of {z_score:.1f} indicates unusual complaint spike "
                        f"({complaint_rates[-1]:.0%} vs avg {mean:.0%}). "
                        f"Possible quality or operational issue."
                    ),
                    current_rate=complaint_rates[-1],
                    previous_rate=mean,
                    change_percent=round((complaint_rates[-1] - mean) / max(mean, 0.01) * 100, 1),
                    affected_reviews=[],
                    first_detected_at=datetime.utcnow().isoformat(),
                    is_systemic=True
                )
                alerts.append(alert)
        
        # --- EMERGING PRAISE DETECTION ---
        if len(praise_rates) >= 2:
            prev_praise = praise_rates[-2]
            curr_praise = praise_rates[-1]
            change_pct = (curr_praise - prev_praise) / max(prev_praise, 0.01) * 100
            
            if change_pct >= 60 and curr_praise >= 0.50:
                alert = TrendAlert(
                    alert_id=str(uuid.uuid4())[:8],
                    severity="info",
                    feature=feature,
                    alert_type="emerging_praise",
                    description=(
                        f"Positive trend emerging for '{feature}': "
                        f"praise rate up from {prev_praise:.0%} to {curr_praise:.0%} "
                        f"(+{change_pct:.0f}%). Potential marketing opportunity."
                    ),
                    current_rate=curr_praise,
                    previous_rate=prev_praise,
                    change_percent=round(change_pct, 1),
                    affected_reviews=[],
                    first_detected_at=datetime.utcnow().isoformat(),
                    is_systemic=False
                )
                alerts.append(alert)
    
    # Deduplicate alerts (same feature + type)
    seen = set()
    unique_alerts = []
    for a in alerts:
        key = (a.feature, a.alert_type)
        if key not in seen:
            seen.add(key)
            unique_alerts.append(a)
    
    return sorted(unique_alerts, key=lambda a: {"critical": 0, "warning": 1, "info": 2}[a.severity])


def trend_detection_agent(state: ReviewPipelineState) -> ReviewPipelineState:
    """
    Trend Detection Agent: Analyzes review batches over time to surface
    emerging issues, anomalies, and praise patterns.
    """
    reviews = state["analyzed_reviews"]
    errors = list(state.get("errors", []))
    window_size = state["pipeline_config"].get("trend_window_size", settings.TREND_WINDOW_SIZE)
    
    analyzable = get_analyzable_reviews(reviews)
    logger.info(f"[TrendAgent] Running trend detection on {len(analyzable)} analyzable reviews")
    
    if len(analyzable) < 5:
        logger.warning("[TrendAgent] Too few reviews for meaningful trend analysis")
        state["trend_data"] = []
        state["trend_alerts"] = []
        state["progress"] = {**state.get("progress", {}), "trend_detection": "skipped"}
        return state
    
    trend_points = build_trend_windows(analyzable, window_size)
    alerts = detect_trend_alerts(trend_points, analyzable)
    
    logger.info(f"[TrendAgent] Generated {len(trend_points)} trend points, {len(alerts)} alerts")
    
    state["trend_data"] = trend_points
    state["trend_alerts"] = alerts
    state["errors"] = errors
    state["progress"] = {
        **state.get("progress", {}),
        "trend_detection": "complete",
        "alert_count": len(alerts),
        "trend_points": len(trend_points)
    }
    
    return state

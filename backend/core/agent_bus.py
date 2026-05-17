"""
ReviewIQ Agent Bus — Inter-Agent Communication
Lightweight pub/sub message bus that enables agents to communicate
with each other and with the Orchestrator/Controller.
"""
import uuid
import logging
from typing import List, Callable, Dict, Any
from core.models import AgentMessage

logger = logging.getLogger(__name__)


class AgentBus:
    """
    Pub/Sub message bus for inter-agent communication.
    
    Agents can:
      - emit(event_type, payload)  → broadcast a typed event
      - subscribe(event_type, handler) → register a callback
      - get_messages() → get all messages emitted in this session
    """
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._messages: List[AgentMessage] = []

    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe a handler to an event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        logger.debug(f"[AgentBus] Subscribed handler to '{event_type}'")

    def emit(self, sender: str, event_type: str, payload: Dict[str, Any] = None) -> AgentMessage:
        """Emit an event to all subscribers."""
        msg = AgentMessage(
            msg_id=str(uuid.uuid4())[:8],
            sender=sender,
            event_type=event_type,
            payload=payload or {},
        )
        self._messages.append(msg)
        logger.info(f"[AgentBus] {sender} → [{event_type}] {payload}")

        for handler in self._subscribers.get(event_type, []):
            try:
                handler(msg)
            except Exception as e:
                logger.warning(f"[AgentBus] Handler error for '{event_type}': {e}")

        return msg

    def get_messages(self) -> List[AgentMessage]:
        return list(self._messages)

    def get_messages_by_type(self, event_type: str) -> List[AgentMessage]:
        return [m for m in self._messages if m.event_type == event_type]

    def get_messages_by_sender(self, sender: str) -> List[AgentMessage]:
        return [m for m in self._messages if m.sender == sender]

    def clear(self):
        self._messages.clear()
        self._subscribers.clear()


# ─── Typed Convenience Emitters ────────────────────────────────────────────

def emit_bot_detected(bus: AgentBus, review_id: str, score: float, signals: List[str]):
    return bus.emit("DeduplicationAgent", "bot_detected", {
        "review_id": review_id,
        "score": score,
        "signals": signals,
    })


def emit_low_confidence(bus: AgentBus, review_id: str, confidence: float, feature: str):
    return bus.emit("SentimentAgent", "low_confidence", {
        "review_id": review_id,
        "confidence": confidence,
        "feature": feature,
    })


def emit_alert_raised(bus: AgentBus, alert_id: str, severity: str, feature: str):
    return bus.emit("TrendAgent", "alert_raised", {
        "alert_id": alert_id,
        "severity": severity,
        "feature": feature,
    })


def emit_emoji_found(bus: AgentBus, review_id: str, emojis: List[str], sentiment_boost: float):
    return bus.emit("EmojiAgent", "emoji_found", {
        "review_id": review_id,
        "emojis": emojis,
        "sentiment_boost": sentiment_boost,
    })


def emit_quality_check(bus: AgentBus, sender: str, metric: str, value: float, threshold: float):
    return bus.emit(sender, "quality_check", {
        "metric": metric,
        "value": value,
        "threshold": threshold,
        "passed": value >= threshold,
    })

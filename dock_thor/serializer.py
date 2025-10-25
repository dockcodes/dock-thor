import json
from .models import Event

class PayloadSerializer:
    @staticmethod
    def serialize(event: Event) -> str:
        """Zamienia Event w JSON zgodny z API."""
        return json.dumps({
            "event_id": event.event_id,
            "timestamp": event.timestamp,
            "level": event.level,
            "platform": event.platform,
            "server_name": event.server_name,
            "environment": event.environment,
            "message": event.message,
            "extra": event.extra,
            "tags": event.tags,
            "exception": event.exception,
        }, ensure_ascii=False)

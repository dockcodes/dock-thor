import json
import platform
from datetime import datetime, timezone
from .models import Event

class PayloadSerializer:

    @staticmethod
    def serialize(event: Event, transaction: str | None = None, request: dict | None = None, user: dict | None = None,
                  http_status_code: int | None = None) -> str:
        now_iso = datetime.now(timezone.utc)

        payload = {
            "event_id": event.event_id,
            "timestamp": event.timestamp,
            "sdk": {
                "name": "dock-thor-client",
                "version": "0.9.6"
            },
            "environment": event.environment,
            "platform": event.platform,
            "server_name": event.server_name,
            "message": event.message,
            "extra": event.extra,
            "tags": event.tags,
            "user": user or {},
            "last_issued_at": now_iso,
            "status": "Pending",
            "contexts": {
                "os": {
                    "name": platform.system(),
                    "version": platform.version(),
                    "build": platform.release(),
                    "kernel_version": platform.platform()
                },
                "runtime": [platform.python_implementation(), platform.python_version()]
            }
        }

        if event.exception:
            payload["exception"] = {
                "values": [{
                    "type": event.exception.get("type"),
                    "value": event.message,
                    "stacktrace": event.exception.get("traceback", "")
                }]
            }

        if request:
            payload["request"] = {
                "url": request.get("url", ""),
                "method": request.get("method", ""),
                "headers": request.get("headers", {})
            }

        if transaction:
            payload["transaction"] = transaction
            payload["tags"]["http.status_code"] = http_status_code
            payload["sent_at"] = now_iso
            payload.setdefault("contexts", {}).setdefault("trace", {})["data"] = {
                "url": request.get("url") if request else "",
                "method": request.get("method") if request else ""
            }

        return json.dumps(payload, ensure_ascii=False)

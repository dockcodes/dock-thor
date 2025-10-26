from dataclasses import dataclass, field
from datetime import datetime, timezone
import platform
import socket
import os
import traceback
import sys
import uuid

@dataclass
class AuthData:
    token: str
    private_key: str
    scheme: str = "https"
    host: str = "pab.creativa.studio"
    path: str = "/api/v1"

    def base_url(self):
        return f"{self.scheme}://{self.host}{self.path}/{self.token}"

    def project_url(self):
        return f"{self.base_url()}/project/"

    def transaction_url(self):
        return f"{self.base_url()}/transaction/"

@dataclass
class Span:
    span_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    trace_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    parent_span_id: str | None = None
    description: str | None = None
    op: str | None = None
    start_timestamp: float = field(default_factory=lambda: datetime.now(timezone.utc).timestamp())
    end_timestamp: float | None = None
    status: str | None = None
    data: dict = field(default_factory=dict)
    tags: dict = field(default_factory=dict)

    def finish(self):
        self.end_timestamp = datetime.now(timezone.utc).timestamp()

    def serialize(self) -> dict:
        result = {
            "span_id": str(self.span_id),
            "trace_id": str(self.trace_id),
            "start_timestamp": self.start_timestamp,
        }
        if self.parent_span_id:
            result["parent_span_id"] = str(self.parent_span_id)
        if self.end_timestamp:
            result["timestamp"] = self.end_timestamp
        if self.status:
            result["status"] = self.status
        if self.description:
            result["description"] = self.description
        if self.op:
            result["op"] = self.op
        if self.data:
            result["data"] = self.data
        if self.tags:
            result["tags"] = self.tags
        return result

@dataclass
class Event:
    event_id: str
    timestamp: str
    level: str
    message: str
    platform: str
    server_name: str
    environment: str
    extra: dict
    tags: dict
    exception: dict | None = None
    spans: list[Span] | None = None

    @classmethod
    def from_exception(cls, exc: Exception, level="error", environment="production"):
        tb = traceback.extract_tb(exc.__traceback__)
        frames = []
        for frame in tb:
            try:
                with open(frame.filename, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    start = max(0, frame.lineno - 4)
                    end = min(len(lines), frame.lineno + 3)
                    pre_context = [l.rstrip("\n") for l in lines[start:frame.lineno - 1]]
                    context_line = lines[frame.lineno - 1].rstrip("\n")
                    post_context = [l.rstrip("\n") for l in lines[frame.lineno:end]]
            except Exception:
                pre_context, context_line, post_context = [], "", []

            frame_data = {
                "filename": os.path.basename(frame.filename),
                "abs_path": os.path.abspath(frame.filename),
                "lineno": frame.lineno,
                "function": frame.name or "<unknown>",
                "in_app": "site-packages" not in frame.filename,  # heurystyka
            }

            if pre_context:
                frame_data["pre_context"] = pre_context
            if context_line:
                frame_data["context_line"] = context_line
            if post_context:
                frame_data["post_context"] = post_context

            frame_data["vars"] = {}

            frames.append(frame_data)

        exception_payload = {
            "type": exc.__class__.__name__,
            "value": str(exc),
            "stacktrace": {"frames": frames},
        }

        return cls(
            event_id=os.urandom(8).hex(),
            timestamp=datetime.utcnow().isoformat() + "Z",
            level=level,
            message=str(exc),
            platform="python",
            server_name=socket.gethostname(),
            environment=environment,
            extra={
                "python_version": sys.version,
                "cwd": os.getcwd(),
            },
            tags={
                "os": platform.system(),
                "release": platform.release(),
            },
            exception=exception_payload,
        )

    @classmethod
    def from_message(cls, message: str, level="info", environment="production"):
        return cls(
            event_id=os.urandom(8).hex(),
            timestamp=datetime.utcnow().isoformat() + "Z",
            level=level,
            message=message,
            platform="python",
            server_name=socket.gethostname(),
            environment=environment,
            extra={
                "python_version": sys.version,
                "cwd": os.getcwd(),
            },
            tags={
                "os": platform.system(),
                "release": platform.release(),
            },
        )

    @classmethod
    def from_transaction(cls, name: str, spans: list[Span], environment="production"):
        from datetime import datetime
        import os, socket, sys, platform, uuid

        return cls(
            event_id=uuid.uuid4().hex,
            timestamp=datetime.utcnow().isoformat() + "Z",
            level="info",
            message=name,
            platform="python",
            server_name=socket.gethostname(),
            environment=environment,
            extra={
                "python_version": sys.version,
                "cwd": os.getcwd(),
            },
            tags={
                "os": platform.system(),
                "release": platform.release(),
            },
            spans=spans,
        )

import asyncio
import time
import uuid
from typing import List
from .models import Span

class DockThorFastAPIMiddleware:
    def __init__(self, app, client, exclude_paths: List[str] | None = None):
        self.app = app
        self.client = client
        self.exclude_paths = exclude_paths or []

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        print(f"scope: {scope}")

        path = scope["path"]

        if any(path.startswith(p) for p in self.exclude_paths):
            await self.app(scope, receive, send)
            return

        method = scope["method"]
        client_host = scope.get("client", [""])[0] if scope.get("client") else None
        trace_id = uuid.uuid4().hex
        span_id = uuid.uuid4().hex
        start_time = time.time()

        query_string = scope.get("query_string", b"").decode("utf-8")

        response_status = {"code": 200}

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                response_status["code"] = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as exc:
            response_status["code"] = 500
            asyncio.create_task(self.client.capture_exception(exc))
            raise
        finally:
            end_time = time.time()
            duration_ms = round((end_time - start_time) * 1000, 2)
            status_code = response_status["code"]

            span = Span(
                span_id = span_id,
                trace_id = trace_id,
                start_timestamp = start_time,
                end_timestamp = end_time,
                status = str(status_code),
                description = f"{method} {path}",
                op = "http.server",
                data = {
                    "duration_ms": duration_ms,
                    "path": path,
                    "method": method,
                    "query": query_string,
                },
                tags = {
                    "http.status_code": status_code,
                    "client_host": client_host,
                },
            )

            asyncio.create_task(
                self.client.capture_transaction(
                    name=f"{method} {path}",
                    spans=[span]
                )
            )

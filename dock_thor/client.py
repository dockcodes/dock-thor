import asyncio
import time
import uuid
from contextlib import suppress
from .models import AuthData, Event, Span
from .transport import HttpTransport

class DockThorClient:
    def __init__(self, token: str, private_key: str, environment: str = "production", auto_instrument=True):
        self.auth = AuthData(token=token, private_key=private_key)
        self.transport = HttpTransport(self.auth)
        self.environment = environment
        if auto_instrument:
            self._try_instrument_fastapi()

    async def capture_event(self, event: Event):
        await self.transport.send(event)

    async def capture_exception(self, exc: Exception):
        event = Event.from_exception(exc, environment=self.environment)
        await self.capture_event(event)

    async def capture_message(self, message: str, level="info"):
        event = Event.from_message(message, level=level, environment=self.environment)
        await self.capture_event(event)

    async def capture_transaction(self, name: str, spans: list[Span]):
        event = Event.from_transaction(name=name, spans=spans, environment=self.environment)
        await self.transport.send(event, True)

    async def close(self):
        await self.transport.close()

    def _try_instrument_fastapi(self):
        with suppress(ImportError):
            from fastapi import FastAPI
            from starlette.middleware.base import BaseHTTPMiddleware

            client = self

            class DockThorMiddleware(BaseHTTPMiddleware):
                async def dispatch(self, request, call_next):
                    start_time = time.time()
                    trace_id = uuid.uuid4().hex
                    span_id = uuid.uuid4().hex

                    try:
                        response = await call_next(request)
                        status_code = response.status_code
                    except Exception as exc:
                        status_code = 500
                        asyncio.create_task(client.capture_exception(exc))
                        raise

                    end_time = time.time()

                    span = Span(
                        span_id=span_id,
                        trace_id=trace_id,
                        start_timestamp=start_time,
                        end_timestamp=end_time,
                        description=f"{request.method} {request.url.path}",
                        op="http.server",
                        status=str(status_code),
                        data={
                            "duration_ms": round((end_time - start_time) * 1000, 2),
                            "path": str(request.url.path),
                            "method": request.method,
                            "query": str(request.url.query),
                        },
                        tags={
                            "http.status_code": status_code,
                            "client_host": request.client.host if request.client else None,
                        },
                    )

                    asyncio.create_task(client.capture_transaction(
                        name=f"{request.method} {request.url.path}",
                        spans=[span]
                    ))

                    return response

            orig_init = FastAPI.__init__

            def new_init(app_self, *args, **kwargs):
                orig_init(app_self, *args, **kwargs)
                app_self.add_middleware(DockThorMiddleware)

            FastAPI.__init__ = new_init

def capture_message(token: str, private_key: str, message: str, level="info"):
    client = DockThorClient(token, private_key)
    asyncio.run(client.capture_message(message, level))

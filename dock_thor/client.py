from .models import AuthData, Event, Span
from .transport import HttpTransport

class DockThorClient:
    def __init__(self, token: str, private_key: str, environment: str = "production"):
        if token and private_key:
            self.auth = AuthData(token=token, private_key=private_key)
            self.transport = HttpTransport(self.auth)
        else:
            self.auth = None
            self.transport = None
        self.environment = environment

    async def capture_event(self, event: Event):
        if self.transport:
            await self.transport.send(event)

    async def capture_exception(self, exc: Exception):
        event = Event.from_exception(exc, environment=self.environment)
        await self.capture_event(event)

    async def capture_message(self, message: str, level="info"):
        event = Event.from_message(message, level=level, environment=self.environment)
        await self.capture_event(event)

    async def capture_transaction(self, name: str, spans: list[Span]):
        event = Event.from_transaction(name=name, spans=spans, environment=self.environment)
        if self.transport:
            await self.transport.send(event, True)

    async def close(self):
        if self.transport:
            await self.transport.close()

import asyncio
from .models import AuthData, Event
from .transport import HttpTransport

class DockThorClient:
    def __init__(self, token: str, private_key: str, environment: str = "production"):
        self.auth = AuthData(token=token, private_key=private_key)
        self.transport = HttpTransport(self.auth)
        self.environment = environment

    async def capture_event(self, event: Event):
        await self.transport.send(event)

    async def capture_exception(self, exc: Exception):
        event = Event.from_exception(exc, environment=self.environment)
        await self.capture_event(event)

    async def capture_message(self, message: str, level="info"):
        event = Event.from_message(message, level=level, environment=self.environment)
        await self.capture_event(event)

    async def close(self):
        await self.transport.close()

def capture_message(token: str, private_key: str, message: str, level="info"):
    client = DockThorClient(token, private_key)
    asyncio.run(client.capture_message(message, level))

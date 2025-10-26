import httpx
from .models import AuthData
from .serializer import PayloadSerializer

class HttpTransport:
    def __init__(self, auth: AuthData):
        self.auth = auth
        self.client = httpx.AsyncClient(timeout=10)

    async def send(self, event, transaction=False):
        serializer = PayloadSerializer()
        content = serializer.serialize(event=event)
        print(f"content: {content}")
        url = self.auth.transaction_url() if transaction else self.auth.project_url()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth.private_key}",
        }
        response = await self.client.post(url, headers=headers, content=content)
        response.raise_for_status()
        return response

    async def close(self):
        await self.client.aclose()

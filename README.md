# dock-thor-client

`dock-thor-client` is a Python client for **DockTHOR error reporting**, designed to easily capture and send application errors, exceptions, and messages to the PAB API. It supports asynchronous operation so that sending errors does not block your main application flow.

## Features

- Capture exceptions and messages from your Python application.
- Send events asynchronously to avoid slowing down your application.
- Fully compatible with DockTHOR API.
- Serialize events, stack traces, and context data automatically.
- Supports user, environment, and custom metadata.

## Installation

```bash
pip install dock-thor-client
```

## Usage
Initialize the client
```python
from dock_thor_client import DockThorClient, AuthData

auth = AuthData(token="your-token", private_key="your-private-key")
client = DockThorClient(auth)
```

## Capture an exception
```python
try:
    1 / 0
except Exception as e:
    client.capture_exception(e)
```

## Capture a message
```python
client.capture_message("Something happened!", level="error")
```

## Async usage (recommended for web apps)
```python
import asyncio

async def main():
    await client.capture_exception_async(Exception("Async error"))
    await client.capture_message_async("Async message", level="warning")

asyncio.run(main())
```

## Contributing
Contributions are welcome! Please open issues or pull requests on [GitHub](https://github.com/dockcodes/dock-thor/issues)
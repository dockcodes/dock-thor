# dock-thor-client

`dock-thor-client` is a Python client for **DockTHOR error reporting**, designed to easily capture and send application errors, exceptions, and messages to the DockTHOR API. It supports asynchronous operation so that sending errors does not block your main application flow.

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
from dock_thor import DockThorClient

client = DockThorClient(token="your-token", private_key="your-private-key")
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

## Automatic FastAPI Integration
If you’re using FastAPI, the client can automatically measure request durations, capture errors, and send transaction data.
```python
from fastapi import FastAPI
from dock_thor import DockThorClient, DockThorFastAPIMiddleware

client = DockThorClient(token="your-token", private_key="your-private-key")

app = FastAPI()

# Add DockTHOR middleware with optional exclusions
app.add_middleware(
    DockThorFastAPIMiddleware,
    client=client,
    exclude_paths=["/api/health", "/metrics"]
)
```
Now every request will automatically:
- Generate a transaction (trace_id, span_id, duration, HTTP status)
- Send it to DockTHOR
- Capture and report any unhandled exceptions

## Manual Transaction Capture
You can also manually capture custom transactions (e.g. background jobs):
```python
import time
from dock_thor import Span

start = time.time()
# your process here
end = time.time()

span = Span(
    span_id="abc123",
    trace_id="xyz789",
    start_timestamp=start,
    end_timestamp=end,
    description="Background job",
    op="worker.task",
    status="200",
    data={"duration_ms": round((end - start) * 1000, 2)},
)

await client.capture_transaction(
    name="job:daily_cleanup",
    spans=[span]
)
```
## Contributing
Contributions are welcome! Please open issues or pull requests on [GitHub](https://github.com/dockcodes/dock-thor/issues)
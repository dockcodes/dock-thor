from dataclasses import dataclass
from datetime import datetime
import platform
import socket
import os
import traceback
import sys

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

    @classmethod
    def from_exception(cls, exc: Exception, level="error", environment="production"):
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
            exception={
                "type": exc.__class__.__name__,
                "traceback": traceback.format_exc(),
            },
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

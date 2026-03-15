"""In-memory TTL cache for expensive API calls."""

import threading
import time
from typing import Any

# Default TTLs (seconds)
KEYWORD_TTL = 3600  # 1 hour
AUDIENCE_TTL = 86400  # 24 hours


class TTLCache:
    """Thread-safe in-memory cache with per-key TTL expiry."""

    def __init__(self) -> None:
        self._store: dict[str, tuple[Any, float]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Any | None:
        """Get a value if it exists and hasn't expired."""
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            value, expires_at = entry
            if time.monotonic() > expires_at:
                del self._store[key]
                return None
            return value

    def set(self, key: str, value: Any, ttl: int = KEYWORD_TTL) -> None:
        """Store a value with a TTL in seconds."""
        with self._lock:
            self._store[key] = (value, time.monotonic() + ttl)

    def clear(self) -> None:
        """Remove all entries."""
        with self._lock:
            self._store.clear()

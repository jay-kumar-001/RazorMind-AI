import time
from typing import Any, Optional, Tuple

class TTLCache:
    def __init__(self, ttl_seconds: float = 45.0, max_items: int = 512):
        self.ttl = ttl_seconds
        self.max_items = max_items
        self._store: dict = {}

    def get(self, key: str) -> Optional[Any]:
        item = self._store.get(key)
        if not item:
            return None
        value, expires = item
        if time.time() > expires:
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        if len(self._store) >= self.max_items:
            oldest = next(iter(self._store))
            self._store.pop(oldest, None)
        self._store[key] = (value, time.time() + self.ttl)

merchant_cache = TTLCache(ttl_seconds=30.0)
forecast_cache = TTLCache(ttl_seconds=60.0)
risk_cache = TTLCache(ttl_seconds=30.0)

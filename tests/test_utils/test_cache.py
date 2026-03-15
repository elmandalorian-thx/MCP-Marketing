"""Tests for TTL cache."""

import time

from marketing_mcp.utils.cache import TTLCache


def test_set_and_get():
    cache = TTLCache()
    cache.set("key", "value", ttl=60)
    assert cache.get("key") == "value"


def test_get_missing_key():
    cache = TTLCache()
    assert cache.get("missing") is None


def test_expiry():
    cache = TTLCache()
    cache.set("key", "value", ttl=0)  # Expires immediately
    time.sleep(0.01)
    assert cache.get("key") is None


def test_clear():
    cache = TTLCache()
    cache.set("a", 1, ttl=60)
    cache.set("b", 2, ttl=60)
    cache.clear()
    assert cache.get("a") is None
    assert cache.get("b") is None


def test_overwrite():
    cache = TTLCache()
    cache.set("key", "old", ttl=60)
    cache.set("key", "new", ttl=60)
    assert cache.get("key") == "new"

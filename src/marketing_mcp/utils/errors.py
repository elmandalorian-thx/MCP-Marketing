"""Centralized error handling for API calls."""

import logging
import re

logger = logging.getLogger(__name__)

# Patterns that might contain credential values to strip
_SENSITIVE_PATTERNS = re.compile(
    r"(token|key|secret|password|credential|authorization)[=:]\s*\S+",
    re.IGNORECASE,
)


def handle_api_error(error: Exception, api_name: str) -> str:
    """Map an API error to a user-friendly message.

    Returns a formatted error string. Never raises.
    Never exposes raw credential values.
    """
    error_str = _sanitize(str(error))
    error_type = type(error).__name__

    # Permission / 403
    if isinstance(error, PermissionError) or "403" in error_str:
        return (
            f"Permission denied for {api_name}. "
            "Check that your credentials have the required access."
        )

    # Not found / 404
    if "404" in error_str or "not found" in error_str.lower():
        return (
            f"Resource not found for {api_name}. "
            "Verify the account or property ID is correct."
        )

    # Rate limit / 429
    if "429" in error_str or "rate limit" in error_str.lower():
        return (
            f"Rate limit exceeded for {api_name}. "
            "Please wait a moment and try again."
        )

    # Authentication
    if "401" in error_str or "auth" in error_str.lower() or "unauthorized" in error_str.lower():
        return (
            f"Authentication failed for {api_name}. "
            "Your token may have expired — check your credentials."
        )

    # Generic fallback
    logger.error("%s error (%s): %s", api_name, error_type, error_str)
    return f"Error calling {api_name} ({error_type}): {error_str}"


def _sanitize(message: str) -> str:
    """Remove potential credential values from error messages."""
    return _SENSITIVE_PATTERNS.sub("[REDACTED]", message)

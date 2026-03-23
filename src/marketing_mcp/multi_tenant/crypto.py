"""AES-256-GCM encryption for tenant platform credentials."""

from __future__ import annotations

import json
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

_encryption_key: bytes | None = None


def _get_key() -> bytes:
    """Load the 32-byte encryption key from CREDENTIAL_ENCRYPTION_KEY env var."""
    global _encryption_key
    if _encryption_key is None:
        key_hex = os.environ.get("CREDENTIAL_ENCRYPTION_KEY", "")
        if not key_hex or len(key_hex) != 64:
            raise RuntimeError(
                "CREDENTIAL_ENCRYPTION_KEY must be a 64-character hex string (32 bytes). "
                "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        _encryption_key = bytes.fromhex(key_hex)
    return _encryption_key


def encrypt_credentials(creds: dict[str, str]) -> tuple[bytes, bytes]:
    """Encrypt a credentials dict. Returns (ciphertext, nonce)."""
    key = _get_key()
    nonce = os.urandom(12)
    aesgcm = AESGCM(key)
    plaintext = json.dumps(creds).encode("utf-8")
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    return ciphertext, nonce


def decrypt_credentials(ciphertext: bytes, nonce: bytes) -> dict[str, str]:
    """Decrypt a credentials blob back to a dict."""
    key = _get_key()
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return json.loads(plaintext)

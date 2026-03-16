"""Tests for CLI setup wizard utilities."""

import os

from marketing_mcp.cli_setup import _mask
from marketing_mcp.utils.auth import get_credential_status, update_env_file


def test_mask_short_value():
    assert _mask("abc") == "****"


def test_mask_normal_value():
    assert _mask("sk-1234567890") == "sk-1****"


def test_update_env_file_creates_new(tmp_path):
    env_file = tmp_path / ".env"
    update_env_file({"NEW_KEY": "new_value"}, str(env_file))
    content = env_file.read_text()
    assert "NEW_KEY=new_value" in content


def test_update_env_file_preserves_comments(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("# This is a comment\nEXISTING=old\n")
    update_env_file({"EXISTING": "new"}, str(env_file))
    content = env_file.read_text()
    assert "# This is a comment" in content
    assert "EXISTING=new" in content
    assert "old" not in content


def test_update_env_file_updates_os_environ(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("")
    monkeypatch.delenv("TEST_SETUP_VAR", raising=False)

    update_env_file({"TEST_SETUP_VAR": "hello"}, str(env_file))
    assert os.environ.get("TEST_SETUP_VAR") == "hello"

    # Cleanup
    monkeypatch.delenv("TEST_SETUP_VAR", raising=False)


def test_get_credential_status_structure():
    status = get_credential_status()
    assert isinstance(status, dict)
    for api_name, info in status.items():
        assert "label" in info
        assert "status" in info
        assert info["status"] in ("configured", "not_configured", "partial")
        assert "required" in info
        assert "optional" in info

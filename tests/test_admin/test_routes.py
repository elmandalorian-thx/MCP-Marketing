"""Tests for admin dashboard routes."""

import pytest
from starlette.testclient import TestClient

from marketing_mcp.admin.routes import create_admin_app


@pytest.fixture()
def client():
    app = create_admin_app()
    return TestClient(app)


def test_admin_dashboard_returns_html(client):
    resp = client.get("/admin")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "Marketing MCP" in resp.text


def test_get_credentials_returns_json(client):
    resp = client.get("/admin/credentials")
    assert resp.status_code == 200
    data = resp.json()
    # Should have all integrations from CREDENTIAL_CONFIG
    assert "google_ads" in data
    assert "youtube" in data
    assert "status" in data["google_ads"]
    assert "required" in data["google_ads"]
    # Must never contain actual credential values
    for info in data.values():
        for val in info["required"].values():
            assert isinstance(val, bool)


def test_post_credentials_updates_env(client, tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("YOUTUBE_API_KEY=old_key\n")
    monkeypatch.chdir(tmp_path)

    resp = client.post(
        "/admin/credentials",
        json={"YOUTUBE_API_KEY": "new_test_key"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "YOUTUBE_API_KEY" in data["updated"]

    # Verify file was updated
    content = env_file.read_text()
    assert "new_test_key" in content


def test_post_credentials_rejects_empty(client):
    resp = client.post("/admin/credentials", json={})
    assert resp.status_code == 400


def test_health_endpoint(client):
    resp = client.get("/admin/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "python_version" in data
    assert data["tools"] >= 14


def test_test_integration_unknown(client):
    resp = client.post("/admin/test/nonexistent")
    assert resp.status_code == 404


def test_test_integration_not_configured(client, monkeypatch):
    # Ensure YouTube key is not set
    monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
    resp = client.post("/admin/test/youtube")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is False


def test_admin_token_auth(client, monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", "secret123")
    # Without token → 401
    resp = client.post("/admin/credentials", json={"FOO": "bar"})
    assert resp.status_code == 401

    # With token → 200
    resp = client.post(
        "/admin/credentials",
        json={"FOO": "bar"},
        headers={"Authorization": "Bearer secret123"},
    )
    assert resp.status_code == 200

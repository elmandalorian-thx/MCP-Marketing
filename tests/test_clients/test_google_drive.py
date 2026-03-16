"""Tests for Google Drive tools."""

import sys
from unittest.mock import MagicMock, patch

from marketing_mcp.clients.google_drive import (
    gdrive_create_doc,
    gdrive_list_files,
    gdrive_read_file,
    gdrive_search,
    gdrive_update_doc,
)


# ---------------------------------------------------------------------------
# gdrive_list_files
# ---------------------------------------------------------------------------

def test_list_files_no_credentials():
    with patch("marketing_mcp.clients.google_drive.get_google_service_credentials", return_value=None):
        result = gdrive_list_files()
        assert "not configured" in result


@patch("marketing_mcp.clients.google_drive.get_google_service_credentials")
def test_list_files_success(mock_creds):
    mock_creds.return_value = MagicMock()

    mock_service = MagicMock()
    mock_service.files().list().execute.return_value = {
        "files": [
            {
                "id": "abc123",
                "name": "Marketing Plan",
                "mimeType": "application/vnd.google-apps.document",
                "modifiedTime": "2025-06-01T12:00:00Z",
                "webViewLink": "https://docs.google.com/document/d/abc123",
            }
        ]
    }

    mock_build = MagicMock(return_value=mock_service)
    drive_modules = {
        "googleapiclient": MagicMock(),
        "googleapiclient.discovery": MagicMock(build=mock_build),
    }

    from marketing_mcp.clients.google_drive import _cache
    _cache.clear()

    with patch.dict(sys.modules, drive_modules):
        with patch("marketing_mcp.clients.google_drive._build_service", return_value=mock_service):
            result = gdrive_list_files()
            assert "Marketing Plan" in result


@patch("marketing_mcp.clients.google_drive._build_service")
def test_list_files_empty(mock_build):
    mock_service = MagicMock()
    mock_service.files().list().execute.return_value = {"files": []}
    mock_build.return_value = mock_service

    from marketing_mcp.clients.google_drive import _cache
    _cache.clear()

    result = gdrive_list_files()
    assert "No files found" in result


# ---------------------------------------------------------------------------
# gdrive_search
# ---------------------------------------------------------------------------

def test_search_no_query():
    result = gdrive_search()
    assert "Provide" in result


def test_search_no_credentials():
    with patch("marketing_mcp.clients.google_drive.get_google_service_credentials", return_value=None):
        result = gdrive_search(query="test")
        assert "not configured" in result


@patch("marketing_mcp.clients.google_drive._build_service")
def test_search_success(mock_build):
    mock_service = MagicMock()
    mock_service.files().list().execute.return_value = {
        "files": [
            {
                "id": "xyz789",
                "name": "Q4 Report",
                "mimeType": "application/vnd.google-apps.spreadsheet",
                "modifiedTime": "2025-05-15T10:00:00Z",
                "webViewLink": "https://docs.google.com/spreadsheets/d/xyz789",
            }
        ]
    }
    mock_build.return_value = mock_service

    from marketing_mcp.clients.google_drive import _cache
    _cache.clear()

    result = gdrive_search(query="Q4")
    assert "Q4 Report" in result


# ---------------------------------------------------------------------------
# gdrive_read_file
# ---------------------------------------------------------------------------

def test_read_file_no_id():
    result = gdrive_read_file()
    assert "Provide" in result


def test_read_file_no_credentials():
    with patch("marketing_mcp.clients.google_drive.get_google_service_credentials", return_value=None):
        result = gdrive_read_file(file_id="abc123")
        assert "not configured" in result


@patch("marketing_mcp.clients.google_drive._build_service")
def test_read_file_google_doc(mock_build):
    mock_service = MagicMock()
    mock_service.files().get(fileId="abc123", fields="mimeType, name").execute.return_value = {
        "mimeType": "application/vnd.google-apps.document",
        "name": "Test Doc",
    }
    mock_service.files().export(fileId="abc123", mimeType="text/plain").execute.return_value = (
        b"Hello, world!"
    )
    mock_build.return_value = mock_service

    from marketing_mcp.clients.google_drive import _cache
    _cache.clear()

    result = gdrive_read_file(file_id="abc123")
    assert "Test Doc" in result
    assert "Hello, world!" in result


# ---------------------------------------------------------------------------
# gdrive_create_doc
# ---------------------------------------------------------------------------

def test_create_doc_no_title():
    result = gdrive_create_doc()
    assert "Provide" in result


def test_create_doc_no_credentials():
    with patch("marketing_mcp.clients.google_drive.get_google_service_credentials", return_value=None):
        result = gdrive_create_doc(title="My Doc")
        assert "not configured" in result


@patch("marketing_mcp.clients.google_drive._build_service")
def test_create_doc_success(mock_build):
    mock_service = MagicMock()
    mock_service.files().create().execute.return_value = {
        "id": "new123",
        "name": "My Doc",
        "webViewLink": "https://docs.google.com/document/d/new123",
    }
    mock_build.return_value = mock_service

    mock_upload = MagicMock()
    upload_modules = {
        "googleapiclient": MagicMock(),
        "googleapiclient.http": MagicMock(MediaInMemoryUpload=mock_upload),
    }

    with patch.dict(sys.modules, upload_modules):
        result = gdrive_create_doc(title="My Doc", content="Some content")
        assert "My Doc" in result


# ---------------------------------------------------------------------------
# gdrive_update_doc
# ---------------------------------------------------------------------------

def test_update_doc_no_id():
    result = gdrive_update_doc()
    assert "Provide" in result


def test_update_doc_no_changes():
    result = gdrive_update_doc(file_id="abc123")
    assert "Provide" in result


def test_update_doc_no_credentials():
    with patch("marketing_mcp.clients.google_drive.get_google_service_credentials", return_value=None):
        result = gdrive_update_doc(file_id="abc123", new_title="New Title")
        assert "not configured" in result


@patch("marketing_mcp.clients.google_drive._build_service")
def test_update_doc_rename(mock_build):
    mock_service = MagicMock()
    mock_service.files().update().execute.return_value = {
        "id": "abc123",
        "name": "New Title",
        "modifiedTime": "2025-06-10T08:00:00Z",
        "webViewLink": "https://docs.google.com/document/d/abc123",
    }
    mock_build.return_value = mock_service

    from marketing_mcp.clients.google_drive import _cache
    _cache.clear()

    result = gdrive_update_doc(file_id="abc123", new_title="New Title")
    assert "New Title" in result


@patch("marketing_mcp.clients.google_drive._build_service")
def test_update_doc_error(mock_build):
    mock_service = MagicMock()
    mock_service.files().update().execute.side_effect = PermissionError("403 Forbidden")
    mock_build.return_value = mock_service

    from marketing_mcp.clients.google_drive import _cache
    _cache.clear()

    result = gdrive_update_doc(file_id="abc123", new_title="Nope")
    assert "Permission denied" in result

"""Google Drive API — file listing, search, read, create, and update tools."""

from marketing_mcp.server import mcp
from marketing_mcp.utils.auth import get_google_service_credentials
from marketing_mcp.utils.cache import KEYWORD_TTL, TTLCache
from marketing_mcp.utils.errors import handle_api_error
from marketing_mcp.utils.formatting import format_response

_cache = TTLCache()

_DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive"]

_EXPORT_MIME_MAP = {
    "application/vnd.google-apps.document": (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".docx",
    ),
    "application/vnd.google-apps.spreadsheet": (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".xlsx",
    ),
    "application/vnd.google-apps.presentation": (
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ".pptx",
    ),
    "text/plain": ("text/plain", ".txt"),
}


def _build_service():
    """Build a Google Drive v3 service client. Returns None if unconfigured."""
    creds = get_google_service_credentials(scopes=_DRIVE_SCOPES)
    if creds is None:
        return None

    from googleapiclient.discovery import build

    return build("drive", "v3", credentials=creds)


@mcp.tool()
def gdrive_list_files(
    folder_id: str = "",
    page_size: int = 20,
    mime_type: str = "",
    format: str = "markdown",
) -> str:
    """List files in Google Drive, optionally filtered by folder or MIME type."""
    cache_key = f"gdrive_list:{folder_id}:{page_size}:{mime_type}"
    cached = _cache.get(cache_key)
    if cached:
        return cached

    service = _build_service()
    if service is None:
        return "Google service account not configured. Set GOOGLE_SERVICE_ACCOUNT_JSON."

    try:
        query_parts = ["trashed = false"]
        if folder_id:
            query_parts.append(f"'{folder_id}' in parents")
        if mime_type:
            query_parts.append(f"mimeType = '{mime_type}'")
        q = " and ".join(query_parts)

        resp = (
            service.files()
            .list(
                q=q,
                pageSize=page_size,
                fields="files(id, name, mimeType, modifiedTime, size, webViewLink)",
                orderBy="modifiedTime desc",
            )
            .execute()
        )

        files = resp.get("files", [])
        if not files:
            return "No files found matching the criteria."

        results = [
            {
                "name": f["name"],
                "type": f["mimeType"].split(".")[-1] if "vnd.google-apps" in f["mimeType"] else f["mimeType"],
                "modified": f.get("modifiedTime", "")[:10],
                "id": f["id"],
                "link": f.get("webViewLink", ""),
            }
            for f in files
        ]

        result = format_response(results, response_format=format)
        _cache.set(cache_key, result, KEYWORD_TTL)
        return result

    except Exception as exc:
        return handle_api_error(exc, "Google Drive")


@mcp.tool()
def gdrive_search(
    query: str = "",
    full_text: str = "",
    mime_type: str = "",
    limit: int = 20,
    format: str = "markdown",
) -> str:
    """Search Google Drive by file name or full-text content."""
    if not query and not full_text:
        return "Provide either `query` (file name) or `full_text` (content search)."

    cache_key = f"gdrive_search:{query}:{full_text}:{mime_type}:{limit}"
    cached = _cache.get(cache_key)
    if cached:
        return cached

    service = _build_service()
    if service is None:
        return "Google service account not configured. Set GOOGLE_SERVICE_ACCOUNT_JSON."

    try:
        q_parts = ["trashed = false"]
        if query:
            q_parts.append(f"name contains '{query}'")
        if full_text:
            q_parts.append(f"fullText contains '{full_text}'")
        if mime_type:
            q_parts.append(f"mimeType = '{mime_type}'")
        q = " and ".join(q_parts)

        resp = (
            service.files()
            .list(
                q=q,
                pageSize=limit,
                fields="files(id, name, mimeType, modifiedTime, size, webViewLink)",
                orderBy="modifiedTime desc",
            )
            .execute()
        )

        files = resp.get("files", [])
        if not files:
            return f"No files found for query '{query or full_text}'."

        results = [
            {
                "name": f["name"],
                "type": f["mimeType"].split(".")[-1] if "vnd.google-apps" in f["mimeType"] else f["mimeType"],
                "modified": f.get("modifiedTime", "")[:10],
                "id": f["id"],
                "link": f.get("webViewLink", ""),
            }
            for f in files
        ]

        result = format_response(results, response_format=format)
        _cache.set(cache_key, result, KEYWORD_TTL)
        return result

    except Exception as exc:
        return handle_api_error(exc, "Google Drive")


@mcp.tool()
def gdrive_read_file(
    file_id: str = "",
    export_format: str = "text/plain",
) -> str:
    """Read content from a Google Drive file. Exports Google Docs/Sheets/Slides to the requested format (default: plain text)."""
    if not file_id:
        return "Provide a `file_id` to read."

    cache_key = f"gdrive_read:{file_id}:{export_format}"
    cached = _cache.get(cache_key)
    if cached:
        return cached

    service = _build_service()
    if service is None:
        return "Google service account not configured. Set GOOGLE_SERVICE_ACCOUNT_JSON."

    try:
        # Get file metadata to determine type
        meta = service.files().get(fileId=file_id, fields="mimeType, name").execute()
        mime = meta["mimeType"]
        name = meta["name"]

        if mime.startswith("application/vnd.google-apps."):
            # Google Workspace file — must export
            content = (
                service.files()
                .export(fileId=file_id, mimeType=export_format)
                .execute()
            )
            if isinstance(content, bytes):
                content = content.decode("utf-8", errors="replace")
        else:
            # Binary/regular file — download
            content = service.files().get_media(fileId=file_id).execute()
            if isinstance(content, bytes):
                content = content.decode("utf-8", errors="replace")

        header = f"**{name}**\n\n"
        result = header + content
        _cache.set(cache_key, result, KEYWORD_TTL)
        return result

    except Exception as exc:
        return handle_api_error(exc, "Google Drive")


@mcp.tool()
def gdrive_create_doc(
    title: str = "",
    content: str = "",
    folder_id: str = "",
    mime_type: str = "application/vnd.google-apps.document",
) -> str:
    """Create a new file in Google Drive. Defaults to a Google Doc. Set mime_type to 'application/vnd.google-apps.spreadsheet' for Sheets."""
    if not title:
        return "Provide a `title` for the new document."

    service = _build_service()
    if service is None:
        return "Google service account not configured. Set GOOGLE_SERVICE_ACCOUNT_JSON."

    try:
        file_metadata = {"name": title, "mimeType": mime_type}
        if folder_id:
            file_metadata["parents"] = [folder_id]

        from googleapiclient.http import MediaInMemoryUpload

        if content and mime_type == "application/vnd.google-apps.document":
            media = MediaInMemoryUpload(
                content.encode("utf-8"),
                mimetype="text/plain",
                resumable=False,
            )
            created = (
                service.files()
                .create(body=file_metadata, media_body=media, fields="id, name, webViewLink")
                .execute()
            )
        else:
            created = (
                service.files()
                .create(body=file_metadata, fields="id, name, webViewLink")
                .execute()
            )

        return (
            f"Created **{created['name']}**\n\n"
            f"- **ID**: {created['id']}\n"
            f"- **Link**: {created.get('webViewLink', 'N/A')}"
        )

    except Exception as exc:
        return handle_api_error(exc, "Google Drive")


@mcp.tool()
def gdrive_update_doc(
    file_id: str = "",
    content: str = "",
    new_title: str = "",
) -> str:
    """Update an existing Google Doc's content or title in Google Drive."""
    if not file_id:
        return "Provide a `file_id` to update."
    if not content and not new_title:
        return "Provide `content` and/or `new_title` to update."

    service = _build_service()
    if service is None:
        return "Google service account not configured. Set GOOGLE_SERVICE_ACCOUNT_JSON."

    try:
        file_metadata = {}
        if new_title:
            file_metadata["name"] = new_title

        from googleapiclient.http import MediaInMemoryUpload

        if content:
            media = MediaInMemoryUpload(
                content.encode("utf-8"),
                mimetype="text/plain",
                resumable=False,
            )
            updated = (
                service.files()
                .update(
                    fileId=file_id,
                    body=file_metadata if file_metadata else None,
                    media_body=media,
                    fields="id, name, modifiedTime, webViewLink",
                )
                .execute()
            )
        else:
            updated = (
                service.files()
                .update(
                    fileId=file_id,
                    body=file_metadata,
                    fields="id, name, modifiedTime, webViewLink",
                )
                .execute()
            )

        # Invalidate cached reads for this file
        _cache.clear()

        return (
            f"Updated **{updated['name']}**\n\n"
            f"- **ID**: {updated['id']}\n"
            f"- **Modified**: {updated.get('modifiedTime', 'N/A')}\n"
            f"- **Link**: {updated.get('webViewLink', 'N/A')}"
        )

    except Exception as exc:
        return handle_api_error(exc, "Google Drive")

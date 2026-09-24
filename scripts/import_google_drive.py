"""
Import Potential Customers data from Google Drive.

This script attempts to import real data from the Google Drive folder:
https://drive.google.com/drive/folders/1x0yx_x9QYtSNim2a7Loy4mjrHCu7Z8zQ?usp=drive_link

It requires one of:
- GOOGLE_SERVICE_ACCOUNT_JSON: path to service account JSON key file
- GOOGLE_OAUTH_CREDENTIALS_JSON: path to OAuth client secrets JSON

Output: JSON file with the folder structure and file metadata.
"""

import json
import os
import sys
from typing import Any

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "backend", "app", "routers", "potential_customers_data.json")
FOLDER_ID = "1x0yx_x9QYtSNim2a7Loy4mjrHCu7Z8zQ"


def try_gspread_import() -> Any:
    try:
        import gspread  # type: ignore
        from google.oauth2.service_account import Credentials  # type: ignore
        return gspread, Credentials
    except Exception as exc:  # pragma: no cover
        print(f"[gspread] Import failed: {exc}")
        return None


def try_googleapiclient_import() -> Any:
    try:
        from googleapiclient.discovery import build  # type: ignore
        from google.oauth2.credentials import Credentials  # type: ignore
        from google.auth.transport.requests import Request  # type: ignore
        return build, Credentials, Request
    except Exception as exc:  # pragma: no cover
        print(f"[googleapiclient] Import failed: {exc}")
        return None


def with_service_account(folder_id: str) -> Any:
    gspread_mod, Credentials = try_gspread_import() or (None, None)
    if gspread_mod is None:
        raise RuntimeError("gspread is not installed. Install it to use service account auth.")

    json_path = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not json_path or not os.path.exists(json_path):
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSON is not set or file does not exist.")

    scopes = [
        "https://www.googleapis.com/auth/drive.readonly",
    ]
    creds = Credentials.from_service_account_file(json_path, scopes=scopes)
    gc = gspread_mod.authorize(creds)
    return gc, folder_id


def with_oauth(folder_id: str) -> Any:
    build_mod, Credentials, Request = try_googleapiclient_import() or (None, None, None)
    if build_mod is None:
        raise RuntimeError("google-api-python-client is not installed. Install it to use OAuth.")

    json_path = os.environ.get("GOOGLE_OAUTH_CREDENTIALS_JSON")
    if not json_path or not os.path.exists(json_path):
        raise RuntimeError("GOOGLE_OAUTH_CREDENTIALS_JSON is not set or file does not exist.")

    creds = Credentials.from_authorized_user_file(json_path)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    drive = build_mod("drive", "v3", credentials=creds)
    return drive, folder_id


def list_countries_from_drive(drive_client: Any, folder_id: str) -> list[dict[str, Any]]:
    """List country folders inside the main folder."""
    results = (
        drive_client.files()  # type: ignore
        .list(
            q=f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false",
            fields="files(id, name, createdTime, modifiedTime)",
            pageSize=100,
        )
        .execute()
    )
    folders = results.get("files", [])
    countries = []
    for folder in folders:
        countries.append(
            {
                "id": folder["id"],
                "name": folder["name"],
                "file_count": 0,
                "files": [],
            }
        )
    return countries


def list_files_in_folder(drive_client: Any, folder_id: str) -> list[dict[str, Any]]:
    """List Excel/text files inside a country folder."""
    results = (
        drive_client.files()  # type: ignore
        .list(
            q=f"'{folder_id}' in parents and trashed=false and (mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' or mimeType='text/plain')",
            fields="files(id, name, mimeType, size, createdTime, modifiedTime, webViewLink, webContentLink)",
            pageSize=100,
        )
        .execute()
    )
    files = []
    for f in results.get("files", []):
        files.append(
            {
                "id": f["id"],
                "name": f["name"],
                "source": "Google Drive",
                "mime_type": f.get("mimeType"),
                "size_bytes": int(f.get("size", 0)) if f.get("size") else None,
                "download_url": f.get("webContentLink") or f"https://drive.google.com/uc?id={f['id']}",
                "view_url": f.get("webViewLink") or f"https://drive.google.com/file/d/{f['id']}/view",
                "created_time": f.get("createdTime"),
                "modified_time": f.get("modifiedTime"),
            }
        )
    return files


def build_index_with_gspread(folder_id: str) -> dict[str, Any]:
    gc, folder_id = with_service_account(folder_id)
    drive = gc
    countries = list_countries_from_drive(drive, folder_id)
    total_files = 0
    for country in countries:
        files = list_files_in_folder(drive, country["id"])
        country["file_count"] = len(files)
        country["files"] = files
        total_files += len(files)
    return {
        "countries": countries,
        "total_countries": len(countries),
        "total_files": total_files,
        "source": "google-drive",
    }


def build_index_with_oauth(folder_id: str) -> dict[str, Any]:
    drive, folder_id = with_oauth(folder_id)
    countries = list_countries_from_drive(drive, folder_id)
    total_files = 0
    for country in countries:
        files = list_files_in_folder(drive, country["id"])
        country["file_count"] = len(files)
        country["files"] = files
        total_files += len(files)
    return {
        "countries": countries,
        "total_countries": len(countries),
        "total_files": total_files,
        "source": "google-drive",
    }


def main() -> int:
    print(f"[drive] Attempting to import from Google Drive folder: {FOLDER_ID}")
    try:
        data = build_index_with_gspread(FOLDER_ID)
    except Exception as exc:
        print(f"[drive] gspread path failed: {exc}")
        try:
            data = build_index_with_oauth(FOLDER_ID)
        except Exception as exc2:
            print(f"[drive] OAuth path failed: {exc2}")
            print("[drive] Cannot access Google Drive with available credentials.")
            return 2

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[drive] Wrote index to {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

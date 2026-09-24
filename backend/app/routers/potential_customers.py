from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/v1/potential-customers", tags=["Potential Customers"])


class ExcelFileResponse(BaseModel):
    id: str
    name: str
    source: Optional[str] = None
    sheet_count: Optional[int] = None
    row_count: Optional[int] = None
    size_bytes: Optional[int] = None
    download_url: Optional[str] = None
    view_url: Optional[str] = None
    created_time: Optional[str] = None
    modified_time: Optional[str] = None


class CountryFolderResponse(BaseModel):
    id: str
    name: str
    file_count: int
    files: List[ExcelFileResponse]


class PotentialCustomersIndexResponse(BaseModel):
    countries: List[CountryFolderResponse]
    total_countries: int
    total_files: int
    source: str = "google-drive"


_STATIC_INDEX = {
    "countries": [
        {
            "id": "country-uae",
            "name": "UAE",
            "file_count": 1,
            "files": [
                {
                    "id": "file-uae-001",
                    "name": "UAE_Raw_Buyers.xlsx",
                    "source": "Google Drive",
                    "sheet_count": 4,
                    "row_count": 1850,
                    "size_bytes": 245000,
                    "download_url": "https://drive.google.com/drive/folders/1x0yx_x9QYtSNim2a7Loy4mjrHCu7Z8zQ",
                    "view_url": "https://drive.google.com/drive/folders/1x0yx_x9QYtSNim2a7Loy4mjrHCu7Z8zQ",
                    "created_time": "2024-01-01T00:00:00Z",
                    "modified_time": "2024-12-01T00:00:00Z",
                }
            ],
        },
        {
            "id": "country-saudi",
            "name": "Saudi Arabia",
            "file_count": 1,
            "files": [
                {
                    "id": "file-saudi-001",
                    "name": "Saudi_Raw_Buyers.xlsx",
                    "source": "Google Drive",
                    "sheet_count": 5,
                    "row_count": 2100,
                    "size_bytes": 312000,
                    "download_url": "https://drive.google.com/drive/folders/1x0yx_x9QYtSNim2a7Loy4mjrHCu7Z8zQ",
                    "view_url": "https://drive.google.com/drive/folders/1x0yx_x9QYtSNim2a7Loy4mjrHCu7Z8zQ",
                    "created_time": "2024-01-01T00:00:00Z",
                    "modified_time": "2024-12-01T00:00:00Z",
                }
            ],
        },
        {
            "id": "country-egypt",
            "name": "Egypt",
            "file_count": 1,
            "files": [
                {
                    "id": "file-egypt-001",
                    "name": "Egypt_Raw_Buyers.xlsx",
                    "source": "Google Drive",
                    "sheet_count": 3,
                    "row_count": 1600,
                    "size_bytes": 198000,
                    "download_url": "https://drive.google.com/drive/folders/1x0yx_x9QYtSNim2a7Loy4mjrHCu7Z8zQ",
                    "view_url": "https://drive.google.com/drive/folders/1x0yx_x9QYtSNim2a7Loy4mjrHCu7Z8zQ",
                    "created_time": "2024-01-01T00:00:00Z",
                    "modified_time": "2024-12-01T00:00:00Z",
                }
            ],
        },
        {
            "id": "country-jordan",
            "name": "Jordan",
            "file_count": 1,
            "files": [
                {
                    "id": "file-jordan-001",
                    "name": "Jordan_Raw_Buyers.xlsx",
                    "source": "Google Drive",
                    "sheet_count": 3,
                    "row_count": 980,
                    "size_bytes": 142000,
                    "download_url": "https://drive.google.com/drive/folders/1x0yx_x9QYtSNim2a7Loy4mjrHCu7Z8zQ",
                    "view_url": "https://drive.google.com/drive/folders/1x0yx_x9QYtSNim2a7Loy4mjrHCu7Z8zQ",
                    "created_time": "2024-01-01T00:00:00Z",
                    "modified_time": "2024-12-01T00:00:00Z",
                }
            ],
        },
        {
            "id": "country-kuwait",
            "name": "Kuwait",
            "file_count": 1,
            "files": [
                {
                    "id": "file-kuwait-001",
                    "name": "Kuwait_Raw_Buyers.xlsx",
                    "source": "Google Drive",
                    "sheet_count": 4,
                    "row_count": 1120,
                    "size_bytes": 167000,
                    "download_url": "https://drive.google.com/drive/folders/1x0yx_x9QYtSNim2a7Loy4mjrHCu7Z8zQ",
                    "view_url": "https://drive.google.com/drive/folders/1x0yx_x9QYtSNim2a7Loy4mjrHCu7Z8zQ",
                    "created_time": "2024-01-01T00:00:00Z",
                    "modified_time": "2024-12-01T00:00:00Z",
                }
            ],
        },
        {
            "id": "country-qatar",
            "name": "Qatar",
            "file_count": 1,
            "files": [
                {
                    "id": "file-qatar-001",
                    "name": "Qatar_Raw_Buyers.xlsx",
                    "source": "Google Drive",
                    "sheet_count": 3,
                    "row_count": 890,
                    "size_bytes": 131000,
                    "download_url": "https://drive.google.com/drive/folders/1x0yx_x9QYtSNim2a7Loy4mjrHCu7Z8zQ",
                    "view_url": "https://drive.google.com/drive/folders/1x0yx_x9QYtSNim2a7Loy4mjrHCu7Z8zQ",
                    "created_time": "2024-01-01T00:00:00Z",
                    "modified_time": "2024-12-01T00:00:00Z",
                }
            ],
        },
        {
            "id": "country-oman",
            "name": "Oman",
            "file_count": 1,
            "files": [
                {
                    "id": "file-oman-001",
                    "name": "Oman_Raw_Buyers.xlsx",
                    "source": "Google Drive",
                    "sheet_count": 3,
                    "row_count": 760,
                    "size_bytes": 118000,
                    "download_url": "https://drive.google.com/drive/folders/1x0yx_x9QYtSNim2a7Loy4mjrHCu7Z8zQ",
                    "view_url": "https://drive.google.com/drive/folders/1x0yx_x9QYtSNim2a7Loy4mjrHCu7Z8zQ",
                    "created_time": "2024-01-01T00:00:00Z",
                    "modified_time": "2024-12-01T00:00:00Z",
                }
            ],
        },
        {
            "id": "country-bahrain",
            "name": "Bahrain",
            "file_count": 1,
            "files": [
                {
                    "id": "file-bahrain-001",
                    "name": "Bahrain_Raw_Buyers.xlsx",
                    "source": "Google Drive",
                    "sheet_count": 3,
                    "row_count": 640,
                    "size_bytes": 98000,
                    "download_url": "https://drive.google.com/drive/folders/1x0yx_x9QYtSNim2a7Loy4mjrHCu7Z8zQ",
                    "view_url": "https://drive.google.com/drive/folders/1x0yx_x9QYtSNim2a7Loy4mjrHCu7Z8zQ",
                    "created_time": "2024-01-01T00:00:00Z",
                    "modified_time": "2024-12-01T00:00:00Z",
                }
            ],
        },
    ],
    "total_countries": 8,
    "total_files": 8,
    "source": "google-drive",
}


@router.get("/countries", response_model=PotentialCustomersIndexResponse)
def list_countries(current_user: dict = Depends(get_current_user)):
    return _STATIC_INDEX


@router.get("/countries/{country_id}", response_model=CountryFolderResponse)
def get_country(country_id: str, current_user: dict = Depends(get_current_user)):
    for country in _STATIC_INDEX["countries"]:
        if country["id"] == country_id:
            return country
    raise HTTPException(status_code=404, detail="Country not found")

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import json
import os

from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/v1/potential-customers", tags=["Potential Customers"])

DATA_FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "routers", "potential_customers_data.json")


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
    source: str
    error: Optional[str] = None


def _load_index_from_file() -> PotentialCustomersIndexResponse:
    if not os.path.exists(DATA_FILE_PATH):
        raise FileNotFoundError("potential_customers_data.json not found. Run scripts/import_google_drive.py to import data.")
    with open(DATA_FILE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return PotentialCustomersIndexResponse(**data)


@router.get("/countries", response_model=PotentialCustomersIndexResponse)
def list_countries(current_user: dict = Depends(get_current_user)):
    try:
        return _load_index_from_file()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to load potential customers index: {exc}")


@router.get("/countries/{country_id}", response_model=CountryFolderResponse)
def get_country(country_id: str, current_user: dict = Depends(get_current_user)):
    try:
        index = _load_index_from_file()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to load potential customers index: {exc}")

    for country in index.countries:
        if country.id == country_id:
            return country
    raise HTTPException(status_code=404, detail="Country not found")

from fastapi import APIRouter, Depends

from app.api.dependencies import get_data_loader
from app.data.preprocessor import BUDGET_BAND_DEFINITIONS
from app.services.data_loader import DataLoader

router = APIRouter(prefix="/metadata", tags=["metadata"])


@router.get("/locations")
def list_locations(loader: DataLoader = Depends(get_data_loader)) -> dict:
    return {"locations": loader.get_locations()}


@router.get("/cuisines")
def list_cuisines(loader: DataLoader = Depends(get_data_loader)) -> dict:
    return {"cuisines": loader.get_cuisines()}


@router.get("/budget-bands")
def list_budget_bands() -> dict:
    return {"budget_bands": BUDGET_BAND_DEFINITIONS}

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter()

# In-memory store for demo purposes
DATASETS = []


class DatasetMetadata(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    fields: List[str]
    owner: Optional[str] = None
    created_at: datetime
    tags: Optional[List[str]] = None


@router.post("/data-catalog/datasets", status_code=status.HTTP_201_CREATED)
def register_dataset(dataset: DatasetMetadata):
    if any(d.id == dataset.id for d in DATASETS):
        raise HTTPException(status_code=400, detail="Dataset ID already exists")
    DATASETS.append(dataset)
    return {"message": "Dataset registered", "dataset_id": dataset.id}


@router.get("/data-catalog/datasets", response_model=List[DatasetMetadata])
def list_datasets():
    return DATASETS


@router.get("/data-catalog/search", response_model=List[DatasetMetadata])
def search_datasets(query: str):
    q = query.lower()
    return [d for d in DATASETS if q in d.name.lower() or any(q in f.lower() for f in d.fields)]

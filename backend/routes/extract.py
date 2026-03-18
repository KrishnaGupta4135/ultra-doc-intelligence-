from fastapi import APIRouter
from pydantic import BaseModel
from backend.services.extraction import extract_data

router = APIRouter()


class ExtractRequest(BaseModel):
    document_id: str


@router.post("/extract")
def extract(req: ExtractRequest):
    return extract_data(req.document_id)
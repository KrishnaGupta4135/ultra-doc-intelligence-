from fastapi import APIRouter
from pydantic import BaseModel
from backend.services.rag import answer_question

router = APIRouter()


class AskRequest(BaseModel):
    document_id: str
    question: str


@router.post("/ask")
def ask(req: AskRequest):
    return answer_question(req.document_id, req.question)
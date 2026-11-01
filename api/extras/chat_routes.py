from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from chatbot.extras.roadmap import generate_learning_roadmap
from chatbot.extras.text_to_sql import answer_question


router = APIRouter(prefix="/extras", tags=["extras"])


class ExtrasChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    target_role: Optional[str] = Field(default=None, max_length=160)
    missing_skills: Optional[List[str]] = Field(default=None, max_length=50)


@router.post("/chat")
def extras_chat(request: ExtrasChatRequest):
    if request.target_role or any(
        phrase in request.question.casefold()
        for phrase in ("roadmap", "learning plan", "what should i learn")
    ):
        if not request.target_role:
            raise HTTPException(
                status_code=400,
                detail="A target_role is required to generate a learning roadmap.",
            )
        try:
            return generate_learning_roadmap(request.target_role, request.missing_skills)
        except (ValueError, LookupError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    try:
        return answer_question(request.question)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

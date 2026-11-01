from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.extras.skill_gap import analyze_skill_gap


router = APIRouter(prefix="/extras", tags=["extras"])


class SkillGapRequest(BaseModel):
    target_role: str = Field(min_length=1, max_length=160)
    user_skills: Optional[List[str]] = None
    resume_text: Optional[str] = Field(default=None, max_length=30000)


@router.post("/skill-gap")
def skill_gap(request: SkillGapRequest):
    try:
        return analyze_skill_gap(
            target_role=request.target_role,
            user_skills=request.user_skills,
            resume_text=request.resume_text or "",
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

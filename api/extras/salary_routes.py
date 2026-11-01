from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.extras.salary_model import predict_salary


router = APIRouter(prefix="/extras", tags=["extras"])


class SalaryPredictionRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    city: Optional[str] = Field(default=None, max_length=100)
    experience_level: Optional[str] = Field(default=None, max_length=50)
    skills: List[str] = Field(default_factory=list, max_length=100)
    work_mode: Optional[str] = Field(default=None, max_length=30)


@router.post("/salary/predict")
def salary_prediction(request: SalaryPredictionRequest):
    try:
        return predict_salary(request.model_dump())
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

from fastapi import APIRouter, HTTPException, Query

from backend.extras.fresher_insights import get_fresher_insights


router = APIRouter(prefix="/extras", tags=["extras"])


@router.get("/fresher-insights")
def fresher_insights(top_n: int = Query(default=10, ge=1, le=50)):
    try:
        return get_fresher_insights(top_n=top_n)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

from fastapi import APIRouter, HTTPException, Query

from backend.extras.trend_forecast import forecast_skill_trends


router = APIRouter(prefix="/extras", tags=["extras"])


@router.get("/trends")
def skill_trends(
    horizon_months: int = Query(default=3, ge=1, le=12),
    top_n: int = Query(default=10, ge=1, le=50),
):
    try:
        return forecast_skill_trends(horizon_months=horizon_months, top_n=top_n)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

from fastapi import APIRouter, Query

from backend.extras.city_opportunities import aggregate_city_opportunities


router = APIRouter(prefix="/extras", tags=["extras"])


@router.get("/cities")
def city_opportunities(remote_only: bool = Query(default=False)):
    return aggregate_city_opportunities(remote_only=remote_only)

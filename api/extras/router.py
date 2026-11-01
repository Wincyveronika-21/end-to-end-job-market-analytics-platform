from fastapi import APIRouter

from api.extras.chat_routes import router as chat_router
from api.extras.city_routes import router as city_router
from api.extras.fresher_routes import router as fresher_router
from api.extras.salary_routes import router as salary_router
from api.extras.skill_gap_routes import router as skill_gap_router
from api.extras.trend_routes import router as trend_router


router = APIRouter()
router.include_router(skill_gap_router)
router.include_router(salary_router)
router.include_router(trend_router)
router.include_router(fresher_router)
router.include_router(city_router)
router.include_router(chat_router)

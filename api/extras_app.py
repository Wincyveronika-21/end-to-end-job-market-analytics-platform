from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api.extras.router import router as extras_router
from config.config import BASE_DIR


app = FastAPI(
    title="Job Market Analytics Extras",
    description="Standalone API and dashboard for additive job-market features.",
    version="1.0.0",
)
app.include_router(extras_router)
app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "dashboard"),
    name="static",
)


@app.get("/", include_in_schema=False)
def extras_home():
    return FileResponse(BASE_DIR / "dashboard" / "extras" / "index.html")

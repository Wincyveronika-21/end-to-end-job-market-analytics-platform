from fastapi import FastAPI

from api.extras_app import app as standalone_app
from api.extras.router import router


def test_extras_router_exposes_all_feature_endpoints():
    app = FastAPI()
    app.include_router(router)
    paths = app.openapi()["paths"]

    assert {
        "/extras/skill-gap",
        "/extras/salary/predict",
        "/extras/trends",
        "/extras/fresher-insights",
        "/extras/cities",
        "/extras/chat",
    }.issubset(paths)


def test_standalone_app_exposes_features_and_dashboard_assets():
    paths = standalone_app.openapi()["paths"]
    mounts = {route.path for route in standalone_app.routes if hasattr(route, "path")}

    assert "/extras/skill-gap" in paths
    assert "/extras/chat" in paths
    assert "/" in mounts
    assert "/static" in mounts

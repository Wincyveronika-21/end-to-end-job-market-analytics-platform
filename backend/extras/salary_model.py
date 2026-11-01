from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from config.config import BASE_DIR
from backend.extras._data import load_jobs, normalize_skills


DEFAULT_MODEL_PATH = BASE_DIR / "models" / "salary_predictor.joblib"


def _features(posting: Dict[str, Any]) -> Dict[str, Any]:
    features: Dict[str, Any] = {
        "title": str(posting.get("title") or "").strip().casefold(),
        "city": str(posting.get("city") or "").strip().casefold(),
        "experience_level": str(posting.get("experience_level") or "").strip().casefold(),
        "work_mode": str(posting.get("work_mode") or "").strip().casefold(),
    }
    for skill in normalize_skills(posting.get("skills") or ()):
        features[f"skill:{skill.casefold()}"] = 1
    return features


def train_salary_model(
    jobs: Optional[Sequence[Dict[str, Any]]] = None,
    model_path: Optional[Path] = None,
) -> Dict[str, Optional[float]]:
    try:
        from joblib import dump
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.feature_extraction import DictVectorizer
        from sklearn.metrics import mean_absolute_error, r2_score
        from sklearn.model_selection import train_test_split
        from sklearn.pipeline import make_pipeline
    except ImportError as exc:
        raise RuntimeError(
            "Salary prediction dependencies are missing; install requirements-extras.txt."
        ) from exc

    records = list(jobs if jobs is not None else load_jobs())
    labeled = [
        (job, float(job.get("salary_avg") or 0))
        for job in records
        if float(job.get("salary_avg") or 0) > 0
    ]
    if len(labeled) < 4:
        raise ValueError("At least four postings with known salaries are required to train.")

    features = [_features(job) for job, _ in labeled]
    targets = [salary for _, salary in labeled]
    indices = list(range(len(labeled)))
    train_indices, test_indices = train_test_split(
        indices, test_size=max(1, int(round(len(indices) * 0.2))), random_state=42
    )
    model = make_pipeline(
        DictVectorizer(),
        RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=1),
    )
    model.fit([features[index] for index in train_indices], [targets[index] for index in train_indices])
    predictions = model.predict([features[index] for index in test_indices])
    actual = [targets[index] for index in test_indices]
    mae = float(mean_absolute_error(actual, predictions))
    r2 = float(r2_score(actual, predictions)) if len(actual) >= 2 else None

    destination = model_path or DEFAULT_MODEL_PATH
    destination.parent.mkdir(parents=True, exist_ok=True)
    dump({"model": model, "version": 1}, destination)
    print(f"Salary model MAE: {mae:.2f}; R2: {r2:.4f}" if r2 is not None else f"Salary model MAE: {mae:.2f}; R2: unavailable")
    return {"mae": mae, "r2": r2}


def predict_salary(
    posting: Dict[str, Any],
    model_path: Optional[Path] = None,
) -> Dict[str, Any]:
    try:
        from joblib import load
    except ImportError as exc:
        raise RuntimeError(
            "Salary prediction dependencies are missing; install requirements-extras.txt."
        ) from exc

    destination = model_path or DEFAULT_MODEL_PATH
    if not destination.exists():
        train_salary_model(model_path=destination)
    bundle = load(destination)
    prediction = max(0.0, float(bundle["model"].predict([_features(posting)])[0]))
    return {
        "predicted_salary": round(prediction, 2),
        "currency": "USD",
        "model_version": bundle["version"],
    }

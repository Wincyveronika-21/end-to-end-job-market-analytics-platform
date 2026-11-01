from collections import Counter, defaultdict
from datetime import date
from typing import Any, Dict, List, Optional, Sequence, Tuple

from backend.extras._data import load_jobs


MIN_HISTORY_MONTHS = 6


def _month(value: Any) -> Optional[str]:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10]).strftime("%Y-%m")
    except ValueError:
        return None


def _next_month(month: str, offset: int) -> str:
    year, number = (int(part) for part in month.split("-"))
    absolute = year * 12 + number - 1 + offset
    return f"{absolute // 12:04d}-{absolute % 12 + 1:02d}"


def forecast_skill_trends(
    jobs: Optional[Sequence[Dict[str, Any]]] = None,
    horizon_months: int = 3,
    top_n: int = 10,
) -> Dict[str, Any]:
    if horizon_months < 1 or horizon_months > 12:
        raise ValueError("Forecast horizon must be between 1 and 12 months.")
    if top_n < 1 or top_n > 50:
        raise ValueError("top_n must be between 1 and 50.")

    postings = list(jobs if jobs is not None else load_jobs())
    monthly: Dict[str, Counter] = defaultdict(Counter)
    for job in postings:
        month = _month(job.get("date_posted"))
        if month:
            monthly[month].update(set(job.get("skills") or []))
    months = sorted(monthly)
    if len(months) < MIN_HISTORY_MONTHS:
        return {
            "available": False,
            "message": (
                f"At least {MIN_HISTORY_MONTHS} distinct months of posting history are "
                f"required; only {len(months)} month(s) are available."
            ),
            "available_months": len(months),
            "forecasts": [],
        }

    ranked = Counter()
    for counts in monthly.values():
        ranked.update(counts)
    top_skills = [skill for skill, _ in ranked.most_common(top_n)]
    future_months = [_next_month(months[-1], index) for index in range(1, horizon_months + 1)]
    forecasts = []

    for skill in top_skills:
        values = [monthly[month].get(skill, 0) for month in months]
        history = [{"month": month, "count": value} for month, value in zip(months, values)]
        predicted = _predict_counts(months, values, horizon_months)
        forecasts.append({
            "skill": skill,
            "history": history,
            "forecast": [
                {"month": month, "count": round(max(0.0, float(value)), 2)}
                for month, value in zip(future_months, predicted)
            ],
        })
    return {
        "available": True,
        "message": None,
        "available_months": len(months),
        "forecasts": forecasts,
    }


def _predict_counts(months: List[str], values: List[int], horizon: int) -> List[float]:
    try:
        from prophet import Prophet
    except ImportError:
        Prophet = None

    if Prophet is not None:
        import pandas as pd

        model = Prophet(yearly_seasonality=False, weekly_seasonality=False, daily_seasonality=False)
        frame = pd.DataFrame({
            "ds": [f"{month}-01" for month in months],
            "y": values,
        })
        model.fit(frame)
        future = model.make_future_dataframe(periods=horizon, freq="MS")
        prediction = model.predict(future)
        return prediction["yhat"].tail(horizon).tolist()

    try:
        from statsmodels.tsa.holtwinters import ExponentialSmoothing
    except ImportError as exc:
        raise RuntimeError(
            "Trend forecasting dependencies are missing; install requirements-extras.txt."
        ) from exc
    model = ExponentialSmoothing(
        values, trend="add", seasonal=None, initialization_method="estimated"
    ).fit()
    return model.forecast(horizon).tolist()

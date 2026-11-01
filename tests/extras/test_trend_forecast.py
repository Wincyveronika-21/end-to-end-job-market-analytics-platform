from backend.extras.trend_forecast import forecast_skill_trends


def test_trend_forecast_explains_insufficient_history():
    result = forecast_skill_trends(
        jobs=[
            {"date_posted": "2026-01-03", "skills": ["Python"]},
            {"date_posted": "2026-02-03", "skills": ["Python"]},
        ]
    )

    assert result["available"] is False
    assert "At least 6 distinct months" in result["message"]
    assert result["forecasts"] == []


def test_trend_forecast_returns_actual_and_future_counts(monkeypatch):
    jobs = [
        {"date_posted": f"2026-{month:02d}-10", "skills": ["Python"]}
        for month in range(1, 7)
    ]
    monkeypatch.setattr(
        "backend.extras.trend_forecast._predict_counts",
        lambda months, values, horizon: [7.0] * horizon,
    )

    result = forecast_skill_trends(jobs=jobs)

    assert result["available"] is True
    assert len(result["forecasts"][0]["history"]) == 6
    assert result["forecasts"][0]["forecast"] == [
        {"month": "2026-07", "count": 7.0},
        {"month": "2026-08", "count": 7.0},
        {"month": "2026-09", "count": 7.0},
    ]

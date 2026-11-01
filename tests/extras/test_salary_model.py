import pytest

from backend.extras.salary_model import predict_salary, train_salary_model


pytest.importorskip("sklearn")
pytest.importorskip("joblib")


def sample_jobs():
    return [
        {
            "title": f"Data Analyst {index % 2}",
            "city": "Pune" if index % 2 else "Remote",
            "experience_level": "Entry" if index < 8 else "Senior",
            "work_mode": "Remote" if index % 2 else "Onsite",
            "skills": ["Python", "SQL"] if index % 2 else ["SQL", "Power BI"],
            "salary_avg": 50000 + index * 2500,
        }
        for index in range(20)
    ]


def test_salary_model_trains_saves_and_predicts(tmp_path):
    model_path = tmp_path / "model.joblib"
    metrics = train_salary_model(jobs=sample_jobs(), model_path=model_path)
    prediction = predict_salary(
        {
            "title": "Data Analyst",
            "city": "Pune",
            "experience_level": "Entry",
            "skills": ["Python", "SQL"],
            "work_mode": "Remote",
        },
        model_path=model_path,
    )

    assert model_path.exists()
    assert metrics["mae"] >= 0
    assert prediction["predicted_salary"] > 0
    assert prediction["currency"] == "USD"


def test_salary_model_requires_labeled_rows():
    with pytest.raises(ValueError, match="four postings"):
        train_salary_model(jobs=[{"salary_avg": 0}] * 4)

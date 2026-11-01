import pytest

from backend.extras.skill_gap import analyze_skill_gap


def test_skill_gap_ranks_role_demand_and_parses_resume():
    jobs = [
        {"title": "Data Analyst", "skills": ["Python", "SQL"]},
        {"title": "Data Analyst", "skills": ["Python", "Power BI"]},
        {"title": "Senior Engineer", "skills": ["Rust"]},
    ]

    result = analyze_skill_gap("Data Analyst", resume_text="I use Python.", jobs=jobs)

    assert result["posting_count"] == 2
    assert result["match_score"] == 50.0
    assert {
        item["skill"] for item in result["missing_skills"]
    } == {"SQL", "Power BI"}
    assert all(item["demand_count"] == 1 for item in result["missing_skills"])
    assert len(result["top_skills_to_learn"]) <= 3


def test_skill_gap_errors_when_role_has_no_postings():
    with pytest.raises(LookupError):
        analyze_skill_gap("No such role", jobs=[])

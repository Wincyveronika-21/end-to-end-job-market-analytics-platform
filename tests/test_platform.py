import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.db_manager import db
from etl.pipeline import ETLPipeline
from backend.services import AnalyticsService
from chatbot.ai_engine import chatbot_engine

def test_etl_pipeline():
    pipeline = ETLPipeline()
    result = pipeline.run_pipeline(include_synthetic=True, synthetic_count=20)
    assert result["status"] == "success"
    assert result["jobs_ingested"] > 0
    assert result["skills_extracted"] > 0

def test_database_overview_metrics():
    overview = db.get_overview_metrics()
    assert overview["total_jobs"] > 0
    assert overview["avg_salary"] >= 0

def test_analytics_demanded_skills():
    skills = AnalyticsService.get_demanded_skills(limit=5)
    assert isinstance(skills, list)
    assert len(skills) > 0
    assert "skill" in skills[0]
    assert "demand_count" in skills[0]

def test_analytics_salary_trends():
    trends = AnalyticsService.get_salary_trends()
    assert "salary_by_skill" in trends
    assert "salary_by_experience" in trends

def test_analytics_work_mode_stats():
    work_modes = AnalyticsService.get_work_mode_stats()
    assert len(work_modes) > 0

def test_chatbot_engine():
    res1 = chatbot_engine.process_query("What are the most demanded skills?")
    assert "answer" in res1
    assert "Top 10 Most Demanded Skills" in res1["answer"]

    res2 = chatbot_engine.process_query("What is the average remote salary?")
    assert "answer" in res2
    assert "Remote" in res2["answer"]

def test_resume_skill_matcher():
    match = AnalyticsService.match_resume_skills(["Python", "SQL", "Power BI"])
    assert match["match_score"] >= 0
    assert "matched_skills" in match
    assert "missing_high_demand_skills" in match

if __name__ == "__main__":
    print("[Tests] Running platform test suite...")
    test_etl_pipeline()
    test_database_overview_metrics()
    test_analytics_demanded_skills()
    test_analytics_salary_trends()
    test_analytics_work_mode_stats()
    test_chatbot_engine()
    test_resume_skill_matcher()
    print("[Tests] All tests passed cleanly!")

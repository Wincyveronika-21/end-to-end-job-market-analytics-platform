import sys
from pathlib import Path
import asyncio
from io import BytesIO
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import api.main as api_main
from api.main import extract_resume_pdf_text
from database.db_manager import db
from etl.pipeline import ETLPipeline
from backend.services import AnalyticsService
import backend.services as services
from chatbot.ai_engine import chatbot_engine
from fastapi import HTTPException, UploadFile
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

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

def test_job_specific_career_plan():
    class CareerPlanDatabase:
        def execute_query(self, query, params=()):
            if "FROM jobs WHERE id" in query:
                return [{
                    "id": "career-test",
                    "title": "Data Analyst",
                    "company": "Example Co",
                    "city": "Remote",
                    "work_mode": "Remote",
                    "url": "https://example.com/jobs/1",
                    "description": "Analyze data with Python, SQL, and R."
                }]
            return [{"name": skill} for skill in ("Python", "R", "SQL")]

    original_db = services.db
    services.db = CareerPlanDatabase()
    try:
        plan = AnalyticsService.build_job_career_plan(
            "career-test", "Experienced Python developer with a career in analytics."
        )
        assert plan["job"]["title"] == "Data Analyst"
        assert plan["matched_skills"] == ["Python"]
        assert plan["missing_skills"] == ["R", "SQL"]
        assert plan["match_score"] == 33.3
        assert len(plan["learning_path"]) == 2
        assert plan["learning_path"][1]["project_title"] == "Build a job-market SQL dashboard"
        assert all("R" not in skill for skill in plan["resume_skills"])
    finally:
        services.db = original_db

def test_pdf_resume_text_extraction():
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    font = writer._add_object(DictionaryObject({
        NameObject("/Type"): NameObject("/Font"),
        NameObject("/Subtype"): NameObject("/Type1"),
        NameObject("/BaseFont"): NameObject("/Helvetica")
    }))
    page[NameObject("/Resources")] = DictionaryObject({
        NameObject("/Font"): DictionaryObject({NameObject("/F1"): font})
    })
    content = DecodedStreamObject()
    content.set_data(b"BT /F1 12 Tf 72 720 Td (Python SQL) Tj ET")
    page[NameObject("/Contents")] = writer._add_object(content)
    pdf_buffer = BytesIO()
    writer.write(pdf_buffer)

    extracted_text = extract_resume_pdf_text(pdf_buffer.getvalue())
    assert "Python SQL" in extracted_text

    original_plan = api_main.AnalyticsService.build_job_career_plan
    api_main.AnalyticsService.build_job_career_plan = (
        lambda job_id, resume_text: {"job_id": job_id, "resume_text": resume_text}
    )
    try:
        upload = UploadFile(filename="resume.pdf", file=BytesIO(pdf_buffer.getvalue()))
        result = asyncio.run(api_main.build_job_career_plan_from_pdf("career-test", upload))
        assert result["job_id"] == "career-test"
        assert "Python SQL" in result["resume_text"]
    finally:
        api_main.AnalyticsService.build_job_career_plan = original_plan

    try:
        extract_resume_pdf_text(b"not a pdf")
        raise AssertionError("Invalid PDF should be rejected.")
    except HTTPException as exc:
        assert exc.status_code == 400

if __name__ == "__main__":
    print("[Tests] Running platform test suite...")
    test_etl_pipeline()
    test_database_overview_metrics()
    test_analytics_demanded_skills()
    test_analytics_salary_trends()
    test_analytics_work_mode_stats()
    test_chatbot_engine()
    test_resume_skill_matcher()
    test_job_specific_career_plan()
    test_pdf_resume_text_extraction()
    print("[Tests] All tests passed cleanly!")

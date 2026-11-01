import sys
from pathlib import Path

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import io
import csv
from typing import List, Optional
from fastapi import FastAPI, Query, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pypdf import PdfReader
from pypdf.errors import PdfReadError

from config.config import BASE_DIR
from database.db_manager import db
from backend.services import AnalyticsService
from chatbot.ai_engine import chatbot_engine
from etl.pipeline import ETLPipeline
from etl.scheduler import scheduler
from api.extras.router import router as extras_router

app = FastAPI(
    title="Job Market Analytics Platform API",
    description="End-to-End Real-Time Job Market Intelligence & AI Assistant",
    version="1.0.0"
)
app.include_router(extras_router)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database and run initial ETL on startup
@app.on_event("startup")
def startup_event():
    print("[API] Running initial database setup & data ingestion pipeline...")
    pipeline = ETLPipeline()
    pipeline.run_pipeline(include_synthetic=True, synthetic_count=60)
    scheduler.start()

@app.on_event("shutdown")
def shutdown_event():
    scheduler.stop()

# Data Models
class ChatQueryRequest(BaseModel):
    question: str

class ResumeMatchRequest(BaseModel):
    skills: List[str]

class JobCareerPlanRequest(BaseModel):
    job_id: str
    resume_text: str


MAX_RESUME_PDF_BYTES = 5 * 1024 * 1024
MAX_RESUME_PDF_PAGES = 30


def extract_resume_pdf_text(pdf_content: bytes) -> str:
    if not pdf_content.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="The uploaded file is not a valid PDF.")

    try:
        reader = PdfReader(io.BytesIO(pdf_content), strict=True)
    except (PdfReadError, ValueError, OSError) as exc:
        raise HTTPException(status_code=400, detail="The uploaded PDF could not be read.") from exc

    if reader.is_encrypted:
        raise HTTPException(status_code=400, detail="Password-protected PDFs are not supported.")
    if len(reader.pages) > MAX_RESUME_PDF_PAGES:
        raise HTTPException(
            status_code=413,
            detail=f"PDF resumes must have {MAX_RESUME_PDF_PAGES} pages or fewer."
        )

    extracted_text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    if not extracted_text:
        raise HTTPException(
            status_code=400,
            detail="No selectable text was found. Upload a text-based PDF or paste your resume text."
        )
    if len(extracted_text) > 30000:
        raise HTTPException(status_code=413, detail="Extracted resume text exceeds 30,000 characters.")
    return extracted_text


# API Endpoints
@app.get("/api/analytics/overview")
def get_overview():
    return AnalyticsService.get_overview_metrics()

@app.get("/api/analytics/demanded-skills")
def get_demanded_skills(limit: int = Query(15, ge=1, le=50), category: Optional[str] = None):
    return AnalyticsService.get_demanded_skills(limit=limit, category=category)

@app.get("/api/analytics/salary-trends")
def get_salary_trends():
    return AnalyticsService.get_salary_trends()

@app.get("/api/analytics/work-mode")
def get_work_mode():
    return AnalyticsService.get_work_mode_stats()

@app.get("/api/analytics/city-hiring")
def get_city_hiring(limit: int = Query(10, ge=1, le=30)):
    return AnalyticsService.get_city_hiring_stats(limit=limit)

@app.get("/api/jobs")
def get_jobs(
    title: Optional[str] = None,
    city: Optional[str] = None,
    work_mode: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    query = "SELECT id, title, company, category, location, city, country, work_mode, experience_level, salary_min, salary_max, salary_avg, date_posted, source, url FROM jobs WHERE 1=1"
    params = []

    if title:
        query += " AND LOWER(title) LIKE ?"
        params.append(f"%{title.lower()}%")
    if city and city.lower() != "all":
        query += " AND LOWER(city) = ?"
        params.append(city.lower())
    if work_mode and work_mode.lower() != "all":
        query += " AND LOWER(work_mode) = ?"
        params.append(work_mode.lower())
    if search:
        query += " AND (LOWER(title) LIKE ? OR LOWER(description) LIKE ? OR LOWER(company) LIKE ?)"
        params.extend([f"%{search.lower()}%", f"%{search.lower()}%", f"%{search.lower()}%"])

    query += " ORDER BY date_posted DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    jobs = db.execute_query(query, tuple(params))
    return {"count": len(jobs), "jobs": jobs}

@app.post("/api/ingest/trigger")
def trigger_ingestion():
    pipeline = ETLPipeline()
    result = pipeline.run_pipeline(include_synthetic=True, synthetic_count=20)
    return result

@app.post("/api/chatbot/query")
def chat_query(req: ChatQueryRequest):
    if not req.question or not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    return chatbot_engine.process_query(req.question)

@app.post("/api/career/match-resume")
def match_resume(req: ResumeMatchRequest):
    return AnalyticsService.match_resume_skills(req.skills)

@app.post("/api/career/job-plan")
def build_job_career_plan(req: JobCareerPlanRequest):
    if not req.job_id.strip():
        raise HTTPException(status_code=400, detail="A job posting must be selected.")
    if not req.resume_text.strip():
        raise HTTPException(status_code=400, detail="Resume text cannot be empty.")
    if len(req.resume_text) > 30000:
        raise HTTPException(status_code=413, detail="Resume text must be 30,000 characters or fewer.")
    try:
        return AnalyticsService.build_job_career_plan(req.job_id, req.resume_text)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

@app.post("/api/career/job-plan-pdf")
async def build_job_career_plan_from_pdf(
    job_id: str = Form(...),
    resume_file: UploadFile = File(...)
):
    if not job_id.strip():
        raise HTTPException(status_code=400, detail="A job posting must be selected.")
    if not resume_file.filename or not resume_file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF resume.")

    pdf_content = await resume_file.read(MAX_RESUME_PDF_BYTES + 1)
    if len(pdf_content) > MAX_RESUME_PDF_BYTES:
        raise HTTPException(status_code=413, detail="PDF resumes must be 5 MB or smaller.")

    resume_text = extract_resume_pdf_text(pdf_content)
    try:
        return AnalyticsService.build_job_career_plan(job_id, resume_text)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

@app.get("/api/export/csv")
def export_csv():
    """Generates downloadable CSV for Power BI Desktop ingestion."""
    query = """
    SELECT 
        j.id AS JobID,
        j.title AS JobTitle,
        j.company AS Company,
        j.category AS Category,
        j.location AS Location,
        j.city AS City,
        j.country AS Country,
        j.work_mode AS WorkMode,
        j.experience_level AS ExperienceLevel,
        j.salary_min AS MinSalaryUSD,
        j.salary_max AS MaxSalaryUSD,
        j.salary_avg AS AvgSalaryUSD,
        j.date_posted AS DatePosted,
        j.source AS DataSource,
        COALESCE(GROUP_CONCAT(s.name, '; '), 'None') AS RequiredSkills
    FROM jobs j
    LEFT JOIN job_skills js ON j.id = js.job_id
    LEFT JOIN skills s ON js.skill_id = s.id
    GROUP BY j.id
    ORDER BY j.date_posted DESC
    """
    rows = db.execute_query(query)

    output = io.StringIO()
    if rows:
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=job_market_dataset.csv"}
    )

# Serve Dashboard Frontend Static Files
dashboard_dir = BASE_DIR / "dashboard"
if dashboard_dir.exists():
    app.mount("/static", StaticFiles(directory=dashboard_dir), name="static")

    @app.get("/", response_class=HTMLResponse)
    def read_root():
        index_path = dashboard_dir / "index.html"
        if index_path.exists():
            with open(index_path, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        return HTMLResponse(content="<h1>Job Market Analytics Platform</h1><p>Dashboard UI loading...</p>")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)

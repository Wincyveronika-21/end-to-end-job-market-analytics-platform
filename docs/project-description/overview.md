# Job Market Analytics Platform

## Project description

The Job Market Analytics Platform is a Python web application for collecting,
organizing, and analyzing job-posting data. It turns raw listings into
actionable insights about skills, compensation, experience levels, work modes,
and hiring locations. A dashboard presents those insights, while job seekers
can explore role-specific skill gaps and learning suggestions.

The project combines a FastAPI backend, a SQLite database, an ETL pipeline, and
a browser-based dashboard. Its extras workspace adds forecasting, salary
estimation, early-career insights, opportunity mapping, and read-only
natural-language analytics.

## Goals

- Ingest job listings from public job data sources and normalize their fields.
- Extract skills from job descriptions and maintain structured job/skill
  relationships.
- Summarize hiring patterns, salary ranges, work modes, and skill demand.
- Help job seekers compare their skills to a selected role and plan learning.
- Make data available to dashboard users and Power BI through a CSV endpoint.
- Keep additive career and analytics features organized, tested, and documented.

## Main components

### Data collection and ETL

The ETL pipeline collects postings from the Remotive and Jobicy APIs, optionally
adds synthetic demonstration postings, normalizes job and salary fields,
extracts skills using the project taxonomy, and upserts the results into SQLite.
A background scheduler periodically runs ingestion.

### Database

The existing schema stores jobs, normalized skills, and job-to-skill links in
`jobs`, `skills`, and `job_skills`. Analytical views provide skill demand,
work-mode summaries, and city hiring statistics. Extras query this existing
data; no new tables are required.

### Analytics and APIs

FastAPI exposes the existing analytics, job search, resume analysis, chatbot,
ingestion, and CSV export endpoints. Feature-specific routers provide role
skill-gap analysis, salary prediction, demand forecasting, fresher insights,
city aggregation, and a read-only SQL chat and learning roadmap.

### Dashboard

The main HTML/CSS/JavaScript dashboard uses Chart.js for market charts and
provides job search, resume matching, a career learning portal, and the market
chat assistant. A puzzle-piece launcher opens the extras workspace on the same
server. Every extras page includes a home button back to the main dashboard.

### Career Learning Portal

Users select a live posting, paste resume text or upload a PDF, and compare
their skills with that specific role. The portal returns matched and missing
skills, a role-match score, learning goals, practical portfolio-project
briefs, and an employer application link when one is present. Applications are
completed on the employer's website.

Resume text is used only to produce the requested plan and is not stored. PDF
uploads are limited to 5 MB and 30 pages. Password-protected or scanned,
image-only PDFs are not supported.

### Extras workspace

- **Skill Gap Analyzer:** matches user skills or resume text against postings
  for a target role, ranks missing skills by demand, and recommends three next
  skills.
- **Salary Predictor:** trains a Random Forest regressor on labeled salary
  postings and estimates salary for postings without a reported salary. Model
  artifacts are generated locally and ignored by Git.
- **Skill Trend Forecast:** forecasts demand for popular skills over the next
  few months using Prophet when installed or statsmodels otherwise. It explains
  when the available posting history is too short.
- **Fresher Insights:** compares fresher and senior skill demand, counts
  internships by city, and reports postings per distinct skill as a demand
  proxy (not applicant competition).
- **City and Remote Opportunity Map:** aggregates postings and available
  salaries by city and work mode, plots cities with known coordinates, and
  compares remote versus in-person options.
- **Chat and Learning Roadmap:** maps supported job-market questions to
  allowlisted, read-only SQL and creates a three-month role-focused learning
  plan. SQL execution is restricted to approved tables/views and a fixed row
  limit.

## Technology

- Python and FastAPI
- SQLite and SQL
- Pandas, scikit-learn, joblib, and statsmodels for data and modeling
- HTML, CSS, JavaScript, Chart.js, and Plotly
- pytest for platform and feature tests

## Data flow

```text
Remotive / Jobicy APIs
          |
          v
     ETL collector -> transformer / skill extraction
          |                         |
          +-------------------------+
                                    v
                          SQLite jobs and skills
                                    |
                +-------------------+------------------+
                v                                      v
      Analytics and extras APIs           Dashboard and career tools
```

## Run and validate

From the repository root, install `requirements.txt` and
`requirements-extras.txt`, then start the app with:

```powershell
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

Open the dashboard at `http://127.0.0.1:8000/`. The FastAPI schema is at
`http://127.0.0.1:8000/docs`. Run the platform and extras tests with:

```powershell
python -m pytest -q tests/extras tests/test_platform.py
```

## Screenshots

See the [main README](../../README.md) and [extras guide](../extras/README.md)
for screenshots and feature-level usage instructions.

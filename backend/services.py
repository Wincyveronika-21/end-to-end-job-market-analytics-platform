import re
from typing import Dict, Any, List
from database.db_manager import db
from utils.skill_taxonomy import CANONICAL_SKILLS, SKILL_TAXONOMY


LEARNING_PATHS = {
    "python": {
        "focus": "Practice core syntax, functions, data structures, and writing reusable modules.",
        "project_title": "Automate a job-market report",
        "project_brief": "Use Python to clean a small jobs dataset, summarize in-demand skills, and export a weekly report.",
        "resource_url": "https://docs.python.org/3/tutorial/"
    },
    "sql": {
        "focus": "Learn joins, grouping, subqueries, and window functions using realistic datasets.",
        "project_title": "Build a job-market SQL dashboard",
        "project_brief": "Create a relational jobs dataset and write queries for skill demand, salary ranges, and city hiring trends.",
        "resource_url": "https://www.postgresql.org/docs/current/tutorial.html"
    },
    "power bi": {
        "focus": "Practice data modeling, Power Query transformations, DAX measures, and report design.",
        "project_title": "Create a hiring trends report",
        "project_brief": "Build an interactive report showing hiring by city, salary bands, remote share, and skill demand.",
        "resource_url": "https://learn.microsoft.com/en-us/training/powerplatform/power-bi/"
    },
    "excel": {
        "focus": "Strengthen data cleaning, lookup formulas, pivot tables, and charts.",
        "project_title": "Analyze a hiring spreadsheet",
        "project_brief": "Turn raw job postings into a cleaned workbook with pivot tables for salaries, skills, and locations.",
        "resource_url": "https://support.microsoft.com/en-us/excel"
    },
    "pandas": {
        "focus": "Practice DataFrame selection, cleaning, grouping, merging, and export workflows.",
        "project_title": "Explore job postings with Pandas",
        "project_brief": "Load job data, normalize locations and skills, then publish a reproducible market analysis notebook.",
        "resource_url": "https://pandas.pydata.org/docs/getting_started/intro_tutorials/"
    },
    "aws": {
        "focus": "Learn cloud storage, identity and access basics, and how to deploy a small data workflow.",
        "project_title": "Publish a cloud-hosted job report",
        "project_brief": "Store a sample jobs dataset and serve a documented analytics report using AWS free-tier services.",
        "resource_url": "https://aws.amazon.com/training/learn-about/"
    },
    "docker": {
        "focus": "Learn images, containers, environment configuration, and reproducible application builds.",
        "project_title": "Containerize a job analytics API",
        "project_brief": "Package a small API and its analytics dependencies into a documented, reproducible Docker setup.",
        "resource_url": "https://docs.docker.com/get-started/"
    },
    "tableau": {
        "focus": "Practice connecting data, creating calculated fields, and building interactive dashboards.",
        "project_title": "Visualize regional hiring demand",
        "project_brief": "Create a dashboard comparing job volume, skills, and salary across cities and work modes.",
        "resource_url": "https://www.tableau.com/learn/training"
    },
    "machine learning": {
        "focus": "Study model evaluation, feature preparation, and baseline supervised learning workflows.",
        "project_title": "Estimate job salary bands",
        "project_brief": "Train and evaluate a baseline model that estimates salary ranges from role, skills, and location.",
        "resource_url": "https://scikit-learn.org/stable/tutorial/basic/tutorial.html"
    },
    "javascript": {
        "focus": "Practice modern JavaScript, asynchronous requests, DOM updates, and accessible interactions.",
        "project_title": "Build a job-search interface",
        "project_brief": "Create a searchable job listing page that calls an API and presents filters and role details.",
        "resource_url": "https://developer.mozilla.org/en-US/docs/Learn/JavaScript"
    }
}


def _canonical_skill(skill: str) -> str:
    cleaned = skill.strip()
    return CANONICAL_SKILLS.get(cleaned.lower(), cleaned.title())


def _extract_resume_skills(resume_text: str) -> set:
    text = resume_text.lower()
    aliases = set(CANONICAL_SKILLS)
    for skills in SKILL_TAXONOMY.values():
        aliases.update(skill.lower() for skill in skills)
    return {_canonical_skill(alias) for alias in aliases
            if re.search(r"(?<![a-z0-9])" + re.escape(alias) + r"(?![a-z0-9])", text)}

class AnalyticsService:
    """Provides high-performance analytical queries and business intelligence calculations."""

    @staticmethod
    def get_overview_metrics() -> Dict[str, Any]:
        return db.get_overview_metrics()

    @staticmethod
    def get_demanded_skills(limit: int = 15, category: str = None) -> List[Dict[str, Any]]:
        query = """
        SELECT 
            s.name AS skill,
            s.category AS category,
            COUNT(js.job_id) AS demand_count,
            ROUND(COUNT(js.job_id) * 100.0 / (SELECT COUNT(*) FROM jobs), 1) AS percentage,
            ROUND(AVG(j.salary_avg), 0) AS avg_salary
        FROM skills s
        JOIN job_skills js ON s.id = js.skill_id
        JOIN jobs j ON js.job_id = j.id
        """
        params = []
        if category and category.lower() != "all":
            query += " WHERE LOWER(s.category) = LOWER(?)"
            params.append(category)

        query += " GROUP BY s.id, s.name, s.category ORDER BY demand_count DESC LIMIT ?"
        params.append(limit)

        return db.execute_query(query, tuple(params))

    @staticmethod
    def get_salary_trends() -> Dict[str, Any]:
        # Salary by Skill (Top 10)
        by_skill_query = """
        SELECT 
            s.name AS skill,
            ROUND(MIN(j.salary_min), 0) AS min_salary,
            ROUND(AVG(j.salary_avg), 0) AS avg_salary,
            ROUND(MAX(j.salary_max), 0) AS max_salary
        FROM skills s
        JOIN job_skills js ON s.id = js.skill_id
        JOIN jobs j ON js.job_id = j.id
        WHERE j.salary_avg > 0
        GROUP BY s.id, s.name
        ORDER BY COUNT(js.job_id) DESC
        LIMIT 10
        """
        # Salary by Experience Level
        by_exp_query = """
        SELECT 
            experience_level,
            COUNT(*) AS job_count,
            ROUND(AVG(salary_avg), 0) AS avg_salary,
            ROUND(MIN(salary_min), 0) AS min_salary,
            ROUND(MAX(salary_max), 0) AS max_salary
        FROM jobs
        WHERE salary_avg > 0
        GROUP BY experience_level
        ORDER BY avg_salary ASC
        """
        return {
            "salary_by_skill": db.execute_query(by_skill_query),
            "salary_by_experience": db.execute_query(by_exp_query)
        }

    @staticmethod
    def get_work_mode_stats() -> List[Dict[str, Any]]:
        query = "SELECT * FROM v_work_mode_stats"
        return db.execute_query(query)

    @staticmethod
    def get_city_hiring_stats(limit: int = 10) -> List[Dict[str, Any]]:
        query = """
        SELECT 
            city,
            country,
            total_postings,
            avg_salary
        FROM v_city_hiring_stats
        WHERE city != 'Remote' AND city IS NOT NULL
        ORDER BY total_postings DESC
        LIMIT ?
        """
        return db.execute_query(query, (limit,))

    @staticmethod
    def match_resume_skills(user_skills: List[str]) -> Dict[str, Any]:
        """Matches user skill input against overall market demand and returns skill gap analysis."""
        canonical_user_skills = set()
        for s in user_skills:
            s_clean = s.strip().lower()
            if s_clean:
                canon = CANONICAL_SKILLS.get(s_clean, s.strip().title())
                canonical_user_skills.add(canon)

        top_market_skills = AnalyticsService.get_demanded_skills(limit=25)
        
        matching_skills = []
        missing_skills = []
        
        for item in top_market_skills:
            skill_name = item["skill"]
            if skill_name in canonical_user_skills or any(us.lower() == skill_name.lower() for us in canonical_user_skills):
                matching_skills.append(item)
            else:
                missing_skills.append(item)

        # Match score calculation
        total_market_demand = sum(s["demand_count"] for s in top_market_skills) or 1
        matched_demand = sum(s["demand_count"] for s in matching_skills)
        match_score = round((matched_demand / total_market_demand) * 100, 1)

        return {
            "match_score": match_score,
            "matched_skills": matching_skills,
            "missing_high_demand_skills": missing_skills[:8],
            "user_skills_processed": list(canonical_user_skills)
        }

    @staticmethod
    def build_job_career_plan(job_id: str, resume_text: str) -> Dict[str, Any]:
        """Compare resume text with a job's skills and create a focused learning plan."""
        job_rows = db.execute_query(
            """
            SELECT id, title, company, city, work_mode, url, description
            FROM jobs WHERE id = ?
            """,
            (job_id,)
        )
        if not job_rows:
            raise LookupError("Job posting not found.")

        job = job_rows[0]
        skill_rows = db.execute_query(
            """
            SELECT s.name
            FROM skills s
            JOIN job_skills js ON js.skill_id = s.id
            WHERE js.job_id = ?
            ORDER BY s.name
            """,
            (job_id,)
        )
        required_skills = list(dict.fromkeys(
            _canonical_skill(row["name"]) for row in skill_rows if row["name"]
        ))
        if not required_skills and job.get("description"):
            required_skills = sorted(_extract_resume_skills(job["description"]))

        resume_skills = _extract_resume_skills(resume_text)
        matched_skills = [skill for skill in required_skills if skill in resume_skills]
        missing_skills = [skill for skill in required_skills if skill not in resume_skills]
        match_score = (
            round(len(matched_skills) * 100 / len(required_skills), 1)
            if required_skills else None
        )

        learning_path = []
        for skill in missing_skills:
            resource = LEARNING_PATHS.get(skill.lower())
            learning_path.append({
                "skill": skill,
                "focus": resource["focus"] if resource else f"Build practical {skill} skills through guided exercises and documentation.",
                "project_title": resource["project_title"] if resource else f"Create a {skill} portfolio project",
                "project_brief": resource["project_brief"] if resource else (
                    f"Build a small, documented project using {skill} to solve a problem relevant to a "
                    f"{job['title']} role."
                ),
                "resource_url": resource["resource_url"] if resource else None
            })

        return {
            "job": {key: job.get(key) for key in ("id", "title", "company", "city", "work_mode", "url")},
            "required_skills": required_skills,
            "resume_skills": sorted(resume_skills),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "match_score": match_score,
            "learning_path": learning_path
        }

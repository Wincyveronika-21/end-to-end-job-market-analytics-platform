from typing import Dict, Any, List
from database.db_manager import db
from utils.skill_taxonomy import CANONICAL_SKILLS

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

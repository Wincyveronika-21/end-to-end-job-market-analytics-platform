import sqlite3
from typing import List, Dict, Any, Optional
from config.config import DB_PATH
from utils.skill_taxonomy import get_skill_category

class DatabaseManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initialize database with schema.sql DDL."""
        schema_path = self.db_path.parent.parent / "database" / "schema.sql"
        if not schema_path.exists():
            schema_path = DB_PATH.parent.parent / "database" / "schema.sql"

        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executescript(schema_sql)
            conn.commit()

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Executes a SELECT query and returns rows as dictionaries."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def insert_job(self, job_data: Dict[str, Any], extracted_skills: List[str]) -> bool:
        """Inserts or updates a job posting and its extracted skills."""
        sql_job = """
        INSERT INTO jobs (id, title, company, category, location, city, country, work_mode, 
                          experience_level, salary_min, salary_max, salary_avg, salary_currency, 
                          date_posted, source, url, description)
        VALUES (:id, :title, :company, :category, :location, :city, :country, :work_mode,
                :experience_level, :salary_min, :salary_max, :salary_avg, :salary_currency,
                :date_posted, :source, :url, :description)
        ON CONFLICT(id) DO UPDATE SET
            title=excluded.title,
            company=excluded.company,
            salary_min=excluded.salary_min,
            salary_max=excluded.salary_max,
            salary_avg=excluded.salary_avg,
            work_mode=excluded.work_mode;
        """

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql_job, job_data)
            job_id = job_data["id"]

            for skill_name in extracted_skills:
                category = get_skill_category(skill_name)
                cursor.execute(
                    "INSERT OR IGNORE INTO skills (name, category) VALUES (?, ?)",
                    (skill_name, category)
                )
                cursor.execute("SELECT id FROM skills WHERE name = ?", (skill_name,))
                skill_row = cursor.fetchone()
                if skill_row:
                    skill_id = skill_row[0]
                    cursor.execute(
                        "INSERT OR IGNORE INTO job_skills (job_id, skill_id) VALUES (?, ?)",
                        (job_id, skill_id)
                    )
            conn.commit()
        return True

    def get_overview_metrics(self) -> Dict[str, Any]:
        """Returns overall KPI metrics."""
        query = """
        SELECT 
            (SELECT COUNT(*) FROM jobs) AS total_jobs,
            (SELECT ROUND(AVG(salary_avg), 0) FROM jobs WHERE salary_avg > 0) AS avg_salary,
            (SELECT ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM jobs), 0), 1) FROM jobs WHERE work_mode = 'Remote') AS remote_pct,
            (SELECT name FROM skills s JOIN job_skills js ON s.id = js.skill_id GROUP BY s.id ORDER BY COUNT(js.job_id) DESC LIMIT 1) AS top_skill,
            (SELECT city FROM jobs WHERE city IS NOT NULL AND city != 'Remote' GROUP BY city ORDER BY COUNT(*) DESC LIMIT 1) AS top_city
        """
        rows = self.execute_query(query)
        if rows:
            return rows[0]
        return {
            "total_jobs": 0,
            "avg_salary": 0,
            "remote_pct": 0,
            "top_skill": "N/A",
            "top_city": "N/A"
        }

db = DatabaseManager()

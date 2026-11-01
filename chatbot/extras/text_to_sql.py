import re
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from config.config import DB_PATH


MAX_ROWS = 100
FORBIDDEN_WORDS = {
    "ALTER", "ATTACH", "BEGIN", "COMMIT", "CREATE", "DELETE", "DETACH",
    "DROP", "INSERT", "PRAGMA", "REPLACE", "ROLLBACK", "UPDATE",
}
ALLOWED_TABLES = {
    "jobs", "skills", "job_skills",
    "v_skill_demand", "v_work_mode_stats", "v_city_hiring_stats",
}
ALLOWED_FUNCTIONS = {
    "avg", "cast", "coalesce", "count", "lower", "max", "min",
    "round", "substr", "sum", "upper",
}


def question_to_sql(question: str) -> str:
    normalized = question.strip().casefold()
    if not normalized:
        raise ValueError("Question cannot be empty.")
    if any(word in normalized for word in ("skill", "demanded", "popular", "tech stack")):
        return (
            "SELECT s.name AS skill, COUNT(js.job_id) AS posting_count "
            "FROM skills s JOIN job_skills js ON js.skill_id=s.id "
            "GROUP BY s.id, s.name ORDER BY posting_count DESC LIMIT 10"
        )
    if any(word in normalized for word in ("salary", "pay", "compensation")):
        return (
            "SELECT experience_level, COUNT(*) AS posting_count, "
            "ROUND(AVG(salary_avg), 2) AS average_salary FROM jobs "
            "WHERE salary_avg > 0 GROUP BY experience_level "
            "ORDER BY average_salary DESC LIMIT 10"
        )
    if any(word in normalized for word in ("remote", "onsite", "hybrid", "work mode")):
        return (
            "SELECT work_mode, COUNT(*) AS posting_count, "
            "ROUND(AVG(salary_avg), 2) AS average_salary FROM jobs "
            "GROUP BY work_mode ORDER BY posting_count DESC LIMIT 10"
        )
    if any(word in normalized for word in ("city", "cities", "location", "where")):
        return (
            "SELECT city, country, COUNT(*) AS posting_count, "
            "ROUND(AVG(salary_avg), 2) AS average_salary FROM jobs "
            "WHERE city IS NOT NULL GROUP BY city, country "
            "ORDER BY posting_count DESC LIMIT 10"
        )
    if any(word in normalized for word in ("job", "posting", "hiring", "engineer", "analyst")):
        return (
            "SELECT title, company, city, work_mode, salary_avg, date_posted "
            "FROM jobs ORDER BY date_posted DESC LIMIT 10"
        )
    raise ValueError("I could not map that question to a supported job-market query.")


def validate_readonly_sql(sql: str, max_rows: int = MAX_ROWS) -> str:
    if not isinstance(sql, str) or not sql.strip():
        raise ValueError("SQL query cannot be empty.")
    if max_rows < 1 or max_rows > MAX_ROWS:
        raise ValueError(f"Result limit must be between 1 and {MAX_ROWS}.")
    query = sql.strip()
    if "--" in query or "/*" in query or "*/" in query:
        raise ValueError("SQL comments are not allowed.")
    if query.endswith(";"):
        query = query[:-1].rstrip()
    if ";" in query:
        raise ValueError("Only one SQL statement is allowed.")
    tokens = re.findall(r"'(?:''|[^'])*'|\"(?:\"\"|[^\"])*\"|[A-Za-z_][A-Za-z_0-9]*", query)
    words = {
        token.upper() for token in tokens
        if not token.startswith(("'", '"'))
    }
    if words.intersection(FORBIDDEN_WORDS):
        raise ValueError("Only read-only SELECT queries are allowed.")
    if not re.match(r"^(SELECT|WITH)\b", query, re.IGNORECASE):
        raise ValueError("Only read-only SELECT queries are allowed.")
    return f"SELECT * FROM ({query}) AS readonly_result LIMIT {max_rows}"


def execute_readonly_sql(
    sql: str,
    database_path: Optional[Path] = None,
    max_rows: int = MAX_ROWS,
) -> List[Dict[str, Any]]:
    path = Path(database_path or DB_PATH).resolve()
    safe_query = validate_readonly_sql(sql, max_rows)
    uri = f"file:{path.as_posix()}?mode=ro"
    connection = sqlite3.connect(uri, uri=True)
    connection.row_factory = sqlite3.Row

    def authorize(action: int, arg1: Optional[str], arg2: Optional[str], _db: str, _source: str) -> int:
        if action in (sqlite3.SQLITE_SELECT, sqlite3.SQLITE_RECURSIVE):
            return sqlite3.SQLITE_OK
        if action == sqlite3.SQLITE_READ:
            return sqlite3.SQLITE_OK if (arg1 or "").casefold() in ALLOWED_TABLES else sqlite3.SQLITE_DENY
        if action == sqlite3.SQLITE_FUNCTION:
            function = (arg2 or arg1 or "").casefold()
            return sqlite3.SQLITE_OK if function in ALLOWED_FUNCTIONS else sqlite3.SQLITE_DENY
        return sqlite3.SQLITE_DENY

    try:
        connection.set_authorizer(authorize)
        cursor = connection.execute(safe_query)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        connection.close()


def answer_question(question: str) -> Dict[str, Any]:
    sql = question_to_sql(question)
    rows = execute_readonly_sql(sql)
    answer = (
        f"The query returned {len(rows)} row(s) from the job-market database."
        if rows else "The query completed successfully but found no matching data."
    )
    return {"answer": answer, "sql": sql, "rows": rows}

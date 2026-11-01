import re
from typing import Any, Dict, Iterable, List, Set

from database.db_manager import db
from utils.skill_taxonomy import CANONICAL_SKILLS, SKILL_TAXONOMY


def canonical_skill(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        return ""
    canonical = CANONICAL_SKILLS.get(cleaned.lower())
    if canonical:
        return canonical
    for skills in SKILL_TAXONOMY.values():
        for skill in skills:
            if skill.lower() == cleaned.lower():
                return CANONICAL_SKILLS.get(cleaned.lower(), skill.title())
    return cleaned.title()


def extract_skills(text: str) -> Set[str]:
    if not text:
        return set()
    aliases = set(CANONICAL_SKILLS)
    for skills in SKILL_TAXONOMY.values():
        aliases.update(skill.lower() for skill in skills)
    found = set()
    lowered = text.lower()
    for alias in aliases:
        if re.search(r"(?<![a-z0-9])" + re.escape(alias) + r"(?![a-z0-9])", lowered):
            found.add(canonical_skill(alias))
    return found


def normalize_skills(skills: Iterable[str] = (), resume_text: str = "") -> Set[str]:
    normalized = {canonical_skill(skill) for skill in skills if skill and skill.strip()}
    normalized.update(extract_skills(resume_text))
    return normalized


def load_jobs() -> List[Dict[str, Any]]:
    rows = db.execute_query(
        """
        SELECT j.id, j.title, j.company, j.city, j.country, j.work_mode,
               j.experience_level, j.salary_min, j.salary_max, j.salary_avg,
               j.date_posted, j.description, s.name AS skill
        FROM jobs j
        LEFT JOIN job_skills js ON js.job_id = j.id
        LEFT JOIN skills s ON s.id = js.skill_id
        ORDER BY j.id
        """
    )
    grouped: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        job_id = str(row["id"])
        if job_id not in grouped:
            grouped[job_id] = {key: value for key, value in row.items() if key != "skill"}
            grouped[job_id]["skills"] = []
        if row.get("skill"):
            grouped[job_id]["skills"].append(canonical_skill(row["skill"]))
    return list(grouped.values())

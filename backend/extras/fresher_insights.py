import re
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Sequence

from backend.extras._data import load_jobs


FRESHER_LEVELS = {"entry", "intern", "internship", "junior", "graduate"}
SENIOR_LEVELS = {"senior", "lead", "executive", "staff", "principal"}


def get_fresher_insights(
    jobs: Optional[Sequence[Dict[str, Any]]] = None,
    top_n: int = 10,
) -> Dict[str, Any]:
    if top_n < 1 or top_n > 50:
        raise ValueError("top_n must be between 1 and 50.")
    postings = list(jobs if jobs is not None else load_jobs())
    fresher_jobs = [
        job for job in postings
        if str(job.get("experience_level") or "").strip().casefold() in FRESHER_LEVELS
        or re.search(r"\b(intern|internship|junior|graduate|entry[- ]level)\b",
                     str(job.get("title") or ""), re.IGNORECASE)
    ]
    senior_jobs = [
        job for job in postings
        if str(job.get("experience_level") or "").strip().casefold() in SENIOR_LEVELS
    ]
    fresher_skills = Counter(skill for job in fresher_jobs for skill in set(job.get("skills") or []))
    senior_skills = Counter(skill for job in senior_jobs for skill in set(job.get("skills") or []))
    internships: Dict[str, int] = defaultdict(int)
    for job in postings:
        if re.search(r"\b(intern|internship)\b", str(job.get("title") or ""), re.IGNORECASE):
            city = str(job.get("city") or "Unspecified")
            internships[city] += 1

    postings_by_role: Dict[str, int] = Counter()
    skills_by_role: Dict[str, set] = defaultdict(set)
    for job in postings:
        title = str(job.get("title") or "Unspecified")
        postings_by_role[title] += 1
        skills_by_role[title].update(job.get("skills") or [])
    competition = [
        {
            "role": role,
            "posting_count": count,
            "skill_count": len(skills_by_role[role]),
            "postings_per_skill": round(count / len(skills_by_role[role]), 2)
            if skills_by_role[role] else None,
        }
        for role, count in sorted(postings_by_role.items(), key=lambda item: (-item[1], item[0].casefold()))
    ]

    return {
        "fresher_posting_count": len(fresher_jobs),
        "senior_posting_count": len(senior_jobs),
        "fresher_top_skills": [
            {"skill": skill, "posting_count": count}
            for skill, count in fresher_skills.most_common(top_n)
        ],
        "senior_top_skills": [
            {"skill": skill, "posting_count": count}
            for skill, count in senior_skills.most_common(top_n)
        ],
        "internship_by_city": [
            {"city": city, "internship_count": count}
            for city, count in sorted(internships.items(), key=lambda item: (-item[1], item[0].casefold()))
        ],
        "role_competition": competition[:top_n],
        "competition_metric": "Postings per distinct listed skill; this is a demand proxy, not applicant competition.",
    }

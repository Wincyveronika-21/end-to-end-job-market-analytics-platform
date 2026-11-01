from collections import Counter
from typing import Any, Dict, Iterable, List, Optional

from backend.extras._data import load_jobs, normalize_skills


def analyze_skill_gap(
    target_role: str,
    user_skills: Optional[Iterable[str]] = None,
    resume_text: str = "",
    jobs: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    role = target_role.strip()
    if not role:
        raise ValueError("A target role is required.")

    postings = jobs if jobs is not None else load_jobs()
    role_postings = [
        job for job in postings
        if role.casefold() in str(job.get("title", "")).casefold()
    ]
    if not role_postings:
        raise LookupError(f"No job postings found for the target role '{role}'.")

    demand = Counter()
    for job in role_postings:
        demand.update(set(job.get("skills") or []))

    owned = normalize_skills(user_skills or (), resume_text)
    total_demand = sum(demand.values())
    matched_demand = sum(count for skill, count in demand.items() if skill in owned)
    missing = [
        {"skill": skill, "demand_count": count}
        for skill, count in sorted(demand.items(), key=lambda item: (-item[1], item[0].casefold()))
        if skill not in owned
    ]
    return {
        "target_role": role,
        "posting_count": len(role_postings),
        "match_score": round(matched_demand * 100 / total_demand, 1) if total_demand else 0.0,
        "matched_skills": [
            {"skill": skill, "demand_count": demand[skill]}
            for skill in sorted(demand, key=lambda name: (-demand[name], name.casefold()))
            if skill in owned
        ],
        "missing_skills": missing,
        "top_skills_to_learn": missing[:3],
    }

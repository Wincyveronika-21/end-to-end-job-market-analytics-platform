from typing import Any, Dict, Iterable, List, Optional

from backend.extras.skill_gap import analyze_skill_gap


def generate_learning_roadmap(
    target_role: str,
    missing_skills: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
    role = target_role.strip()
    if not role:
        raise ValueError("A target role is required.")
    skills = list(dict.fromkeys(
        skill.strip() for skill in (missing_skills or []) if skill and skill.strip()
    ))
    if missing_skills is None:
        analysis = analyze_skill_gap(target_role=role)
        skills = [item["skill"] for item in analysis["top_skills_to_learn"]]
    if not skills:
        return {
            "target_role": role,
            "duration_months": 3,
            "message": "No missing skills were provided or found for this role.",
            "months": [],
        }

    months: List[Dict[str, Any]] = []
    for month in range(1, 4):
        skill = skills[(month - 1) % len(skills)]
        months.append({
            "month": month,
            "focus_skill": skill,
            "weeks": [
                {"week": 1, "goal": f"Learn the core concepts and vocabulary of {skill}."},
                {"week": 2, "goal": f"Complete guided exercises and practice common {skill} workflows."},
                {"week": 3, "goal": f"Apply {skill} to a small task related to a {role} role."},
                {"week": 4, "goal": f"Build and document a portfolio deliverable using {skill}."},
            ],
        })
    return {
        "target_role": role,
        "duration_months": 3,
        "message": None,
        "months": months,
    }

from collections import defaultdict
from typing import Any, Dict, List, Optional, Sequence

from backend.extras._data import load_jobs
from utils.extras.city_coordinates import CITY_COORDINATES, TIER_2_CITIES


def aggregate_city_opportunities(
    jobs: Optional[Sequence[Dict[str, Any]]] = None,
    remote_only: bool = False,
) -> Dict[str, Any]:
    postings = list(jobs if jobs is not None else load_jobs())
    cities: Dict[tuple, Dict[str, Any]] = {}
    remote_count = 0
    remote_salaries = []
    for job in postings:
        mode = str(job.get("work_mode") or "").strip().casefold()
        is_remote = mode == "remote"
        if is_remote:
            remote_count += 1
            salary = _positive_salary(job.get("salary_avg"))
            if salary is not None:
                remote_salaries.append(salary)
        if remote_only and not is_remote:
            continue
        city = str(job.get("city") or "Unspecified").strip()
        country = str(job.get("country") or "Unspecified").strip()
        key = (city, country)
        aggregate = cities.setdefault(key, {
            "city": city,
            "country": country,
            "job_count": 0,
            "salary_total": 0.0,
            "salary_count": 0,
            "remote_jobs": 0,
            "onsite_jobs": 0,
        })
        aggregate["job_count"] += 1
        aggregate["remote_jobs" if is_remote else "onsite_jobs"] += 1
        salary = _positive_salary(job.get("salary_avg"))
        if salary is not None:
            aggregate["salary_total"] += salary
            aggregate["salary_count"] += 1

    results = []
    for (city, _), aggregate in sorted(cities.items(), key=lambda item: (-item[1]["job_count"], item[0][0].casefold())):
        coordinates = CITY_COORDINATES.get(city.casefold())
        results.append({
            "city": aggregate["city"],
            "country": aggregate["country"],
            "job_count": aggregate["job_count"],
            "average_salary": round(aggregate["salary_total"] / aggregate["salary_count"], 2)
            if aggregate["salary_count"] else None,
            "remote_jobs": aggregate["remote_jobs"],
            "onsite_jobs": aggregate["onsite_jobs"],
            "latitude": coordinates[0] if coordinates else None,
            "longitude": coordinates[1] if coordinates else None,
            "tier": "Tier 2" if city.casefold() in TIER_2_CITIES else "Other",
        })

    return {
        "remote_only": remote_only,
        "remote_job_count": remote_count,
        "remote_average_salary": round(sum(remote_salaries) / len(remote_salaries), 2)
        if remote_salaries else None,
        "cities": results,
    }


def _positive_salary(value: Any) -> Optional[float]:
    try:
        salary = float(value)
    except (TypeError, ValueError):
        return None
    return salary if salary > 0 else None

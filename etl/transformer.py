import re
from typing import Dict, Any, List, Tuple
from utils.skill_taxonomy import SKILL_TAXONOMY, CANONICAL_SKILLS

class JobTransformer:
    """Transforms raw job postings into normalized structure and extracts technical skills."""

    def __init__(self):
        # Build regex patterns for skill matching
        self.skill_patterns = {}
        for category, skills in SKILL_TAXONOMY.items():
            for skill in skills:
                # Use word boundary or exact match
                escaped = re.escape(skill)
                # Handle special terms like C++, C#, .NET
                if skill in ["c++", "c#", ".net"]:
                    pattern = re.compile(r'(?i)(?:\b|(?<=\s))' + escaped + r'(?:\b|(?=\s))')
                else:
                    pattern = re.compile(r'\b' + escaped + r'\b', re.IGNORECASE)
                self.skill_patterns[skill] = pattern

    def extract_skills(self, text: str) -> List[str]:
        """Extracts unique canonical skill names from title and job description."""
        if not text:
            return []
        
        found_skills = set()
        for skill_term, pattern in self.skill_patterns.items():
            if pattern.search(text):
                canonical = CANONICAL_SKILLS.get(skill_term.lower(), skill_term.title())
                found_skills.add(canonical)

        return sorted(list(found_skills))

    def detect_work_mode(self, location: str, title: str, description: str) -> str:
        """Determines if a job is Remote, Onsite, or Hybrid."""
        text = f"{location} {title} {description}".lower()
        if "remote" in text or "work from home" in text or "telecommute" in text:
            if "hybrid" in text:
                return "Hybrid"
            return "Remote"
        elif "hybrid" in text:
            return "Hybrid"
        return "Onsite"

    def normalize_salary(self, salary_min: float, salary_max: float, salary_str: str = "") -> Tuple[float, float, float]:
        """Standardizes salary into annual USD values."""
        min_sal = float(salary_min) if salary_min else 0.0
        max_sal = float(salary_max) if salary_max else 0.0

        # If min > max, swap them
        if min_sal > max_sal and max_sal > 0:
            min_sal, max_sal = max_sal, min_sal

        # If only min or only max present
        if min_sal > 0 and max_sal == 0:
            max_sal = min_sal * 1.25
        elif max_sal > 0 and min_sal == 0:
            min_sal = max_sal * 0.75

        # Check for hourly rates (e.g. $45 - $65/hr)
        if 0 < min_sal < 250:
            min_sal = min_sal * 2080  # 40 hrs * 52 weeks
            max_sal = max_sal * 2080

        avg_sal = round((min_sal + max_sal) / 2.0, 2) if (min_sal or max_sal) else 0.0
        return round(min_sal, 2), round(max_sal, 2), avg_sal

    def transform_job(self, raw_job: Dict[str, Any], source_name: str = "API") -> Tuple[Dict[str, Any], List[str]]:
        """Transforms a raw job payload into database schema format."""
        job_id = str(raw_job.get("id") or raw_job.get("slug") or raw_job.get("job_id") or hash(raw_job.get("url", "")))
        title = raw_job.get("title") or raw_job.get("jobTitle") or "Software Engineering Specialist"
        company = raw_job.get("company_name") or raw_job.get("company") or "Tech Organization"
        location = raw_job.get("candidate_required_location") or raw_job.get("location") or "Remote"
        description = raw_job.get("description") or ""

        # Remove HTML tags if present in description
        clean_desc = re.sub(r'<[^>]+>', ' ', description)

        # Detect skills
        combined_text = f"{title} {clean_desc}"
        extracted_skills = self.extract_skills(combined_text)

        # Detect work mode
        work_mode = raw_job.get("work_mode") or self.detect_work_mode(location, title, clean_desc)

        # Extract city and country
        city = raw_job.get("city")
        country = raw_job.get("country")
        if not city:
            if work_mode == "Remote" or "remote" in location.lower():
                city = "Remote"
                country = "Global"
            else:
                parts = [p.strip() for p in location.split(",")]
                city = parts[0] if len(parts) > 0 else "Unspecified"
                country = parts[1] if len(parts) > 1 else "USA"

        # Salary standardization
        sal_min = raw_job.get("salary_min") or raw_job.get("min_salary") or 0.0
        sal_max = raw_job.get("salary_max") or raw_job.get("max_salary") or 0.0
        s_min, s_max, s_avg = self.normalize_salary(sal_min, sal_max)

        processed_job = {
            "id": job_id,
            "title": title.strip(),
            "company": company.strip(),
            "category": raw_job.get("category") or "Engineering & Data",
            "location": location.strip(),
            "city": city,
            "country": country,
            "work_mode": work_mode,
            "experience_level": raw_job.get("experience_level") or "Mid",
            "salary_min": s_min,
            "salary_max": s_max,
            "salary_avg": s_avg,
            "salary_currency": "USD",
            "date_posted": raw_job.get("publication_date") or raw_job.get("date_posted") or "2026-09-10",
            "source": raw_job.get("source") or source_name,
            "url": raw_job.get("url") or "",
            "description": clean_desc.strip()[:2000] # Cap description length
        }

        return processed_job, extracted_skills

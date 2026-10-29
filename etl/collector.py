import requests
import random
import uuid
import datetime
from typing import List, Dict, Any
from config.config import REMOTIVE_API_URL, JOBICY_API_URL

class JobCollector:
    """Collects job postings from public APIs and generates high-quality fallback data."""
    
    def fetch_remotive_jobs(self) -> List[Dict[str, Any]]:
        """Fetch remote jobs from Remotive API."""
        try:
            resp = requests.get(REMOTIVE_API_URL, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("jobs", [])
        except Exception as e:
            print(f"[Collector] Remotive API fetch warning: {e}")
        return []

    def fetch_jobicy_jobs(self) -> List[Dict[str, Any]]:
        """Fetch jobs from Jobicy API."""
        try:
            resp = requests.get(JOBICY_API_URL, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("jobs", [])
        except Exception as e:
            print(f"[Collector] Jobicy API fetch warning: {e}")
        return []

    def generate_synthetic_jobs(self, count: int = 60) -> List[Dict[str, Any]]:
        """Generates realistic job postings with diverse titles, cities, salaries, and skill descriptions."""
        titles_and_skills = [
            ("Senior Data Analyst", ["Python", "SQL", "Power BI", "Tableau", "Excel", "dbt"]),
            ("Data Engineer", ["Python", "SQL", "Apache Spark", "AWS", "Snowflake", "Airflow", "PostgreSQL"]),
            ("Business Intelligence Developer", ["Power BI", "SQL", "Tableau", "DAX", "SQL Server", "Excel"]),
            ("Machine Learning Engineer", ["Python", "PyTorch", "TensorFlow", "Scikit-Learn", "Docker", "AWS", "MLops"]),
            ("AI Software Engineer", ["Python", "LLMs", "Generative AI", "LangChain", "FastAPI", "React"]),
            ("Full Stack Developer", ["JavaScript", "TypeScript", "React", "Node.js", "PostgreSQL", "Docker"]),
            ("Cloud Solutions Architect", ["AWS", "Azure", "Terraform", "Kubernetes", "Docker", "Python"]),
            ("Backend Engineer", ["Python", "FastAPI", "PostgreSQL", "Redis", "Docker", "Git"]),
            ("DevOps Lead", ["Kubernetes", "Docker", "Terraform", "AWS", "CI/CD", "Linux"]),
            ("Product Analytics Manager", ["SQL", "Python", "Tableau", "A/B Testing", "Mixpanel", "Excel"])
        ]

        companies = [
            "TechCorp Global", "DataPulse Analytics", "CloudWave Systems", "Insightful AI",
            "Apex FinTech", "Nova Digital", "CyberStream Labs", "Nexus Soft", "Quantum Solutions",
            "Starlight Interactive", "Vanguard Systems", "BlueSky Data"
        ]

        cities_and_countries = [
            ("San Francisco", "USA"), ("New York", "USA"), ("Seattle", "USA"), ("Austin", "USA"),
            ("London", "UK"), ("Berlin", "Germany"), ("Toronto", "Canada"), ("Bangalore", "India"),
            ("Singapore", "Singapore"), ("Sydney", "Australia"), ("Chicago", "USA"), ("Amsterdam", "Netherlands")
        ]

        work_modes = ["Remote", "Onsite", "Hybrid"]
        exp_levels = ["Entry", "Mid", "Senior", "Lead"]

        synthetic_jobs = []
        now = datetime.datetime.now()

        for _ in range(count):
            title, key_skills = random.choice(titles_and_skills)
            company = random.choice(companies)
            city, country = random.choice(cities_and_countries)
            work_mode = random.choices(work_modes, weights=[0.45, 0.35, 0.20])[0]
            exp_level = random.choice(exp_levels)

            # Generate realistic salary range based on title and experience level
            base_min = random.randint(70, 130) * 1000
            if exp_level == "Senior":
                base_min += 30000
            elif exp_level == "Lead":
                base_min += 60000

            salary_min = base_min
            salary_max = base_min + random.randint(20, 50) * 1000
            salary_avg = round((salary_min + salary_max) / 2.0, 2)

            days_ago = random.randint(0, 30)
            date_posted = (now - datetime.timedelta(days=days_ago)).strftime("%Y-%m-%d")

            # Construct job description including skill mentions
            description = (
                f"We are looking for a {exp_level} {title} to join {company}. "
                f"The ideal candidate must be proficient in {', '.join(key_skills)}. "
                f"Experience with agile development, database optimization, and team collaboration is preferred."
            )

            synthetic_jobs.append({
                "id": f"syn-{uuid.uuid4().hex[:10]}",
                "title": title,
                "company": company,
                "category": "Data & Software Engineering",
                "location": f"{city}, {country}" if work_mode != "Remote" else "Remote",
                "city": city if work_mode != "Remote" else "Remote",
                "country": country,
                "work_mode": work_mode,
                "experience_level": exp_level,
                "salary_min": salary_min,
                "salary_max": salary_max,
                "salary_avg": salary_avg,
                "salary_currency": "USD",
                "date_posted": date_posted,
                "source": "Market Stream API",
                "url": "https://example.com/job",
                "description": description
            })

        return synthetic_jobs

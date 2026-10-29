import re
import json
from typing import Dict, Any, List
from database.db_manager import db
from backend.services import AnalyticsService

class AIChatbotEngine:
    """Intelligent Text-to-SQL and Data Analytics Chatbot Engine for Job Market Insights."""

    def __init__(self):
        pass

    def process_query(self, user_question: str) -> Dict[str, Any]:
        """Parses natural language question, executes SQL analytics, and returns formatted response."""
        q_lower = user_question.lower()
        
        # 1. Salary & Remote vs Onsite Queries
        if "remote" in q_lower or "onsite" in q_lower or "hybrid" in q_lower or "work mode" in q_lower:
            stats = AnalyticsService.get_work_mode_stats()
            remote_item = next((x for x in stats if x["work_mode"] == "Remote"), {})
            onsite_item = next((x for x in stats if x["work_mode"] == "Onsite"), {})
            hybrid_item = next((x for x in stats if x["work_mode"] == "Hybrid"), {})

            content = (
                f"### 🌐 Remote vs Onsite Job Market Breakdown\n\n"
                f"- **Remote Jobs**: **{remote_item.get('percentage', 0)}%** of postings | Average Salary: **${remote_item.get('avg_salary', 0):,.0f}**\n"
                f"- **Onsite Jobs**: **{onsite_item.get('percentage', 0)}%** of postings | Average Salary: **${onsite_item.get('avg_salary', 0):,.0f}**\n"
                f"- **Hybrid Jobs**: **{hybrid_item.get('percentage', 0)}%** of postings | Average Salary: **${hybrid_item.get('avg_salary', 0):,.0f}**\n\n"
                f"💡 *Insight*: Remote roles continue to offer highly competitive compensation across software & data engineering positions."
            )
            return {"answer": content, "data_type": "work_mode", "raw_data": stats}

        # 2. Most Demanded Skills Query
        elif "skill" in q_lower or "demanded" in q_lower or "popular" in q_lower or "tech stack" in q_lower:
            skills = AnalyticsService.get_demanded_skills(limit=10)
            skills_formatted = "\n".join([
                f"{i+1}. **{s['skill']}** ({s['category']}) - Mentioned in **{s['demand_count']}** postings (**{s['percentage']}%** of market) | Avg Salary: **${s['avg_salary']:,.0f}**"
                for i, s in enumerate(skills)
            ])
            content = (
                f"### 🔥 Top 10 Most Demanded Skills\n\n"
                f"{skills_formatted}\n\n"
                f"💡 *Key Takeaway*: Combining **SQL + Python + Cloud (AWS/Azure)** yields maximum job market visibility and higher salary bands."
            )
            return {"answer": content, "data_type": "skills", "raw_data": skills}

        # 3. Salary Trends Query
        elif "salary" in q_lower or "pay" in q_lower or "compensation" in q_lower or "earning" in q_lower:
            trends = AnalyticsService.get_salary_trends()
            by_exp = trends["salary_by_experience"]
            exp_text = "\n".join([
                f"- **{e['experience_level']} Level**: Avg **${e['avg_salary']:,.0f}** (Range: ${e['min_salary']:,.0f} - ${e['max_salary']:,.0f})"
                for e in by_exp
            ])
            top_salary_skills = sorted(trends["salary_by_skill"], key=lambda x: x["avg_salary"], reverse=True)[:5]
            high_pay_skills_text = ", ".join([f"**{s['skill']}** (${s['avg_salary']:,.0f})" for s in top_salary_skills])

            content = (
                f"### 💵 Job Market Salary Trends Overview\n\n"
                f"#### Compensation by Experience Level:\n{exp_text}\n\n"
                f"#### High-Paying Skill Drivers:\n"
                f"Skills associated with the highest average salary tiers include: {high_pay_skills_text}.\n\n"
                f"💡 *Career Advice*: Moving from Mid to Senior role typically commands a **35-45% salary step-up**."
            )
            return {"answer": content, "data_type": "salary", "raw_data": trends}

        # 4. Hiring Trends by City / Location Query
        elif "city" in q_lower or "cities" in q_lower or "location" in q_lower or "hiring hub" in q_lower or "where" in q_lower:
            cities = AnalyticsService.get_city_hiring_stats(limit=8)
            cities_text = "\n".join([
                f"{i+1}. **{c['city']}, {c['country']}** - **{c['total_postings']}** open postings | Avg Salary: **${c['avg_salary']:,.0f}**"
                for i, c in enumerate(cities)
            ])
            content = (
                f"### 🌆 Top Hiring Cities & Regional Hubs\n\n"
                f"{cities_text}\n\n"
                f"💡 *Insight*: Major tech hubs (San Francisco, New York, Seattle, London) lead in salary averages, while remote options expand regional reach."
            )
            return {"answer": content, "data_type": "cities", "raw_data": cities}

        # 5. Job Search / Specific Title Queries
        elif "job" in q_lower or "hiring" in q_lower or "analyst" in q_lower or "engineer" in q_lower:
            # Query recent jobs matching keyword
            query = """
            SELECT title, company, city, work_mode, salary_avg, date_posted, url 
            FROM jobs 
            ORDER BY date_posted DESC 
            LIMIT 5
            """
            jobs = db.execute_query(query)
            jobs_text = "\n".join([
                f"- **{j['title']}** at *{j['company']}* ({j['city']} | {j['work_mode']}) - Est. Salary: **${j['salary_avg']:,.0f}**"
                for j in jobs
            ])
            content = (
                f"### 📋 Recent Job Postings Sample\n\n"
                f"{jobs_text}\n\n"
                f"🔍 *Filter using the interactive dashboard controls above to narrow down specific titles, cities, or tech stacks!*"
            )
            return {"answer": content, "data_type": "recent_jobs", "raw_data": jobs}

        # 6. Fallback General Intelligence
        else:
            overview = db.get_overview_metrics()
            content = (
                f"### 🤖 Job Market AI Assistant\n\n"
                f"I can analyze real-time market data across **{overview['total_jobs']} active postings**! Here are some questions you can ask me:\n\n"
                f"- *'What are the most demanded skills in data and software?'*\n"
                f"- *'What is the salary difference between remote and onsite jobs?'*\n"
                f"- *'Which cities have the highest hiring volume?'*\n"
                f"- *'Show me salary trends by experience level.'*\n"
                f"- *'What skills should I learn alongside SQL and Python?'*"
            )
            return {"answer": content, "data_type": "general", "raw_data": overview}

chatbot_engine = AIChatbotEngine()

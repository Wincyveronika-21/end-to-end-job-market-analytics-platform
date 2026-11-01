from backend.extras.fresher_insights import get_fresher_insights


def test_fresher_insights_separates_levels_and_finds_internships():
    jobs = [
        {
            "title": "Data Analyst Intern",
            "experience_level": "Entry",
            "city": "Pune",
            "skills": ["Python", "SQL"],
        },
        {
            "title": "Senior Data Analyst",
            "experience_level": "Senior",
            "city": "Pune",
            "skills": ["SQL", "Cloud"],
        },
    ]

    result = get_fresher_insights(jobs=jobs)

    assert result["fresher_posting_count"] == 1
    assert result["senior_posting_count"] == 1
    assert result["internship_by_city"] == [{"city": "Pune", "internship_count": 1}]
    assert result["role_competition"][0]["postings_per_skill"] == 0.5

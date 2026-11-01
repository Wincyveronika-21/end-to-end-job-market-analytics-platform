from backend.extras.city_opportunities import aggregate_city_opportunities


def test_city_aggregation_includes_salary_and_remote_counts():
    jobs = [
        {"city": "Pune", "country": "India", "work_mode": "Onsite", "salary_avg": 100000},
        {"city": "Pune", "country": "India", "work_mode": "Remote", "salary_avg": 120000},
        {"city": "Remote", "country": "Global", "work_mode": "Remote", "salary_avg": 0},
    ]

    result = aggregate_city_opportunities(jobs=jobs)

    assert result["remote_job_count"] == 2
    assert result["remote_average_salary"] == 120000
    assert result["cities"][0]["city"] == "Pune"
    assert result["cities"][0]["job_count"] == 2
    assert result["cities"][0]["average_salary"] == 110000
    assert result["cities"][0]["remote_jobs"] == 1
    remote = next(city for city in result["cities"] if city["city"] == "Remote")
    assert remote["remote_jobs"] == 1
    assert remote["average_salary"] is None


def test_remote_filter_keeps_remote_jobs_assigned_to_a_city():
    jobs = [
        {"city": "Pune", "country": "India", "work_mode": "Onsite", "salary_avg": 100000},
        {"city": "Pune", "country": "India", "work_mode": "Remote", "salary_avg": 120000},
    ]

    result = aggregate_city_opportunities(jobs=jobs, remote_only=True)

    assert result["cities"][0]["job_count"] == 1
    assert result["cities"][0]["remote_jobs"] == 1

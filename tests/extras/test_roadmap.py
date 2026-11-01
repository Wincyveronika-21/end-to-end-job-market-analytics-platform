from chatbot.extras.roadmap import generate_learning_roadmap


def test_roadmap_has_three_months_and_four_weekly_goals():
    result = generate_learning_roadmap("Data Analyst", ["SQL", "Python"])

    assert result["duration_months"] == 3
    assert [month["month"] for month in result["months"]] == [1, 2, 3]
    assert all(len(month["weeks"]) == 4 for month in result["months"])


def test_roadmap_reports_no_missing_skills():
    result = generate_learning_roadmap("Data Analyst", [])

    assert result["months"] == []
    assert result["message"]

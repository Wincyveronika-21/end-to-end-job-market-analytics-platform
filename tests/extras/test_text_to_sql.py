import sqlite3

import pytest

from chatbot.extras.text_to_sql import execute_readonly_sql, validate_readonly_sql


@pytest.mark.parametrize(
    "query",
    [
        "DROP TABLE jobs",
        "DELETE FROM jobs",
        "UPDATE jobs SET title='x'",
        "INSERT INTO jobs VALUES ('x')",
        "SELECT 1; DELETE FROM jobs",
        "SELECT 1 -- comment",
        "PRAGMA table_info(jobs)",
    ],
)
def test_non_readonly_or_multi_statement_sql_is_rejected(query):
    with pytest.raises(ValueError):
        validate_readonly_sql(query)


def test_select_gets_a_hard_row_limit():
    result = validate_readonly_sql("SELECT 1", max_rows=5)

    assert result.endswith("LIMIT 5")


def test_execution_uses_readonly_database_and_allowlisted_tables(tmp_path):
    path = tmp_path / "jobs.db"
    connection = sqlite3.connect(path)
    connection.execute("CREATE TABLE jobs (title TEXT)")
    connection.executemany("INSERT INTO jobs VALUES (?)", [(f"Role {i}",) for i in range(150)])
    connection.commit()
    connection.close()

    rows = execute_readonly_sql("SELECT title FROM jobs", database_path=path)

    assert len(rows) == 100
    with pytest.raises(sqlite3.DatabaseError):
        execute_readonly_sql("SELECT name FROM sqlite_master", database_path=path)
    with pytest.raises(ValueError):
        execute_readonly_sql("DELETE FROM jobs", database_path=path)


def test_question_to_sql_rejects_unsupported_questions():
    from chatbot.extras.text_to_sql import question_to_sql

    with pytest.raises(ValueError):
        question_to_sql("Tell me about the weather")

-- SQL Schema for Job Market Analytics Platform

CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    company TEXT,
    category TEXT,
    location TEXT,
    city TEXT,
    country TEXT,
    work_mode TEXT DEFAULT 'Onsite', -- Remote, Onsite, Hybrid
    experience_level TEXT DEFAULT 'Mid', -- Entry, Mid, Senior, Executive
    salary_min REAL,
    salary_max REAL,
    salary_avg REAL,
    salary_currency TEXT DEFAULT 'USD',
    date_posted TEXT,
    source TEXT,
    url TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    category TEXT
);

CREATE TABLE IF NOT EXISTS job_skills (
    job_id TEXT NOT NULL,
    skill_id INTEGER NOT NULL,
    PRIMARY KEY (job_id, skill_id),
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
);

-- Analytical Views for Instant SQL Reporting & Power BI Integration

CREATE VIEW IF NOT EXISTS v_skill_demand AS
SELECT 
    s.name AS skill_name,
    s.category AS skill_category,
    COUNT(js.job_id) AS posting_count,
    ROUND(AVG(j.salary_avg), 2) AS avg_salary
FROM skills s
JOIN job_skills js ON s.id = js.skill_id
JOIN jobs j ON js.job_id = j.id
GROUP BY s.id, s.name, s.category
ORDER BY posting_count DESC;

CREATE VIEW IF NOT EXISTS v_work_mode_stats AS
SELECT 
    work_mode,
    COUNT(*) AS total_jobs,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM jobs), 2) AS percentage,
    ROUND(AVG(salary_avg), 2) AS avg_salary,
    ROUND(MIN(salary_avg), 2) AS min_salary,
    ROUND(MAX(salary_avg), 2) AS max_salary
FROM jobs
GROUP BY work_mode;

CREATE VIEW IF NOT EXISTS v_city_hiring_stats AS
SELECT 
    COALESCE(city, 'Remote / Unspecified') AS city,
    COALESCE(country, 'Global') AS country,
    COUNT(*) AS total_postings,
    ROUND(AVG(salary_avg), 2) AS avg_salary
FROM jobs
GROUP BY city, country
ORDER BY total_postings DESC;

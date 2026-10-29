# Power BI Integration & Star Schema Guide

This document provides step-by-step instructions for integrating the **Job Market Analytics Platform** dataset into **Microsoft Power BI Desktop**, creating DAX measures, and designing interactive Power BI dashboards.

---

## 1. Connecting Power BI to the Dataset

You can import data into Power BI in two seamless ways:

### Option A: Using the Automated REST Export (Recommended)
1. Start the platform backend server (`python -m api.main` or `uvicorn api.main:app`).
2. In **Power BI Desktop**, click **Get Data** -> **Web**.
3. Enter the URL: `http://127.0.0.1:8000/api/export/csv`
4. Click **OK** -> **Load** to import the real-time dataset into Power BI.

### Option B: Connecting Directly to the SQLite Database
1. Install the SQLite ODBC Driver on your system.
2. In Power BI Desktop, click **Get Data** -> **ODBC**.
3. Select your SQLite DSN pointing to `data/job_market.db`.
4. Import the following tables and views:
   - `jobs` (Fact Table)
   - `skills` (Dimension Table)
   - `job_skills` (Bridge / Link Table)
   - `v_skill_demand`
   - `v_work_mode_stats`
   - `v_city_hiring_stats`

---

## 2. Data Modeling & Star Schema

In Power BI **Model View**, structure the relationships as follows:

```
        ┌─────────────────────────┐
        │   skills (Dimension)    │
        │   - id                  │
        │   - name                │
        │   - category            │
        └────────────┬────────────┘
                     │ (1)
                     │
                     │ (*)
        ┌────────────┴────────────┐
        │       job_skills        │
        │      (Bridge Table)     │
        └────────────┬────────────┘
                     │ (*)
                     │
                     │ (1)
        ┌────────────┴────────────┐
        │      jobs (Fact)        │
        │   - id                  │
        │   - title               │
        │   - company             │
        │   - work_mode           │
        │   - city                │
        │   - salary_avg          │
        │   - date_posted         │
        └─────────────────────────┘
```

---

## 3. Essential DAX Measures

Create a new Measure Table in Power BI and add the following DAX expressions:

### Total Job Openings
```dax
Total Jobs = COUNTROWS(jobs)
```

### Average Salary (USD)
```dax
Avg Salary USD = AVERAGE(jobs[salary_avg])
```

### Median Salary (USD)
```dax
Median Salary USD = MEDIAN(jobs[salary_avg])
```

### Remote Jobs Count & Percentage
```dax
Remote Jobs Count = CALCULATE(COUNTROWS(jobs), jobs[work_mode] = "Remote")

Remote Job Share % = DIVIDE([Remote Jobs Count], [Total Jobs], 0)
```

### Skill Demand Ratio
```dax
Skill Demand Share % = DIVIDE(COUNTROWS(job_skills), CALCULATE(COUNTROWS(job_skills), ALL(skills)), 0)
```

---

## 4. Visual Layout Recommendations for Power BI

1. **KPI Card Header**:
   - Card 1: `[Total Jobs]`
   - Card 2: `[Avg Salary USD]` (Format as Currency `$#,##0`)
   - Card 3: `[Remote Job Share %]` (Format as Percentage `0.0%`)

2. **Most Demanded Skills (Horizontal Bar Chart)**:
   - **Y-Axis**: `skills[name]`
   - **X-Axis**: `[Total Jobs]` or `Skill Demand Share %`
   - **Legend**: `skills[category]`

3. **Salary Distribution by Skill & Experience (Clustered Column Chart)**:
   - **X-Axis**: `skills[name]`
   - **Y-Axis**: `[Avg Salary USD]`
   - **Legend**: `jobs[experience_level]`

4. **Work Mode Distribution (Donut Chart)**:
   - **Legend**: `jobs[work_mode]`
   - **Values**: `[Total Jobs]`

5. **Top Hiring Cities (Map or Bar Chart)**:
   - **Location**: `jobs[city]`
   - **Size / Values**: `[Total Jobs]`

---

## 5. Scheduled Data Refresh in Power BI Service

If publishing to Power BI Service:
1. Configure an **On-Premises Data Gateway** (Personal Mode or Standard).
2. Set up scheduled dataset refresh (e.g. Daily or Hourly) to sync automatically with the Python ingestion pipeline!

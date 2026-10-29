from typing import Dict, Any
from etl.collector import JobCollector
from etl.transformer import JobTransformer
from database.db_manager import db

class ETLPipeline:
    """Orchestrates end-to-end ingestion pipeline."""

    def __init__(self):
        self.collector = JobCollector()
        self.transformer = JobTransformer()

    def run_pipeline(self, include_synthetic: bool = True, synthetic_count: int = 80) -> Dict[str, Any]:
        """Runs ingestion pipeline fetching from APIs and database insertion."""
        print("[ETL Pipeline] Starting Job Market Data Collection...")
        raw_jobs = []

        # 1. Fetch Remotive API
        remotive_jobs = self.collector.fetch_remotive_jobs()
        print(f"[ETL Pipeline] Fetched {len(remotive_jobs)} postings from Remotive API.")
        for rj in remotive_jobs:
            raw_jobs.append((rj, "Remotive API"))

        # 2. Fetch Jobicy API
        jobicy_jobs = self.collector.fetch_jobicy_jobs()
        print(f"[ETL Pipeline] Fetched {len(jobicy_jobs)} postings from Jobicy API.")
        for jj in jobicy_jobs:
            raw_jobs.append((jj, "Jobicy API"))

        # 3. Add Synthetic Jobs if requested or if APIs yielded low count
        if include_synthetic or len(raw_jobs) < 20:
            synthetic_jobs = self.collector.generate_synthetic_jobs(count=synthetic_count)
            print(f"[ETL Pipeline] Generated {len(synthetic_jobs)} market stream synthetic postings.")
            for sj in synthetic_jobs:
                raw_jobs.append((sj, "Market Stream API"))

        # 4. Transform and Insert into SQL DB
        processed_count = 0
        total_skills_extracted = 0

        for raw_job, source in raw_jobs:
            try:
                processed_job, skills = self.transformer.transform_job(raw_job, source_name=source)
                db.insert_job(processed_job, skills)
                processed_count += 1
                total_skills_extracted += len(skills)
            except Exception as e:
                print(f"[ETL Pipeline] Error transforming job: {e}")

        print(f"[ETL Pipeline] Pipeline completed successfully! Inserted/Updated {processed_count} jobs and extracted {total_skills_extracted} skill tags.")
        
        overview = db.get_overview_metrics()
        return {
            "status": "success",
            "jobs_ingested": processed_count,
            "skills_extracted": total_skills_extracted,
            "overview_metrics": overview
        }

if __name__ == "__main__":
    pipeline = ETLPipeline()
    pipeline.run_pipeline()

import time
import threading
from etl.pipeline import ETLPipeline

class DataScheduler:
    """Runs data ingestion periodically in a background thread."""

    def __init__(self, interval_seconds: int = 3600):
        self.interval_seconds = interval_seconds
        self.pipeline = ETLPipeline()
        self.running = False
        self.thread = None

    def _run_loop(self):
        while self.running:
            try:
                print(f"[Scheduler] Triggering periodic job ingestion...")
                self.pipeline.run_pipeline(include_synthetic=True, synthetic_count=20)
            except Exception as e:
                print(f"[Scheduler] Ingestion loop error: {e}")
            time.sleep(self.interval_seconds)

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()
            print(f"[Scheduler] Background scheduler started (interval: {self.interval_seconds}s).")

    def stop(self):
        self.running = False
        print("[Scheduler] Background scheduler stopped.")

scheduler = DataScheduler(interval_seconds=1800) # Every 30 mins

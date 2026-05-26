"""Persistent job queue with states and resume support."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
import hashlib

JOB_STATES = ("pending", "running", "completed", "failed", "paused")

@dataclass
class Job:
    job_id: str
    kind: str  # "organize", "duplicates", "people_scan", etc.
    state: str  # one of JOB_STATES
    params: dict[str, Any]
    created_at: float
    started_at: float | None = None
    completed_at: float | None = None
    progress: int = 0
    progress_total: int = 0
    checkpoint_path: str | None = None
    result: dict[str, Any] | None = None
    error: str | None = None

class JobQueue:
    def __init__(self, storage_dir: Path | None = None):
        if storage_dir is None:
            import os
            storage_dir = Path(os.environ.get("MEDIA_MANAGER_HOME", Path.home() / ".media-manager")) / "jobs"
        self._dir = storage_dir
        self._dir.mkdir(parents=True, exist_ok=True)
    
    def _job_path(self, job_id: str) -> Path:
        return self._dir / f"{job_id}.json"
    
    def _hash_params(self, params: dict) -> str:
        """Hash parameters to detect duplicate jobs."""
        raw = json.dumps(params, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
    
    def create(self, kind: str, params: dict) -> Job:
        """Create a new job. Returns existing job if identical params already queued."""
        param_hash = self._hash_params(params)
        job_id = f"{kind}_{param_hash}_{int(time.time())}"
        
        # Check for identical pending job
        for existing in self.list(state="pending"):
            if existing.kind == kind and self._hash_params(existing.params) == param_hash:
                return existing  # Already queued, don't duplicate
        
        job = Job(
            job_id=job_id,
            kind=kind,
            state="pending",
            params=params,
            created_at=time.time(),
        )
        self._save(job)
        return job
    
    def start(self, job_id: str) -> Job | None:
        job = self.get(job_id)
        if job and job.state == "pending":
            job.state = "running"
            job.started_at = time.time()
            self._save(job)
        return job
    
    def update_progress(self, job_id: str, progress: int, total: int):
        job = self.get(job_id)
        if job:
            job.progress = progress
            job.progress_total = total
            self._save(job)
    
    def complete(self, job_id: str, result: dict | None = None):
        job = self.get(job_id)
        if job:
            job.state = "completed"
            job.completed_at = time.time()
            job.result = result
            self._save(job)
    
    def fail(self, job_id: str, error: str):
        job = self.get(job_id)
        if job:
            job.state = "failed"
            job.completed_at = time.time()
            job.error = error
            self._save(job)
    
    def pause(self, job_id: str, checkpoint_path: str):
        job = self.get(job_id)
        if job:
            job.state = "paused"
            job.checkpoint_path = checkpoint_path
            self._save(job)
    
    def get(self, job_id: str) -> Job | None:
        path = self._job_path(job_id)
        if path.exists():
            return Job(**json.loads(path.read_text()))
        return None
    
    def list(self, state: str | None = None, kind: str | None = None) -> list[Job]:
        jobs = []
        for path in self._dir.glob("*.json"):
            try:
                job = Job(**json.loads(path.read_text()))
                if state and job.state != state:
                    continue
                if kind and job.kind != kind:
                    continue
                jobs.append(job)
            except Exception:
                pass
        return sorted(jobs, key=lambda j: j.created_at, reverse=True)
    
    def _save(self, job: Job):
        self._job_path(job.job_id).write_text(json.dumps(asdict(job), indent=2))
    
    def has_pending_or_running(self, kind: str, params: dict) -> bool:
        """Check if an identical job is already pending or running."""
        param_hash = self._hash_params(params)
        for job in self.list():
            if job.kind == kind and job.state in ("pending", "running") \
               and self._hash_params(job.params) == param_hash:
                return True
        return False

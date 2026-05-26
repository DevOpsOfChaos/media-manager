from __future__ import annotations

from pathlib import Path

from media_manager.core.job_queue import JobQueue


def test_create_and_get(tmp_path: Path) -> None:
    q = JobQueue(storage_dir=tmp_path / "jobs")
    job = q.create("organize", {"source": "/tmp"})
    assert job.state == "pending"
    retrieved = q.get(job.job_id)
    assert retrieved is not None
    assert retrieved.kind == "organize"


def test_dedup(tmp_path: Path) -> None:
    q = JobQueue(storage_dir=tmp_path / "jobs")
    j1 = q.create("organize", {"source": "/tmp"})
    j2 = q.create("organize", {"source": "/tmp"})
    assert j1.job_id == j2.job_id


def test_state_transitions(tmp_path: Path) -> None:
    q = JobQueue(storage_dir=tmp_path / "jobs")
    job = q.create("test", {})
    q.start(job.job_id)
    assert q.get(job.job_id).state == "running"
    q.complete(job.job_id, {"ok": True})
    assert q.get(job.job_id).state == "completed"
    assert q.get(job.job_id).result == {"ok": True}


def test_list_filter(tmp_path: Path) -> None:
    q = JobQueue(storage_dir=tmp_path / "jobs")
    q.create("a", {})
    q.create("b", {})
    pending = q.list(state="pending")
    assert len(pending) == 2
    a_only = q.list(kind="a")
    assert len(a_only) == 1


def test_has_pending(tmp_path: Path) -> None:
    q = JobQueue(storage_dir=tmp_path / "jobs")
    q.create("x", {"key": "val"})
    assert q.has_pending_or_running("x", {"key": "val"})
    assert not q.has_pending_or_running("y", {"key": "val"})


def test_fail(tmp_path: Path) -> None:
    q = JobQueue(storage_dir=tmp_path / "jobs")
    job = q.create("fail_test", {})
    q.start(job.job_id)
    q.fail(job.job_id, "something went wrong")
    retrieved = q.get(job.job_id)
    assert retrieved.state == "failed"
    assert retrieved.error == "something went wrong"


def test_pause(tmp_path: Path) -> None:
    q = JobQueue(storage_dir=tmp_path / "jobs")
    job = q.create("pause_test", {})
    q.start(job.job_id)
    q.pause(job.job_id, "/tmp/checkpoint.json")
    retrieved = q.get(job.job_id)
    assert retrieved.state == "paused"
    assert retrieved.checkpoint_path == "/tmp/checkpoint.json"


def test_update_progress(tmp_path: Path) -> None:
    q = JobQueue(storage_dir=tmp_path / "jobs")
    job = q.create("progress_test", {})
    q.update_progress(job.job_id, 5, 10)
    retrieved = q.get(job.job_id)
    assert retrieved.progress == 5
    assert retrieved.progress_total == 10


def test_list_empty(tmp_path: Path) -> None:
    q = JobQueue(storage_dir=tmp_path / "jobs")
    assert q.list() == []


def test_get_nonexistent(tmp_path: Path) -> None:
    q = JobQueue(storage_dir=tmp_path / "jobs")
    assert q.get("nonexistent") is None


def test_start_non_pending(tmp_path: Path) -> None:
    q = JobQueue(storage_dir=tmp_path / "jobs")
    job = q.create("test", {})
    q.complete(job.job_id)
    result = q.start(job.job_id)
    assert result is not None
    assert result.state == "completed"


def test_env_default_storage(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("MEDIA_MANAGER_HOME", str(tmp_path / "mm_home"))
    q = JobQueue()
    assert q._dir == tmp_path / "mm_home" / "jobs"

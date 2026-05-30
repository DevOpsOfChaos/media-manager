"""Job queue management CLI."""
import argparse
import time
from dataclasses import asdict

from media_manager.core.job_queue import JobQueue


def cmd_jobs(args):
    queue = JobQueue()
    jobs = queue.list(state=args.state, kind=args.kind)
    
    if args.json:
        import json as _json
        print(_json.dumps([asdict(j) for j in jobs], indent=2, default=str))
        return 0
    
    print(f"\n{'ID':<50} {'Kind':<15} {'State':<12} {'Progress':<12} {'Created'}")
    print("-" * 110)
    for job in jobs:
        pct = f"{job.progress}/{job.progress_total}" if job.progress_total else "—"
        print(f"{job.job_id:<50} {job.kind:<15} {job.state:<12} {pct:<12} {time.strftime('%Y-%m-%d %H:%M', time.localtime(job.created_at))}")
    
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media-manager jobs",
        description="Manage job queue.",
        epilog=(
            "Examples:\n"
            "  media-manager jobs\n"
            "  media-manager jobs --state running\n"
            "  media-manager jobs --kind organize --json\n"
        ),
    )
    parser.add_argument("--state", choices=("pending", "running", "completed", "failed", "paused"))
    parser.add_argument("--kind")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return cmd_jobs(args)

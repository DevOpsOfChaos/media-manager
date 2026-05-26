"""Parallel processing utilities that maximize CPU utilization."""
import os
import multiprocessing

def get_optimal_workers() -> int:
    cpu_count = os.cpu_count() or 4
    return max(1, min(int(cpu_count * 0.75), 8))

def get_io_workers() -> int:
    return get_optimal_workers() * 2

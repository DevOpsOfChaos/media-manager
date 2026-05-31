"""Suggest smart albums based on metadata patterns."""

from __future__ import annotations

from collections import Counter
from datetime import datetime


def suggest_albums(files_meta: list[dict]) -> list[dict]:
    """Analyze file metadata and suggest album groupings."""
    suggestions: list[dict] = []

    dates: list[datetime] = []
    for meta in files_meta:
        dt = meta.get("shot", {}).get("datetime")
        if dt:
            try:
                dates.append(datetime.strptime(str(dt)[:10], "%Y:%m:%d"))
            except (ValueError, IndexError):
                pass

    if len(dates) > 10:
        dates.sort()
        clusters: list[list[datetime]] = []
        current = [dates[0]]
        for i in range(1, len(dates)):
            if (dates[i] - dates[i - 1]).days > 7:
                clusters.append(current)
                current = [dates[i]]
            else:
                current.append(dates[i])
        clusters.append(current)

        for cluster in clusters:
            if len(cluster) >= 5:
                suggestions.append({
                    "type": "date_cluster",
                    "name": f"{cluster[0].strftime('%B %Y')} ({len(cluster)} photos)",
                    "start": cluster[0].isoformat(),
                    "end": cluster[-1].isoformat(),
                    "file_count": len(cluster),
                    "confidence": 0.7,
                })

    cameras: Counter[str] = Counter()
    for meta in files_meta:
        cam = meta.get("camera", {}).get("model")
        if cam:
            cameras[str(cam)] += 1

    for cam, count in cameras.most_common(5):
        if count >= 10:
            suggestions.append({
                "type": "camera",
                "name": f"Shot with {cam} ({count} photos)",
                "camera": cam,
                "file_count": count,
                "confidence": 0.8,
            })

    return suggestions

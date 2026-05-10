"""SQLite cache for media file metadata — avoids full rescans on every operation."""

from __future__ import annotations

import os
import sqlite3
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

CACHE_DIR = Path.home() / ".media-manager"
CACHE_DB = CACHE_DIR / "media-cache.db"

IMG_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff", ".tif",
            ".heic", ".raw", ".cr2", ".nef", ".arw", ".dng"}
VID_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".wmv", ".webm", ".mts", ".m2ts"}
MUS_EXTS = {".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"}
ALL_EXTS = IMG_EXTS | VID_EXTS | MUS_EXTS


def _kind(ext: str) -> str:
    if ext in IMG_EXTS:
        return "image"
    if ext in VID_EXTS:
        return "video"
    if ext in MUS_EXTS:
        return "music"
    return "other"


class MediaCache:
    """Thread-safe SQLite cache for media file metadata."""

    def __init__(self, db_path: Path | None = None):
        self._db_path = db_path or CACHE_DB
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._local = threading.local()

    # ── connection management ──

    def _conn(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn") or self._local.conn is None:
            self._local.conn = sqlite3.connect(str(self._db_path))
            self._local.conn.execute("PRAGMA journal_mode=WAL")
            self._local.conn.execute("PRAGMA synchronous=NORMAL")
            self._local.conn.execute("PRAGMA cache_size=-8000")
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    def _ensure_schema(self) -> None:
        self._conn().executescript("""
            CREATE TABLE IF NOT EXISTS media_files (
                path TEXT PRIMARY KEY,
                source_root TEXT NOT NULL,
                relative_path TEXT NOT NULL,
                extension TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                mtime REAL NOT NULL,
                kind TEXT NOT NULL,
                date_taken TEXT,
                date_source TEXT,
                exif_json TEXT,
                last_seen TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_mf_root ON media_files(source_root);
            CREATE INDEX IF NOT EXISTS idx_mf_kind ON media_files(kind);
            CREATE INDEX IF NOT EXISTS idx_mf_date ON media_files(date_taken);
            CREATE INDEX IF NOT EXISTS idx_mf_mtime ON media_files(mtime, source_root);
            CREATE TABLE IF NOT EXISTS cache_meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
        """)

    # ── sync: compare filesystem with cache ──

    def sync(self, source_roots: list[str], *, progress_cb=None, cancel_ev=None) -> dict:
        """Walk source directories and update cache. Returns change summary."""
        self._ensure_schema()
        conn = self._conn()
        now = datetime.now(timezone.utc).isoformat()

        total_files = 0
        new_files = 0
        changed_files = 0
        deleted_files = 0

        # Load existing cache for these roots
        placeholders = ",".join("?" for _ in source_roots)
        cached: dict[str, tuple[int, float]] = {}
        for row in conn.execute(
            f"SELECT path, size_bytes, mtime FROM media_files WHERE source_root IN ({placeholders})",
            source_roots,
        ):
            cached[row[0]] = (row[1], row[2])

        cached_paths = set(cached.keys())
        seen_paths: set[str] = set()
        inserts: list[tuple] = []
        updates: list[tuple] = []

        for source_root in source_roots:
            root = Path(source_root)
            if not root.exists():
                continue
            for dirpath, dirnames, filenames in os.walk(root):
                if cancel_ev and cancel_ev.is_set():
                    break
                dirnames[:] = [d for d in dirnames if not d.startswith(".")]
                for fname in filenames:
                    ext = os.path.splitext(fname)[1].lower()
                    if ext not in ALL_EXTS:
                        continue
                    full = os.path.join(dirpath, fname)
                    full_norm = os.path.normcase(full)
                    seen_paths.add(full_norm)
                    total_files += 1

                    try:
                        st = os.stat(full)
                    except OSError:
                        continue

                    if full_norm in cached:
                        prev_size, prev_mtime = cached[full_norm]
                        if st.st_size == prev_size and abs(st.st_mtime - prev_mtime) < 1.0:
                            continue  # unchanged
                        changed_files += 1
                    else:
                        new_files += 1

                    rel = os.path.relpath(full, source_root).replace("\\", "/")
                    inserts.append((
                        full_norm, source_root, rel, ext, st.st_size, st.st_mtime,
                        _kind(ext), None, None, None, now,
                    ))

        # Remove deleted files
        deleted = cached_paths - seen_paths
        deleted_files = len(deleted)
        if deleted:
            batch = list(deleted)
            for i in range(0, len(batch), 500):
                chunk = batch[i:i + 500]
                placeholders = ",".join("?" for _ in chunk)
                conn.execute(f"DELETE FROM media_files WHERE path IN ({placeholders})", chunk)

        # Batch insert/update new and changed files
        if inserts:
            conn.executemany(
                "INSERT OR REPLACE INTO media_files(path, source_root, relative_path, extension, size_bytes, mtime, kind, date_taken, date_source, exif_json, last_seen) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                inserts,
            )

        conn.commit()
        return {
            "total": total_files,
            "new": new_files,
            "changed": changed_files,
            "deleted": deleted_files,
            "unchanged": total_files - new_files - changed_files,
        }

    # ── stats ──

    def get_stats(self, source_roots: list[str]) -> dict[str, int]:
        """Return counts by kind for the given source roots."""
        self._ensure_schema()
        conn = self._conn()
        placeholders = ",".join("?" for _ in source_roots)
        stats = {"images": 0, "videos": 0, "music": 0, "subdirs": 0, "total": 0}
        for row in conn.execute(
            f"SELECT kind, COUNT(*) as cnt FROM media_files WHERE source_root IN ({placeholders}) GROUP BY kind",
            source_roots,
        ):
            kind = row[0]
            cnt = row[1]
            stats["total"] += cnt
            if kind == "image":
                stats["images"] = cnt
            elif kind == "video":
                stats["videos"] = cnt
            elif kind == "music":
                stats["music"] = cnt
        # Subdir count: distinct top-level dirs from relative_path
        if source_roots:
            row = conn.execute(
                f"SELECT COUNT(DISTINCT CASE WHEN instr(replace(relative_path, '\\', '/'), '/') > 0 THEN substr(replace(relative_path, '\\', '/'), 1, instr(replace(relative_path, '\\', '/'), '/') - 1) ELSE relative_path END) FROM media_files WHERE source_root IN ({placeholders})",
                source_roots,
            ).fetchone()
            stats["subdirs"] = row[0] if row else 0
        return stats

    # ── date resolution cache ──

    def get_unresolved(self, source_roots: list[str], limit: int = 0) -> list[str]:
        """Return paths that have no cached date_taken."""
        self._ensure_schema()
        placeholders = ",".join("?" for _ in source_roots)
        q = f"SELECT path FROM media_files WHERE source_root IN ({placeholders}) AND date_taken IS NULL"
        if limit > 0:
            q += f" LIMIT {limit}"
        return [row[0] for row in self._conn().execute(q, source_roots)]

    def get_resolved_dates(self, source_roots: list[str]) -> dict[str, str]:
        """Return {path: date_taken} for all files with cached dates."""
        self._ensure_schema()
        placeholders = ",".join("?" for _ in source_roots)
        result: dict[str, str] = {}
        for row in self._conn().execute(
            f"SELECT path, date_taken FROM media_files WHERE source_root IN ({placeholders}) AND date_taken IS NOT NULL",
            source_roots,
        ):
            result[row[0]] = row[1]
        return result

    def set_date(self, path: str, date_taken: str, date_source: str, exif_json: str | None = None) -> None:
        """Cache resolved date for a single file."""
        conn = self._conn()
        conn.execute(
            "UPDATE media_files SET date_taken=?, date_source=?, exif_json=? WHERE path=?",
            (date_taken, date_source, exif_json, os.path.normcase(path)),
        )
        conn.commit()

    def set_dates_batch(self, entries: list[tuple[str, str, str, str | None]]) -> None:
        """Cache resolved dates for multiple files. Each entry: (path, date_taken, date_source, exif_json)."""
        conn = self._conn()
        conn.executemany(
            "UPDATE media_files SET date_taken=?, date_source=?, exif_json=? WHERE path=?",
            [(date, source, exif, os.path.normcase(p)) for p, date, source, exif in entries],
        )
        conn.commit()

    def get_file_list(self, source_roots: list[str]) -> list[dict]:
        """Return all cached files with metadata for the given roots."""
        self._ensure_schema()
        placeholders = ",".join("?" for _ in source_roots)
        rows = self._conn().execute(
            f"SELECT path, source_root, relative_path, extension, size_bytes, kind, date_taken, date_source FROM media_files WHERE source_root IN ({placeholders}) ORDER BY path",
            source_roots,
        )
        return [dict(r) for r in rows]

    def close(self) -> None:
        if hasattr(self._local, "conn") and self._local.conn:
            self._local.conn.close()
            self._local.conn = None

    # ── global singleton ──

    _instance: MediaCache | None = None

    @classmethod
    def get(cls) -> MediaCache:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

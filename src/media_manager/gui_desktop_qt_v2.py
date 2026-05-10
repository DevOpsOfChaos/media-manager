"""Media Manager — Modern Desktop GUI v2"""
from __future__ import annotations
import json, os, shutil, subprocess, sys, threading
from pathlib import Path
from typing import Any

def _qt():
    from PySide6 import QtCore, QtGui, QtWidgets
    return QtCore, QtGui, QtWidgets

def _python_exe():
    """Find the real python.exe, not the pip wrapper exe."""
    exe = sys.executable
    # Check if this is a real python or a wrapper
    name = Path(exe).name.lower()
    if "python" in name:
        return exe
    # Fall back to base_prefix
    base = Path(sys.base_prefix)
    candidates = [base / "python.exe", base / "python3.exe", base / "bin" / "python"]
    for c in candidates:
        if c.is_file():
            return str(c)
    # Last resort: PATH
    found = shutil.which("python") or shutil.which("python3")
    return found or exe

# ── Settings ──
SETTINGS_DIR = Path.home() / ".media-manager"
SETTINGS_FILE = SETTINGS_DIR / "gui-settings.json"
_ERROR_LOG = SETTINGS_DIR / "gui-error.log"
def _log_error(msg):
    try:
        from datetime import datetime
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
        with open(_ERROR_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {msg}\n")
    except Exception:
        pass
DEFAULTS = {"language":"en","theme":"dark","source_dir":"","target_dir":"",
            "exiftool_path":"","organize_mode":"move","delete_empty":False,"conflict_policy":"conflict",
            "media_scope":"all","last_stats":{"images":0,"videos":0,"music":0,"subdirs":0,"organized":0}}
def _ls():
    if SETTINGS_FILE.exists():
        try: return json.loads(SETTINGS_FILE.read_text())
        except: pass
    return dict(DEFAULTS)
def _ss(s):
    SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(json.dumps(s, indent=2))

# ── ExifTool ──
def _find_exiftool():
    try:
        from media_manager.exiftool import resolve_exiftool_path
        s=_ls(); custom=s.get("exiftool_path","")
        return resolve_exiftool_path(Path(custom) if custom else None)
    except Exception: return None
def _exiftool_ok(): return _find_exiftool() is not None

# ── CLI ──
_CANCEL_EVENTS: dict[int, threading.Event] = {}
_CANCEL_LOCK = threading.Lock()

def _cancel_all():
    with _CANCEL_LOCK:
        for ev in _CANCEL_EVENTS.values():
            ev.set()
        _CANCEL_EVENTS.clear()

def _count_files_fast(directory, max_depth=3):
    """Count files quickly, limiting recursion depth. Returns file count."""
    try:
        count = 0
        stack = [(Path(directory), 0)]
        while stack:
            path, depth = stack.pop()
            if depth > max_depth: continue
            try:
                for entry in os.scandir(path):
                    if entry.is_file(follow_symlinks=False):
                        count += 1
                    elif entry.is_dir(follow_symlinks=False) and depth < max_depth:
                        stack.append((Path(entry.path), depth + 1))
            except (OSError, PermissionError):
                pass
        return count
    except Exception:
        return 0

def _count_source_media(sources):
    """Count media files in source dirs recursively (matching CLI behavior)."""
    exts = {'.jpg','.jpeg','.png','.gif','.mp4','.mov','.avi','.mkv','.raw','.cr2','.nef','.arw','.dng','.heic','.webp','.bmp','.tiff','.tif','.mp3','.wav','.flac','.aac','.ogg','.wma','.m4a'}
    count = 0
    for src in sources:
        if not src: continue
        try:
            for root, dirs, files in os.walk(src):
                # Skip hidden dirs
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                for f in files:
                    if Path(f).suffix.lower() in exts:
                        count += 1
                        if count % 500 == 0:
                            pass  # allow interrupt
        except: pass
    return count

def _count_organized_fast(target, initial=0):
    """Count files in date-structured target dirs (year/month/day). Only scans 4-digit year dirs."""
    count = 0
    try:
        for year_entry in os.scandir(target):
            if not year_entry.is_dir(follow_symlinks=False): continue
            if not (year_entry.name.isdigit() and len(year_entry.name) == 4): continue
            for month_entry in os.scandir(year_entry.path):
                if not month_entry.is_dir(follow_symlinks=False): continue
                try:
                    for day_entry in os.scandir(month_entry.path):
                        if day_entry.is_file(follow_symlinks=False): count += 1
                except (OSError, PermissionError): pass
    except (OSError, PermissionError): pass
    return count

def _run_cli_with_poll(apply_args, target_dir, total, progress_cb, cancel_event=None, poll_interval=1.0):
    """Run CLI while polling target dir for progress. Returns result dict."""
    python = _python_exe()
    cmd = [python, "-m", "media_manager"] + list(apply_args) + ["--json"]
    s=_ls(); et=s.get("exiftool_path","")
    if et: cmd += ["--exiftool-path", et]
    _log_error(f"CLI START: {' '.join(cmd)}")
    initial_count = _count_files_fast(target_dir)
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        import time as _time
        while proc.poll() is None:
            if cancel_event and cancel_event.is_set():
                proc.kill(); proc.wait()
                return {"error":"Cancelled","ok":False}
            current = _count_files_fast(target_dir) - initial_count
            progress_cb(max(0, min(current, total)), total)
            _time.sleep(poll_interval)
        out, err = proc.communicate(timeout=5)
        out=(out or "").strip(); err=(err or "").strip()
        # Final count
        final = _count_files_fast(target_dir) - initial_count
        progress_cb(max(0, min(final, total)), total)
        if out:
            try: return json.loads(out)
            except: pass
        if err: _log_error(f"CLI stderr: {err[:300]}")
        return {"ok": proc.returncode==0, "executed": final, "_text": out or err}
    except Exception as e:
        _log_error(f"CLI POLL ERROR: {e}")
        try: proc.kill()
        except: pass
        return {"error": str(e), "ok": False}

def _cli(*args, timeout=600, cancel_event=None):
    python = _python_exe()
    cmd = [python, "-m", "media_manager"] + list(args) + ["--json"]
    s=_ls(); et=s.get("exiftool_path","")
    if et: cmd += ["--exiftool-path", et]
    _log_error(f"CLI PREVIEW: {' '.join(cmd)}")
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if cancel_event is not None:
            while proc.poll() is None:
                if cancel_event.is_set():
                    proc.kill()
                    _log_error(f"CLI CANCELLED: {' '.join(cmd)}")
                    return {"error": "Cancelled", "ok": False}
                try:
                    proc.wait(0.1)
                except subprocess.TimeoutExpired:
                    pass
            out, err = proc.communicate(timeout=1)
        else:
            out, err = proc.communicate(timeout=timeout)
        out = (out or "").strip(); err = (err or "").strip()
        rc = proc.returncode
        if rc != 0:
            _log_error(f"CLI rc={rc} cmd={' '.join(cmd)}\nstderr: {err[:500]}")
        if out:
            try: return json.loads(out)
            except:
                _log_error(f"CLI JSON parse failed, raw: {out[:300]}")
                pass
        return {"_text": out or err, "exit": rc, "ok": rc == 0, "stderr": err}
    except subprocess.TimeoutExpired:
        try: proc.kill()
        except: pass
        _log_error(f"CLI TIMEOUT: {' '.join(cmd)}")
        return {"error": "Timeout", "ok": False}
    except Exception as e:
        _log_error(f"CLI EXCEPTION: {e}  cmd={' '.join(cmd)}")
        return {"error": str(e), "ok": False, "stderr": str(e)}

# ═══════════════════════════════════════════
# THEMES
# ═══════════════════════════════════════════

DARK = """QWidget{background:#0d1117;color:#e6edf3;font:13px "Segoe UI"}
#sidebar{background:#161b22;border-right:1px solid #30363d;min-width:220px;max-width:220px}
#sidebar QPushButton{background:transparent;color:#8b949e;border:none;border-radius:8px;padding:10px 14px;text-align:left;font-weight:500;margin:1px 8px}
#sidebar QPushButton:hover{background:#1c2128;color:#e6edf3}
#sidebar QPushButton:checked{background:#1f6feb33;color:#58a6ff;font-weight:600}
#sidebar QLabel#sh{color:#8b949e;font-size:11px;font-weight:600;padding:20px 16px 6px 16px}
#topbar{background:#161b22;border-bottom:1px solid #30363d;min-height:52px;max-height:52px;padding:0 24px}
#topbar QLabel#pageTitle{font-size:15px;font-weight:600;color:#e6edf3}
#langBtn{background:transparent;border:1px solid #30363d;border-radius:8px;padding:6px 12px;font-size:20px;min-width:52px;min-height:36px}
#langBtn:hover{background:#1c2128;border-color:#58a6ff}
#pageTitle{font-size:22px;font-weight:700;padding:0}
#pageSubtitle{font-size:13px;color:#8b949e;padding:2px 0 16px 0}
#card{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:20px}
#card QLabel#cardTitle{font-size:14px;font-weight:600}
#card QLabel#cardValue{font-size:28px;font-weight:700;color:#58a6ff}
#card QLabel#cardSub{font-size:12px;color:#8b949e}
#optionTile{background:#161b22;border:2px solid #30363d;border-radius:12px;padding:14px 8px;min-width:88px;min-height:68px}
#optionTile:hover{border-color:#58a6ff;background:#1c2128}
#optionTile[selected="true"]{border-color:#58a6ff;background:#1f6feb22}
#optionTile QLabel{background:transparent;font-size:11px;color:#c9d1d9}
QLabel#previewLabel{background:#0d1117;border:1px solid #30363d;border-radius:8px;padding:12px 16px;font:13px "Cascadia Code",monospace;color:#7ee787}
QPushButton#primaryBtn{background:#238636;color:#fff;border:1px solid #2ea043;border-radius:8px;padding:10px 24px;font-weight:600;font-size:13px}
QPushButton#primaryBtn:hover{background:#2ea043}
QPushButton#primaryBtn:disabled{background:#21262d;color:#484f58;border-color:#30363d}
QPushButton#secondaryBtn{background:#21262d;color:#c9d1d9;border:1px solid #30363d;border-radius:8px;padding:10px 24px;font-weight:500;font-size:13px}
QPushButton#secondaryBtn:hover{background:#30363d}
QPushButton#addBtn{background:#1f6feb22;color:#58a6ff;border:1px solid #1f6feb44;border-radius:8px;padding:8px 16px;font-weight:600;font-size:13px}
QPushButton#addBtn:hover{background:#1f6feb33;border-color:#58a6ff}
QPushButton#removeBtn{background:transparent;color:#8b949e;border:none;border-radius:4px;padding:4px 8px;font-size:16px;min-width:28px;min-height:28px}
QPushButton#removeBtn:hover{background:#da363322;color:#f85149}
QLineEdit,QComboBox{background:#0d1117;border:1px solid #30363d;border-radius:6px;padding:8px 12px;color:#e6edf3}
QLineEdit:focus,QComboBox:focus{border-color:#58a6ff}
QComboBox::drop-down{border:none;width:24px}
QComboBox QAbstractItemView{background:#161b22;border:1px solid #30363d;border-radius:6px;color:#e6edf3;selection-background-color:#1f6feb33;outline:none;padding:4px}
QComboBox QAbstractItemView::item{padding:8px 12px;min-height:28px}
QComboBox QAbstractItemView::item:hover{background:#1c2128}
QProgressBar{background:#21262d;border:none;border-radius:4px;height:8px}
QProgressBar::chunk{background:#58a6ff;border-radius:4px}
QTableWidget{background:#161b22;border:1px solid #30363d;border-radius:8px;gridline-color:#21262d}
QTableWidget::item{padding:8px 12px;border-bottom:1px solid #21262d}
QHeaderView::section{background:#0d1117;color:#8b949e;font-weight:600;padding:10px 12px;border:none;border-bottom:1px solid #30363d}
QScrollBar:vertical{background:#0d1117;width:8px;border-radius:4px}
QScrollBar::handle:vertical{background:#30363d;border-radius:4px;min-height:30px}
QScrollBar:horizontal{background:#0d1117;height:8px;border-radius:4px}
QScrollBar::handle:horizontal{background:#30363d;border-radius:4px;min-width:30px}
QScrollArea{border:none;background:transparent}
QDateEdit{background:#0d1117;border:1px solid #30363d;border-radius:6px;padding:8px 12px;color:#e6edf3}
QDateEdit::drop-down{border:none;width:24px}
QDateEdit QAbstractItemView{background:#161b22;border:1px solid #30363d;border-radius:6px;color:#e6edf3;selection-background-color:#1f6feb33}
QRadioButton,QCheckBox{spacing:10px;color:#c9d1d9}
QRadioButton::indicator{width:18px;height:18px;border:2px solid #30363d;border-radius:9px;background:#0d1117}
QRadioButton::indicator:checked{background:#58a6ff;border-color:#58a6ff}
QCheckBox::indicator{width:18px;height:18px;border:2px solid #30363d;border-radius:4px;background:#0d1117}
QCheckBox::indicator:checked{background:#58a6ff;border-color:#58a6ff}
QGroupBox{border:1px solid #30363d;border-radius:8px;margin-top:16px;padding:24px 16px 16px 16px;color:#e6edf3;font-weight:600;font-size:13px}
QGroupBox::title{subcontrol-origin:margin;left:14px;padding:0 8px}
QTextEdit,QPlainTextEdit{background:#0d1117;border:1px solid #30363d;border-radius:8px;padding:12px;color:#c9d1d9;font:12px "Cascadia Code",monospace}
QDialog{background:#161b22;border:1px solid #30363d;border-radius:12px}
QDialog QLabel{color:#e6edf3}
QDialog QLineEdit{min-width:300px}
QToolTip{background:#161b22;color:#e6edf3;border:1px solid #30363d;border-radius:4px;padding:6px 10px}
#statusBar{background:#161b22;border-top:1px solid #30363d;min-height:30px;max-height:30px;padding:0 16px;font-size:12px;color:#8b949e}
#sourceRow{background:#0d1117;border:1px solid #30363d;border-radius:8px;padding:4px 4px 4px 12px}
#sourceRow:hover{border-color:#58a6ff}"""

LIGHT = """QWidget{background:#ffffff;color:#24292f;font:13px "Segoe UI"}
#sidebar{background:#f6f8fa;border-right:1px solid #d0d7de;min-width:220px;max-width:220px}
#sidebar QPushButton{background:transparent;color:#656d76;border:none;border-radius:8px;padding:10px 14px;text-align:left;font-weight:500;margin:1px 8px}
#sidebar QPushButton:hover{background:#eaeef2;color:#24292f}
#sidebar QPushButton:checked{background:#ddf4ff;color:#0969da;font-weight:600}
#sidebar QLabel#sh{color:#656d76;font-size:11px;font-weight:600;padding:20px 16px 6px 16px}
#topbar{background:#f6f8fa;border-bottom:1px solid #d0d7de;min-height:52px;max-height:52px;padding:0 24px}
#topbar QLabel#pageTitle{font-size:15px;font-weight:600;color:#24292f}
#langBtn{background:transparent;border:1px solid #d0d7de;border-radius:8px;padding:6px 12px;font-size:20px;min-width:52px;min-height:36px}
#langBtn:hover{background:#eaeef2;border-color:#0969da}
#pageTitle{font-size:22px;font-weight:700;padding:0}
#pageSubtitle{font-size:13px;color:#656d76;padding:2px 0 16px 0}
#card{background:#f6f8fa;border:1px solid #d0d7de;border-radius:12px;padding:20px}
#card QLabel#cardTitle{font-size:14px;font-weight:600}
#card QLabel#cardValue{font-size:28px;font-weight:700;color:#0969da}
#card QLabel#cardSub{font-size:12px;color:#656d76}
#optionTile{background:#f6f8fa;border:2px solid #d0d7de;border-radius:12px;padding:14px 8px;min-width:88px;min-height:68px}
#optionTile:hover{border-color:#0969da;background:#eaeef2}
#optionTile[selected="true"]{border-color:#0969da;background:#ddf4ff}
#optionTile QLabel{background:transparent;font-size:11px;color:#24292f}
QLabel#previewLabel{background:#f6f8fa;border:1px solid #d0d7de;border-radius:8px;padding:12px 16px;font:13px "Cascadia Code",monospace;color:#1a7f37}
QPushButton#primaryBtn{background:#1f883d;color:#fff;border:1px solid #1a7f37;border-radius:8px;padding:10px 24px;font-weight:600;font-size:13px}
QPushButton#primaryBtn:hover{background:#1a7f37}
QPushButton#primaryBtn:disabled{background:#afb8c1;color:#8c959f;border-color:#afb8c1}
QPushButton#secondaryBtn{background:#f6f8fa;color:#24292f;border:1px solid #d0d7de;border-radius:8px;padding:10px 24px;font-weight:500;font-size:13px}
QPushButton#secondaryBtn:hover{background:#eaeef2}
QPushButton#addBtn{background:#ddf4ff;color:#0969da;border:1px solid #0969da33;border-radius:8px;padding:8px 16px;font-weight:600;font-size:13px}
QPushButton#addBtn:hover{background:#b6e3ff;border-color:#0969da}
QPushButton#removeBtn{background:transparent;color:#656d76;border:none;border-radius:4px;padding:4px 8px;font-size:16px;min-width:28px;min-height:28px}
QPushButton#removeBtn:hover{background:#ffebe9;color:#cf222e}
QLineEdit,QComboBox{background:#ffffff;border:1px solid #d0d7de;border-radius:6px;padding:8px 12px;color:#24292f}
QLineEdit:focus,QComboBox:focus{border-color:#0969da}
QComboBox::drop-down{border:none;width:24px}
QComboBox QAbstractItemView{background:#ffffff;border:1px solid #d0d7de;border-radius:6px;color:#24292f;selection-background-color:#ddf4ff;outline:none;padding:4px}
QComboBox QAbstractItemView::item{padding:8px 12px;min-height:28px}
QComboBox QAbstractItemView::item:hover{background:#eaeef2}
QProgressBar{background:#eaeef2;border:none;border-radius:4px;height:8px}
QProgressBar::chunk{background:#0969da;border-radius:4px}
QTableWidget{background:#ffffff;border:1px solid #d0d7de;border-radius:8px;gridline-color:#eaeef2}
QTableWidget::item{padding:8px 12px;border-bottom:1px solid #eaeef2}
QHeaderView::section{background:#f6f8fa;color:#656d76;font-weight:600;padding:10px 12px;border:none;border-bottom:1px solid #d0d7de}
QScrollBar:vertical{background:#ffffff;width:8px;border-radius:4px}
QScrollBar::handle:vertical{background:#d0d7de;border-radius:4px;min-height:30px}
QScrollBar:horizontal{background:#ffffff;height:8px;border-radius:4px}
QScrollBar::handle:horizontal{background:#d0d7de;border-radius:4px;min-width:30px}
QScrollArea{border:none;background:transparent}
QDateEdit{background:#ffffff;border:1px solid #d0d7de;border-radius:6px;padding:8px 12px;color:#24292f}
QDateEdit::drop-down{border:none;width:24px}
QDateEdit QAbstractItemView{background:#ffffff;border:1px solid #d0d7de;border-radius:6px;color:#24292f;selection-background-color:#ddf4ff}
QRadioButton,QCheckBox{spacing:10px;color:#24292f}
QRadioButton::indicator{width:18px;height:18px;border:2px solid #d0d7de;border-radius:9px;background:#ffffff}
QRadioButton::indicator:checked{background:#0969da;border-color:#0969da}
QCheckBox::indicator{width:18px;height:18px;border:2px solid #d0d7de;border-radius:4px;background:#ffffff}
QCheckBox::indicator:checked{background:#0969da;border-color:#0969da}
QGroupBox{border:1px solid #d0d7de;border-radius:8px;margin-top:16px;padding:24px 16px 16px 16px;color:#24292f;font-weight:600;font-size:13px}
QGroupBox::title{subcontrol-origin:margin;left:14px;padding:0 8px}
QTextEdit,QPlainTextEdit{background:#f6f8fa;border:1px solid #d0d7de;border-radius:8px;padding:12px;color:#24292f;font:12px "Cascadia Code",monospace}
QDialog{background:#ffffff;border:1px solid #d0d7de;border-radius:12px}
QDialog QLabel{color:#24292f}
QDialog QLineEdit{min-width:300px}
QToolTip{background:#f6f8fa;color:#24292f;border:1px solid #d0d7de;border-radius:4px;padding:6px 10px}
#statusBar{background:#f6f8fa;border-top:1px solid #d0d7de;min-height:30px;max-height:30px;padding:0 16px;font-size:12px;color:#656d76}
#sourceRow{background:#ffffff;border:1px solid #d0d7de;border-radius:8px;padding:4px 4px 4px 12px}
#sourceRow:hover{border-color:#0969da}"""

# ═══════════════════════════════════════════
# i18n
# ═══════════════════════════════════════════

T = {
    "en": {
        "nav.dashboard":"🏠  Dashboard","nav.organize":"📁  Organize","nav.rename":"✏️  Rename",
        "nav.duplicates":"🔍  Duplicates","nav.people":"👤  People","nav.trips":"📍  Trips","nav.settings":"⚙️  Settings",
        "sh.main":"MAIN","sh.tools":"TOOLS",
        "dashboard.title":"Dashboard","dashboard.sub":"Your media library at a glance.",
        "dashboard.quick":"Quick Actions","dashboard.files":"Media Files",
        "dashboard.images":"Images","dashboard.videos":"Videos","dashboard.music":"Music",
        "dashboard.src_files":"Source Files","dashboard.org_files":"Organized","dashboard.subdirs":"Subdirectories","dashboard.exif":"ExifTool",
        "dashboard.organize":"Organize files","dashboard.rename":"Rename files",
        "dashboard.find_dups":"Find duplicates","dashboard.face":"Face recognition",
        "dashboard.welcome":"Welcome back","dashboard.no_source":"Set a source folder in Settings to see your library stats.",
        "dashboard.open_settings":"Open Settings","dashboard.refreshing":"Refreshing",
        "onboarding.title":"Welcome to Media Manager",
        "onboarding.sub":"Organize, rename, and manage your photos, videos, and music — all on your computer.",
        "onboarding.folder_hint":"Select your media folder...",
        "onboarding.browse":"Browse",
        "onboarding.media_types":"Media types to manage:",
        "onboarding.images":"Images","onboarding.videos":"Videos","onboarding.music":"Music",
        "onboarding.scope":"How to manage images & videos:",
        "onboarding.scope_separate":"Separate — organize images and videos independently",
        "onboarding.scope_together":"Together — manage images and videos as one collection",
        "onboarding.start":"Get Started",
        "onboarding.scanning":"Scanning your media...",
        "organize.title":"Organize Media","organize.sub":"Sort photos and videos into folders by date.",
        "organize.source_folders":"Source Folders","organize.add_source":"+ Add Folder",
        "organize.target":"Target Folder","organize.group_by":"Folder Structure",
        "organize.flat":"Flat","organize.year":"Year","organize.ym":"Year / Month",
        "organize.ymd":"Year / Month / Day","organize.ym_name_day":"Year / Month Name / Day",
        "organize.ym_month_name":"Year / Month Name","organize.ym_event":"Year / Event",
        "organize.custom_pattern":"Custom","organize.event_name":"Event name",
        "organize.event_placeholder":"Italy Trip, Wedding...",
        "organize.mode":"File Handling","organize.copy":"Copy files (keep originals)",
        "organize.move":"Move files (delete originals)","organize.options":"Options",
        "organize.delete_empty":"Remove empty folders after organizing",
        "organize.conflict":"If file already exists:","organize.conflict_skip":"Skip","organize.conflict_rename":"Rename new file",
        "organize.preview":"Preview","organize.apply":"Organize Files",
        "organize.apply_confirm":"This will {mode} your files into date-based folders.\n\nSource: {sources}\nTarget: {target}\n\nThis cannot be undone. Continue?",
        "organize.working":"Organizing files...","organize.done":"Done — {count} files organized.",
        "organize.skipped":"Skipped: {count} files (missing date or unsupported format).",
        "organize.empty_removed":"Removed {count} empty folders.",
        "organize.error":"Error: {error}","organize.no_files":"No media files found in the selected source folders.",
        "organize.custom_title":"Custom Pattern","organize.custom_help":"Build your folder pattern using tokens. Preview updates live.",
        "organize.custom_tokens":"Available tokens:","organize.custom_save":"Use Pattern",
        "organize.custom_desc":"{year} = 2025    {month} = 07    {month_name} = July    {day} = 15\n{year_month} = 2025-07    {year_month_day} = 2025-07-15    {source_name} = folder name\n\nExamples:\n{year}/{year_month_day}  →  2025/2025-07-15\n{year}/{month_name}  →  2025/July\n{year}/{month_name}/{day}  →  2025/July/15\n{year}/{year_month}-{source_name}  →  2025/2025-07-TripName",
        "rename.title":"Rename Media","rename.sub":"Give your files meaningful names — check what to include.",
        "rename.src":"Source Folder","rename.include":"Filename parts:",
        "rename.date":"Date taken","rename.camera":"Camera model",
        "rename.original":"Original filename","rename.counter":"Number sequence (001, 002...)",
        "rename.date_format":"Date format:","rename.separator":"Separator:",
        "rename.preview":"Preview","rename.apply":"Rename Files",
        "rename.apply_confirm":"This will rename files in:\n{src}\n\nThis cannot be undone. Continue?",
        "rename.working":"Renaming files...","rename.done":"Done — {count} files renamed.","rename.error":"Error: {error}",
        "duplicates.title":"Find Duplicates","duplicates.sub":"Scan for exact and similar duplicate files.",
        "duplicates.src":"Source Folder","duplicates.scan":"Scan for Duplicates",
        "duplicates.exact":"Exact Duplicates","duplicates.similar":"Similar Images",
        "duplicates.no_results":"No duplicates found — your library is clean!",
        "duplicates.groups":"{eg} exact groups ({ef} files, {ed} extras)  |  {sg} similar groups",
        "duplicates.table_group":"Group","duplicates.table_files":"Files","duplicates.table_size":"Size","duplicates.table_name":"Same Name",
        "duplicates.cleanup":"Clean Up","duplicates.keep_policy":"Keep:",
        "duplicates.keep_first":"First (by name)","duplicates.keep_newest":"Newest","duplicates.keep_oldest":"Oldest",
        "duplicates.action_mode":"Action:","duplicates.delete":"Delete duplicates","duplicates.move_to":"Move duplicates to",
        "duplicates.target":"Target folder","duplicates.apply":"Clean Up Duplicates",
        "duplicates.apply_confirm":"This will {action} {count} duplicate files. {target}\n\nThis cannot be undone. Continue?",
        "duplicates.deleted":"Deleted {count} duplicate files.","duplicates.moved":"Moved {count} duplicate files to {target}.",
        "duplicates.clean_similar":"Keep Best / Trash Similar","duplicates.clean_similar_hint":"Keeps the anchor image, moves similar copies to trash.",
        "duplicates.clean_similar_confirm":"This will trash {files} similar images across {groups} groups, keeping only the best (anchor) image from each group.\n\nThe anchor images will be preserved.\n\nContinue?",
        "duplicates.similar_done":"Trashed {count} similar images. {errors} errors.","duplicates.no_similar":"No similar images to clean up.",
        "duplicates.error":"Error: {error}",
        "people.title":"People","people.sub":"Local face recognition — everything stays on your computer.",
        "people.scan":"Scan for Faces","people.missing":"Face recognition not installed.",
        "people.install_hint":"Run: pip install -e \".[people]\"","people.backend_ok":"Face recognition is ready. Select a folder and scan.",
        "people.scanning":"Scanning for faces...","people.hint":"Click 'Scan for Faces' to find people in your media.",
        "people.results":"Scan Results","people.files_scanned":"Files scanned","people.faces_found":"Faces found",
        "people.matched":"Matched","people.unknown":"Unknown","people.clusters":"Clusters","people.unnamed":"(unnamed)",
        "people.col_file":"File","people.col_person":"Person","people.col_location":"Location","people.col_conf":"Confidence",
        "people.review_cli":"Open CLI Review","people.review_cli_tip":"Launch terminal with people review tools",
        "people.cli_hint":"Tip: Use the CLI review to name people, merge duplicates, and export a catalog.",
        "people.detected":"Found {faces} faces in {files} files.","people.no_faces":"No faces found.",
        "trips.title":"Trips","trips.sub":"Create organized collections from your media.",
        "trips.name":"Trip Name","trips.start":"Start Date","trips.end":"End Date",
        "trips.src":"Source Folder","trips.tgt":"Target Folder",
        "trips.link":"Hard links (no extra disk space)","trips.copy":"Copies (independent files)",
        "trips.create":"Create Trip","trips.created":"Trip '{name}' created — {count} files linked/copied to {target}.",
        "trips.no_files":"No media files found in the selected date range.","trips.error":"Error: {error}",
        "settings.title":"Settings","settings.sub":"Language, appearance, and default folders.",
        "settings.scope":"Media Management",
        "settings.lang":"Language","settings.theme":"Appearance","settings.dark":"Dark","settings.light":"Light",
        "settings.data":"Default Folders","settings.src_hint":"Source folder for media files","settings.tgt_hint":"Target folder for organized files",
        "settings.save":"Save Settings","settings.saved":"Settings saved.",
        "settings.exiftool":"ExifTool","settings.exiftool_find":"Auto-Detect",
        "settings.exiftool_found":"Found:","settings.exiftool_notfound":"Not found — browse or install from exiftool.org",
        "filter.kind":"File type:","filter.all":"All media","filter.img_vid":"Images + Videos","filter.img":"Images only","filter.vid":"Videos only","filter.aud":"Music only",
        "status.ready":"Ready","status.scanning":"Scanning...","status.hashing":"Hashing...","status.done":"Done",
        "exiftool.missing":"ExifTool not found. Needed for reading photo/video dates.","exiftool.dl":"Download ExifTool",
    },
    "de": {
        "nav.dashboard":"🏠  Übersicht","nav.organize":"📁  Organisieren","nav.rename":"✏️  Umbenennen",
        "nav.duplicates":"🔍  Duplikate","nav.people":"👤  Personen","nav.trips":"📍  Reisen","nav.settings":"⚙️  Einstellungen",
        "sh.main":"HAUPTMENÜ","sh.tools":"WERKZEUGE",
        "dashboard.title":"Übersicht","dashboard.sub":"Deine Medienbibliothek auf einen Blick.",
        "dashboard.quick":"Schnellaktionen","dashboard.files":"Mediendateien",
        "dashboard.images":"Bilder","dashboard.videos":"Videos","dashboard.music":"Musik",
        "dashboard.src_files":"Quelldateien","dashboard.org_files":"Organisiert","dashboard.subdirs":"Unterordner","dashboard.exif":"ExifTool",
        "dashboard.organize":"Dateien organisieren","dashboard.rename":"Dateien umbenennen",
        "dashboard.find_dups":"Duplikate finden","dashboard.face":"Gesichtserkennung",
        "dashboard.welcome":"Willkommen zurück","dashboard.no_source":"Lege ein Quellverzeichnis in den Einstellungen fest.",
        "dashboard.open_settings":"Einstellungen öffnen","dashboard.refreshing":"Aktualisiere",
        "onboarding.title":"Willkommen bei Media Manager",
        "onboarding.sub":"Organisiere, benenne um und verwalte deine Fotos, Videos und Musik — alles auf deinem Computer.",
        "onboarding.folder_hint":"Medienordner auswählen...",
        "onboarding.browse":"Durchsuchen",
        "onboarding.media_types":"Zu verwaltende Medientypen:",
        "onboarding.images":"Bilder","onboarding.videos":"Videos","onboarding.music":"Musik",
        "onboarding.scope":"Bilder & Videos verwalten:",
        "onboarding.scope_separate":"Getrennt — Bilder und Videos unabhängig organisieren",
        "onboarding.scope_together":"Zusammen — Bilder und Videos als eine Sammlung verwalten",
        "onboarding.start":"Los geht's",
        "onboarding.scanning":"Medien werden gescannt...",
        "organize.title":"Medien organisieren","organize.sub":"Sortiere Fotos und Videos in Ordner nach Datum.",
        "organize.source_folders":"Quellordner","organize.add_source":"+ Ordner hinzufügen",
        "organize.target":"Zielordner","organize.group_by":"Ordnerstruktur",
        "organize.flat":"Flach","organize.year":"Jahr","organize.ym":"Jahr / Monat",
        "organize.ymd":"Jahr / Monat / Tag","organize.ym_name_day":"Jahr / Monatsname / Tag",
        "organize.ym_month_name":"Jahr / Monatsname","organize.ym_event":"Jahr / Ereignis",
        "organize.custom_pattern":"Eigene","organize.event_name":"Ereignisname",
        "organize.event_placeholder":"Italien-Reise, Hochzeit...",
        "organize.mode":"Dateibehandlung","organize.copy":"Dateien kopieren (Originale bleiben)",
        "organize.move":"Dateien verschieben (Originale löschen)","organize.options":"Optionen",
        "organize.delete_empty":"Leere Ordner nach dem Organisieren entfernen",
        "organize.conflict":"Bei Namenskonflikt:","organize.conflict_skip":"Überspringen","organize.conflict_rename":"Umbenennen",
        "organize.preview":"Vorschau","organize.apply":"Dateien organisieren",
        "organize.apply_confirm":"Deine Dateien werden in datumsbasierte Ordner {mode}.\n\nQuelle: {sources}\nZiel: {target}\n\nKann nicht rückgängig gemacht werden. Fortsetzen?",
        "organize.working":"Organisiere Dateien...","organize.done":"Fertig — {count} Dateien organisiert.",
        "organize.skipped":"Übersprungen: {count} Dateien (fehlendes Datum oder ungültiges Format).",
        "organize.empty_removed":"{count} leere Ordner entfernt.","organize.error":"Fehler: {error}",
        "organize.no_files":"Keine Mediendateien in den ausgewählten Quellordnern gefunden.",
        "organize.custom_title":"Eigenes Muster","organize.custom_help":"Erstelle dein Ordnermuster mit Token. Vorschau aktualisiert sich live.",
        "organize.custom_tokens":"Verfügbare Token:","organize.custom_save":"Muster übernehmen",
        "organize.custom_desc":"{year} = 2025    {month} = 07    {month_name_de} = Juli    {day} = 15\n{year_month} = 2025-07    {year_month_day} = 2025-07-15    {source_name} = Ordnername\n\nBeispiele:\n{year}/{year_month_day}  →  2025/2025-07-15\n{year}/{month_name_de}  →  2025/Juli\n{year}/{month_name_de}/{day}  →  2025/Juli/15\n{year}/{year_month}-{source_name}  →  2025/2025-07-Reisename",
        "rename.title":"Medien umbenennen","rename.sub":"Gib deinen Dateien aussagekräftige Namen.",
        "rename.src":"Quellordner","rename.include":"Dateinamen-Teile:",
        "rename.date":"Aufnahmedatum","rename.camera":"Kamera-Modell",
        "rename.original":"Original-Dateiname","rename.counter":"Nummerierung (001, 002...)",
        "rename.date_format":"Datumsformat:","rename.separator":"Trennzeichen:",
        "rename.preview":"Vorschau","rename.apply":"Dateien umbenennen",
        "rename.apply_confirm":"Dateien werden umbenannt in:\n{src}\n\nKann nicht rückgängig gemacht werden. Fortsetzen?",
        "rename.working":"Benenne Dateien um...","rename.done":"Fertig — {count} Dateien umbenannt.","rename.error":"Fehler: {error}",
        "duplicates.title":"Duplikate finden","duplicates.sub":"Scanne nach exakten und ähnlichen Duplikaten.",
        "duplicates.src":"Quellordner","duplicates.scan":"Nach Duplikaten suchen",
        "duplicates.exact":"Exakte Duplikate","duplicates.similar":"Ähnliche Bilder",
        "duplicates.no_results":"Keine Duplikate gefunden — deine Bibliothek ist sauber!",
        "duplicates.groups":"{eg} exakte Gruppen ({ef} Dateien, {ed} Extras)  |  {sg} ähnliche Gruppen",
        "duplicates.table_group":"Gruppe","duplicates.table_files":"Dateien","duplicates.table_size":"Größe","duplicates.table_name":"Gleicher Name",
        "duplicates.cleanup":"Aufräumen","duplicates.keep_policy":"Behalten:",
        "duplicates.keep_first":"Erste (nach Name)","duplicates.keep_newest":"Neueste","duplicates.keep_oldest":"Älteste",
        "duplicates.action_mode":"Aktion:","duplicates.delete":"Duplikate löschen","duplicates.move_to":"Duplikate verschieben nach",
        "duplicates.target":"Zielordner","duplicates.apply":"Duplikate bereinigen",
        "duplicates.apply_confirm":"Dies wird {action}: {count} Dateien. {target}\n\nKann nicht rückgängig gemacht werden. Fortsetzen?",
        "duplicates.deleted":"{count} Duplikate gelöscht.","duplicates.moved":"{count} Duplikate verschoben nach {target}.",
        "duplicates.clean_similar":"Bestes behalten / Ähnliche löschen","duplicates.clean_similar_hint":"Behält das Anker-Bild, verschiebt ähnliche Kopien in den Papierkorb.",
        "duplicates.clean_similar_confirm":"Dies wird {files} ähnliche Bilder in {groups} Gruppen in den Papierkorb verschieben. Das beste Bild (Anker) jeder Gruppe bleibt erhalten.\n\nFortsetzen?",
        "duplicates.similar_done":"{count} ähnliche Bilder gelöscht. {errors} Fehler.","duplicates.no_similar":"Keine ähnlichen Bilder zum Bereinigen.",
        "duplicates.error":"Fehler: {error}",
        "people.title":"Personen","people.sub":"Lokale Gesichtserkennung — alles bleibt auf deinem Computer.",
        "people.scan":"Nach Gesichtern scannen","people.missing":"Gesichtserkennung nicht installiert.",
        "people.install_hint":"Ausführen: pip install -e \".[people]\"","people.backend_ok":"Gesichtserkennung bereit. Ordner wählen und scannen.",
        "people.scanning":"Suche nach Gesichtern...","people.hint":"Klicke 'Nach Gesichtern scannen' um Personen in deinen Medien zu finden.",
        "people.results":"Scan-Ergebnisse","people.files_scanned":"Dateien gescannt","people.faces_found":"Gesichter gefunden",
        "people.matched":"Zugeordnet","people.unknown":"Unbekannt","people.clusters":"Cluster","people.unnamed":"(unbenannt)",
        "people.col_file":"Datei","people.col_person":"Person","people.col_location":"Position","people.col_conf":"Genauigkeit",
        "people.review_cli":"CLI-Review öffnen","people.review_cli_tip":"Terminal mit Personen-Review-Tools starten",
        "people.cli_hint":"Tipp: Nutze das CLI-Review um Personen zu benennen, Duplikate zu mergen und einen Katalog zu exportieren.",
        "people.detected":"{faces} Gesichter in {files} Dateien gefunden.","people.no_faces":"Keine Gesichter gefunden.",
        "trips.title":"Reisen","trips.sub":"Erstelle organisierte Sammlungen aus deinen Medien.",
        "trips.name":"Reisename","trips.start":"Startdatum","trips.end":"Enddatum",
        "trips.src":"Quellordner","trips.tgt":"Zielordner",
        "trips.link":"Hardlinks (kein zusätzlicher Speicher)","trips.copy":"Kopien (unabhängige Dateien)",
        "trips.create":"Reise erstellen","trips.created":"Reise '{name}' erstellt — {count} Dateien verknüpft/kopiert nach {target}.",
        "trips.no_files":"Keine Mediendateien im gewählten Zeitraum gefunden.","trips.error":"Fehler: {error}",
        "settings.title":"Einstellungen","settings.sub":"Sprache, Erscheinungsbild und Standardordner.",
        "settings.scope":"Medien-Verwaltung",
        "settings.lang":"Sprache","settings.theme":"Erscheinungsbild","settings.dark":"Dunkel","settings.light":"Hell",
        "settings.data":"Standardordner","settings.src_hint":"Quellordner für Mediendateien","settings.tgt_hint":"Zielordner für Ausgabe",
        "settings.save":"Einstellungen speichern","settings.saved":"Einstellungen gespeichert.",
        "settings.exiftool":"ExifTool","settings.exiftool_find":"Auto-Erkennung",
        "settings.exiftool_found":"Gefunden:","settings.exiftool_notfound":"Nicht gefunden — auswählen oder von exiftool.org installieren",
        "filter.kind":"Dateityp:","filter.all":"Alle Medien","filter.img_vid":"Bilder + Videos","filter.img":"Nur Bilder","filter.vid":"Nur Videos","filter.aud":"Nur Musik",
        "status.ready":"Bereit","status.scanning":"Scanne...","status.hashing":"Berechne Hashes...","status.done":"Fertig",
        "exiftool.missing":"ExifTool nicht gefunden. Wird für Foto-/Video-Datumsdaten benötigt.","exiftool.dl":"ExifTool herunterladen",
    },
}
def _(k, l=None):
    l = l or _ls().get("language", "en")
    return T.get(l, T["en"]).get(k, T["en"].get(k, k))

# ═══════════════════════════════════════════
# UI helpers
# ═══════════════════════════════════════════

def _btn(txt, obj=""):
    qc,qg,qw=_qt(); b=qw.QPushButton(txt); b.setCursor(qg.QCursor(qc.Qt.CursorShape.PointingHandCursor))
    if obj: b.setObjectName(obj)
    return b
def _lbl(txt, obj="", wrap=True):
    qc,qg,qw=_qt(); l=qw.QLabel(txt); l.setWordWrap(wrap)
    if obj: l.setObjectName(obj)
    return l
def _hb(*ws, sp=12):
    qc,qg,qw=_qt(); lo=qw.QHBoxLayout(); lo.setSpacing(sp)
    for w in ws:
        if isinstance(w,int): lo.addStretch(w)
        elif isinstance(w,qw.QLayout): lo.addLayout(w)
        else: lo.addWidget(w)
    return lo
def _vb(*ws, sp=12, margins=(0,0,0,0)):
    qc,qg,qw=_qt(); lo=qw.QVBoxLayout(); lo.setSpacing(sp); lo.setContentsMargins(*margins)
    for w in ws:
        if isinstance(w,int): lo.addStretch(w)
        elif isinstance(w,qw.QLayout): lo.addLayout(w)
        else: lo.addWidget(w)
    return lo
def _browse_btn(edit, caption="Select Folder"):
    qc,qg,qw=_qt(); b=_btn("Browse","secondaryBtn")
    def _cb():
        p=qw.QFileDialog.getExistingDirectory(None, caption)
        if p: edit.setText(p)
    b.clicked.connect(_cb); return b
def _file_browse_btn(edit, caption="Select File", filter_str="*.exe;;*"):
    qc,qg,qw=_qt(); b=_btn("Browse","secondaryBtn")
    def _cb():
        p,_=qw.QFileDialog.getOpenFileName(None, caption, "", filter_str)
        if p: edit.setText(p)
    b.clicked.connect(_cb); return b
def _media_filter(lang):
    qc,qg,qw=_qt(); c=qw.QComboBox()
    c.addItems([_("filter.all",lang),_("filter.img_vid",lang),_("filter.img",lang),_("filter.vid",lang),_("filter.aud",lang)])
    return _hb(_lbl(_("filter.kind",lang)),c,sp=8),c
def _mk_args(combo):
    i=combo.currentIndex()
    if i==1: return ["--media-kind","image","--media-kind","video"]
    if i==2: return ["--media-kind","image"]
    if i==3: return ["--media-kind","video"]
    if i==4: return ["--media-kind","audio"]
    return []
def _filter_patterns(combo):
    i=combo.currentIndex()
    img=("*.jpg","*.jpeg","*.png","*.gif","*.webp","*.bmp","*.tiff","*.tif","*.heic","*.raw","*.cr2","*.nef","*.arw","*.dng")
    vid=("*.mp4","*.mov","*.avi","*.mkv")
    aud=("*.mp3","*.wav","*.flac","*.aac","*.ogg","*.wma","*.m4a")
    if i==1: return img+vid
    if i==2: return img
    if i==3: return vid
    if i==4: return aud
    return ()
def _folder_row(label,lang,placeholder_key="settings.src_hint",browse_caption=None):
    qc,qg,qw=_qt(); e=qw.QLineEdit(); e.setPlaceholderText(_(placeholder_key,lang))
    status=qw.QLabel(); status.setFixedWidth(24); status.setStyleSheet("font-size:14px")
    row=_hb(_lbl(label),e,status,_browse_btn(e,browse_caption or "Select Folder"),sp=6)
    def _validate():
        p=Path(e.text().strip())
        if p.exists() and p.is_dir():
            try: cnt=len(list(p.iterdir())); status.setText(f"✅" if cnt>0 else "📂"); status.setToolTip(f"{cnt} items")
            except: status.setText("📂"); status.setToolTip("Directory exists")
        elif e.text().strip(): status.setText("❌"); status.setToolTip("Path does not exist")
        else: status.setText(""); status.setToolTip("")
    e.textChanged.connect(_validate); _validate()
    return row,e

def _fmt(r, lang):
    if not r: return _("status.error",lang)
    if isinstance(r,dict):
        if r.get("error"): return _(f"organize.error",lang).format(error=r["error"])
        plan=r.get("plan",{}) or {}; entries=plan.get("entries",[])
        if entries:
            lines=[f"Files planned: {len(entries)}"]
            for e in entries[:20]:
                sn=Path(e.get("source","")).name if e.get("source") else "?"
                tg=e.get("target",str(e.get("target_name","?")))
                lines.append(f"  {sn}  →  {tg}")
            if len(entries)>20: lines.append(f"  ... and {len(entries)-20} more")
            return "\n".join(lines)
        executed=r.get("executed")
        if executed is not None:
            skipped=r.get("skipped",0); txt=_(f"organize.done",lang).format(count=executed)
            if skipped: txt+="\n"+_(f"organize.skipped",lang).format(count=skipped)
            return txt
        renames=r.get("renames") or plan.get("renames") or {}
        rn=renames if isinstance(renames,list) else renames.get("entries",[])
        if rn:
            lines=[f"Files planned: {len(rn)}"]
            for e in rn[:20]:
                sn=Path(e.get("source","")).name if e.get("source") else "?"
                nn=e.get("target_name",e.get("target","?"))
                lines.append(f"  {sn}  →  {nn}")
            if len(rn)>20: lines.append(f"  ... and {len(rn)-20} more")
            return "\n".join(lines)
        renamed=r.get("renamed")
        if renamed is not None: return _(f"rename.done",lang).format(count=renamed)
        sc=r.get("scan",{})
        if sc:
            eg=sc.get("exact_groups",0); ef=sc.get("duplicate_files",0); ed=sc.get("extra_duplicates",0)
            simd=r.get("similar_images",{}) or {}; sg=len(simd.get("groups",[]) or [])
            return _(f"duplicates.groups",lang).format(eg=eg,ef=ef,ed=ed,sg=sg)
        planned=r.get("planned_count",0)
        if planned: return _(f"trips.created",lang).format(name=r.get("label",""),count=planned)
        summary=r.get("summary",{})
        if summary:
            faces=summary.get("face_count",0); files=summary.get("processed_files",0)
            if faces: return _(f"people.detected",lang).format(faces=faces,files=files)
            return _(f"people.no_faces",lang)
        status=r.get("status","")
        if status=="backend_missing": return _("people.missing",lang)
        backend=r.get("backend")
        if backend:
            caps=r.get("capabilities",{}) or {}
            det=caps.get("face_detection",False); mat=caps.get("named_person_matching",False)
            return f"Backend: {backend}  |  Detection: {'Yes' if det else 'No'}  |  Matching: {'Yes' if mat else 'No'}"
        keys=[k for k in r if not k.startswith("_")]
        if keys: return f"Result: {', '.join(keys)}"
    if isinstance(r,str): return r[:2000]
    return json.dumps(r,indent=2)[:2000]

# ═══════════════════════════════════════════
# ProgressWidget
# ═══════════════════════════════════════════

class ProgressWidget:
    def __init__(self):
        qc,qg,qw=_qt(); self.w=qw.QWidget(); lo=_vb(sp=6)
        self.label=_lbl("","cardSub")
        self.pb=qw.QProgressBar(); self.pb.setRange(0,100); self.pb.setValue(0)
        self.pb.setTextVisible(True); self.pb.setFixedHeight(26)
        self.pb.setStyleSheet("QProgressBar{background:#21262d;border:none;border-radius:4px;height:26px;text-align:center;font-weight:600;font-size:12px;color:#e6edf3}QProgressBar::chunk{background:#238636;border-radius:4px}")
        row=_hb(sp=8); row.addWidget(self.label,1)
        self.cancel_btn=_btn("✕ Cancel","secondaryBtn")
        self.cancel_btn.setVisible(False); self.cancel_btn.setMaximumWidth(90)
        self.cancel_btn.setStyleSheet("QPushButton#secondaryBtn{padding:6px 12px;font-size:12px;min-height:28px;background:#21262d;color:#f85149;border:1px solid #f8514966;border-radius:6px}QPushButton#secondaryBtn:hover{background:#da363322}")
        self._total=0; self._timer=None; self._start=0
        row.addWidget(self.cancel_btn); lo.addLayout(row); lo.addWidget(self.pb)
        self.w.setLayout(lo); self.w.setVisible(False)
        self.cancel_btn.clicked.connect(self._cancel)
    def show(self, msg="", cancellable=False, total=0):
        self.w.setVisible(True); self._total=total; self._start=__import__("time").time()
        if total>0:
            self.pb.setRange(0,total); self.pb.setValue(0)
            self.pb.setFormat(f"0 / {total}  (0%)")
        else:
            self.pb.setRange(0,0); self.pb.setFormat("Working...")
        self.label.setText(msg); self.cancel_btn.setVisible(cancellable)
        self._start_timer()
    def _start_timer(self):
        qc,qg,qw=_qt(); self._timer=qc.QTimer(); self._timer.timeout.connect(self._update_elapsed)
        self._timer.start(1000)
    def _update_elapsed(self):
        if not self.w.isVisible(): self._timer.stop(); return
        elapsed=int(__import__("time").time()-self._start)
        base=self.label.text().split("(")[0].strip()
        self.label.setText(f"{base} ({elapsed}s)")
        self.pb.setFormat(f"{self.pb.format()}  [{elapsed}s]")
    def hide(self, msg=""):
        if self._timer: self._timer.stop(); self._timer=None
        if self._total>0:
            self.pb.setValue(self._total); self.pb.setFormat(f"{self._total} / {self._total}  (100%)")
        else:
            self.pb.setRange(0,100); self.pb.setValue(100); self.pb.setFormat("Done")
        self.cancel_btn.setVisible(False)
        if msg: self.label.setText(msg)
        qc,qg,qw=_qt(); qc.QTimer.singleShot(5000, lambda: self.w.setVisible(False))
    def tick(self, current, total):
        """Thread-safe. Call from any thread."""
        qc,qg,qw=_qt()
        qc.QTimer.singleShot(0, lambda c=current,t=total: self._do_tick(c,t))
    def _do_tick(self, current, total):
        if not self.w.isVisible(): return
        if total>0:
            self._total=total; self.pb.setRange(0,total)
            self.pb.setValue(min(current,total))
            pct=int(current/total*100) if total else 0
            self.pb.setFormat(f"{current} / {total}  ({pct}%)")
            self.label.setText(f"Phase 2/2: Organizing... {current}/{total} files ({pct}%)")
        else:
            elapsed=int(__import__("time").time()-self._start)
            self.label.setText(f"Phase 1/2: Scanning files... ({elapsed}s)")
    def _cancel(self):
        _cancel_all()
        self.label.setText("Cancelling..."); self.cancel_btn.setEnabled(False)

# ═══════════════════════════════════════════
# CustomPatternDialog
# ═══════════════════════════════════════════

class CustomPatternDialog:
    def __init__(self, parent, lang):
        qc,qg,qw=_qt(); self.dlg=qw.QDialog(parent)
        self.dlg.setWindowTitle(_("organize.custom_title",lang)); self.dlg.setMinimumSize(540,400)
        lo=qw.QVBoxLayout(self.dlg); lo.setSpacing(12); lo.setContentsMargins(20,20,20,20)
        lo.addWidget(_lbl(_("organize.custom_help",lang)))
        self.edit=qw.QLineEdit(); self.edit.setText("{year}/{year_month_day}")
        lo.addWidget(self.edit)
        lo.addWidget(_lbl(_("organize.custom_tokens",lang),"cardTitle"))
        lo.addWidget(_lbl(_("organize.custom_desc",lang),"cardSub"))
        self.preview=qw.QLabel(); self.preview.setObjectName("previewLabel")
        self._up(); self.edit.textChanged.connect(self._up); lo.addWidget(self.preview)
        br=_hb(sp=8); br.addStretch(1)
        cancel=_btn("Cancel","secondaryBtn"); cancel.clicked.connect(self.dlg.reject)
        save=_btn(_("organize.custom_save",lang),"primaryBtn"); save.clicked.connect(self.dlg.accept)
        br.addWidget(cancel); br.addWidget(save); lo.addLayout(br)
    def _up(self):
        p=self.edit.text()
        self.preview.setText(f"📂  Target/{p}/IMG_0001.jpg".replace("{year}","2025").replace("{month}","07").replace("{month_name}","July").replace("{month_name_de}","Juli").replace("{day}","15").replace("{year_month}","2025-07").replace("{year_month_day}","2025-07-15").replace("{source_name}","Photos"))
    def exec_(self):
        if self.dlg.exec()==_qt()[2].QDialog.DialogCode.Accepted: return self.edit.text()
        return None

# ═══════════════════════════════════════════
# PAGES
# ═══════════════════════════════════════════

class DashboardPage:
    def __init__(self,shell): self.shell=shell; self.stat_labels={}; self._scanning=False
    def build(self):
        qc,qg,qw=_qt(); lang=_ls().get("language","en"); s=_ls()
        w=qw.QWidget(); scroll=qw.QScrollArea(); scroll.setWidgetResizable(True)
        cw=qw.QWidget(); self.lo=_vb(sp=24,margins=(32,28,32,28))

        # ── Hero ──
        hero=qw.QWidget(); hero.setObjectName("card"); hl=qw.QVBoxLayout(hero); hl.setSpacing(8)
        hl.addWidget(_lbl(f"{_('dashboard.welcome',lang)} 👋","pageTitle"))
        hl.addWidget(_lbl(_("dashboard.sub",lang),"cardSub"))
        if not _exiftool_ok():
            wr=qw.QWidget(); wr.setStyleSheet("background:#da36331a;border:1px solid #f8514966;border-radius:8px;padding:10px 14px;margin-top:8px")
            wrl=qw.QHBoxLayout(wr); wrl.setContentsMargins(0,0,0,0)
            wrl.addWidget(_lbl(_("exiftool.missing",lang),"cardSub"))
            dl=_btn(_("exiftool.dl",lang),"secondaryBtn")
            dl.clicked.connect(lambda: qg.QDesktopServices.openUrl(qc.QUrl("https://exiftool.org")))
            wrl.addWidget(dl); hl.addWidget(wr)
        self.lo.addWidget(hero)

        # ── Stack: onboarding or stats ──
        self.view_stack=qw.QStackedWidget()
        self.onboarding_w=self._build_onboarding(lang)
        self.stats_w=self._build_stats_section(lang)
        self.view_stack.addWidget(self.onboarding_w)
        self.view_stack.addWidget(self.stats_w)
        self.lo.addWidget(self.view_stack)

        # ── Quick actions ──
        self.lo.addWidget(_lbl(_("dashboard.quick",lang),"cardTitle"))
        ag=qw.QGridLayout(); ag.setSpacing(10)
        quick=[("organize","📁",_("dashboard.organize",lang)),("rename","✏️",_("dashboard.rename",lang)),("duplicates","🔍",_("dashboard.find_dups",lang)),("people","👤",_("dashboard.face",lang))]
        for i,(pid,icon,label) in enumerate(quick):
            b=qw.QPushButton(f"  {icon}  {label}"); b.setCursor(qg.QCursor(qc.Qt.CursorShape.PointingHandCursor)); b.setMinimumHeight(52)
            b.setStyleSheet("QPushButton{background:#161b22;border:1px solid #30363d;border-radius:10px;padding:12px 16px;text-align:left;font-size:13px;font-weight:500;color:#c9d1d9}QPushButton:hover{background:#1c2128;border-color:#58a6ff;color:#e6edf3}")
            b.clicked.connect(lambda _,p=pid: self.shell.navigate(p)); ag.addWidget(b,i//2,i%2)
        self.lo.addLayout(ag)
        self.lo.addStretch(1); cw.setLayout(self.lo); scroll.setWidget(cw)

        src=s.get("source_dir","")
        if src and Path(src).exists():
            self._show_stats(lang); self._start_scan(lang)
        else:
            self._show_onboarding()
        return scroll

    # ── Onboarding ──
    def _build_onboarding(self,lang):
        qc,qg,qw=_qt(); s=_ls()
        card=qw.QWidget(); card.setObjectName("card"); cl=qw.QVBoxLayout(card); cl.setSpacing(18)

        cl.addWidget(_lbl(_("onboarding.title",lang),"pageTitle"))
        cl.addWidget(_lbl(_("onboarding.sub",lang),"cardSub"))

        # Folder picker
        fr=qw.QWidget(); fr.setStyleSheet("#onFolderRow{background:#0d1117;border:1px solid #30363d;border-radius:8px;padding:4px 4px 4px 14px}"); fr.setObjectName("onFolderRow")
        frl=qw.QHBoxLayout(fr); frl.setContentsMargins(0,0,0,0); frl.setSpacing(8)
        self.on_folder=qw.QLineEdit(); self.on_folder.setPlaceholderText(_("onboarding.folder_hint",lang))
        self.on_folder.setMinimumHeight(40); frl.addWidget(self.on_folder,1)
        br=_btn(_("onboarding.browse",lang),"secondaryBtn")
        br.clicked.connect(lambda: self._browse_onboarding())
        frl.addWidget(br); cl.addWidget(fr)

        # Folder validation
        self.on_status=qw.QLabel(""); self.on_status.setStyleSheet("font-size:13px;color:#8b949e"); cl.addWidget(self.on_status)
        self.on_folder.textChanged.connect(lambda: self._validate_onboarding_folder())

        # Media type checkboxes
        cl.addWidget(_lbl(_("onboarding.media_types",lang),"cardTitle"))
        cbr=_hb(sp=20)
        self.cb_img=qw.QCheckBox(_("onboarding.images",lang)); self.cb_img.setChecked(True); cbr.addWidget(self.cb_img)
        self.cb_vid=qw.QCheckBox(_("onboarding.videos",lang)); self.cb_vid.setChecked(True); cbr.addWidget(self.cb_vid)
        self.cb_mus=qw.QCheckBox(_("onboarding.music",lang)); self.cb_mus.setChecked(True); cbr.addWidget(self.cb_mus)
        cbr.addStretch(1); cl.addLayout(cbr)

        # Scope: separate vs together
        self.scope_card=qw.QWidget(); self.scope_card.setObjectName("card")
        scope_card_style="background:#0d1117;border:1px solid #30363d;border-radius:8px;padding:12px 16px"
        self.scope_card.setStyleSheet(scope_card_style)
        scl=qw.QVBoxLayout(self.scope_card); scl.setSpacing(6)
        scl.addWidget(_lbl(_("onboarding.scope",lang),"cardTitle"))
        self.rb_together=qw.QRadioButton(_("onboarding.scope_together",lang))
        self.rb_separate=qw.QRadioButton(_("onboarding.scope_separate",lang))
        self.rb_separate.setChecked(True)
        scl.addWidget(self.rb_together); scl.addWidget(self.rb_separate)
        cl.addWidget(self.scope_card)

        # Start button
        sr=_hb(sp=12)
        self.start_btn=_btn(_("onboarding.start",lang),"primaryBtn"); self.start_btn.setMinimumHeight(44)
        self.start_btn.clicked.connect(lambda: self._on_start(lang))
        sr.addWidget(self.start_btn); sr.addStretch(1); cl.addLayout(sr)

        return card

    def _browse_onboarding(self):
        qc,qg,qw=_qt(); p=qw.QFileDialog.getExistingDirectory(None,_("onboarding.browse",_ls().get("language","en")))
        if p: self.on_folder.setText(p)

    def _validate_onboarding_folder(self):
        p=Path(self.on_folder.text().strip())
        if p.exists() and p.is_dir():
            try: cnt=sum(1 for _ in p.iterdir()); self.on_status.setText(f"✅  {cnt} items found"); self.on_status.setStyleSheet("font-size:13px;color:#3fb950")
            except: self.on_status.setText("✅  Directory exists"); self.on_status.setStyleSheet("font-size:13px;color:#3fb950")
        elif self.on_folder.text().strip(): self.on_status.setText("❌  Directory not found"); self.on_status.setStyleSheet("font-size:13px;color:#f85149")
        else: self.on_status.setText(""); self.on_status.setStyleSheet("font-size:13px;color:#8b949e")

    def _show_onboarding(self):
        self._onboarding=True; self.view_stack.setCurrentIndex(0)
        s=_ls(); self.on_folder.setText(s.get("source_dir",""))
        if s.get("source_dir"): self._validate_onboarding_folder()

    def _on_start(self,lang):
        folder=self.on_folder.text().strip()
        if not folder or not Path(folder).exists(): return
        s=_ls(); s["source_dir"]=folder
        scope="together" if self.rb_together.isChecked() else "separate"
        s["media_scope"]=scope
        _ss(s)
        # Switch to stats view
        self._show_stats(lang)
        self.shell.set_status(_("onboarding.scanning",lang))
        self._start_scan(lang)

    # ── Stats section ──
    def _build_stats_section(self,lang):
        qc,qg,qw=_qt()
        w=qw.QWidget(); lo=_vb(sp=14)

        # 3x2 stat grid
        grid=qw.QGridLayout(); grid.setSpacing(14)
        stat_defs=[
            ("🖼️",_("dashboard.images",lang)),("🎬",_("dashboard.videos",lang)),
            ("🎵",_("dashboard.music",lang)),("📂",_("dashboard.subdirs",lang)),
            ("🗂️",_("dashboard.org_files",lang)),("🔧",_("dashboard.exif",lang)),
        ]
        self.stat_labels={}
        for i,(icon,title) in enumerate(stat_defs):
            c=qw.QWidget(); c.setObjectName("card"); cl=qw.QVBoxLayout(c); cl.setSpacing(8)
            ir=qw.QHBoxLayout(); ir.setSpacing(10)
            ic=qw.QLabel(icon); ic.setStyleSheet("font-size:22px;background:transparent"); ir.addWidget(ic)
            if i==5:
                vl=qw.QLabel("—"); vl.setStyleSheet("font-size:30px")
            else:
                vl=qw.QLabel("..."); vl.setObjectName("cardValue"); vl.setStyleSheet("font-size:26px")
            ir.addWidget(vl); ir.addStretch(1); cl.addLayout(ir)
            cl.addWidget(_lbl(title,"cardTitle"))
            grid.addWidget(c,i//3,i%3)
            key=["images","videos","music","subdirs","organized","exif"][i]
            self.stat_labels[key]=vl
        lo.addLayout(grid)

        # Scanning indicator
        self.scan_status=qw.QLabel(""); self.scan_status.setStyleSheet("font-size:12px;color:#8b949e;padding:0 4px")
        lo.addWidget(self.scan_status)
        lo.addStretch(1); w.setLayout(lo)
        return w

    def _show_stats(self,lang):
        self._onboarding=False; self.view_stack.setCurrentIndex(1)
        # Show cached stats immediately
        s=_ls(); cached=s.get("last_stats",{})
        if cached:
            self._set_stat("images",cached.get("images",0),cached=True)
            self._set_stat("videos",cached.get("videos",0),cached=True)
            self._set_stat("music",cached.get("music",0),cached=True)
            self._set_stat("subdirs",cached.get("subdirs",0),cached=True)
            self._set_stat("organized",cached.get("organized",0),cached=True)
        et_ok=_exiftool_ok()
        self._set_exif_stat(et_ok)

    def _set_stat(self,key,value,cached=False):
        if key not in self.stat_labels: return
        lbl=self.stat_labels[key]
        if isinstance(value,int):
            if cached: lbl.setText(f"~{value:,}"); lbl.setStyleSheet("font-size:26px;color:#8b949e")
            else: lbl.setText(f"{value:,}"); lbl.setStyleSheet("font-size:26px")
        else:
            lbl.setText(str(value))

    def _set_exif_stat(self,ok):
        if "exif" not in self.stat_labels: return
        lbl=self.stat_labels["exif"]; lbl.setText("✓" if ok else "✗")
        lbl.setStyleSheet(f"font-size:30px;color:{'#3fb950' if ok else '#f85149'}")

    # ── Background scan ──
    def _start_scan(self,lang):
        if self._scanning: return
        self._scanning=True
        self.scan_status.setText(f"🔄 {_('dashboard.refreshing',lang)}...")
        s=_ls(); folder=s.get("source_dir","")
        threading.Thread(target=self._do_scan,args=(folder,lang),daemon=True).start()

    def _do_scan(self,folder,lang):
        qc,qg,qw=_qt()
        img_exts={'.jpg','.jpeg','.png','.gif','.webp','.bmp','.tiff','.tif','.heic','.raw','.cr2','.nef','.arw','.dng'}
        vid_exts={'.mp4','.mov','.avi','.mkv','.wmv','.webm','.mts','.m2ts'}
        mus_exts={'.mp3','.wav','.flac','.aac','.ogg','.wma','.m4a'}
        images=videos=music=subdirs=organized=0
        if folder and Path(folder).exists():
            try:
                for root,dirs,files in os.walk(folder):
                    dirs[:]=[d for d in dirs if not d.startswith('.')]
                    subdirs+=len(dirs)
                    for f in files:
                        ext=Path(f).suffix.lower()
                        if ext in img_exts: images+=1
                        elif ext in vid_exts: videos+=1
                        elif ext in mus_exts: music+=1
            except: pass
        tgt=_ls().get("target_dir","")
        if tgt and Path(tgt).exists():
            try: organized=_count_organized_fast(tgt)
            except: organized=0
        et_ok=_exiftool_ok()
        # Cache
        s=_ls(); s["last_stats"]={"images":images,"videos":videos,"music":music,"subdirs":subdirs,"organized":organized}
        _ss(s)
        def _update():
            self._set_stat("images",images); self._set_stat("videos",videos)
            self._set_stat("music",music); self._set_stat("subdirs",subdirs)
            self._set_stat("organized",organized); self._set_exif_stat(et_ok)
            self.scan_status.setText(f"✓ {_('status.ready',lang)}")
            self._scanning=False
        qc.QTimer.singleShot(0,_update)


# ═══ ORGANIZE ═══

class OrganizePage:
    def __init__(self,shell):
        self.shell=shell; self._tiles={}; self._mode="ym_name_day"; self._src_rows=[]

    def build(self):
        qc,qg,qw=_qt(); lang=_ls().get("language","en"); s=_ls()
        w=qw.QWidget(); scroll=qw.QScrollArea(); scroll.setWidgetResizable(True)
        cw=qw.QWidget(); lo=_vb(sp=16,margins=(28,24,28,24))
        lo.addWidget(_lbl(_("organize.title",lang),"pageTitle"))
        lo.addWidget(_lbl(_("organize.sub",lang),"pageSubtitle"))

        # ── Source folders ──
        src_card=qw.QWidget(); src_card.setObjectName("card")
        self.src_layout=qw.QVBoxLayout(src_card); self.src_layout.setSpacing(8)
        self.src_layout.addWidget(_lbl(_("organize.source_folders",lang),"cardTitle"))
        self._add_src_row(s.get("source_dir",""))
        add=qw.QWidget(); al=qw.QHBoxLayout(add); al.setContentsMargins(0,0,0,0)
        ab=_btn(_("organize.add_source",lang),"addBtn")
        ab.clicked.connect(lambda: self._add_src_row("")); al.addWidget(ab); al.addStretch(1)
        self.src_layout.addWidget(add)
        lo.addWidget(src_card)

        # ── Target ──
        tr,self.te=_folder_row(_("organize.target",lang),lang,"settings.tgt_hint","Select target folder"); lo.addLayout(tr)
        if s.get("target_dir"): self.te.setText(s["target_dir"])

        # ── Filter ──
        fk,self.mk=_media_filter(lang); lo.addLayout(fk)

        # ── Folder structure tiles ──
        grp=qw.QWidget(); grp.setObjectName("card"); gcl=qw.QVBoxLayout(grp); gcl.setSpacing(12)
        gcl.addWidget(_lbl(_("organize.group_by",lang),"cardTitle"))
        tg=qw.QGridLayout(); tg.setSpacing(8)
        mn_tok = "{month_name}" if lang=="en" else "{month_name_de}"
        modes=[
            ("flat","📂",_("organize.flat",lang),"flat"),
            ("year","📅",_("organize.year",lang),"{year}"),
            ("ym","📁",_("organize.ym",lang),"{year}/{year_month}"),
            ("ymd","🗂️",_("organize.ymd",lang),"{year}/{year_month_day}"),
            ("ym_name","📆",_("organize.ym_month_name",lang),f"{{year}}/{mn_tok}"),
            ("ym_name_day","📋",_("organize.ym_name_day",lang),f"{{year}}/{mn_tok}/{{day}}"),
            ("ym_event","🏷️",_("organize.ym_event",lang),"ym_event"),
            ("custom","✏️",_("organize.custom_pattern",lang),"custom"),
        ]
        for i,(mode,icon,label,_pat) in enumerate(modes):
            tile=qw.QPushButton(f"{icon}\n{label}"); tile.setObjectName("optionTile")
            tile.setCheckable(True); tile.setMinimumSize(100,72)
            tile.setCursor(qg.QCursor(qc.Qt.CursorShape.PointingHandCursor))
            tile.clicked.connect(lambda checked,m=mode: self._sel_mode(m))
            col=i%4 if i<4 else i%4 if i<8 else i-8
            row=i//4
            tg.addWidget(tile,row,col)
            self._tiles[mode]=tile
        self._tiles["ym_name_day"].setChecked(True); self._tiles["ym_name_day"].setProperty("selected","true")
        self._tiles["ym_name_day"].style().unpolish(self._tiles["ym_name_day"])
        self._tiles["ym_name_day"].style().polish(self._tiles["ym_name_day"])
        gcl.addLayout(tg)

        # Event name (ym_event only)
        self.ev_row=qw.QWidget(); erl=qw.QHBoxLayout(self.ev_row); erl.setContentsMargins(0,0,0,0); erl.setSpacing(8)
        erl.addWidget(_lbl(_("organize.event_name",lang)))
        self.ev_name=qw.QLineEdit(); self.ev_name.setPlaceholderText(_("organize.event_placeholder",lang))
        self.ev_name.setMinimumWidth(240); erl.addWidget(self.ev_name); erl.addStretch(1)
        self.ev_row.setVisible(False); gcl.addWidget(self.ev_row)
        lo.addWidget(grp)

        # ── Mode: Copy / Move ──
        mc=qw.QWidget(); mc.setObjectName("card"); mcl=qw.QVBoxLayout(mc); mcl.setSpacing(10)
        mcl.addWidget(_lbl(_("organize.mode",lang),"cardTitle"))
        mr=_hb(sp=8)
        self.rb_move=qw.QRadioButton(_("organize.move",lang)); self.rb_copy=qw.QRadioButton(_("organize.copy",lang))
        org_mode=s.get("organize_mode","move")
        self.rb_move.setChecked(org_mode!="copy"); self.rb_copy.setChecked(org_mode=="copy")
        mr.addWidget(self.rb_move); mr.addWidget(self.rb_copy); mr.addStretch(1); mcl.addLayout(mr)
        lo.addWidget(mc)

        # ── Options ──
        oc=qw.QWidget(); oc.setObjectName("card"); ocl=qw.QVBoxLayout(oc); ocl.setSpacing(10)
        ocl.addWidget(_lbl(_("organize.options",lang),"cardTitle"))
        opts=_hb(sp=16)
        self.cb_del=qw.QCheckBox(_("organize.delete_empty",lang))
        self.cb_del.setChecked(s.get("delete_empty",False))
        opts.addWidget(self.cb_del)
        opts.addSpacing(20); opts.addWidget(_lbl(_("organize.conflict",lang)))
        self.conf=qw.QComboBox()
        self.conf.addItems([_("organize.conflict_skip",lang),_("organize.conflict_rename",lang)])
        opts.addWidget(self.conf); opts.addStretch(1); ocl.addLayout(opts)
        lo.addWidget(oc)

        # ── Preview ──
        self.prev=qw.QLabel(); self.prev.setObjectName("previewLabel"); lo.addWidget(self.prev)

        # ── Progress ──
        self.prog=ProgressWidget(); lo.addWidget(self.prog.w)

        # ── Buttons ──
        br=_hb(sp=12)
        self.pv_btn=_btn(_("organize.preview",lang),"secondaryBtn")
        self.ap_btn=_btn(_("organize.apply",lang),"primaryBtn")
        br.addWidget(self.pv_btn); br.addWidget(self.ap_btn); br.addStretch(1); lo.addLayout(br)
        self.res=qw.QTextEdit(); self.res.setReadOnly(True); self.res.setMaximumHeight(250); lo.addWidget(self.res)

        self.pv_btn.clicked.connect(lambda: self._preview(lang))
        self.ap_btn.clicked.connect(lambda: self._apply(lang))
        self.te.textChanged.connect(lambda: self._update_preview(lang))
        self.ev_name.textChanged.connect(lambda: self._update_preview(lang))

        lo.addStretch(1); cw.setLayout(lo); scroll.setWidget(cw); self._update_preview(lang)
        return scroll

    def _add_src_row(self,text=""):
        qc,qg,qw=_qt(); lang=_ls().get("language","en")
        row=qw.QWidget(); row.setObjectName("sourceRow"); rl=qw.QHBoxLayout(row); rl.setContentsMargins(0,0,0,0); rl.setSpacing(6)
        edit=qw.QLineEdit(text); edit.setPlaceholderText(_("settings.src_hint",lang)); edit.setMinimumHeight(34)
        status=qw.QLabel(); status.setFixedWidth(22); status.setStyleSheet("font-size:13px")
        rl.addWidget(edit,1); rl.addWidget(status); rl.addWidget(_browse_btn(edit,"Select source folder"))
        if len(self._src_rows)>0:
            rm=_btn("✕","removeBtn")
            rm.clicked.connect(lambda: self._rm_src(row)); rl.addWidget(rm)
        def _validate():
            p=Path(edit.text().strip())
            if p.exists() and p.is_dir():
                try: has=any(True for _ in os.scandir(p)); status.setText("✅" if has else "📂"); status.setToolTip(f"Path exists" + (", has files" if has else ", empty"))
                except: status.setText("📂"); status.setToolTip("Path exists")
            elif edit.text().strip(): status.setText("❌"); status.setToolTip("Path does not exist")
            else: status.setText(""); status.setToolTip("")
        edit.textChanged.connect(lambda: (_validate(), self._update_preview(lang)))
        idx=self.src_layout.count()-1
        self.src_layout.insertWidget(idx,row); self._src_rows.append((row,edit)); _validate()

    def _rm_src(self,row):
        self.src_layout.removeWidget(row); row.deleteLater()
        self._src_rows=[(r,e) for r,e in self._src_rows if r is not row]
        self._update_preview(_ls().get("language","en"))

    def _sources(self):
        return [e.text().strip() for _,e in self._src_rows if e.text().strip()]

    def _sel_mode(self,mode):
        self._mode=mode
        for m,tile in self._tiles.items():
            tile.setChecked(m==mode); tile.setProperty("selected","true" if m==mode else "false")
            tile.style().unpolish(tile); tile.style().polish(tile)
        self.ev_row.setVisible(mode=="ym_event")
        if mode=="custom":
            lang=_ls().get("language","en")
            dlg=CustomPatternDialog(self.shell.window,lang)
            pat=dlg.exec_()
            if pat: self._mode=pat
            else:
                self._mode="ym_name_day"
                self._tiles["ym_name_day"].setChecked(True); self._tiles["ym_name_day"].setProperty("selected","true")
                self._tiles["ym_name_day"].style().unpolish(self._tiles["ym_name_day"])
                self._tiles["ym_name_day"].style().polish(self._tiles["ym_name_day"])
        self._update_preview(_ls().get("language","en"))

    def _build_pat(self):
        mode=self._mode; lang=_ls().get("language","en")
        if "{" in mode and "}" in mode: return mode
        mn_tok="{month_name}" if lang=="en" else "{month_name_de}"
        patterns={"flat":"flat","year":"{year}","ym":"{year}/{year_month}",
                  "ymd":"{year}/{year_month_day}","ym_name":f"{{year}}/{mn_tok}",
                  "ym_name_day":f"{{year}}/{mn_tok}/{{day}}"}
        if mode in patterns: return patterns[mode]
        if mode=="ym_event":
            ev=self.ev_name.text().strip() or "Event"
            return f"{{year}}/{{year_month}}-{ev}"
        return "{year}/{year_month}"

    def _update_preview(self,lang):
        tgt=self.te.text().strip()
        tn=f"/{Path(tgt).name}" if tgt and Path(tgt).name else "/Target"
        p=self._build_pat()
        p=p.replace("{year}","2025").replace("{month}","07")
        p=p.replace("{month_name}","July").replace("{month_name_de}","Juli")
        p=p.replace("{day}","15").replace("{year_month}","2025-07")
        p=p.replace("{year_month_day}","2025-07-15").replace("{source_name}","Photos")
        if self.ev_name.text().strip():
            p=p.replace(self.ev_name.text().strip(),self.ev_name.text().strip())
        self.prev.setText(f"📂  {tn}/{p}/IMG_0001.jpg")

    def _preview(self,lang):
        sources=self._sources(); tgt=self.te.text().strip()
        if not sources or not tgt: return
        pat=self._build_pat(); self.res.clear(); self.prog.show(_("status.scanning",lang), cancellable=True)
        self.pv_btn.setEnabled(False); self.ap_btn.setEnabled(False)
        self.shell.set_status(_("status.scanning",lang))
        def _run():
            try:
                from media_manager.core.organizer.planner import build_organize_dry_run, OrganizePlannerOptions
                source_paths=[Path(s) for s in sources]
                mode="move" if self.rb_move.isChecked() else "copy"
                patterns=_filter_patterns(self.mk)
                opts=OrganizePlannerOptions(source_dirs=tuple(source_paths), target_root=Path(tgt), pattern=pat, operation_mode=mode, include_patterns=patterns)
                plan=build_organize_dry_run(opts, progress_callback=lambda c,t: progress.tick(c,t))
                lines=[f"Files planned: {len(plan.entries)}"]
                for e in plan.entries[:30]:
                    sn=Path(e.source_path).name if e.source_path else "?"
                    lines.append(f"  {sn}  →  {e.target_relative_dir}/{Path(e.source_path).name}" if e.source_path else f"  → {e.target_relative_dir}")
                if len(plan.entries)>30: lines.append(f"  ... and {len(plan.entries)-30} more")
                txt="\n".join(lines)
                qc,qg,qw=_qt()
                qc.QTimer.singleShot(0,lambda:(
                    self.res.setPlainText(txt),self.prog.hide(_("status.done",lang)),
                    self.shell.set_status(_("status.ready",lang)),
                    self.pv_btn.setEnabled(True),self.ap_btn.setEnabled(True)))
            except Exception as e:
                _log_error(f"PREVIEW ERROR: {e}"); import traceback; _log_error(traceback.format_exc())
                qc,qg,qw=_qt()
                qc.QTimer.singleShot(0,lambda:(self.res.setPlainText(f"Error: {e}"),self.prog.hide(),self.shell.set_status(_("status.ready",lang)),self.pv_btn.setEnabled(True),self.ap_btn.setEnabled(True)))
        threading.Thread(target=_run,daemon=True).start()

    def _apply(self,lang):
        qc,qg,qw=_qt()
        sources=self._sources(); tgt=self.te.text().strip()
        _log_error(f"APPLY CALLED: sources={sources} tgt={tgt}")
        if not sources:
            _log_error("APPLY ABORT: no source"); qw.QMessageBox.warning(None,_("organize.apply",lang),"No source folder selected."); return
        if not tgt:
            _log_error("APPLY ABORT: no target"); qw.QMessageBox.warning(None,_("organize.apply",lang),"No target folder selected."); return
        pat=self._build_pat()
        mode_word=_("organize.move",lang).split("(")[0].strip().lower() if self.rb_move.isChecked() else _("organize.copy",lang).split("(")[0].strip().lower()
        src_list="\n".join(f"  • {s}" for s in sources[:5])
        if len(sources)>5: src_list+=f"\n  • ... and {len(sources)-5} more"
        ans=qw.QMessageBox.warning(None,_("organize.apply",lang),
            _("organize.apply_confirm",lang).format(mode=mode_word,sources=src_list,target=tgt),
            qw.QMessageBox.StandardButton.Yes|qw.QMessageBox.StandardButton.No)
        if ans!=qw.QMessageBox.StandardButton.Yes: return

        self.res.clear(); self.prog.show("Phase 1/2: Scanning files (reading dates)...", cancellable=False, total=0)
        self.pv_btn.setEnabled(False); self.ap_btn.setEnabled(False)
        self.shell.set_status("Phase 1/2: Scanning files...")

        cancel_ev=threading.Event(); progress=self.prog
        with _CANCEL_LOCK: _CANCEL_EVENTS[id(cancel_ev)]=cancel_ev

        def _run():
            try:
                from media_manager.core.organizer.planner import build_organize_dry_run, OrganizePlannerOptions
                from media_manager.core.organizer.executor import execute_organize_plan
                from media_manager.core.organizer.patterns import DEFAULT_ORGANIZE_PATTERN

                source_paths=[Path(s) for s in sources]
                mode="move" if self.rb_move.isChecked() else "copy"
                conflict="conflict" if self.conf.currentIndex()==0 else "skip"
                _log_error(f"BUILDING PLAN: sources={[str(s) for s in source_paths]} tgt={tgt} pat={pat} mode={mode}")

                patterns=_filter_patterns(self.mk)
                opts=OrganizePlannerOptions(
                    source_dirs=tuple(source_paths), target_root=Path(tgt), pattern=pat,
                    operation_mode=mode, conflict_policy=conflict, include_patterns=patterns,
                )
                plan=build_organize_dry_run(opts, progress_callback=lambda c,t: progress.tick(c,t))
                total=len(plan.entries)
                _log_error(f"ORGANIZE PLAN: {total} entries")
                if total==0:
                    qc.QTimer.singleShot(0,lambda:(self.res.setPlainText(_("organize.no_files",lang)),self.prog.hide(),self.shell.set_status(_("status.ready",lang)),self.pv_btn.setEnabled(True),self.ap_btn.setEnabled(True)))
                    return

                qc.QTimer.singleShot(0,lambda:(self.prog.show(f"0 / {total}  (0%)",cancellable=True,total=total),self.shell.set_status(f"Organizing {total} files...")))

                # Execute plan directly — no subprocess
                result=execute_organize_plan(plan)
                executed=sum(1 for e in result.entries if e.outcome in ("copied","moved"))
                progress.tick(total,total)
                _log_error(f"ORGANIZE DONE: {executed} files")

                del_msg=""
                if self.cb_del.isChecked():
                    deleted=0
                    for src in sources:
                        sp=Path(src)
                        if sp.exists():
                            try:
                                for d in sorted(sp.rglob('*'),reverse=True):
                                    if d.is_dir() and not any(d.iterdir()): d.rmdir(); deleted+=1
                            except: pass
                    if deleted: del_msg="\n"+_("organize.empty_removed",lang).format(count=deleted)

                result_text=_("organize.done",lang).format(count=executed) if executed>0 else _("organize.no_files",lang)
                qc.QTimer.singleShot(0,lambda:(
                    self.res.setPlainText(result_text+del_msg),self.prog.hide(_("status.done",lang)),
                    self.shell.set_status(_("status.ready",lang)),
                    self.pv_btn.setEnabled(True),self.ap_btn.setEnabled(True)))
            except Exception as e:
                _log_error(f"ORGANIZE CRASH: {e}")
                import traceback
                _log_error(traceback.format_exc())
                qc.QTimer.singleShot(0,lambda:(
                    self.res.setPlainText(_("organize.error",lang).format(error=str(e))),
                    self.prog.hide(),self.shell.set_status(_("status.ready",lang)),
                    self.pv_btn.setEnabled(True),self.ap_btn.setEnabled(True)))
        threading.Thread(target=_run,daemon=True).start()


# ═══ RENAME ═══

class RenamePage:
    def __init__(self,shell): self.shell=shell
    def build(self):
        qc,qg,qw=_qt(); lang=_ls().get("language","en")
        w=qw.QWidget(); scroll=qw.QScrollArea(); scroll.setWidgetResizable(True)
        cw=qw.QWidget(); lo=_vb(sp=20,margins=(28,24,28,24))
        lo.addWidget(_lbl(_("rename.title",lang),"pageTitle"))
        lo.addWidget(_lbl(_("rename.sub",lang),"pageSubtitle"))
        sr,self.se=_folder_row(_("rename.src",lang),lang); lo.addLayout(sr)
        fk,self.mk=_media_filter(lang); lo.addLayout(fk)
        card=qw.QWidget(); card.setObjectName("card"); cl=qw.QVBoxLayout(card); cl.setSpacing(14)
        cl.addWidget(_lbl(_("rename.include",lang),"cardTitle"))
        self.cb_date=qw.QCheckBox(_("rename.date",lang)); self.cb_date.setChecked(True)
        self.cb_orig=qw.QCheckBox(_("rename.original",lang)); self.cb_orig.setChecked(True)
        self.cb_cam=qw.QCheckBox(_("rename.camera",lang))
        self.cb_cnt=qw.QCheckBox(_("rename.counter",lang))
        cl.addWidget(self.cb_date); cl.addWidget(self.cb_orig); cl.addWidget(self.cb_cam); cl.addWidget(self.cb_cnt)
        df=qw.QHBoxLayout(); df.setSpacing(8); df.addWidget(_lbl(_("rename.date_format",lang)))
        self.dfmt=qw.QComboBox(); self.dfmt.addItems(["2025-07-15","20250715","2025_07_15","Jul-15-2025","15-07-2025"])
        self.dfmt.setMinimumWidth(150); df.addWidget(self.dfmt); df.addStretch(1); cl.addLayout(df)
        sf=qw.QHBoxLayout(); sf.setSpacing(8); sf.addWidget(_lbl(_("rename.separator",lang)))
        self.sep=qw.QComboBox(); self.sep.addItems(["_ (underscore)","- (dash)","  (space)"]); self.sep.setMinimumWidth(150)
        sf.addWidget(self.sep); sf.addStretch(1); cl.addLayout(sf)
        lo.addWidget(card)
        self.prev=qw.QLabel(); self.prev.setObjectName("previewLabel"); self._up_prev(); lo.addWidget(self.prev)
        for cb in[self.cb_date,self.cb_cam,self.cb_orig,self.cb_cnt]: cb.toggled.connect(self._up_prev)
        self.dfmt.currentIndexChanged.connect(self._up_prev); self.sep.currentIndexChanged.connect(self._up_prev)
        self.prog=ProgressWidget(); lo.addWidget(self.prog.w)
        br=_hb(sp=12)
        self.pv_btn=_btn(_("rename.preview",lang),"secondaryBtn")
        self.ap_btn=_btn(_("rename.apply",lang),"primaryBtn")
        br.addWidget(self.pv_btn); br.addWidget(self.ap_btn); br.addStretch(1); lo.addLayout(br)
        self.res=qw.QTextEdit(); self.res.setReadOnly(True); self.res.setMaximumHeight(250); lo.addWidget(self.res)
        self.pv_btn.clicked.connect(lambda: self._preview(lang))
        self.ap_btn.clicked.connect(lambda: self._apply(lang))
        s=_ls()
        if s.get("source_dir"): self.se.setText(s["source_dir"])
        lo.addStretch(1); cw.setLayout(lo); scroll.setWidget(cw)
        return scroll

    def _tmpl(self):
        parts=[]
        if self.cb_date.isChecked():
            fm=self.dfmt.currentText()
            m={"2025-07-15":"{date}","20250715":"{date|YYYYMMDD}","2025_07_15":"{date|YYYY_MM_DD}","Jul-15-2025":"{date|MMM-DD-YYYY}","15-07-2025":"{date|DD-MM-YYYY}"}
            parts.append(m.get(fm,"{date}"))
        if self.cb_cam.isChecked(): parts.append("{camera}")
        if self.cb_orig.isChecked(): parts.append("{original_name}")
        if self.cb_cnt.isChecked(): parts.append("{index:03d}")
        if not parts: parts.append("{original_name}")
        sepidx=self.sep.currentIndex(); sep={0:"_",1:"-",2:" "}[sepidx]
        return sep.join(parts)

    def _up_prev(self):
        sepidx=self.sep.currentIndex(); sep={0:"_",1:"-",2:" "}[sepidx]
        parts=[]
        if self.cb_date.isChecked(): parts.append("2025-07-15")
        if self.cb_cam.isChecked(): parts.append("Canon_EOS")
        if self.cb_orig.isChecked(): parts.append("IMG_0001")
        if self.cb_cnt.isChecked(): parts.append("001")
        if not parts: parts.append("IMG_0001")
        self.prev.setText(f"📄  {sep.join(parts)}.jpg")

    def _preview(self,lang):
        src=self.se.text().strip()
        if not src: return
        tmpl=self._tmpl(); self.res.clear(); self.prog.show(_("status.scanning",lang), cancellable=True)
        self.pv_btn.setEnabled(False); self.ap_btn.setEnabled(False)
        def _run():
            try:
                from media_manager.core.renamer.planner import build_rename_dry_run, RenamePlannerOptions
                src_paths=tuple(Path(src) for src in [src] if Path(src).exists())
                if not src_paths:
                    qc,qg,qw=_qt(); qc.QTimer.singleShot(0,lambda:(self.res.setPlainText("Source not found."),self.prog.hide(),self.pv_btn.setEnabled(True),self.ap_btn.setEnabled(True))); return
                patterns=_filter_patterns(self.mk)
                opts=RenamePlannerOptions(source_dirs=src_paths, template=tmpl, include_patterns=patterns)
                plan=build_rename_dry_run(opts)
                lines=[f"Files planned: {len(plan.entries)}"]
                for e in plan.entries[:30]:
                    sn=Path(e.source_path).name if e.source_path else "?"
                    lines.append(f"  {sn}  →  {e.rendered_name or '?'}.jpg")
                if len(plan.entries)>30: lines.append(f"  ... and {len(plan.entries)-30} more")
                txt="\n".join(lines)
                qc,qg,qw=_qt()
                qc.QTimer.singleShot(0,lambda:(self.res.setPlainText(txt),self.prog.hide(),self.pv_btn.setEnabled(True),self.ap_btn.setEnabled(True)))
            except Exception as e:
                _log_error(f"RENAME PREVIEW ERROR: {e}"); import traceback; _log_error(traceback.format_exc())
                qc,qg,qw=_qt()
                qc.QTimer.singleShot(0,lambda:(self.res.setPlainText(f"Error: {e}"),self.prog.hide(),self.pv_btn.setEnabled(True),self.ap_btn.setEnabled(True)))
        threading.Thread(target=_run,daemon=True).start()

    def _apply(self,lang):
        qc,qg,qw=_qt(); src=self.se.text().strip()
        if not src:
            qw.QMessageBox.warning(None,_("rename.apply",lang),"No source folder selected."); return
        tmpl=self._tmpl()
        ans=qw.QMessageBox.warning(None,_("rename.apply",lang),_(f"rename.apply_confirm",lang).format(src=src),qw.QMessageBox.StandardButton.Yes|qw.QMessageBox.StandardButton.No)
        if ans!=qw.QMessageBox.StandardButton.Yes: return
        self.res.clear(); self.prog.show("Building plan...", cancellable=False, total=0)
        self.pv_btn.setEnabled(False); self.ap_btn.setEnabled(False)
        self.shell.set_status("Building rename plan...")
        cancel_ev=threading.Event(); progress=self.prog
        with _CANCEL_LOCK: _CANCEL_EVENTS[id(cancel_ev)]=cancel_ev
        def _run():
            try:
                from media_manager.core.renamer.planner import build_rename_dry_run, RenamePlannerOptions
                from media_manager.core.renamer.executor import execute_rename_dry_run
                src_paths=tuple(Path(src) for src in [src] if Path(src).exists())
                if not src_paths:
                    qc.QTimer.singleShot(0,lambda:(self.res.setPlainText("Source folder not found."),self.prog.hide(),self.shell.set_status(_("status.ready",lang)),self.pv_btn.setEnabled(True),self.ap_btn.setEnabled(True)))
                    return
                patterns=_filter_patterns(self.mk)
                opts=RenamePlannerOptions(source_dirs=src_paths, template=tmpl, include_patterns=patterns)
                plan=build_rename_dry_run(opts)
                total=len(plan.entries)
                _log_error(f"RENAME PLAN: {total} entries")
                if total==0:
                    qc.QTimer.singleShot(0,lambda:(self.res.setPlainText("No files to rename."),self.prog.hide(),self.shell.set_status(_("status.ready",lang)),self.pv_btn.setEnabled(True),self.ap_btn.setEnabled(True)))
                    return
                qc.QTimer.singleShot(0,lambda:(self.prog.show(f"0 / {total}  (0%)",cancellable=True,total=total),self.shell.set_status(f"Renaming {total} files...")))
                result=execute_rename_dry_run(plan, apply=True)
                executed=sum(1 for e in result.entries if getattr(e,"outcome",None)=="renamed")
                progress.tick(total,total)
                _log_error(f"RENAME DONE: {executed} files")
                result_text=_("rename.done",lang).format(count=executed) if executed>0 else "No files renamed."
                qc.QTimer.singleShot(0,lambda:(self.res.setPlainText(result_text),self.prog.hide(_("status.done",lang)),self.shell.set_status(_("status.ready",lang)),self.pv_btn.setEnabled(True),self.ap_btn.setEnabled(True)))
            except Exception as e:
                _log_error(f"RENAME CRASH: {e}"); import traceback; _log_error(traceback.format_exc())
                qc.QTimer.singleShot(0,lambda:(self.res.setPlainText(_("rename.error",lang).format(error=str(e))),self.prog.hide(),self.shell.set_status(_("status.ready",lang)),self.pv_btn.setEnabled(True),self.ap_btn.setEnabled(True)))
        threading.Thread(target=_run,daemon=True).start()


# ═══ DUPLICATES ═══

class DuplicatesPage:
    def __init__(self,shell): self.shell=shell; self.scan_result=None; self.sim_result=None; self.data=None; self.sim=None
    def build(self):
        qc,qg,qw=_qt(); lang=_ls().get("language","en")
        w=qw.QWidget(); scroll=qw.QScrollArea(); scroll.setWidgetResizable(True)
        cw=qw.QWidget(); lo=_vb(sp=20,margins=(28,24,28,24))
        lo.addWidget(_lbl(_("duplicates.title",lang),"pageTitle"))
        lo.addWidget(_lbl(_("duplicates.sub",lang),"pageSubtitle"))
        sr,self.se=_folder_row(_("duplicates.src",lang),lang); lo.addLayout(sr)
        fr=_hb(sp=16); fk,self.mk=_media_filter(lang); fr.addLayout(fk); fr.addStretch(1)
        self.sb=_btn(_("duplicates.scan",lang),"primaryBtn"); fr.addWidget(self.sb); lo.addLayout(fr)
        self.prog=ProgressWidget(); lo.addWidget(self.prog.w)
        self.stack=qw.QStackedWidget()
        e=qw.QWidget(); el=_vb(sp=8,margins=(40,40,40,40))
        el.addWidget(_lbl("Select a folder and click Scan.","cardSub"),alignment=qc.Qt.AlignmentFlag.AlignCenter)
        e.setLayout(el); self.stack.addWidget(e); lo.addWidget(self.stack,1)
        # Action controls (hidden until scan)
        self.action_card=qw.QWidget(); self.action_card.setObjectName("card"); self.action_card.setVisible(False)
        acl=qw.QVBoxLayout(self.action_card); acl.setSpacing(14)
        acl.addWidget(_lbl(_("duplicates.cleanup",lang),"cardTitle"))
        # Keep policy
        kr=_hb(sp=12); kr.addWidget(_lbl(_("duplicates.keep_policy",lang)))
        self.kp=qw.QComboBox(); self.kp.addItems([_("duplicates.keep_first",lang),_("duplicates.keep_newest",lang),_("duplicates.keep_oldest",lang)])
        kr.addWidget(self.kp); kr.addStretch(1); acl.addLayout(kr)
        # Operation mode
        or_=_hb(sp=16); or_.addWidget(_lbl(_("duplicates.action_mode",lang)))
        self.rb_del=qw.QRadioButton(_("duplicates.delete",lang)); self.rb_move=qw.QRadioButton(_("duplicates.move_to",lang))
        self.rb_del.setChecked(True); or_.addWidget(self.rb_del); or_.addWidget(self.rb_move); or_.addStretch(1); acl.addLayout(or_)
        # Target folder (move only)
        self.move_row=qw.QWidget(); mrl=qw.QHBoxLayout(self.move_row); mrl.setContentsMargins(0,0,0,0); mrl.setSpacing(8)
        mrl.addWidget(_lbl(_("duplicates.target",lang)))
        self.move_edit=qw.QLineEdit(); self.move_edit.setMinimumHeight(34); self.move_edit.setPlaceholderText(_("settings.tgt_hint",lang))
        mrl.addWidget(self.move_edit,1); mrl.addWidget(_browse_btn(self.move_edit,"Select target folder"))
        self.move_row.setVisible(False); acl.addWidget(self.move_row)
        s=_ls()
        if s.get("target_dir"): self.move_edit.setText(s["target_dir"])
        self.rb_move.toggled.connect(lambda checked: self.move_row.setVisible(checked))
        # Apply button
        ar=_hb(sp=12)
        self.ap_btn=_btn(_("duplicates.apply",lang),"primaryBtn"); ar.addWidget(self.ap_btn); ar.addStretch(1); acl.addLayout(ar)
        lo.addWidget(self.action_card)
        self.res=qw.QTextEdit(); self.res.setReadOnly(True); self.res.setMaximumHeight(200); lo.addWidget(self.res)
        self.sb.clicked.connect(lambda: self._scan(lang))
        self.ap_btn.clicked.connect(lambda: self._apply(lang))
        if s.get("source_dir"): self.se.setText(s["source_dir"])
        lo.addStretch(1); cw.setLayout(lo); scroll.setWidget(cw)
        return scroll

    def _scan(self,lang):
        src=self.se.text().strip()
        if not src or not Path(src).exists(): return
        self.prog.show(_("status.scanning",lang), cancellable=True); self.sb.setEnabled(False)
        self.shell.set_status(_("status.scanning",lang))
        cancel_ev = threading.Event()
        with _CANCEL_LOCK: _CANCEL_EVENTS[id(cancel_ev)] = cancel_ev
        def _run():
            try:
                from media_manager.duplicates import DuplicateScanConfig, scan_exact_duplicates
                from media_manager.similar_images import scan_similar_images
                cfg=DuplicateScanConfig(source_dirs=[Path(src)])
                d=scan_exact_duplicates(cfg)
                self.scan_result=d
                try: s=scan_similar_images(source_dirs=[Path(src)])
                except Exception: s=None
                self.sim_result=s
                self.data={"scan":{
                    "exact_groups":len(d.exact_groups),
                    "duplicate_files":d.duplicate_files,
                    "extra_duplicates":d.extra_duplicates,
                },"review":{"groups":[{"group_id":g.files[0].name,"candidate_count":len(g.files),"file_size":g.file_size,"same_name":g.same_name} for g in d.exact_groups]}}
                if s:
                    self.sim={"similar_images":{"groups":[{"id":g.id,"similarity":g.similarity,"files":g.files} for g in s.groups]}}
                else: self.sim={}
                qc,qg,qw=_qt(); qc.QTimer.singleShot(0,lambda:(self._show(lang),self.sb.setEnabled(True),self.prog.hide(),self.shell.set_status(_("status.ready",lang))))
            except Exception as e:
                _log_error(f"DUPLICATES ERROR: {e}"); import traceback; _log_error(traceback.format_exc())
                qc,qg,qw=_qt(); qc.QTimer.singleShot(0,lambda:(self.sb.setEnabled(True),self.prog.hide()))
        threading.Thread(target=_run,daemon=True).start()

    def _show(self,lang):
        qc,qg,qw=_qt(); d=self.data or {}; s=self.sim or {}
        rw=qw.QWidget(); rl=_vb(sp=16)
        sc=d.get("scan",{}); eg=sc.get("exact_groups",0); ef=sc.get("duplicate_files",0); ed=sc.get("extra_duplicates",0)
        simd=s.get("similar_images",{}) if s else {}; sg=len(simd.get("groups",[]) or [])
        rl.addWidget(_lbl(_("duplicates.groups",lang).format(eg=eg,ef=ef,ed=ed,sg=sg),"cardSub"))
        if not eg and not sg: rl.addWidget(_lbl(_("duplicates.no_results",lang),"cardSub"))
        if eg:
            rl.addWidget(_lbl(_("duplicates.exact",lang),"cardTitle"))
            t=qw.QTableWidget(); gs=(d.get("review") or {}).get("groups",[]) or []
            t.setRowCount(min(len(gs),100)); t.setColumnCount(4)
            t.setHorizontalHeaderLabels([_("duplicates.table_group",lang),_("duplicates.table_files",lang),_("duplicates.table_size",lang),_("duplicates.table_name",lang)])
            for i,g in enumerate(gs[:100]):
                t.setItem(i,0,qw.QTableWidgetItem(str(g.get("group_id",""))[:40]))
                t.setItem(i,1,qw.QTableWidgetItem(str(g.get("candidate_count",0))))
                t.setItem(i,2,qw.QTableWidgetItem(str(g.get("file_size",0))))
                t.setItem(i,3,qw.QTableWidgetItem("Yes" if g.get("same_name") else "No"))
            t.resizeColumnsToContents(); rl.addWidget(t)
        if sg:
            rl.addWidget(_lbl(_("duplicates.similar",lang),"cardTitle"))
            t2=qw.QTableWidget(); gs2=simd.get("groups",[]) or []
            t2.setRowCount(min(len(gs2),50)); t2.setColumnCount(3)
            t2.setHorizontalHeaderLabels([_("duplicates.table_group",lang),"Similarity",_("duplicates.table_files",lang)])
            for i,g in enumerate(gs2[:50]):
                t2.setItem(i,0,qw.QTableWidgetItem(str(g.get("id",g.get("group_id","")))[:40]))
                sv=g.get("similarity",g.get("score",0))
                st=f"{sv:.1%}" if isinstance(sv,(int,float)) else str(sv) if sv else ""
                t2.setItem(i,1,qw.QTableWidgetItem(st))
                t2.setItem(i,2,qw.QTableWidgetItem(str(len(g.get("files",g.get("members",[]))) or g.get("count",0))))
            t2.resizeColumnsToContents(); rl.addWidget(t2)
            # Similar action row
            sim_act=_hb(sp=12)
            self.sim_clean_btn=_btn(_("duplicates.clean_similar",lang),"secondaryBtn")
            self.sim_clean_btn.clicked.connect(lambda: self._clean_similar(lang))
            sim_act.addWidget(self.sim_clean_btn)
            sim_act.addWidget(_lbl(_("duplicates.clean_similar_hint",lang),"cardSub"))
            sim_act.addStretch(1); rl.addLayout(sim_act)
        rl.addStretch(1); rw.setLayout(rl)
        while self.stack.count()>0: self.stack.removeWidget(self.stack.widget(0))
        self.stack.addWidget(rw)
        self.action_card.setVisible(eg > 0)

    def _apply(self,lang):
        qc,qg,qw=_qt()
        if not self.scan_result or not self.scan_result.exact_groups:
            qw.QMessageBox.information(None,_("duplicates.title",lang),_("duplicates.no_results",lang)); return
        policy_map={0:"first",1:"newest",2:"oldest"}
        keep_policy=policy_map[self.kp.currentIndex()]
        do_move=self.rb_move.isChecked()
        tgt=self.move_edit.text().strip() if do_move else None
        if do_move and not tgt:
            qw.QMessageBox.warning(None,_("duplicates.apply",lang),"No target folder selected."); return
        mode="move" if do_move else "delete"
        total_dupes=self.scan_result.duplicate_files
        action_word=_("duplicates.delete",lang) if not do_move else _("duplicates.move_to",lang)
        ans=qw.QMessageBox.warning(None,_("duplicates.apply",lang),
            _("duplicates.apply_confirm",lang).format(action=action_word,count=total_dupes,target=tgt or ""),
            qw.QMessageBox.StandardButton.Yes|qw.QMessageBox.StandardButton.No)
        if ans!=qw.QMessageBox.StandardButton.Yes: return
        self.res.clear(); self.prog.show(_("status.scanning",lang), cancellable=False)
        self.ap_btn.setEnabled(False); self.sb.setEnabled(False)
        self.shell.set_status("Cleaning up duplicates...")
        def _run():
            try:
                from media_manager.duplicate_workflow import build_duplicate_workflow_from_scan, execute_duplicate_workflow_bundle
                bundle=build_duplicate_workflow_from_scan(
                    self.scan_result, mode,
                    decision_policy=keep_policy,
                    target_root=Path(tgt) if tgt else None,
                )
                result=execute_duplicate_workflow_bundle(bundle, apply=True)
                executed=sum(1 for e in result.entries if getattr(e,"outcome",None) in ("deleted","moved"))
                _log_error(f"DUPLICATE CLEANUP DONE: {executed} files {mode}d")
                if do_move:
                    msg=_("duplicates.moved",lang).format(count=executed,target=tgt)
                else:
                    msg=_("duplicates.deleted",lang).format(count=executed)
                qc.QTimer.singleShot(0,lambda:(
                    self.res.setPlainText(msg),self.prog.hide(_("status.done",lang)),
                    self.ap_btn.setEnabled(True),self.sb.setEnabled(True),
                    self.shell.set_status(_("status.ready",lang))))
            except Exception as e:
                _log_error(f"DUPLICATE APPLY ERROR: {e}"); import traceback; _log_error(traceback.format_exc())
                qc.QTimer.singleShot(0,lambda:(
                    self.res.setPlainText(_("duplicates.error",lang).format(error=str(e))),
                    self.prog.hide(),self.ap_btn.setEnabled(True),self.sb.setEnabled(True),
                    self.shell.set_status(_("status.ready",lang))))
        threading.Thread(target=_run,daemon=True).start()

    def _clean_similar(self,lang):
        qc,qg,qw=_qt()
        if not self.sim_result or not self.sim_result.similar_groups:
            qw.QMessageBox.information(None,_("duplicates.title",lang),_("duplicates.no_similar",lang)); return
        groups=self.sim_result.similar_groups
        total_remove=sum(len(g.members) for g in groups)
        ans=qw.QMessageBox.warning(None,_("duplicates.clean_similar",lang),
            _("duplicates.clean_similar_confirm",lang).format(groups=len(groups),files=total_remove),
            qw.QMessageBox.StandardButton.Yes|qw.QMessageBox.StandardButton.No)
        if ans!=qw.QMessageBox.StandardButton.Yes: return
        self.res.clear(); self.prog.show("Trashing similar duplicates...", cancellable=False)
        self.sim_clean_btn.setEnabled(False); self.shell.set_status("Trashing similar duplicates...")
        def _run():
            try:
                from send2trash import send2trash
                trashed=0; errors=0
                for g in groups:
                    for m in g.members:
                        try:
                            if m.path.exists(): send2trash(str(m.path)); trashed+=1
                        except Exception: errors+=1
                _log_error(f"SIMILAR CLEAN: {trashed} trashed, {errors} errors")
                qc.QTimer.singleShot(0,lambda:(
                    self.res.setPlainText(_("duplicates.similar_done",lang).format(count=trashed,errors=errors)),
                    self.prog.hide(_("status.done",lang)),self.sim_clean_btn.setEnabled(True),
                    self.shell.set_status(_("status.ready",lang))))
            except Exception as e:
                _log_error(f"SIMILAR CLEAN ERROR: {e}"); import traceback; _log_error(traceback.format_exc())
                qc.QTimer.singleShot(0,lambda:(
                    self.res.setPlainText(_("duplicates.error",lang).format(error=str(e))),
                    self.prog.hide(),self.sim_clean_btn.setEnabled(True),
                    self.shell.set_status(_("status.ready",lang))))
        threading.Thread(target=_run,daemon=True).start()


# ═══ PEOPLE ═══

class PeoplePage:
    def __init__(self,shell): self.shell=shell; self.scan_result=None
    def build(self):
        qc,qg,qw=_qt(); lang=_ls().get("language","en")
        w=qw.QWidget(); scroll=qw.QScrollArea(); scroll.setWidgetResizable(True)
        cw=qw.QWidget(); lo=_vb(sp=20,margins=(28,24,28,24))
        lo.addWidget(_lbl(_("people.title",lang),"pageTitle"))
        lo.addWidget(_lbl(_("people.sub",lang),"pageSubtitle"))
        try:
            from media_manager.core.people_recognition import backend_available as _ba
            ok=_ba()
        except: ok=False
        if not ok:
            lo.addWidget(_lbl(_("people.missing",lang),"cardSub"))
            lo.addWidget(_lbl(_("people.install_hint",lang),"cardSub"))
        else:
            lo.addWidget(_lbl(_("people.backend_ok",lang),"cardSub"))
            sr,self.se=_folder_row(_("organize.src",lang),lang); lo.addLayout(sr)
            fr=_hb(sp=16); fk,self.mk=_media_filter(lang); fr.addLayout(fk); fr.addStretch(1)
            self.sb=_btn(_("people.scan",lang),"primaryBtn"); fr.addWidget(self.sb); lo.addLayout(fr)
            self.prog=ProgressWidget(); lo.addWidget(self.prog.w)
            # Results area — stacked: empty / results
            self.result_stack=qw.QStackedWidget()
            empty=qw.QWidget(); el2=_vb(sp=8,margins=(20,20,20,20))
            el2.addWidget(_lbl(_("people.hint",lang),"cardSub"),alignment=qc.Qt.AlignmentFlag.AlignCenter)
            empty.setLayout(el2); self.result_stack.addWidget(empty)
            self.result_w=qw.QWidget(); self.result_stack.addWidget(self.result_w)
            lo.addWidget(self.result_stack,1)
            self.sb.clicked.connect(lambda: self._scan(lang))
            s=_ls()
            if s.get("source_dir"): self.se.setText(s["source_dir"])
        lo.addStretch(1); cw.setLayout(lo); scroll.setWidget(cw)
        return scroll

    def _scan(self,lang):
        src=self.se.text().strip()
        if not src: return
        self.prog.show(_("people.scanning",lang), cancellable=True); self.sb.setEnabled(False)
        self.shell.set_status(_("people.scanning",lang))
        cancel_ev = threading.Event()
        with _CANCEL_LOCK: _CANCEL_EVENTS[id(cancel_ev)] = cancel_ev
        def _run():
            try:
                from media_manager.core.people_recognition import PeopleScanConfig, scan_people
                cfg=PeopleScanConfig(source_dirs=[Path(src)])
                r=scan_people(cfg); self.scan_result=r
                qc,qg,qw=_qt()
                qc.QTimer.singleShot(0,lambda:(self._show_results(r,lang),self.prog.hide(),self.sb.setEnabled(True),self.shell.set_status(_("status.ready",lang))))
            except Exception as e:
                _log_error(f"PEOPLE ERROR: {e}"); import traceback; _log_error(traceback.format_exc())
                qc,qg,qw=_qt()
                qc.QTimer.singleShot(0,lambda:(self._show_error(str(e),lang),self.prog.hide(),self.sb.setEnabled(True),self.shell.set_status(_("status.ready",lang))))
        threading.Thread(target=_run,daemon=True).start()

    def _show_results(self,r,lang):
        qc,qg,qw=_qt()
        # Clear old result widget
        if self.result_w:
            self.result_stack.removeWidget(self.result_w); self.result_w.deleteLater()
        rw=qw.QWidget(); rl=_vb(sp=14)

        # Summary card
        card=qw.QWidget(); card.setObjectName("card"); cl2=qw.QVBoxLayout(card); cl2.setSpacing(8)
        cl2.addWidget(_lbl(_("people.results",lang),"cardTitle"))
        cl2.addWidget(_lbl(f"📁 {_('people.files_scanned',lang)}: {r.scanned_files}  |  🙂 {_('people.faces_found',lang)}: {r.face_count}  |  ✅ {_('people.matched',lang)}: {r.matched_faces}  |  ❓ {_('people.unknown',lang)}: {r.unknown_faces}","cardSub"))
        if r.unknown_cluster_count:
            cl2.addWidget(_lbl(f"🔍 {_('people.clusters',lang)}: {r.unknown_cluster_count}","cardSub"))
        rl.addWidget(card)

        # Face detections table (top faces)
        if r.detections:
            limit=min(len(r.detections),50)
            t=qw.QTableWidget(); t.setRowCount(limit); t.setColumnCount(4)
            t.setHorizontalHeaderLabels([_("people.col_file",lang),_("people.col_person",lang),_("people.col_location",lang),_("people.col_conf",lang)])
            for i,d in enumerate(r.detections[:limit]):
                t.setItem(i,0,qw.QTableWidgetItem(str(Path(d.file_path).name)[:40]))
                t.setItem(i,1,qw.QTableWidgetItem(d.person_name or _("people.unnamed",lang)))
                t.setItem(i,2,qw.QTableWidgetItem(f"{d.box_left},{d.box_top} {d.box_width}x{d.box_height}" if hasattr(d,'box_left') else "—"))
                t.setItem(i,3,qw.QTableWidgetItem(f"{d.confidence:.0%}" if d.confidence else "—"))
            t.resizeColumnsToContents(); rl.addWidget(t)

        # CLI review button
        rev=_hb(sp=12)
        cli_btn=_btn(_("people.review_cli",lang),"primaryBtn")
        cli_btn.setToolTip(_("people.review_cli_tip",lang))
        cli_btn.clicked.connect(lambda: self._launch_cli_review(lang))
        rev.addWidget(cli_btn); rev.addStretch(1); rl.addLayout(rev)
        rl.addWidget(_lbl(_("people.cli_hint",lang),"cardSub"))

        rl.addStretch(1); rw.setLayout(rl)
        self.result_w=rw; self.result_stack.addWidget(rw); self.result_stack.setCurrentIndex(1)

    def _show_error(self,err,lang):
        qc,qg,qw=_qt()
        if self.result_w:
            self.result_stack.removeWidget(self.result_w); self.result_w.deleteLater()
        rw=qw.QWidget(); rl=_vb(sp=10)
        rl.addWidget(_lbl(f"❌ {err}","cardSub")); rl.addStretch(1); rw.setLayout(rl)
        self.result_w=rw; self.result_stack.addWidget(rw); self.result_stack.setCurrentIndex(1)

    def _launch_cli_review(self,lang):
        src=self.se.text().strip()
        if not src: return
        try:
            cmd=f'start "People Review" cmd /k "cd /d {Path.cwd()} && python -m media_manager people --source-dir \"{src}\""'
            subprocess.Popen(cmd, shell=True)
        except Exception as e:
            _log_error(f"CLI LAUNCH ERROR: {e}")


# ═══ TRIPS ═══

class TripsPage:
    def __init__(self,shell): self.shell=shell
    def build(self):
        qc,qg,qw=_qt(); lang=_ls().get("language","en")
        w=qw.QWidget(); scroll=qw.QScrollArea(); scroll.setWidgetResizable(True)
        cw=qw.QWidget(); lo=_vb(sp=20,margins=(28,24,28,24))
        lo.addWidget(_lbl(_("trips.title",lang),"pageTitle"))
        lo.addWidget(_lbl(_("trips.sub",lang),"pageSubtitle"))
        fm=qw.QWidget(); fm.setObjectName("card"); fl=qw.QVBoxLayout(fm); fl.setSpacing(14)
        nr=_hb(sp=8); nr.addWidget(_lbl(_("trips.name",lang)))
        self.tn=qw.QLineEdit(); self.tn.setPlaceholderText("e.g. Italy 2025"); nr.addWidget(self.tn); fl.addLayout(nr)
        sl,self.ts=_folder_row(_("trips.src",lang),lang); fl.addLayout(sl)
        tl,self.tt=_folder_row(_("trips.tgt",lang),lang); fl.addLayout(tl)
        dr=_hb(sp=12)
        dr.addWidget(_lbl(_("trips.start",lang)))
        self.sd=qw.QDateEdit(); self.sd.setCalendarPopup(True); self.sd.setDate(qc.QDate.currentDate().addYears(-1))
        dr.addWidget(self.sd); dr.addSpacing(20)
        dr.addWidget(_lbl(_("trips.end",lang)))
        self.ed=qw.QDateEdit(); self.ed.setCalendarPopup(True); self.ed.setDate(qc.QDate.currentDate())
        dr.addWidget(self.ed); dr.addStretch(1); fl.addLayout(dr)
        mr=_hb(sp=16); self.ml=qw.QRadioButton(_("trips.link",lang)); self.mc=qw.QRadioButton(_("trips.copy",lang))
        self.ml.setChecked(True); mr.addWidget(self.ml); mr.addWidget(self.mc); mr.addStretch(1); fl.addLayout(mr)
        self.cb=_btn(_("trips.create",lang),"primaryBtn"); fl.addWidget(self.cb)
        self.prog=ProgressWidget(); fl.addWidget(self.prog.w)
        self.res=qw.QTextEdit(); self.res.setReadOnly(True); self.res.setMaximumHeight(200); fl.addWidget(self.res)
        lo.addWidget(fm); lo.addStretch(1)
        self.cb.clicked.connect(lambda: self._create(lang))
        s=_ls()
        if s.get("source_dir"): self.ts.setText(s["source_dir"])
        if s.get("target_dir"): self.tt.setText(s["target_dir"])
        cw.setLayout(lo); scroll.setWidget(cw)
        return scroll

    def _create(self,lang):
        name=self.tn.text().strip(); src=self.ts.text().strip(); tgt=self.tt.text().strip()
        if not name or not src or not tgt: return
        start=self.sd.date().toString("yyyy-MM-dd"); end=self.ed.date().toString("yyyy-MM-dd")
        mode="link" if self.ml.isChecked() else "copy"
        self.res.clear(); self.prog.show(_("status.scanning",lang), cancellable=True); self.cb.setEnabled(False)
        def _run():
            try:
                from media_manager.core.workflows.trip import TripWorkflowOptions, build_trip_dry_run, execute_trip_plan
                from datetime import date as dt_date
                sdate=dt_date.fromisoformat(start); edate=dt_date.fromisoformat(end)
                opts=TripWorkflowOptions(source_dirs=[Path(src)],target_root=Path(tgt),label=name,start_date=sdate,end_date=edate,mode=mode)
                plan=build_trip_dry_run(opts)
                total=len(plan.entries)
                _log_error(f"TRIP PLAN: {total} entries")
                if total==0:
                    qc2,qg2,qw2=_qt()
                    qc2.QTimer.singleShot(0,lambda:(
                        self.res.setPlainText(_("trips.no_files",lang)),
                        self.prog.hide(),self.cb.setEnabled(True),
                        self.shell.set_status(_("status.ready",lang))))
                    return
                result=execute_trip_plan(plan, apply=True)
                executed=sum(1 for e in result.entries if getattr(e,"outcome",None) in ("linked","copied"))
                _log_error(f"TRIP DONE: {executed} files")
                qc2,qg2,qw2=_qt()
                msg=_("trips.created",lang).format(name=name,count=executed,target=tgt)
                qc2.QTimer.singleShot(0,lambda:(
                    self.res.setPlainText(msg),self.prog.hide(_("status.done",lang)),
                    self.cb.setEnabled(True),self.shell.set_status(_("status.ready",lang))))
            except Exception as e:
                _log_error(f"TRIP ERROR: {e}"); import traceback; _log_error(traceback.format_exc())
                qc2,qg2,qw2=_qt()
                qc2.QTimer.singleShot(0,lambda:(
                    self.res.setPlainText(_("trips.error",lang).format(error=str(e))),
                    self.prog.hide(),self.cb.setEnabled(True),
                    self.shell.set_status(_("status.ready",lang))))
        threading.Thread(target=_run,daemon=True).start()


# ═══ SETTINGS ═══

class SettingsPage:
    def __init__(self,shell): self.shell=shell
    def build(self):
        qc,qg,qw=_qt(); s=_ls(); lang=s.get("language","en")
        w=qw.QWidget(); scroll=qw.QScrollArea(); scroll.setWidgetResizable(True)
        cw=qw.QWidget(); lo=_vb(sp=18,margins=(28,24,28,24))
        lo.addWidget(_lbl(_("settings.title",lang),"pageTitle"))
        lo.addWidget(_lbl(_("settings.sub",lang),"pageSubtitle"))
        lf=qw.QWidget(); lf.setObjectName("card"); lfl=qw.QVBoxLayout(lf); lfl.setSpacing(10)
        lfl.addWidget(_lbl(_("settings.lang",lang),"cardTitle"))
        lr=_hb(sp=8)
        le=qw.QPushButton("🇺🇸 English"); ld=qw.QPushButton("🇩🇪 Deutsch")
        le.setCheckable(True); ld.setCheckable(True); le.setMinimumHeight(36); ld.setMinimumHeight(36)
        if lang=="en": le.setChecked(True)
        else: ld.setChecked(True)
        le.clicked.connect(lambda: self._sl("en")); ld.clicked.connect(lambda: self._sl("de"))
        lr.addWidget(le); lr.addWidget(ld); lr.addStretch(1); lfl.addLayout(lr); lo.addWidget(lf)
        tf=qw.QWidget(); tf.setObjectName("card"); tfl=qw.QVBoxLayout(tf); tfl.setSpacing(10)
        tfl.addWidget(_lbl(_("settings.theme",lang),"cardTitle"))
        tr=_hb(sp=8)
        td=qw.QRadioButton(_("settings.dark",lang)); tl=qw.QRadioButton(_("settings.light",lang))
        td.setChecked(s.get("theme","dark")!="light"); tl.setChecked(s.get("theme")=="light")
        td.toggled.connect(lambda checked: checked and self._st("dark"))
        tl.toggled.connect(lambda checked: checked and self._st("light"))
        tr.addWidget(td); tr.addWidget(tl); tr.addStretch(1); tfl.addLayout(tr); lo.addWidget(tf)
        ef=qw.QWidget(); ef.setObjectName("card"); efl=qw.QVBoxLayout(ef); efl.setSpacing(10)
        efl.addWidget(_lbl(_("settings.exiftool",lang),"cardTitle"))
        etr=_hb(sp=8); self.et=qw.QLineEdit(); etr.addWidget(self.et)
        fb=_btn(_("settings.exiftool_find",lang),"secondaryBtn"); etr.addWidget(fb)
        eb=_file_browse_btn(self.et,"Select exiftool.exe","exiftool*.exe;;*.exe;;*"); etr.addWidget(eb)
        def _find():
            p=_find_exiftool()
            if p: self.et.setText(str(p)); self.etlbl.setText(f"{_('settings.exiftool_found',lang)} {p}")
            else: self.etlbl.setText(_("settings.exiftool_notfound",lang))
        fb.clicked.connect(_find); efl.addLayout(etr)
        found=_find_exiftool()
        self.etlbl=_lbl(f"{_('settings.exiftool_found',lang)} {found}" if found else _("settings.exiftool_notfound",lang),"cardSub")
        efl.addWidget(self.etlbl)
        if s.get("exiftool_path"): self.et.setText(s["exiftool_path"])
        lo.addWidget(ef)
        # Media scope
        sc=qw.QWidget(); sc.setObjectName("card"); scl=qw.QVBoxLayout(sc); scl.setSpacing(10)
        scl.addWidget(_lbl(_("settings.scope",lang),"cardTitle"))
        sr2=_hb(sp=16)
        self.scope_together=qw.QRadioButton(_("onboarding.scope_together",lang))
        self.scope_separate=qw.QRadioButton(_("onboarding.scope_separate",lang))
        scope=s.get("media_scope","separate")
        self.scope_together.setChecked(scope=="together"); self.scope_separate.setChecked(scope!="together")
        sr2.addWidget(self.scope_together); sr2.addWidget(self.scope_separate); sr2.addStretch(1)
        scl.addLayout(sr2); lo.addWidget(sc)
        # Default folders
        df=qw.QWidget(); df.setObjectName("card"); dfl=qw.QVBoxLayout(df); dfl.setSpacing(10)
        dfl.addWidget(_lbl(_("settings.data",lang),"cardTitle"))
        sl,self.se=_folder_row(_("organize.src",lang),lang); dfl.addLayout(sl)
        tl2,self.te=_folder_row(_("organize.tgt",lang),lang); dfl.addLayout(tl2)
        if s.get("source_dir"): self.se.setText(s["source_dir"])
        if s.get("target_dir"): self.te.setText(s["target_dir"])
        lo.addWidget(df)
        sv=_btn(_("settings.save",lang),"primaryBtn"); sv.clicked.connect(self._save); lo.addWidget(sv)
        lo.addStretch(1); cw.setLayout(lo); scroll.setWidget(cw)
        return scroll
    def _sl(self,lang):
        s=_ls(); s["language"]=lang; _ss(s); self.shell._rebuild()
    def _st(self,theme):
        s=_ls(); s["theme"]=theme; _ss(s)
        sheet=LIGHT if theme=="light" else DARK; self.shell.window.setStyleSheet(sheet)
    def _save(self):
        qc,qg,qw=_qt(); s=_ls()
        s["source_dir"]=self.se.text(); s["target_dir"]=self.te.text()
        s["exiftool_path"]=self.et.text() if hasattr(self,'et') else ""
        s["media_scope"]="together" if self.scope_together.isChecked() else "separate"
        _ss(s)
        qw.QMessageBox.information(None,_("settings.title",s.get("language","en")),_("settings.saved",s.get("language","en")))


# ═══════════════════════════════════════════
# MAIN SHELL
# ═══════════════════════════════════════════

class MediaManagerShell:
    def __init__(self):
        qc,qg,qw=_qt(); s=_ls(); self.lang=s.get("language","en"); self.theme=s.get("theme","dark")
        self.app=qw.QApplication.instance() or qw.QApplication(sys.argv)
        self.window=qw.QMainWindow(); self.window.setWindowTitle("Media Manager")
        self.window.resize(1400,850); self.window.setMinimumSize(1000,650)
        sheet=LIGHT if self.theme=="light" else DARK; self.window.setStyleSheet(sheet)
        _log_error(f"GUI START: python={_python_exe()} sys.exe={sys.executable} lang={self.lang} exiftool={_find_exiftool()}")
        self._build()

    def _build(self):
        qc,qg,qw=_qt(); lang=_ls().get("language","en")
        c=qw.QWidget(); ml=qw.QHBoxLayout(c); ml.setContentsMargins(0,0,0,0); ml.setSpacing(0)

        # Sidebar
        sb=qw.QWidget(); sb.setObjectName("sidebar")
        sl=qw.QVBoxLayout(sb); sl.setContentsMargins(0,0,0,12); sl.setSpacing(0)
        tl=qw.QLabel("  Media Manager"); tl.setStyleSheet("font-size:16px;font-weight:700;padding:16px 16px 8px 16px")
        sl.addWidget(tl); sl.addWidget(_lbl(_("sh.main",lang),"sh")); self.nb={}
        main_items=[("dashboard",_("nav.dashboard",lang)),("organize",_("nav.organize",lang)),("rename",_("nav.rename",lang)),("duplicates",_("nav.duplicates",lang))]
        for pid,label in main_items:
            b=qw.QPushButton(label); b.setCheckable(True); b.setCursor(qg.QCursor(qc.Qt.CursorShape.PointingHandCursor))
            b.clicked.connect(lambda _,p=pid: self.navigate(p)); sl.addWidget(b); self.nb[pid]=b
        sl.addWidget(_lbl(_("sh.tools",lang),"sh"))
        tool_items=[("people",_("nav.people",lang)),("trips",_("nav.trips",lang)),("settings",_("nav.settings",lang))]
        for pid,label in tool_items:
            b=qw.QPushButton(label); b.setCheckable(True); b.setCursor(qg.QCursor(qc.Qt.CursorShape.PointingHandCursor))
            b.clicked.connect(lambda _,p=pid: self.navigate(p)); sl.addWidget(b); self.nb[pid]=b
        sl.addStretch(1); sl.addWidget(_lbl("  v0.6.0","")); ml.addWidget(sb)

        # Content
        r=qw.QWidget(); rl=qw.QVBoxLayout(r); rl.setContentsMargins(0,0,0,0); rl.setSpacing(0)

        # Top bar
        tb=qw.QWidget(); tb.setObjectName("topbar"); tbl=qw.QHBoxLayout(tb); tbl.setContentsMargins(24,0,24,0)
        self.pt=_lbl("","pageTitle"); self.pt.setObjectName("pageTitle"); tbl.addWidget(self.pt); tbl.addStretch(1)

        # Language toggle — shows CURRENT language flag
        self.lang_btn=qw.QPushButton(); self.lang_btn.setObjectName("langBtn")
        self.lang_btn.setCursor(qg.QCursor(qc.Qt.CursorShape.PointingHandCursor))
        self.lang_btn.clicked.connect(self._toggle_lang); self._up_lang_btn(); tbl.addWidget(self.lang_btn)
        rl.addWidget(tb)

        self.stack=qw.QStackedWidget(); self.pages={}; self.pw={}
        page_classes=[("dashboard",DashboardPage),("organize",OrganizePage),("rename",RenamePage),("duplicates",DuplicatesPage),("people",PeoplePage),("trips",TripsPage),("settings",SettingsPage)]
        for pid,P in page_classes:
            p=P(self); w=p.build(); self.pages[pid]=p; self.pw[pid]=w; self.stack.addWidget(w)
        rl.addWidget(self.stack,1)

        self.status_lbl=qw.QLabel(f"  {_('status.ready',lang)}"); self.status_lbl.setObjectName("statusBar")
        rl.addWidget(self.status_lbl)
        ml.addWidget(r,1); self.window.setCentralWidget(c); self.navigate("dashboard")

    def _toggle_lang(self):
        new_lang="de" if self.lang=="en" else "en"
        self._sl(new_lang)

    def _up_lang_btn(self):
        # Show CURRENT language flag
        self.lang_btn.setText("🇺🇸" if self.lang=="en" else "🇩🇪")
        self.lang_btn.setToolTip("English" if self.lang=="en" else "Deutsch")

    def set_status(self,text):
        self.status_lbl.setText(f"  {text}")

    def _sl(self,lang):
        s=_ls(); s["language"]=lang; _ss(s); self.lang=lang; self._up_lang_btn(); self._rebuild()

    def _rebuild(self):
        lang=_ls().get("language","en")
        all_items=[("dashboard",_("nav.dashboard",lang)),("organize",_("nav.organize",lang)),("rename",_("nav.rename",lang)),("duplicates",_("nav.duplicates",lang)),("people",_("nav.people",lang)),("trips",_("nav.trips",lang)),("settings",_("nav.settings",lang))]
        for pid,label in all_items:
            if pid in self.nb: self.nb[pid].setText(label)
        self.status_lbl.setText(f"  {_('status.ready',lang)}")
        cur=self.stack.currentIndex()
        qc,qg,qw=_qt(); self.stack=qw.QStackedWidget(); self.pages.clear(); self.pw.clear()
        page_classes=[("dashboard",DashboardPage),("organize",OrganizePage),("rename",RenamePage),("duplicates",DuplicatesPage),("people",PeoplePage),("trips",TripsPage),("settings",SettingsPage)]
        for pid,P in page_classes:
            p=P(self); w=p.build(); self.pages[pid]=p; self.pw[pid]=w; self.stack.addWidget(w)
        rl=self.window.centralWidget().layout().itemAt(1).widget().layout()
        ow=rl.itemAt(1).widget(); rl.removeWidget(ow); ow.deleteLater(); rl.insertWidget(1,self.stack,1)
        self.stack.setCurrentIndex(max(0,min(cur,self.stack.count()-1)))

    def navigate(self,pid):
        lang=_ls().get("language","en")
        for nid,b in self.nb.items(): b.setChecked(nid==pid)
        if pid in self.pw:
            i=self.stack.indexOf(self.pw[pid])
            if i>=0: self.stack.setCurrentIndex(i)
        titles={"dashboard":_("dashboard.title",lang),"organize":_("organize.title",lang),"rename":_("rename.title",lang),"duplicates":_("duplicates.title",lang),"people":_("people.title",lang),"trips":_("trips.title",lang),"settings":_("settings.title",lang)}
        self.pt.setText(titles.get(pid,pid.title()))

def run():
    shell=MediaManagerShell(); shell.window.show(); sys.exit(shell.app.exec())
if __name__=="__main__":
    run()

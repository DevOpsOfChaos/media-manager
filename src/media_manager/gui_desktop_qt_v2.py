"""Media Manager — Modern Desktop GUI v2"""
from __future__ import annotations
import json, os, subprocess, sys, threading
from datetime import datetime
from pathlib import Path
from typing import Any

# ── Qt imports ──
def _qt():
    from PySide6 import QtCore, QtGui, QtWidgets
    return QtCore, QtGui, QtWidgets

# ── Settings ──
def _sf():
    return Path.home() / ".media-manager" / "gui-settings.json"
def _ls():
    sf = _sf()
    if sf.exists():
        try: return json.loads(sf.read_text())
        except: pass
    return {"language": "en", "theme": "dark", "source_dir": "", "target_dir": ""}
def _ss(s):
    sf = _sf(); sf.parent.mkdir(parents=True, exist_ok=True)
    sf.write_text(json.dumps(s, indent=2))

# ── ExifTool check ──
def _find_exiftool():
    try:
        from src.media_manager.exiftool import resolve_exiftool_path
        s = _ls()
        custom = s.get("exiftool_path", "")
        path = resolve_exiftool_path(Path(custom) if custom else None)
        return path
    except: return None

def _exiftool_ok():
    return _find_exiftool() is not None

# ── CLI runner ──
def _cli(*args, timeout=120):
    cmd = [sys.executable, "-m", "media_manager"] + list(args) + ["--json"]
    s = _ls()
    et = s.get("exiftool_path", "")
    if et: cmd += ["--exiftool-path", et]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        out = r.stdout.strip()
        if out:
            try: return json.loads(out)
            except: pass
        return {"_text": out or r.stderr.strip(), "exit": r.returncode}
    except subprocess.TimeoutExpired:
        return {"error": "Timeout"}
    except Exception as e:
        return {"error": str(e)}

# ── Theme (compact) ──
DARK = """QWidget{background:#0d1117;color:#e6edf3;font:13px "Segoe UI"}
#sidebar{background:#161b22;border-right:1px solid #30363d;min-width:220px;max-width:220px}
#sidebar QPushButton{background:transparent;color:#8b949e;border:none;border-radius:8px;padding:10px 14px;text-align:left;font-weight:500;margin:1px 8px}
#sidebar QPushButton:hover{background:#1c2128;color:#e6edf3}
#sidebar QPushButton:checked{background:#1f6feb33;color:#58a6ff;font-weight:600}
#sidebar QLabel#sh{color:#8b949e;font-size:11px;font-weight:600;padding:20px 16px 6px 16px}
#topbar{background:#161b22;border-bottom:1px solid #30363d;min-height:48px;max-height:48px;padding:0 20px}
#topbar QLabel{font-size:14px;font-weight:600}
#topbar QPushButton{background:transparent;border:1px solid #30363d;border-radius:6px;padding:4px 10px;font-size:16px}
#topbar QPushButton:hover{background:#1c2128;border-color:#58a6ff}
#pageTitle{font-size:22px;font-weight:700;padding:0}
#pageSubtitle{font-size:13px;color:#8b949e;padding:2px 0 16px 0}
#card{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:20px}
#card QLabel#cardTitle{font-size:14px;font-weight:600}
#card QLabel#cardValue{font-size:28px;font-weight:700;color:#58a6ff}
#card QLabel#cardSub{font-size:12px;color:#8b949e}
QPushButton#primaryBtn{background:#238636;color:#fff;border:1px solid #2ea043;border-radius:8px;padding:8px 20px;font-weight:600}
QPushButton#primaryBtn:hover{background:#2ea043}
QPushButton#secondaryBtn{background:#21262d;color:#c9d1d9;border:1px solid #30363d;border-radius:8px;padding:8px 20px;font-weight:500}
QPushButton#secondaryBtn:hover{background:#30363d}
QPushButton#dangerBtn{background:#da3633;color:#fff;border:1px solid #f85149;border-radius:8px;padding:8px 20px;font-weight:600}
QLineEdit,QComboBox{background:#0d1117;border:1px solid #30363d;border-radius:6px;padding:8px 12px;color:#e6edf3}
QLineEdit:focus,QComboBox:focus{border-color:#58a6ff}
QComboBox QAbstractItemView{background:#161b22;border:1px solid #30363d;color:#e6edf3;selection-background-color:#1f6feb33}
QProgressBar{background:#21262d;border:none;border-radius:4px;height:6px;text-align:center}
QProgressBar::chunk{background:#58a6ff;border-radius:4px}
QTableWidget{background:#161b22;border:1px solid #30363d;border-radius:8px;gridline-color:#21262d}
QTableWidget::item{padding:8px 12px;border-bottom:1px solid #21262d}
QHeaderView::section{background:#0d1117;color:#8b949e;font-weight:600;padding:8px 12px;border:none}
QScrollBar:vertical{background:#0d1117;width:8px;border-radius:4px}
QScrollBar::handle:vertical{background:#30363d;border-radius:4px;min-height:30px}
QDateEdit{background:#0d1117;border:1px solid #30363d;border-radius:6px;padding:8px 12px;color:#e6edf3}
#statusBar{background:#161b22;border-top:1px solid #30363d;min-height:28px;max-height:28px;padding:0 16px;font-size:11px;color:#8b949e}"""

# ── i18n ──
T = {
    "en": {
        "nav.dashboard": "🏠  Dashboard", "nav.organize": "📁  Organize", "nav.rename": "✏️  Rename",
        "nav.duplicates": "🔍  Duplicates", "nav.people": "👤  People", "nav.trips": "📍  Trips", "nav.settings": "⚙️  Settings",
        "sh.main": "MAIN", "sh.tools": "TOOLS",
        "dashboard.title": "Dashboard", "dashboard.sub": "Your media library at a glance.",
        "dashboard.scan": "Scan Directory", "dashboard.quick": "Quick Actions",
        "dashboard.files": "Total Files", "dashboard.dups": "Duplicates Found", "dashboard.people": "People Found", "dashboard.trips": "Trips",
        "organize.title": "Organize Media", "organize.sub": "Sort files into folders by date pattern.",
        "organize.src": "Source", "organize.tgt": "Target", "organize.pat": "Folder Pattern",
        "organize.preview": "Preview", "organize.apply": "Apply",
        "organize.custom": "Custom: use yyyy, MM, dd",
        "rename.title": "Rename Media", "rename.sub": "Rename files with meaningful names from dates and metadata.",
        "rename.src": "Source", "rename.tmpl": "Naming Template",
        "rename.preview": "Preview", "rename.apply": "Apply",
        "rename.custom": "Custom: use {date}, {original_name}, {camera}, {index}",
        "duplicates.title": "Find Duplicates", "duplicates.sub": "Scan for exact and similar duplicate files.",
        "duplicates.src": "Source", "duplicates.scan": "Scan",
        "duplicates.exact": "Exact Duplicates", "duplicates.similar": "Similar Images",
        "people.title": "People", "people.sub": "Local face recognition.",
        "people.scan": "Scan for Faces", "people.setup": "Setup Face Recognition",
        "people.missing": "Face recognition backend not installed. Run: pip install -e .[people]",
        "trips.title": "Trips", "trips.sub": "Browse and manage trip collections.",
        "trips.new": "New Trip", "trips.label": "Trip Name", "trips.start": "Start", "trips.end": "End",
        "trips.link": "Hard links", "trips.copy": "Copies", "trips.create": "Create Trip",
        "settings.title": "Settings", "settings.sub": "Language, theme, and default folders.",
        "settings.lang": "Language", "settings.theme": "Theme", "settings.dark": "Dark", "settings.light": "Light",
        "settings.data": "Data Folders", "settings.src_hint": "Default source directory",
        "settings.tgt_hint": "Default target directory", "settings.save": "Save",
        "settings.exiftool": "ExifTool Location", "settings.exiftool_find": "Auto-Detect", "settings.exiftool_found": "Found:", "settings.exiftool_notfound": "Not found — select manually or install from exiftool.org",
        "filter.kind": "Media Type", "filter.all": "All", "filter.img": "Images", "filter.vid": "Videos", "filter.aud": "Audio",
        "status.ready": "Ready", "status.scanning": "Scanning files...", "status.hashing": "Hashing...",
        "status.done": "Done", "exiftool.missing": "⚠ ExifTool not found. Organize, Rename & Trips need it for reading media dates.",
        "exiftool.dl": "Download ExifTool",
    },
    "de": {
        "nav.dashboard": "🏠  Übersicht", "nav.organize": "📁  Organisieren", "nav.rename": "✏️  Umbenennen",
        "nav.duplicates": "🔍  Duplikate", "nav.people": "👤  Personen", "nav.trips": "📍  Reisen", "nav.settings": "⚙️  Einstellungen",
        "sh.main": "HAUPTMENÜ", "sh.tools": "WERKZEUGE",
        "dashboard.title": "Übersicht", "dashboard.sub": "Deine Medienbibliothek auf einen Blick.",
        "dashboard.scan": "Verzeichnis scannen", "dashboard.quick": "Schnellaktionen",
        "dashboard.files": "Dateien gesamt", "dashboard.dups": "Duplikate gefunden", "dashboard.people": "Personen gefunden", "dashboard.trips": "Reisen",
        "organize.title": "Medien organisieren", "organize.sub": "Sortiere Dateien in Ordner nach Datumsmuster.",
        "organize.src": "Quelle", "organize.tgt": "Ziel", "organize.pat": "Ordner-Muster",
        "organize.preview": "Vorschau", "organize.apply": "Anwenden",
        "organize.custom": "Eigenes: yyyy, MM, dd nutzen",
        "rename.title": "Medien umbenennen", "rename.sub": "Benenne Dateien mit aussagekräftigen Namen.",
        "rename.src": "Quelle", "rename.tmpl": "Namensmuster",
        "rename.preview": "Vorschau", "rename.apply": "Anwenden",
        "rename.custom": "Eigenes: {date}, {original_name}, {camera}, {index}",
        "duplicates.title": "Duplikate finden", "duplicates.sub": "Scanne nach exakten und ähnlichen Duplikaten.",
        "duplicates.src": "Quelle", "duplicates.scan": "Scannen",
        "duplicates.exact": "Exakte Duplikate", "duplicates.similar": "Ähnliche Bilder",
        "people.title": "Personen", "people.sub": "Lokale Gesichtserkennung.",
        "people.scan": "Nach Gesichtern suchen", "people.setup": "Gesichtserkennung einrichten",
        "people.missing": "Gesichtserkennung nicht installiert: pip install -e .[people]",
        "trips.title": "Reisen", "trips.sub": "Durchsuche und verwalte Reisesammlungen.",
        "trips.new": "Neue Reise", "trips.label": "Reisename", "trips.start": "Start", "trips.end": "Ende",
        "trips.link": "Hardlinks", "trips.copy": "Kopien", "trips.create": "Reise erstellen",
        "settings.title": "Einstellungen", "settings.sub": "Sprache, Design und Standardpfade.",
        "settings.lang": "Sprache", "settings.theme": "Design", "settings.dark": "Dunkel", "settings.light": "Hell",
        "settings.data": "Datenverzeichnisse", "settings.src_hint": "Standard-Quellverzeichnis",
        "settings.tgt_hint": "Standard-Zielverzeichnis", "settings.save": "Speichern",
        "settings.exiftool": "ExifTool-Pfad", "settings.exiftool_find": "Auto-Erkennung", "settings.exiftool_found": "Gefunden:", "settings.exiftool_notfound": "Nicht gefunden — manuell auswählen oder von exiftool.org installieren",
        "filter.kind": "Medien-Typ", "filter.all": "Alle", "filter.img": "Bilder", "filter.vid": "Videos", "filter.aud": "Audio",
        "status.ready": "Bereit", "status.scanning": "Scanne Dateien...", "status.hashing": "Berechne Hashes...",
        "status.done": "Fertig", "exiftool.missing": "⚠ ExifTool nicht gefunden. Organisieren, Umbenennen & Reisen brauchen es für Mediendaten.",
        "exiftool.dl": "ExifTool herunterladen",
    },
}
def _(k, l=None):
    l = l or _ls().get("language", "en")
    return T.get(l, T["en"]).get(k, T["en"].get(k, k))

# ── UI helpers ──
def _btn(txt, obj=""):
    qc, qg, qw = _qt()
    b = qw.QPushButton(txt); b.setCursor(qg.QCursor(qc.Qt.CursorShape.PointingHandCursor))
    if obj: b.setObjectName(obj)
    return b
def _lbl(txt, obj="", wrap=True):
    qc, qg, qw = _qt()
    l = qw.QLabel(txt); l.setWordWrap(wrap)
    if obj: l.setObjectName(obj)
    return l
def _hb(*ws, sp=12):
    qc, qg, qw = _qt(); lo = qw.QHBoxLayout(); lo.setSpacing(sp)
    for w in ws:
        if isinstance(w, int): lo.addStretch(w)
        elif isinstance(w, qw.QLayout): lo.addLayout(w)
        else: lo.addWidget(w)
    return lo
def _vb(*ws, sp=12):
    qc, qg, qw = _qt(); lo = qw.QVBoxLayout(); lo.setSpacing(sp)
    for w in ws:
        if isinstance(w, int): lo.addStretch(w)
        elif isinstance(w, qw.QLayout): lo.addLayout(w)
        else: lo.addWidget(w)
    return lo
def _card(title, val, sub=""):
    qc, qg, qw = _qt(); w = qw.QWidget(); w.setObjectName("card")
    lo = qw.QVBoxLayout(w); lo.setSpacing(6)
    lo.addWidget(_lbl(title, "cardTitle")); lo.addWidget(_lbl(str(val), "cardValue"))
    if sub: lo.addWidget(_lbl(sub, "cardSub"))
    return w
def _browse(edit, label="Browse"):
    def _cb():
        p = _qt()[2].QFileDialog.getExistingDirectory(None, "Select")
        if p: edit.setText(p)
    b = _btn(label); b.clicked.connect(_cb)
    return b
def _folder_row(label, lang):
    qc, qg, qw = _qt()
    e = qw.QLineEdit(); e.setPlaceholderText(_("settings.src_hint", lang))
    return _hb(_lbl(label), e, _browse(e), sp=8), e
def _media_filter(lang):
    qc, qg, qw = _qt()
    c = qw.QComboBox()
    c.addItems([_("filter.all",lang), _("filter.img",lang), _("filter.vid",lang), _("filter.aud",lang)])
    return _hb(_lbl(_("filter.kind", lang)), c, sp=8), c
def _mk_args(combo):
    i = combo.currentIndex()
    if i == 1: return ["--media-kind", "image"]
    if i == 2: return ["--media-kind", "video"]
    if i == 3: return ["--media-kind", "audio"]
    return []

# ── StatusWidget ──
class StatusWidget:
    def __init__(self, parent=None):
        qc, qg, qw = _qt()
        self.w = qw.QWidget(parent)
        lo = _vb(sp=8)
        self.pb = qw.QProgressBar(); self.pb.setRange(0, 100); self.pb.setValue(0); self.pb.setVisible(False)
        self.st = _lbl("", "cardSub")
        self.log = qw.QTextEdit(); self.log.setReadOnly(True); self.log.setMaximumHeight(100); self.log.setVisible(False)
        self.log.setStyleSheet("background:#0d1117;border:1px solid #30363d;border-radius:6px;padding:8px;color:#8b949e;font:11px 'Cascadia Code',monospace")
        lo.addWidget(self.pb); lo.addWidget(self.st); lo.addWidget(self.log)
        self.w.setLayout(lo)
    def start(self, msg=""):
        self.pb.setVisible(True); self.pb.setValue(0)
        self.log.setVisible(True); self.log.clear(); self.st.setText(msg)
    def update(self, val, msg=""):
        self.pb.setValue(min(val, 100))
        if msg: self.st.setText(msg); self.log.append(msg)
    def finish(self, msg=""):
        self.pb.setValue(100); self.st.setText(msg)
        qc, qg, qw = _qt(); qc.QTimer.singleShot(2500, lambda: self.pb.setVisible(False))

# ── Pages ──
class DashboardPage:
    def __init__(self, shell): self.shell = shell
    def build(self):
        qc, qg, qw = _qt(); lang = _ls().get("language", "en")
        w = qw.QWidget(); lo = _vb(sp=20)
        lo.addWidget(_lbl(_("dashboard.title", lang), "pageTitle"))
        lo.addWidget(_lbl(_("dashboard.sub", lang), "pageSubtitle"))
        if not _exiftool_ok():
            wrn = qw.QWidget(); wrn.setStyleSheet("background:#da363322;border:1px solid #f85149;border-radius:8px;padding:12px")
            wl = _vb(sp=4); wl.addWidget(_lbl(_("exiftool.missing", lang), "cardSub"))
            btn = _btn(_("exiftool.dl", lang), "secondaryBtn")
            btn.clicked.connect(lambda: qg.QDesktopServices.openUrl(qc.QUrl("https://exiftool.org")))
            wl.addWidget(btn); wrn.setLayout(wl); lo.addWidget(wrn)
        st = _hb(sp=16)
        st.addWidget(_card(_("dashboard.files", lang), "...", "scan to populate"))
        st.addWidget(_card(_("dashboard.dups", lang), "...", "scan to populate"))
        st.addWidget(_card(_("dashboard.people", lang), "...", "scan to populate"))
        st.addWidget(_card(_("dashboard.trips", lang), "...", "create to populate"))
        lo.addLayout(st)
        lo.addWidget(_lbl(_("dashboard.quick", lang), "cardTitle"))
        ac = _hb(sp=12)
        for pid, txt in [("organize", _("dashboard.scan", lang)), ("rename", _("rename.title", lang)), ("duplicates", _("duplicates.scan", lang)), ("people", _("people.scan", lang))]:
            b = _btn(txt, "secondaryBtn"); b.clicked.connect(lambda _, p=pid: self.shell.navigate(p)); ac.addWidget(b)
        ac.addStretch(1); lo.addLayout(ac)
        lo.addStretch(1); w.setLayout(lo)

        # Background scan
        def _scan():
            s = _ls(); src = s.get("source_dir", "")
            if src and Path(src).exists():
                exts = {'.jpg','.jpeg','.png','.gif','.mp4','.mov','.avi','.mkv','.raw','.cr2','.nef','.arw','.dng','.heic','.webp','.bmp','.tiff','.tif'}
                n = sum(1 for _ in list(Path(src).rglob('*'))[:100000] if Path(_).suffix.lower() in exts)
                qc.QTimer.singleShot(0, lambda: self._update_stats(w, n))
        threading.Thread(target=_scan, daemon=True).start()
        return w
    def _update_stats(self, w, n):
        cards = w.findChildren(_qt()[2].QWidget, "card")
        if len(cards) >= 1:
            v = cards[0].findChildren(_qt()[2].QLabel)
            if len(v) > 1: v[1].setText(str(n))

class OrganizePage:
    def __init__(self, shell): self.shell = shell
    def build(self):
        qc, qg, qw = _qt(); lang = _ls().get("language", "en")
        w = qw.QWidget(); lo = _vb(sp=16, margins=(24,24,24,24))
        lo.addWidget(_lbl(_("organize.title", lang), "pageTitle"))
        lo.addWidget(_lbl(_("organize.sub", lang), "pageSubtitle"))
        sr, self.se = _folder_row(_("organize.src", lang), lang); lo.addLayout(sr)
        tr, self.te = _folder_row(_("organize.tgt", lang), lang); lo.addLayout(tr)
        fk, self.mk = _media_filter(lang); lo.addLayout(fk)
        pr = _hb(sp=8); pr.addWidget(_lbl(_("organize.pat", lang)))
        self.pc = qw.QComboBox(); self.pc.setEditable(True)
        self.pc.addItems(["yyyy\\yyyy-MM-dd", "yyyy\\yyyy-MM\\yyyy-MM-dd", "yyyy-MM\\yyyy-MM-dd", "yyyy\\MM-dd", "yyyy-MM\\event", "Custom..."])
        self.pc.setMinimumWidth(280); pr.addWidget(self.pc); pr.addStretch(1); lo.addLayout(pr)
        lo.addWidget(_lbl(_("organize.custom", lang), "cardSub"))
        self.sw = StatusWidget(); lo.addWidget(self.sw.w)
        br = _hb(sp=12)
        pv = _btn(_("organize.preview", lang), "secondaryBtn"); ap = _btn(_("organize.apply", lang), "primaryBtn")
        br.addWidget(pv); br.addWidget(ap); br.addStretch(1); lo.addLayout(br)
        self.pa = qw.QTextEdit(); self.pa.setReadOnly(True); self.pa.setMaximumHeight(300)
        self.pa.setStyleSheet("background:#0d1117;border:1px solid #30363d;border-radius:8px;padding:12px;color:#8b949e;font:12px 'Cascadia Code',monospace")
        lo.addWidget(self.pa)
        pv.clicked.connect(lambda: self._preview(lang)); ap.clicked.connect(lambda: self._apply(lang))
        s = _ls()
        if s.get("source_dir"): self.se.setText(s["source_dir"])
        if s.get("target_dir"): self.te.setText(s["target_dir"])
        lo.addStretch(1); w.setLayout(lo)
        return w
    def _preview(self, lang):
        src, tgt = self.se.text(), self.te.text()
        if not src or not tgt: return
        pat = self.pc.currentText()
        self.sw.start(_("status.scanning", lang)); self.pa.clear()
        def _run():
            args = ["organize", "--source", src, "--target", tgt, "--pattern", pat]
            args.extend(_mk_args(self.mk))
            r = _cli(*args)
            txt = json.dumps(r, indent=2) if r else "No result"
            qc, qg, qw = _qt(); qc.QTimer.singleShot(0, lambda: (self.pa.setText(txt), self.sw.finish(_("status.done", lang))))
        threading.Thread(target=_run, daemon=True).start()
    def _apply(self, lang):
        qc, qg, qw = _qt()
        if qw.QMessageBox.warning(None, "Apply", "Move files? Cannot undo.\nContinue?", qw.QMessageBox.StandardButton.Yes|qw.QMessageBox.StandardButton.No) == qw.QMessageBox.StandardButton.Yes:
            self.sw.start("Apply not yet wired — use CLI: media-manager organize --apply")

class RenamePage:
    def __init__(self, shell): self.shell = shell
    def build(self):
        qc, qg, qw = _qt(); lang = _ls().get("language", "en")
        w = qw.QWidget(); lo = _vb(sp=16, margins=(24,24,24,24))
        lo.addWidget(_lbl(_("rename.title", lang), "pageTitle"))
        lo.addWidget(_lbl(_("rename.sub", lang), "pageSubtitle"))
        sr, self.se = _folder_row(_("rename.src", lang), lang); lo.addLayout(sr)
        fk, self.mk = _media_filter(lang); lo.addLayout(fk)
        tr = _hb(sp=8); tr.addWidget(_lbl(_("rename.tmpl", lang)))
        self.tc = qw.QComboBox(); self.tc.setEditable(True)
        self.tc.addItems(["{date}_{original_name}", "{date}_{camera}_{original_name}", "{date}_{location}_{original_name}", "{date}_{index:03d}", "{year}_{month}_{original_name}", "Custom..."])
        self.tc.setMinimumWidth(320); tr.addWidget(self.tc); tr.addStretch(1); lo.addLayout(tr)
        lo.addWidget(_lbl(_("rename.custom", lang), "cardSub"))
        self.sw = StatusWidget(); lo.addWidget(self.sw.w)
        br = _hb(sp=12)
        pv = _btn(_("rename.preview", lang), "secondaryBtn"); ap = _btn(_("rename.apply", lang), "primaryBtn")
        br.addWidget(pv); br.addWidget(ap); br.addStretch(1); lo.addLayout(br)
        self.pa = qw.QTextEdit(); self.pa.setReadOnly(True); self.pa.setMaximumHeight(300)
        self.pa.setStyleSheet("background:#0d1117;border:1px solid #30363d;border-radius:8px;padding:12px;color:#8b949e;font:12px 'Cascadia Code',monospace")
        lo.addWidget(self.pa)
        pv.clicked.connect(lambda: self._preview(lang)); ap.clicked.connect(lambda: self._apply(lang))
        s = _ls()
        if s.get("source_dir"): self.se.setText(s["source_dir"])
        lo.addStretch(1); w.setLayout(lo)
        return w
    def _preview(self, lang):
        src = self.se.text()
        if not src: return
        tmpl = self.tc.currentText()
        self.sw.start(_("status.scanning", lang)); self.pa.clear()
        def _run():
            args = ["rename", "--source", src, "--template", tmpl]
            args.extend(_mk_args(self.mk))
            r = _cli(*args)
            txt = json.dumps(r, indent=2) if r else "No result"
            qc, qg, qw = _qt(); qc.QTimer.singleShot(0, lambda: (self.pa.setText(txt), self.sw.finish(_("status.done", lang))))
        threading.Thread(target=_run, daemon=True).start()
    def _apply(self, lang):
        qc, qg, qw = _qt()
        if qw.QMessageBox.warning(None, "Apply", "Rename files? Cannot undo.\nContinue?", qw.QMessageBox.StandardButton.Yes|qw.QMessageBox.StandardButton.No) == qw.QMessageBox.StandardButton.Yes:
            self.sw.start("Apply not yet wired — use CLI: media-manager rename --apply")

class DuplicatesPage:
    def __init__(self, shell): self.shell = shell; self.data = None; self.sim = None
    def build(self):
        qc, qg, qw = _qt(); lang = _ls().get("language", "en")
        w = qw.QWidget(); lo = _vb(sp=16, margins=(24,24,24,24))
        lo.addWidget(_lbl(_("duplicates.title", lang), "pageTitle"))
        lo.addWidget(_lbl(_("duplicates.sub", lang), "pageSubtitle"))
        sr, self.se = _folder_row(_("duplicates.src", lang), lang); lo.addLayout(sr)
        fr = _hb(sp=16); fk, self.mk = _media_filter(lang); fr.addLayout(fk); fr.addStretch(1)
        sb = _btn(_("duplicates.scan", lang), "primaryBtn"); fr.addWidget(sb); lo.addLayout(fr)
        self.sw = StatusWidget(); lo.addWidget(self.sw.w)
        self.stack = qw.QStackedWidget()
        e = qw.QWidget(); el = _vb(sp=8, margins=(40,40,40,40))
        el.addWidget(_lbl("Scan a directory to find duplicates.", "cardSub"), alignment=qc.Qt.AlignmentFlag.AlignCenter)
        e.setLayout(el); self.stack.addWidget(e)
        lo.addWidget(self.stack, 1)
        sb.clicked.connect(lambda: self._scan(lang))
        s = _ls()
        if s.get("source_dir"): self.se.setText(s["source_dir"])
        w.setLayout(lo)
        return w
    def _scan(self, lang):
        src = self.se.text()
        if not src or not Path(src).exists(): return
        mk = _mk_args(self.mk)
        self.sw.start(_("status.scanning", lang))
        def _run():
            self.sw.update(20, _("status.hashing", lang))
            d = _cli("duplicates", "--source", src, *mk)
            self.sw.update(70, "Comparing similar images...")
            s = _cli("duplicates", "--source", src, "--similar-images", *mk)
            self.data, self.sim = d, s
            qc, qg, qw = _qt(); qc.QTimer.singleShot(0, lambda: self._show(lang))
        threading.Thread(target=_run, daemon=True).start()
    def _show(self, lang):
        qc, qg, qw = _qt(); d = self.data or {}; s = self.sim or {}
        rw = qw.QWidget(); rl = _vb(sp=16)
        sc = d.get("scan", {})
        eg = sc.get("exact_groups", 0); ef = sc.get("duplicate_files", 0); ed = sc.get("extra_duplicates", 0)
        simd = s.get("similar_images", {}) or {}; sg = len(simd.get("groups", []) or [])
        rl.addWidget(_lbl(f"{eg} exact groups ({ef} files, {ed} extras)  |  {sg} similar groups", "cardSub"))
        if eg:
            rl.addWidget(_lbl(_("duplicates.exact", lang), "cardTitle"))
            t = qw.QTableWidget(); gs = d.get("review", {}).get("groups", []) or []
            t.setRowCount(min(len(gs), 50)); t.setColumnCount(4)
            t.setHorizontalHeaderLabels(["Group", "Files", "Size", "Same Name"])
            for i, g in enumerate(gs[:50]):
                t.setItem(i, 0, qw.QTableWidgetItem(str(g.get("group_id", ""))[:40]))
                t.setItem(i, 1, qw.QTableWidgetItem(str(g.get("candidate_count", 0))))
                t.setItem(i, 2, qw.QTableWidgetItem(str(g.get("file_size", 0))))
                t.setItem(i, 3, qw.QTableWidgetItem("Yes" if g.get("same_name") else "No"))
            t.resizeColumnsToContents(); rl.addWidget(t)
        rl.addStretch(1); rw.setLayout(rl)
        while self.stack.count() > 0: self.stack.removeWidget(self.stack.widget(0))
        self.stack.addWidget(rw); self.sw.finish(_("status.done", lang))

class PeoplePage:
    def __init__(self, shell): self.shell = shell
    def build(self):
        qc, qg, qw = _qt(); lang = _ls().get("language", "en")
        w = qw.QWidget(); lo = _vb(sp=16, margins=(24,24,24,24))
        lo.addWidget(_lbl(_("people.title", lang), "pageTitle"))
        lo.addWidget(_lbl(_("people.sub", lang), "pageSubtitle"))
        try:
            from src.media_manager.core.people_recognition import backend_available
            ok = backend_available()
        except: ok = False
        if not ok:
            lo.addWidget(_lbl(_("people.missing", lang), "cardSub"))
            lo.addWidget(_btn(_("people.setup", lang), "primaryBtn"))
            lo.addStretch(1); w.setLayout(lo)
            return w
        sr, self.se = _folder_row("Source", lang); lo.addLayout(sr)
        fr = _hb(sp=16); fk, self.mk = _media_filter(lang); fr.addLayout(fk); fr.addStretch(1)
        sb = _btn(_("people.scan", lang), "primaryBtn"); fr.addWidget(sb); lo.addLayout(fr)
        self.sw = StatusWidget(); lo.addWidget(self.sw.w)
        self.ra = qw.QTextEdit(); self.ra.setReadOnly(True)
        self.ra.setStyleSheet("background:#0d1117;border:1px solid #30363d;border-radius:8px;padding:12px;color:#8b949e;font:12px 'Cascadia Code',monospace")
        lo.addWidget(self.ra, 1)
        sb.clicked.connect(lambda: self._scan(lang))
        s = _ls()
        if s.get("source_dir"): self.se.setText(s["source_dir"])
        w.setLayout(lo)
        return w
    def _scan(self, lang):
        src = self.se.text()
        if not src: return
        self.sw.start(_("status.scanning", lang))
        def _run():
            r = _cli("people", "backend")
            txt = json.dumps(r, indent=2) if r else "Check failed"
            txt += f"\n\nTo scan faces: media-manager people scan --source \"{src}\""
            qc, qg, qw = _qt(); qc.QTimer.singleShot(0, lambda: (self.ra.setText(txt), self.sw.finish(_("status.done", lang))))
        threading.Thread(target=_run, daemon=True).start()

class TripsPage:
    def __init__(self, shell): self.shell = shell
    def build(self):
        qc, qg, qw = _qt(); lang = _ls().get("language", "en")
        w = qw.QWidget(); lo = _vb(sp=16, margins=(24,24,24,24))
        lo.addWidget(_lbl(_("trips.title", lang), "pageTitle"))
        lo.addWidget(_lbl(_("trips.sub", lang), "pageSubtitle"))
        fm = qw.QWidget(); fm.setObjectName("card"); fl = qw.QVBoxLayout(fm); fl.setSpacing(12)
        fl.addWidget(_lbl(_("trips.new", lang), "cardTitle"))
        nr = _hb(sp=8); nr.addWidget(_lbl(_("trips.label", lang)))
        self.tn = qw.QLineEdit(); self.tn.setPlaceholderText("e.g. Italy 2025"); nr.addWidget(self.tn); fl.addLayout(nr)
        sl, self.ts = _folder_row("Source", lang); fl.addLayout(sl)
        tl, self.tt = _folder_row("Target", lang); fl.addLayout(tl)
        dr = _hb(sp=8)
        dr.addWidget(_lbl(_("trips.start", lang)))
        self.sd = qw.QDateEdit(); self.sd.setCalendarPopup(True); self.sd.setDate(qc.QDate.currentDate().addYears(-1))
        dr.addWidget(self.sd)
        dr.addWidget(_lbl(_("trips.end", lang)))
        self.ed = qw.QDateEdit(); self.ed.setCalendarPopup(True); self.ed.setDate(qc.QDate.currentDate())
        dr.addWidget(self.ed); dr.addStretch(1); fl.addLayout(dr)
        mr = _hb(sp=8); self.ml = qw.QRadioButton(_("trips.link", lang)); self.mc = qw.QRadioButton(_("trips.copy", lang))
        self.ml.setChecked(True); mr.addWidget(self.ml); mr.addWidget(self.mc); mr.addStretch(1); fl.addLayout(mr)
        cb = _btn(_("trips.create", lang), "primaryBtn"); fl.addWidget(cb)
        self.sw = StatusWidget(); fl.addWidget(self.sw.w)
        lo.addWidget(fm); lo.addStretch(1)
        cb.clicked.connect(lambda: self._create(lang))
        s = _ls()
        if s.get("source_dir"): self.ts.setText(s["source_dir"])
        if s.get("target_dir"): self.tt.setText(s["target_dir"])
        w.setLayout(lo)
        return w
    def _create(self, lang):
        name = self.tn.text(); src = self.ts.text(); tgt = self.tt.text()
        if not name or not src or not tgt: return
        start = self.sd.date().toString("yyyy-MM-dd"); end = self.ed.date().toString("yyyy-MM-dd")
        mode = "link" if self.ml.isChecked() else "copy"
        self.sw.start(_("status.scanning", lang))
        def _run():
            args = ["trip", "--source", src, "--target", tgt, "--label", name, "--start", start, "--end", end]
            if mode == "copy": args.append("--copy")
            r = _cli(*args)
            txt = f"Trip '{name}' created. {r.get('planned_count',0)} files." if r and not r.get("error") else f"Error: {r}"
            qc, qg, qw = _qt(); qc.QTimer.singleShot(0, lambda: self.sw.finish(txt))
        threading.Thread(target=_run, daemon=True).start()

class SettingsPage:
    def __init__(self, shell): self.shell = shell
    def build(self):
        qc, qg, qw = _qt(); s = _ls(); lang = s.get("language", "en")
        w = qw.QWidget(); lo = _vb(sp=16, margins=(24,24,24,24))
        lo.addWidget(_lbl(_("settings.title", lang), "pageTitle"))
        lo.addWidget(_lbl(_("settings.sub", lang), "pageSubtitle"))
        # Language
        lf = qw.QWidget(); lf.setObjectName("card"); lfl = qw.QVBoxLayout(lf)
        lfl.addWidget(_lbl(_("settings.lang", lang), "cardTitle"))
        lr = _hb(sp=8)
        le = qw.QPushButton("🇺🇸 English"); ld = qw.QPushButton("🇩🇪 Deutsch")
        le.setCheckable(True); ld.setCheckable(True)
        if lang == "en": le.setChecked(True)
        else: ld.setChecked(True)
        le.clicked.connect(lambda: self._sl("en")); ld.clicked.connect(lambda: self._sl("de"))
        lr.addWidget(le); lr.addWidget(ld); lr.addStretch(1); lfl.addLayout(lr); lo.addWidget(lf)
        # Theme
        tf = qw.QWidget(); tf.setObjectName("card"); tfl = qw.QVBoxLayout(tf)
        tfl.addWidget(_lbl(_("settings.theme", lang), "cardTitle"))
        tr = _hb(sp=8)
        td = qw.QRadioButton(_("settings.dark", lang)); tl = qw.QRadioButton(_("settings.light", lang))
        td.setChecked(s.get("theme")=="dark"); tl.setChecked(s.get("theme")=="light")
        td.toggled.connect(lambda: self._st("dark")); tl.toggled.connect(lambda: self._st("light"))
        tr.addWidget(td); tr.addWidget(tl); tr.addStretch(1); tfl.addLayout(tr); lo.addWidget(tf)
        # ExifTool
        ef = qw.QWidget(); ef.setObjectName("card"); efl = qw.QVBoxLayout(ef)
        efl.addWidget(_lbl(_("settings.exiftool", lang), "cardTitle"))
        etr = _hb(sp=8)
        self.et = qw.QLineEdit(); etr.addWidget(self.et)
        fb = _btn(_("settings.exiftool_find", lang), "secondaryBtn"); etr.addWidget(fb)
        def _find():
            p = _find_exiftool()
            if p: self.et.setText(str(p)); self.etlbl.setText(f"{_('settings.exiftool_found', lang)} {p}")
            else: self.etlbl.setText(_("settings.exiftool_notfound", lang))
        fb.clicked.connect(_find)
        efl.addLayout(etr)
        found = _find_exiftool()
        self.etlbl = _lbl(f"{_('settings.exiftool_found', lang)} {found}" if found else _("settings.exiftool_notfound", lang), "cardSub")
        efl.addWidget(self.etlbl)
        if s.get("exiftool_path"): self.et.setText(s["exiftool_path"])
        lo.addWidget(ef)
        # Data folders
        df = qw.QWidget(); df.setObjectName("card"); dfl = qw.QVBoxLayout(df)
        dfl.addWidget(_lbl(_("settings.data", lang), "cardTitle"))
        sl, self.se = _folder_row(_("organize.src", lang), lang); dfl.addLayout(sl)
        tl2, self.te = _folder_row(_("organize.tgt", lang), lang); dfl.addLayout(tl2)
        if s.get("source_dir"): self.se.setText(s["source_dir"])
        if s.get("target_dir"): self.te.setText(s["target_dir"])
        lo.addWidget(df)
        sv = _btn(_("settings.save", lang), "primaryBtn"); sv.clicked.connect(self._save); lo.addWidget(sv)
        lo.addStretch(1); w.setLayout(lo)
        return w
    def _sl(self, lang):
        s = _ls(); s["language"] = lang; _ss(s); self.shell._rebuild()
    def _st(self, theme):
        s = _ls(); s["theme"] = theme; _ss(s); self.shell.window.setStyleSheet(DARK)
    def _save(self):
        s = _ls(); s["source_dir"] = self.se.text(); s["target_dir"] = self.te.text()
        s["exiftool_path"] = self.et.text() if hasattr(self, 'et') else ""
        _ss(s)
        _qt()[2].QMessageBox.information(None, "Settings", "Saved.")

# ── Main Shell ──
class MediaManagerShell:
    def __init__(self):
        qc, qg, qw = _qt()
        s = _ls(); self.lang = s.get("language", "en")
        self.app = qw.QApplication.instance() or qw.QApplication(sys.argv)
        self.window = qw.QMainWindow(); self.window.setWindowTitle("Media Manager")
        self.window.resize(1400, 850); self.window.setMinimumSize(1000, 650)
        self.window.setStyleSheet(DARK)
        self._build()

    def _build(self):
        qc, qg, qw = _qt(); lang = _ls().get("language", "en")
        c = qw.QWidget(); ml = qw.QHBoxLayout(c); ml.setContentsMargins(0,0,0,0); ml.setSpacing(0)

        # Sidebar
        sb = qw.QWidget(); sb.setObjectName("sidebar")
        sl = qw.QVBoxLayout(sb); sl.setContentsMargins(0,0,0,12); sl.setSpacing(0)
        tl = qw.QLabel("  Media Manager"); tl.setStyleSheet("font-size:16px;font-weight:700;padding:16px 16px 8px 16px")
        sl.addWidget(tl)
        sl.addWidget(_lbl(_("sh.main", lang), "sh"))
        self.nb = {}
        for pid, label in [("dashboard",_("nav.dashboard",lang)),("organize",_("nav.organize",lang)),("rename",_("nav.rename",lang)),("duplicates",_("nav.duplicates",lang))]:
            b = qw.QPushButton(label); b.setCheckable(True); b.setCursor(qg.QCursor(qc.Qt.CursorShape.PointingHandCursor))
            b.clicked.connect(lambda _, p=pid: self.navigate(p)); sl.addWidget(b); self.nb[pid] = b
        sl.addWidget(_lbl(_("sh.tools", lang), "sh"))
        for pid, label in [("people",_("nav.people",lang)),("trips",_("nav.trips",lang)),("settings",_("nav.settings",lang))]:
            b = qw.QPushButton(label); b.setCheckable(True); b.setCursor(qg.QCursor(qc.Qt.CursorShape.PointingHandCursor))
            b.clicked.connect(lambda _, p=pid: self.navigate(p)); sl.addWidget(b); self.nb[pid] = b
        sl.addStretch(1)
        sl.addWidget(_lbl("  v0.6.0", "")); ml.addWidget(sb)

        # Right side
        r = qw.QWidget(); rl = qw.QVBoxLayout(r); rl.setContentsMargins(0,0,0,0); rl.setSpacing(0)
        tb = qw.QWidget(); tb.setObjectName("topbar"); tbl = qw.QHBoxLayout(tb); tbl.setContentsMargins(20,0,20,0)
        self.pt = _lbl("", "pageTitle"); tbl.addWidget(self.pt); tbl.addStretch(1)
        fe = qw.QPushButton("🇺🇸"); fd = qw.QPushButton("🇩🇪")
        fe.setCheckable(True); fd.setCheckable(True); fe.setToolTip("English"); fd.setToolTip("Deutsch")
        fe.clicked.connect(lambda: self._sl("en")); fd.clicked.connect(lambda: self._sl("de"))
        if lang == "en": fe.setChecked(True)
        else: fd.setChecked(True)
        tbl.addWidget(fe); tbl.addWidget(fd); self.fe, self.fd = fe, fd
        rl.addWidget(tb)
        self.stack = qw.QStackedWidget(); self.pages = {}; self.pw = {}
        for pid, P in [("dashboard",DashboardPage),("organize",OrganizePage),("rename",RenamePage),("duplicates",DuplicatesPage),("people",PeoplePage),("trips",TripsPage),("settings",SettingsPage)]:
            p = P(self); w = p.build(); self.pages[pid] = p; self.pw[pid] = w; self.stack.addWidget(w)
        rl.addWidget(self.stack, 1)
        st = qw.QLabel(f"  {_('status.ready', lang)}"); st.setObjectName("statusBar"); self.slbl = st; rl.addWidget(st)
        ml.addWidget(r, 1); self.window.setCentralWidget(c); self.navigate("dashboard")

    def _sl(self, lang):
        s = _ls(); s["language"] = lang; _ss(s); self.lang = lang; self._rebuild()

    def _rebuild(self):
        lang = _ls().get("language", "en")
        for pid, label in [("dashboard",_("nav.dashboard",lang)),("organize",_("nav.organize",lang)),("rename",_("nav.rename",lang)),("duplicates",_("nav.duplicates",lang)),("people",_("nav.people",lang)),("trips",_("nav.trips",lang)),("settings",_("nav.settings",lang))]:
            if pid in self.nb: self.nb[pid].setText(label)
        self.fe.setChecked(lang=="en"); self.fd.setChecked(lang=="de")
        self.slbl.setText(f"  {_('status.ready', lang)}")
        cur = self.stack.currentIndex()
        qc, qg, qw = _qt(); self.stack = qw.QStackedWidget(); self.pages.clear()
        for pid, P in [("dashboard",DashboardPage),("organize",OrganizePage),("rename",RenamePage),("duplicates",DuplicatesPage),("people",PeoplePage),("trips",TripsPage),("settings",SettingsPage)]:
            p = P(self); w = p.build(); self.pages[pid] = p; self.stack.addWidget(w)
        old = self.pw.get("dashboard", None)
        rl = self.window.centralWidget().layout().itemAt(1).widget().layout()
        ow = rl.itemAt(1).widget()
        rl.removeWidget(ow); ow.deleteLater()
        rl.insertWidget(1, self.stack, 1)
        self.pw = {}
        for pid, P in [("dashboard",DashboardPage),("organize",OrganizePage),("rename",RenamePage),("duplicates",DuplicatesPage),("people",PeoplePage),("trips",TripsPage),("settings",SettingsPage)]:
            p = P(self); w = p.build(); self.pages[pid] = p; self.pw[pid] = w; self.stack.addWidget(w)
        self.stack.setCurrentIndex(max(0, min(cur, self.stack.count()-1)))

    def navigate(self, pid):
        lang = _ls().get("language", "en")
        for nid, b in self.nb.items(): b.setChecked(nid == pid)
        if pid in self.pw:
            i = self.stack.indexOf(self.pw[pid])
            if i >= 0: self.stack.setCurrentIndex(i)
        titles = {"dashboard":_("dashboard.title",lang),"organize":_("organize.title",lang),"rename":_("rename.title",lang),"duplicates":_("duplicates.title",lang),"people":_("people.title",lang),"trips":_("trips.title",lang),"settings":_("settings.title",lang)}
        self.pt.setText(titles.get(pid, pid.title()))

def run():
    shell = MediaManagerShell()
    shell.window.show()
    sys.exit(shell.app.exec())

if __name__ == "__main__":
    run()

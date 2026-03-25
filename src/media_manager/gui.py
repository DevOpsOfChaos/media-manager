from __future__ import annotations

import queue
import threading
from dataclasses import dataclass
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from media_manager.constants import DEFAULT_TEMPLATE
from media_manager.exiftool import ExifToolClient, ExifToolError, discover_exiftool
from media_manager.sorter import MediaDecision, OrganizeSummary, organize


@dataclass(slots=True)
class WorkerConfig:
    source: Path
    target: Path
    exiftool_path: str | None
    template: str
    action: str
    apply_changes: bool
    fallback_to_file_time: bool


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Media Manager")
        self.geometry("1360x860")
        self.minsize(1120, 700)

        self.queue: queue.Queue[tuple[str, object]] = queue.Queue()
        self.worker_thread: threading.Thread | None = None

        self.source_var = tk.StringVar()
        self.target_var = tk.StringVar()
        self.exiftool_var = tk.StringVar()
        self.template_var = tk.StringVar(value=DEFAULT_TEMPLATE)
        self.action_var = tk.StringVar(value="copy")
        self.fallback_var = tk.BooleanVar(value=True)
        self.status_var = tk.StringVar(value="Bereit")
        self.summary_var = tk.StringVar(value="Noch keine Analyse ausgeführt.")

        self._configure_style()
        self._build_ui()
        self.after(120, self._poll_queue)

    def _configure_style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Title.TLabel", font=("Segoe UI", 17, "bold"))
        style.configure("Subtitle.TLabel", font=("Segoe UI", 10))
        style.configure("Section.TLabelframe.Label", font=("Segoe UI", 10, "bold"))
        style.configure("Primary.TButton", padding=(14, 8))
        style.configure("Treeview", rowheight=24)

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = ttk.Frame(self, padding=(18, 16, 18, 8))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="Media Manager", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            header,
            text="Desktop-Basis für Sortierung von Fotos und Videos. Kernlogik zuerst, moderne Oberfläche später.",
            style="Subtitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        content = ttk.Panedwindow(self, orient=tk.VERTICAL)
        content.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 12))

        top = ttk.Frame(content, padding=2)
        bottom = ttk.Frame(content, padding=2)
        content.add(top, weight=1)
        content.add(bottom, weight=2)

        top.columnconfigure(0, weight=1)
        top.columnconfigure(1, weight=1)
        top.rowconfigure(0, weight=1)

        config_frame = ttk.LabelFrame(top, text="Konfiguration", style="Section.TLabelframe", padding=14)
        config_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        config_frame.columnconfigure(1, weight=1)

        row = 0
        ttk.Label(config_frame, text="Quellordner").grid(row=row, column=0, sticky="w", pady=6)
        ttk.Entry(config_frame, textvariable=self.source_var).grid(row=row, column=1, sticky="ew", padx=8)
        ttk.Button(config_frame, text="Auswählen", command=self._choose_source).grid(row=row, column=2, sticky="ew")

        row += 1
        ttk.Label(config_frame, text="Zielordner").grid(row=row, column=0, sticky="w", pady=6)
        ttk.Entry(config_frame, textvariable=self.target_var).grid(row=row, column=1, sticky="ew", padx=8)
        ttk.Button(config_frame, text="Auswählen", command=self._choose_target).grid(row=row, column=2, sticky="ew")

        row += 1
        ttk.Label(config_frame, text="ExifTool-Pfad").grid(row=row, column=0, sticky="w", pady=6)
        ttk.Entry(config_frame, textvariable=self.exiftool_var).grid(row=row, column=1, sticky="ew", padx=8)
        ttk.Button(config_frame, text="Suchen", command=self._choose_exiftool).grid(row=row, column=2, sticky="ew")

        row += 1
        ttk.Label(config_frame, text="Ordner-Template").grid(row=row, column=0, sticky="w", pady=6)
        ttk.Entry(config_frame, textvariable=self.template_var).grid(row=row, column=1, columnspan=2, sticky="ew", padx=(8, 0))

        row += 1
        options = ttk.Frame(config_frame)
        options.grid(row=row, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        ttk.Label(options, text="Aktion:").grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(options, text="Kopieren", variable=self.action_var, value="copy").grid(row=0, column=1, sticky="w", padx=(10, 4))
        ttk.Radiobutton(options, text="Verschieben", variable=self.action_var, value="move").grid(row=0, column=2, sticky="w", padx=4)
        ttk.Checkbutton(options, text="Bei fehlenden Metadaten Dateizeit verwenden", variable=self.fallback_var).grid(row=0, column=3, sticky="w", padx=(20, 0))

        row += 1
        actions = ttk.Frame(config_frame)
        actions.grid(row=row, column=0, columnspan=3, sticky="ew", pady=(16, 0))
        ttk.Button(actions, text="Vorschau", style="Primary.TButton", command=self._preview).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(actions, text="Ausführen", style="Primary.TButton", command=self._apply).grid(row=0, column=1, padx=(0, 8))
        ttk.Button(actions, text="Liste leeren", command=self._clear_results).grid(row=0, column=2)

        info_frame = ttk.LabelFrame(top, text="Hinweise", style="Section.TLabelframe", padding=14)
        info_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        info_frame.columnconfigure(0, weight=1)

        hints = (
            "• Vorschau ist sicher und verändert nichts.\n"
            "• ExifTool bleibt für viele Formate und Videos der wichtigste Baustein.\n"
            "• Tkinter ist hier nur die Startbasis. Für eine spätere moderne Oberfläche ist PySide6 der saubere nächste Schritt.\n"
            "• Die Kernlogik bleibt von der Oberfläche getrennt, damit der spätere UI-Wechsel kein Totalschaden wird."
        )
        ttk.Label(info_frame, text=hints, justify="left").grid(row=0, column=0, sticky="nw")

        status_card = ttk.Frame(info_frame)
        status_card.grid(row=1, column=0, sticky="ew", pady=(18, 0))
        status_card.columnconfigure(0, weight=1)
        ttk.Label(status_card, text="Status", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(status_card, textvariable=self.status_var).grid(row=1, column=0, sticky="w", pady=(2, 6))
        ttk.Label(status_card, text="Zusammenfassung", font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky="w")
        ttk.Label(status_card, textvariable=self.summary_var, wraplength=500, justify="left").grid(row=3, column=0, sticky="w", pady=(2, 0))

        bottom.columnconfigure(0, weight=1)
        bottom.rowconfigure(0, weight=4)
        bottom.rowconfigure(1, weight=2)

        table_frame = ttk.LabelFrame(bottom, text="Ergebnisse", style="Section.TLabelframe", padding=10)
        table_frame.grid(row=0, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        columns = ("action", "source", "destination", "date_source", "date_value")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.tree.heading("action", text="Aktion")
        self.tree.heading("source", text="Quelle")
        self.tree.heading("destination", text="Ziel")
        self.tree.heading("date_source", text="Datumsquelle")
        self.tree.heading("date_value", text="Datumswert")
        self.tree.column("action", width=90, stretch=False)
        self.tree.column("source", width=280)
        self.tree.column("destination", width=430)
        self.tree.column("date_source", width=180, stretch=False)
        self.tree.column("date_value", width=180, stretch=False)
        self.tree.grid(row=0, column=0, sticky="nsew")

        tree_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        tree_scroll.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=tree_scroll.set)

        log_frame = ttk.LabelFrame(bottom, text="Protokoll", style="Section.TLabelframe", padding=10)
        log_frame.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log_text = tk.Text(log_frame, wrap="word", height=10, font=("Consolas", 10))
        self.log_text.grid(row=0, column=0, sticky="nsew")
        log_scroll = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        log_scroll.grid(row=0, column=1, sticky="ns")
        self.log_text.configure(yscrollcommand=log_scroll.set)

    def _choose_source(self) -> None:
        path = filedialog.askdirectory(title="Quellordner auswählen")
        if path:
            self.source_var.set(path)

    def _choose_target(self) -> None:
        path = filedialog.askdirectory(title="Zielordner auswählen")
        if path:
            self.target_var.set(path)

    def _choose_exiftool(self) -> None:
        path = filedialog.askopenfilename(
            title="ExifTool auswählen",
            filetypes=[("Exe-Dateien", "*.exe"), ("Alle Dateien", "*.*")],
        )
        if path:
            self.exiftool_var.set(path)

    def _append_log(self, line: str) -> None:
        self.log_text.insert("end", line + "\n")
        self.log_text.see("end")

    def _clear_results(self) -> None:
        if self.worker_thread and self.worker_thread.is_alive():
            messagebox.showwarning("Läuft noch", "Warte, bis der aktuelle Lauf beendet ist.")
            return
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.log_text.delete("1.0", "end")
        self.status_var.set("Bereit")
        self.summary_var.set("Liste geleert.")

    def _build_config(self, apply_changes: bool) -> WorkerConfig | None:
        source = Path(self.source_var.get().strip()) if self.source_var.get().strip() else None
        target = Path(self.target_var.get().strip()) if self.target_var.get().strip() else None
        template = self.template_var.get().strip()

        if not source or not source.exists() or not source.is_dir():
            messagebox.showerror("Fehler", "Quellordner fehlt oder existiert nicht.")
            return None
        if not target:
            messagebox.showerror("Fehler", "Zielordner fehlt.")
            return None
        if not template:
            messagebox.showerror("Fehler", "Ordner-Template darf nicht leer sein.")
            return None

        return WorkerConfig(
            source=source,
            target=target,
            exiftool_path=self.exiftool_var.get().strip() or None,
            template=template,
            action=self.action_var.get(),
            apply_changes=apply_changes,
            fallback_to_file_time=self.fallback_var.get(),
        )

    def _preview(self) -> None:
        config = self._build_config(apply_changes=False)
        if not config:
            return
        self._start_worker(config)

    def _apply(self) -> None:
        config = self._build_config(apply_changes=True)
        if not config:
            return
        prompt = (
            f"Es werden Dateien wirklich {'verschoben' if config.action == 'move' else 'kopiert'}.\n\n"
            f"Quelle: {config.source}\n"
            f"Ziel: {config.target}\n\n"
            "Fortfahren?"
        )
        if not messagebox.askyesno("Ausführung bestätigen", prompt):
            return
        self._start_worker(config)

    def _start_worker(self, config: WorkerConfig) -> None:
        if self.worker_thread and self.worker_thread.is_alive():
            messagebox.showwarning("Läuft noch", "Es läuft bereits ein Vorgang.")
            return

        for item in self.tree.get_children():
            self.tree.delete(item)
        self.log_text.delete("1.0", "end")
        self.status_var.set("Analyse läuft ...")
        self.summary_var.set("Noch keine Ergebnisse.")

        self.worker_thread = threading.Thread(target=self._worker_run, args=(config,), daemon=True)
        self.worker_thread.start()

    def _worker_run(self, config: WorkerConfig) -> None:
        try:
            exiftool_path = discover_exiftool(config.exiftool_path)
            client = ExifToolClient(exiftool_path)
            version = client.get_version()
            self.queue.put(("info", f"ExifTool erkannt: {exiftool_path} (Version {version})"))

            summary = organize(
                source_dir=config.source,
                target_dir=config.target,
                exiftool=client,
                template=config.template,
                action=config.action,
                apply_changes=config.apply_changes,
                fallback_to_file_time=config.fallback_to_file_time,
                on_decision=lambda decision: self.queue.put(("decision", decision)),
                on_error=lambda path, exc: self.queue.put(("error", (path, exc))),
                on_info=lambda text: self.queue.put(("info", text)),
            )
            self.queue.put(("done", summary))
        except ExifToolError as exc:
            self.queue.put(("fatal", str(exc)))
        except Exception as exc:
            self.queue.put(("fatal", f"Unerwarteter Fehler: {exc}"))

    def _poll_queue(self) -> None:
        try:
            while True:
                event, payload = self.queue.get_nowait()
                if event == "decision":
                    self._handle_decision(payload)
                elif event == "error":
                    path, exc = payload
                    self._append_log(f"FEHLER: {path} -> {exc}")
                elif event == "info":
                    self._append_log(str(payload))
                elif event == "fatal":
                    self.status_var.set("Fehlgeschlagen")
                    self.summary_var.set(str(payload))
                    self._append_log(str(payload))
                    messagebox.showerror("Fehler", str(payload))
                elif event == "done":
                    self._handle_done(payload)
        except queue.Empty:
            pass
        finally:
            self.after(120, self._poll_queue)

    def _handle_decision(self, decision: MediaDecision) -> None:
        self.tree.insert(
            "",
            "end",
            values=(
                decision.action.upper(),
                str(decision.source),
                str(decision.destination),
                decision.date_source,
                decision.date_value or "-",
            ),
        )
        self._append_log(f"{decision.action.upper()}: {decision.source.name} -> {decision.destination}")

    def _handle_done(self, summary: OrganizeSummary) -> None:
        self.status_var.set("Fertig")
        mode_text = "ausgeführt" if summary.applied_files else "nur als Vorschau simuliert"
        self.summary_var.set(
            f"Dateien gefunden: {summary.total_files} | verarbeitet: {summary.applied_files} | "
            f"Vorschau: {summary.skipped_files} | ohne Datum: {summary.no_date_files} | Fehler: {summary.errors} | {mode_text}"
        )
        self._append_log("--- Lauf abgeschlossen ---")


def main() -> int:
    app = App()
    app.mainloop()
    return 0

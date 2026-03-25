from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .sorter import SortConfig, organize_media


class MediaManagerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Media Manager")
        self.root.geometry("980x700")
        self.root.minsize(860, 620)

        self.source_var = tk.StringVar()
        self.target_var = tk.StringVar()
        self.exiftool_var = tk.StringVar()
        self.template_var = tk.StringVar(value="{year}/{month}")
        self.mode_var = tk.StringVar(value="copy")
        self.apply_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="Ready")

        self._build_ui()

    def _build_ui(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        main = ttk.Frame(self.root, padding=16)
        main.grid(row=0, column=0, sticky="nsew")
        main.columnconfigure(0, weight=1)
        main.rowconfigure(3, weight=1)

        header = ttk.Frame(main)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="Media Manager", font=("Segoe UI", 20, "bold")).grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            header,
            text="Desktop foundation for sorting photos and videos by date.",
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        form = ttk.LabelFrame(main, text="Inputs", padding=12)
        form.grid(row=1, column=0, sticky="ew")
        form.columnconfigure(1, weight=1)

        self._add_path_row(form, 0, "Source folder", self.source_var, self._choose_source_dir)
        self._add_path_row(form, 1, "Target folder", self.target_var, self._choose_target_dir)
        self._add_path_row(form, 2, "ExifTool", self.exiftool_var, self._choose_exiftool)

        ttk.Label(form, text="Target template").grid(row=3, column=0, sticky="w", pady=(10, 0))
        ttk.Entry(form, textvariable=self.template_var).grid(
            row=3, column=1, columnspan=2, sticky="ew", pady=(10, 0)
        )

        mode_frame = ttk.Frame(form)
        mode_frame.grid(row=4, column=0, columnspan=3, sticky="w", pady=(10, 0))
        ttk.Label(mode_frame, text="Mode:").pack(side="left")
        ttk.Radiobutton(mode_frame, text="Copy", variable=self.mode_var, value="copy").pack(
            side="left", padx=(10, 0)
        )
        ttk.Radiobutton(mode_frame, text="Move", variable=self.mode_var, value="move").pack(
            side="left", padx=(10, 0)
        )
        ttk.Checkbutton(
            mode_frame,
            text="Apply changes for real",
            variable=self.apply_var,
        ).pack(side="left", padx=(20, 0))

        actions = ttk.Frame(main)
        actions.grid(row=2, column=0, sticky="ew", pady=12)
        ttk.Button(actions, text="Preview / Run", command=self._run).pack(side="left")
        ttk.Button(actions, text="Clear results", command=self._clear_results).pack(
            side="left", padx=(8, 0)
        )

        results_frame = ttk.LabelFrame(main, text="Results", padding=8)
        results_frame.grid(row=3, column=0, sticky="nsew")
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

        columns = ("status", "source", "target", "reason")
        self.tree = ttk.Treeview(results_frame, columns=columns, show="headings")
        self.tree.heading("status", text="Status")
        self.tree.heading("source", text="Source")
        self.tree.heading("target", text="Target")
        self.tree.heading("reason", text="Details")
        self.tree.column("status", width=110, anchor="center")
        self.tree.column("source", width=280)
        self.tree.column("target", width=280)
        self.tree.column("reason", width=220)
        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        status_bar = ttk.Label(main, textvariable=self.status_var, relief="sunken", anchor="w")
        status_bar.grid(row=4, column=0, sticky="ew", pady=(12, 0))

    def _add_path_row(self, parent: ttk.Frame, row: int, label: str, variable: tk.StringVar, command) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=(0 if row == 0 else 10, 0))
        ttk.Entry(parent, textvariable=variable).grid(
            row=row,
            column=1,
            sticky="ew",
            padx=(10, 10),
            pady=(0 if row == 0 else 10, 0),
        )
        ttk.Button(parent, text="Browse", command=command).grid(
            row=row,
            column=2,
            pady=(0 if row == 0 else 10, 0),
        )

    def _choose_source_dir(self) -> None:
        selected = filedialog.askdirectory(title="Select source folder")
        if selected:
            self.source_var.set(selected)

    def _choose_target_dir(self) -> None:
        selected = filedialog.askdirectory(title="Select target folder")
        if selected:
            self.target_var.set(selected)

    def _choose_exiftool(self) -> None:
        selected = filedialog.askopenfilename(
            title="Select ExifTool executable",
            filetypes=[("Executable", "*.exe"), ("All files", "*.*")],
        )
        if selected:
            self.exiftool_var.set(selected)

    def _clear_results(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.status_var.set("Results cleared")

    def _run(self) -> None:
        source = Path(self.source_var.get().strip()) if self.source_var.get().strip() else None
        target = Path(self.target_var.get().strip()) if self.target_var.get().strip() else None
        exiftool = Path(self.exiftool_var.get().strip()) if self.exiftool_var.get().strip() else None

        if source is None or not source.is_dir():
            messagebox.showerror("Error", "Please select a valid source folder.")
            return
        if target is None:
            messagebox.showerror("Error", "Please select a target folder.")
            return

        target.mkdir(parents=True, exist_ok=True)

        config = SortConfig(
            source_dir=source,
            target_dir=target,
            target_template=self.template_var.get().strip() or "{year}/{month}",
            dry_run=not self.apply_var.get(),
            mode=self.mode_var.get(),
            exiftool_path=exiftool,
        )

        try:
            self.status_var.set("Processing ...")
            self.root.update_idletasks()
            results = organize_media(config)
        except Exception as exc:  # pragma: no cover - GUI fallback
            messagebox.showerror("Error", str(exc))
            self.status_var.set("An error occurred")
            return

        self._clear_results()
        for entry in results.entries:
            source_text = str(entry.source)
            target_text = str(entry.target) if entry.target is not None else "-"
            reason_text = entry.reason or "-"
            self.tree.insert("", "end", values=(entry.action, source_text, target_text, reason_text))

        self.status_var.set(
            f"Processed: {results.processed} | Planned/Executed: {results.organized} | "
            f"Skipped: {results.skipped} | Errors: {results.errors}"
        )


def main() -> int:
    root = tk.Tk()
    app = MediaManagerApp(root)
    root.mainloop()
    return 0

import json
import tkinter as tk
from tkinter import ttk, messagebox


class LogDetailModal(tk.Toplevel):
    """Modal popup displaying full, untruncated details of a clicked log row."""

    def __init__(self, parent, title: str, fields: dict[str, str]):
        super().__init__(parent)
        self.title(title)
        self.fields = fields
        self.geometry("520x420")
        self.resizable(True, True)
        self.transient(parent.winfo_toplevel())
        self.grab_set()

        self._build_ui()

    def _build_ui(self):
        container = ttk.Frame(self, padding=15)
        container.pack(fill="both", expand=True)

        ttk.Label(
            container, text=self.title(), font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=(0, 10))

        text_frame = ttk.Frame(container)
        text_frame.pack(fill="both", expand=True, pady=(0, 12))

        self.text_area = tk.Text(
            text_frame, wrap="word", font=("Consolas", 10), padx=10, pady=10
        )
        y_scroll = ttk.Scrollbar(text_frame, orient="vertical", command=self.text_area.yview)
        self.text_area.configure(yscrollcommand=y_scroll.set)

        self.text_area.pack(side="left", fill="both", expand=True)
        y_scroll.pack(side="right", fill="y")

        for label, value in self.fields.items():
            self.text_area.insert(tk.END, f"{label}:\n", "bold")
            self.text_area.insert(tk.END, f"{value}\n\n")

        self.text_area.tag_configure("bold", font=("Segoe UI", 10, "bold"))
        self.text_area.configure(state="disabled")

        btn_row = ttk.Frame(container)
        btn_row.pack(fill="x")

        ttk.Button(
            btn_row, text="Copy as JSON", command=self._copy_json
        ).pack(side="left")

        ttk.Button(
            btn_row, text="Close", command=self.destroy
        ).pack(side="right")

    def _copy_json(self):
        self.clipboard_clear()
        self.clipboard_append(json.dumps(self.fields, indent=2))
        messagebox.showinfo("Copied", "Log details copied as JSON.", parent=self)
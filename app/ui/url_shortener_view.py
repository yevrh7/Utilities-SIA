import tkinter as tk
from tkinter import ttk, messagebox
from app.modules.url_shortener import shorten_url, get_user_urls


class UrlShortenerFrame(ttk.Frame):
    def __init__(self, parent, user_id: int):
        super().__init__(parent)
        self.user_id = user_id
        self._build_ui()

    def _build_ui(self):
        ttk.Label(
            self,
            text="3B.1 - URL Shortener",
            style="Header.TLabel",
        ).pack(anchor="w", pady=(0, 15))

        # Input section
        input_frame = ttk.Frame(self)
        input_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(input_frame, text="Enter Long URL:").pack(anchor="w")

        entry_row = ttk.Frame(input_frame)
        entry_row.pack(fill="x", pady=(4, 0))

        self.url_entry = ttk.Entry(entry_row, font=("Segoe UI", 10))
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ttk.Button(
            entry_row,
            text="Shorten URL",
            command=self._handle_shorten,
        ).pack(side="right")

        # Result + Copy row
        result_frame = ttk.Frame(self)
        result_frame.pack(fill="x", pady=(0, 15))

        ttk.Label(result_frame, text="Shortened Link:").pack(side="left", padx=(0, 8))
        self.short_url_var = tk.StringVar()
        self.result_entry = ttk.Entry(
            result_frame, textvariable=self.short_url_var, state="readonly", width=40
        )
        self.result_entry.pack(side="left", padx=(0, 8))

        ttk.Button(
            result_frame,
            text="Copy",
            command=self._copy_short_url,
        ).pack(side="left")

        # History table
        ttk.Label(self, text="Your Shortened URLs:").pack(anchor="w", pady=(0, 5))

        columns = ("original", "short", "date")
        self.url_tree = ttk.Treeview(self, columns=columns, show="headings", height=12)
        self.url_tree.heading("original", text="Original URL")
        self.url_tree.heading("short", text="Short URL")
        self.url_tree.heading("date", text="Created At")

        self.url_tree.column("original", width=380)
        self.url_tree.column("short", width=180)
        self.url_tree.column("date", width=160)
        self.url_tree.pack(fill="both", expand=True)

        self._refresh_url_history()

    def _handle_shorten(self):
        long_url = self.url_entry.get()
        success, result = shorten_url(self.user_id, long_url)
        if success:
            self.short_url_var.set(result)
            self.url_entry.delete(0, tk.END)
            self._refresh_url_history()
        else:
            messagebox.showerror("Error", result)

    def _copy_short_url(self):
        val = self.short_url_var.get()
        if val:
            self.clipboard_clear()
            self.clipboard_append(val)
            messagebox.showinfo("Copied", "Short URL copied to clipboard.")

    def _refresh_url_history(self):
        for row in self.url_tree.get_children():
            self.url_tree.delete(row)

        for record in get_user_urls(self.user_id):
            self.url_tree.insert(
                "", "end", values=(record["original_url"], record["short_url"], record["created_at"])
            )
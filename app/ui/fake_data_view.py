import json
import tkinter as tk
from tkinter import ttk, messagebox
from app.modules.fake_data import create_and_save_fake_data, get_user_mock_data


FIELD_META = {
    "full_name": ("Full Name", 140),
    "email": ("Email", 170),
    "phone_number": ("Phone Number", 130),
    "street_address": ("Street Address", 180),
    "city": ("City", 110),
    "country": ("Country", 120),
    "birthdate": ("Birthdate", 95),
    "job_title": ("Job Title", 140),
    "company": ("Company", 140),
    "national_id": ("National ID", 110),
}


class FakeDataFrame(ttk.Frame):
    def __init__(self, parent, user_id: int):
        super().__init__(parent)
        self.user_id = user_id
        self.field_vars: dict[str, tk.BooleanVar] = {}
        self.active_generated_cols: list[str] = []
        self._build_ui()

    def _build_ui(self):

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.gen_tab = ttk.Frame(self.notebook, padding=10)
        self.history_tab = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.gen_tab, text="Generate Data")
        self.notebook.add(self.history_tab, text="Saved History")

        self._build_generator_tab()
        self._build_history_tab()

    # ==========================================
    # TAB 1: GENERATOR (DYNAMIC CHECKBOXES)
    # ==========================================
    def _build_generator_tab(self):
        # Field Selection Group
        fields_box = ttk.LabelFrame(self.gen_tab, text="Select Fields to Generate", padding=10)
        fields_box.pack(fill="x", pady=(0, 10))

        # Quick toggle buttons
        toggle_row = ttk.Frame(fields_box)
        toggle_row.grid(row=0, column=0, columnspan=5, sticky="w", pady=(0, 8))
        ttk.Button(toggle_row, text="Select All", command=lambda: self._set_all_fields(True)).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(toggle_row, text="Clear All", command=lambda: self._set_all_fields(False)).pack(
            side="left"
        )

        # 2 rows x 5 columns grid of checkboxes
        for idx, (key, (label, _)) in enumerate(FIELD_META.items()):
            var = tk.BooleanVar(value=True)
            self.field_vars[key] = var
            row = (idx // 5) + 1
            col = idx % 5
            ttk.Checkbutton(fields_box, text=label, variable=var).grid(
                row=row, column=col, sticky="w", padx=(0, 16), pady=3
            )

        # Action & Count Row
        action_row = ttk.Frame(self.gen_tab)
        action_row.pack(fill="x", pady=(0, 10))

        ttk.Label(action_row, text="Records (10–100):").pack(side="left", padx=(0, 8))
        self.count_var = tk.StringVar(value="10")
        ttk.Spinbox(
            action_row, from_=10, to=100, textvariable=self.count_var, width=6
        ).pack(side="left", padx=(0, 12))

        ttk.Button(
            action_row, text="Generate & Save", command=self._handle_generate
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            action_row, text="Copy Selected Row (JSON)", command=self._copy_generated_json
        ).pack(side="right")

        self.batch_status_label = ttk.Label(
            self.gen_tab, text="Select fields above and click 'Generate & Save'."
        )
        self.batch_status_label.pack(anchor="w", pady=(0, 6))

        # Results Treeview (shows ONLY the current batch & selected columns)
        gen_table_container = ttk.Frame(self.gen_tab)
        gen_table_container.pack(fill="both", expand=True)

        self.gen_tree = ttk.Treeview(gen_table_container, show="headings", height=12)
        y_scroll = ttk.Scrollbar(gen_table_container, orient="vertical", command=self.gen_tree.yview)
        x_scroll = ttk.Scrollbar(gen_table_container, orient="horizontal", command=self.gen_tree.xview)
        self.gen_tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        self.gen_tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        gen_table_container.rowconfigure(0, weight=1)
        gen_table_container.columnconfigure(0, weight=1)

    def _set_all_fields(self, state: bool):
        for var in self.field_vars.values():
            var.set(state)

    def _handle_generate(self):
        selected_fields = [k for k, var in self.field_vars.items() if var.get()]
        if not selected_fields:
            messagebox.showwarning("No Fields Selected", "Check at least one data field first.")
            return

        try:
            count = int(self.count_var.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Enter a valid integer between 10 and 100.")
            return

        success, result = create_and_save_fake_data(self.user_id, selected_fields, count)
        if not success:
            messagebox.showerror("Error", str(result))
            return

        # Reconfigure columns dynamically to show ONLY checked fields for this batch
        self.active_generated_cols = selected_fields
        self.gen_tree.delete(*self.gen_tree.get_children())
        self.gen_tree["columns"] = selected_fields

        for col in selected_fields:
            label, width = FIELD_META[col]
            self.gen_tree.heading(col, text=label)
            self.gen_tree.column(col, width=width, minwidth=80)

        for record in result:
            self.gen_tree.insert("", "end", values=[record[col] for col in selected_fields])

        batch_id = result[0]["batch_id"]
        self.batch_status_label.config(
            text=f"Generated {len(result)} records (Batch ID: {batch_id}) — Saved to database."
        )
        self._refresh_history_table()

    def _copy_generated_json(self):
        selected = self.gen_tree.selection()
        if not selected or not self.active_generated_cols:
            messagebox.showwarning("No Selection", "Select a generated row first.")
            return

        values = self.gen_tree.item(selected[0], "values")
        record_dict = dict(zip(self.active_generated_cols, values))
        self.clipboard_clear()
        self.clipboard_append(json.dumps(record_dict, indent=2))
        messagebox.showinfo("Copied", "Selected generated row copied as JSON.")

    # ==========================================
    # TAB 2: SAVED HISTORY (ALL STORED RECORDS)
    # ==========================================
    def _build_history_tab(self):
        top_bar = ttk.Frame(self.history_tab)
        top_bar.pack(fill="x", pady=(0, 8))

        ttk.Label(top_bar, text="All Stored Mock Data Batches:").pack(side="left")

        ttk.Button(
            top_bar, text="Copy Selected Row (JSON)", command=self._copy_history_json
        ).pack(side="right")

        ttk.Button(
            top_bar, text="Refresh", command=self._refresh_history_table
        ).pack(side="right", padx=(0, 8))

        hist_container = ttk.Frame(self.history_tab)
        hist_container.pack(fill="both", expand=True)

        cols = ("batch_id", *FIELD_META.keys(), "created_at")
        self.hist_tree = ttk.Treeview(hist_container, columns=cols, show="headings", height=15)

        self.hist_tree.heading("batch_id", text="Batch ID")
        self.hist_tree.column("batch_id", width=80, minwidth=70)

        for key, (label, width) in FIELD_META.items():
            self.hist_tree.heading(key, text=label)
            self.hist_tree.column(key, width=width, minwidth=75)

        self.hist_tree.heading("created_at", text="Created At")
        self.hist_tree.column("created_at", width=140, minwidth=110)

        y_scroll = ttk.Scrollbar(hist_container, orient="vertical", command=self.hist_tree.yview)
        x_scroll = ttk.Scrollbar(hist_container, orient="horizontal", command=self.hist_tree.xview)
        self.hist_tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        self.hist_tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        hist_container.rowconfigure(0, weight=1)
        hist_container.columnconfigure(0, weight=1)

        self._refresh_history_table()

    def _refresh_history_table(self):
        for row in self.hist_tree.get_children():
            self.hist_tree.delete(row)

        for record in get_user_mock_data(self.user_id):
            self.hist_tree.insert(
                "",
                "end",
                values=(
                    record["batch_id"],
                    record["full_name"] or "—",
                    record["email"] or "—",
                    record["phone_number"] or "—",
                    record["street_address"] or "—",
                    record["city"] or "—",
                    record["country"] or "—",
                    record["birthdate"] or "—",
                    record["job_title"] or "—",
                    record["company"] or "—",
                    record["national_id"] or "—",
                    record["created_at"],
                ),
            )

    def _copy_history_json(self):
        selected = self.hist_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a row in History first.")
            return

        values = self.hist_tree.item(selected[0], "values")
        keys = ("batch_id", *FIELD_META.keys(), "created_at")
        # Exclude ungenerated placeholder fields ('—') from copied JSON
        record_dict = {k: v for k, v in zip(keys, values) if v != "—"}
        self.clipboard_clear()
        self.clipboard_append(json.dumps(record_dict, indent=2))
        messagebox.showinfo("Copied", "History record copied as JSON.")
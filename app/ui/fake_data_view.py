import json
import tkinter as tk
from tkinter import ttk, messagebox
from app.modules.fake_data import create_and_save_fake_data, get_user_mock_data


class FakeDataFrame(ttk.Frame):
    def __init__(self, parent, user_id: int):
        super().__init__(parent)
        self.user_id = user_id
        self._build_ui()

    def _build_ui(self):

        # Controls Row
        control_frame = ttk.Frame(self)
        control_frame.pack(fill="x", pady=(0, 12))

        ttk.Label(control_frame, text="Records to Generate (10–100):").pack(side="left", padx=(0, 8))

        self.count_var = tk.StringVar(value="10")
        self.count_spinbox = ttk.Spinbox(
            control_frame, from_=10, to=100, textvariable=self.count_var, width=6
        )
        self.count_spinbox.pack(side="left", padx=(0, 10))

        ttk.Button(
            control_frame,
            text="Generate Data",
            command=self._handle_generate,
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            control_frame,
            text="Copy Selected Row (JSON)",
            command=self._copy_selected_json,
        ).pack(side="right")

        # Scrollable 10-Field (+ Batch ID) Treeview
        table_container = ttk.Frame(self)
        table_container.pack(fill="both", expand=True)

        columns = (
            "batch_id", "full_name", "email", "phone_number",
            "street_address", "city", "country", "birthdate",
            "job_title", "company", "national_id"
        )
        self.tree = ttk.Treeview(table_container, columns=columns, show="headings", height=14)

        headers = {
            "batch_id": ("Batch ID", 80),
            "full_name": ("Full Name", 140),
            "email": ("Email", 170),
            "phone_number": ("Phone", 130),
            "street_address": ("Street Address", 180),
            "city": ("City", 110),
            "country": ("Country", 120),
            "birthdate": ("Birthdate", 95),
            "job_title": ("Job Title", 140),
            "company": ("Company", 140),
            "national_id": ("National ID", 110),
        }

        for col, (label, width) in headers.items():
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, minwidth=75)

        y_scroll = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        x_scroll = ttk.Scrollbar(table_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        table_container.rowconfigure(0, weight=1)
        table_container.columnconfigure(0, weight=1)

        self._refresh_table()

    def _handle_generate(self):
        try:
            count = int(self.count_var.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Enter a valid integer between 10 and 100.")
            return

        success, result = create_and_save_fake_data(self.user_id, count)
        if success:
            self._refresh_table()
        else:
            messagebox.showerror("Error", str(result))

    def _copy_selected_json(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a row in the table first.")
            return

        values = self.tree.item(selected[0], "values")
        keys = (
            "batch_id", "full_name", "email", "phone_number",
            "street_address", "city", "country", "birthdate",
            "job_title", "company", "national_id"
        )
        record_dict = dict(zip(keys, values))
        self.clipboard_clear()
        self.clipboard_append(json.dumps(record_dict, indent=2))
        messagebox.showinfo("Copied", "Selected profile copied as JSON.")

    def _refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for record in get_user_mock_data(self.user_id):
            self.tree.insert(
                "",
                "end",
                values=(
                    record["batch_id"],
                    record["full_name"],
                    record["email"],
                    record["phone_number"],
                    record["street_address"],
                    record["city"],
                    record["country"],
                    record["birthdate"],
                    record["job_title"],
                    record["company"],
                    record["national_id"],
                ),
            )
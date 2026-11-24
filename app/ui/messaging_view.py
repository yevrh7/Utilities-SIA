import threading
import tkinter as tk
from tkinter import ttk, messagebox
from app.modules.messaging import send_email, send_sms, get_user_message_logs
from app.ui.log_detail_modal import LogDetailModal


class MessagingFrame(ttk.Frame):
    def __init__(self, parent, user_id: int):
        super().__init__(parent)
        self.user_id = user_id
        self.logs_cache: dict[str, dict] = {}
        self._build_ui()
        self._refresh_logs()

    def _build_ui(self):
        # Split layout: Left = Compose Form, Right = Sent History Logs
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # --- LEFT PANEL: Compose Form ---
        form_frame = ttk.LabelFrame(self, text="Compose Message", padding=15)
        form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Mode Selector ComboBox (Email / SMS)
        ttk.Label(form_frame, text="Message Type:").pack(anchor="w")
        self.mode_combo = ttk.Combobox(
            form_frame, values=["Email", "SMS"], state="readonly", font=("Segoe UI", 10)
        )
        self.mode_combo.current(0)
        self.mode_combo.pack(fill="x", pady=(2, 12))
        self.mode_combo.bind("<<ComboboxSelected>>", self._on_mode_change)

        # Recipient Field
        self.recipient_label = ttk.Label(form_frame, text="Recipient Email:")
        self.recipient_label.pack(anchor="w")
        self.recipient_entry = ttk.Entry(form_frame, font=("Segoe UI", 10))
        self.recipient_entry.pack(fill="x", pady=(2, 12))

        # Subject Container (Shown only for Email)
        self.subject_container = ttk.Frame(form_frame)
        ttk.Label(self.subject_container, text="Subject:").pack(anchor="w")
        self.subject_entry = ttk.Entry(self.subject_container, font=("Segoe UI", 10))
        self.subject_entry.pack(fill="x", pady=(2, 12))
        self.subject_container.pack(fill="x")

        # Message Body
        self.body_container = ttk.Frame(form_frame)
        self.body_container.pack(fill="both", expand=True)

        ttk.Label(self.body_container, text="Message:").pack(anchor="w")
        self.message_text = tk.Text(
            self.body_container, height=7, font=("Segoe UI", 10), wrap="word"
        )
        self.message_text.pack(fill="both", expand=True, pady=(2, 12))

        # Send Button
        self.send_btn = ttk.Button(
            self.body_container, text="Send Message", command=self._handle_send
        )
        self.send_btn.pack(fill="x")

        # --- RIGHT PANEL: Delivery History from SQLite ---
        logs_frame = ttk.LabelFrame(
            self, text="Recent Delivery Logs (Double-click row to inspect)", padding=15
        )
        logs_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        columns = ("recipient", "subject", "status", "sent_at")
        self.tree = ttk.Treeview(logs_frame, columns=columns, show="headings", height=12)
        self.tree.heading("recipient", text="Recipient")
        self.tree.heading("subject", text="Subject / Type")
        self.tree.heading("status", text="Status")
        self.tree.heading("sent_at", text="Timestamp")

        self.tree.column("recipient", width=110)
        self.tree.column("subject", width=100)
        self.tree.column("status", width=85)
        self.tree.column("sent_at", width=110)
        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<Double-1>", self._on_log_click)

        ttk.Button(
            logs_frame, text="Refresh Logs", command=self._refresh_logs
        ).pack(fill="x", pady=(10, 0))

    def _on_log_click(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        item_id = selected[0]
        log = self.logs_cache.get(item_id)
        if not log:
            return

        body = log.get("body") or "(No message body recorded for older log)"

        details = {
            "Recipient": log.get("recipient", ""),
            "Subject / Type": log.get("subject", ""),
            "Status": log.get("status", ""),
            "Sent At": str(log.get("sent_at", "")),
            "Message Body": body,
        }

        LogDetailModal(self, "Message Delivery Log Details", details)

    def _on_mode_change(self, event):
        mode = self.mode_combo.get()
        if mode == "Email":
            self.recipient_label.config(text="Recipient Email:")
            self.subject_container.pack(fill="x", before=self.body_container)
        else:
            self.recipient_label.config(text="Mobile Number (e.g., 09171234567):")
            self.subject_container.pack_forget()

    def _handle_send(self):
        mode = self.mode_combo.get()
        recipient = self.recipient_entry.get().strip()
        subject = self.subject_entry.get().strip()
        body = self.message_text.get("1.0", tk.END).strip()

        if not recipient or not body:
            messagebox.showwarning("Missing Fields", "Recipient and Message are required.")
            return

        self.send_btn.config(state="disabled", text="Sending...")

        threading.Thread(
            target=self._send_worker,
            args=(mode, recipient, subject, body),
            daemon=True,
        ).start()

    def _send_worker(self, mode: str, recipient: str, subject: str, body: str):
        if mode == "Email":
            success, msg = send_email(self.user_id, recipient, subject, body)
        else:
            success, msg = send_sms(self.user_id, recipient, body)

        self.after(0, lambda: self._on_send_complete(success, msg))

    def _on_send_complete(self, success: bool, msg: str):
        self.send_btn.config(state="normal", text="Send Message")
        self._refresh_logs()

        if success:
            messagebox.showinfo("Success", msg)
            self.recipient_entry.delete(0, tk.END)
            self.subject_entry.delete(0, tk.END)
            self.message_text.delete("1.0", tk.END)
        else:
            messagebox.showerror("Delivery Error", msg)

    def _refresh_logs(self):
        self.logs_cache.clear()
        for row in self.tree.get_children():
            self.tree.delete(row)

        logs = get_user_message_logs(self.user_id)
        for log in logs:
            item_id = self.tree.insert(
                "",
                tk.END,
                values=(log["recipient"], log["subject"], log["status"], log["sent_at"]),
            )
            self.logs_cache[item_id] = dict(log)
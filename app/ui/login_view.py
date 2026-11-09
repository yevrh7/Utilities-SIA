import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable
from app.modules.auth import register_user, authenticate_user


class LoginWindow(tk.Tk):
    def __init__(self, on_login_success: Callable[[int, str], None]):
        super().__init__()
        self.title("Utilities Suite - Authentication")
        self.geometry("400x480")
        self.resizable(False, False)

        self.on_login_success = on_login_success
        self.is_register_mode = False

        self._configure_styles()
        self._build_ui()

    def _configure_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"))
        style.configure("TButton", font=("Segoe UI", 10), padding=6)

    def _build_ui(self):
        self.main_frame = ttk.Frame(self, padding=30)
        self.main_frame.pack(fill="both", expand=True)

        self.title_label = ttk.Label(
            self.main_frame, text="User Login", style="Header.TLabel"
        )
        self.title_label.pack(pady=(0, 20))

        # Username Field
        ttk.Label(self.main_frame, text="Username:").pack(anchor="w")
        self.username_entry = ttk.Entry(self.main_frame, font=("Segoe UI", 10))
        self.username_entry.pack(fill="x", pady=(2, 15))
        self.username_entry.focus()

        # Password Field
        ttk.Label(self.main_frame, text="Password:").pack(anchor="w")
        self.password_entry = ttk.Entry(self.main_frame, show="*", font=("Segoe UI", 10))
        self.password_entry.pack(fill="x", pady=(2, 5))

        # Show/Hide Password Checkbox
        self.show_pwd_var = tk.BooleanVar(value=False)
        self.show_pwd_cb = ttk.Checkbutton(
            self.main_frame,
            text="Show Password",
            variable=self.show_pwd_var,
            command=self._toggle_password_visibility,
        )
        self.show_pwd_cb.pack(anchor="w", pady=(0, 20))

        # Action Button (Login / Register)
        self.submit_btn = ttk.Button(
            self.main_frame, text="Log In", command=self._handle_submit
        )
        self.submit_btn.pack(fill="x", pady=(0, 10))

        # Toggle Mode Button
        self.toggle_btn = ttk.Button(
            self.main_frame,
            text="Need an account? Register here",
            command=self._toggle_mode,
        )
        self.toggle_btn.pack(fill="x")

        # Allow pressing Enter to submit
        self.bind("<Return>", lambda event: self._handle_submit())

    def _toggle_password_visibility(self):
        if self.show_pwd_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")

    def _toggle_mode(self):
        self.is_register_mode = not self.is_register_mode
        if self.is_register_mode:
            self.title_label.config(text="Create Account")
            self.submit_btn.config(text="Register")
            self.toggle_btn.config(text="Already have an account? Log In")
        else:
            self.title_label.config(text="User Login")
            self.submit_btn.config(text="Log In")
            self.toggle_btn.config(text="Need an account? Register here")

    def _handle_submit(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if self.is_register_mode:
            success, msg = register_user(username, password)
            if success:
                messagebox.showinfo("Success", msg)
                self._toggle_mode()
                self.password_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Registration Error", msg)
        else:
            success, user_id, msg = authenticate_user(username, password)
            if success:
                messagebox.showinfo("Authenticated", f"Welcome back, {username}!")
                self.destroy()
                self.on_login_success(user_id, username)
            else:
                messagebox.showerror("Login Failed", msg)
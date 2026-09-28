import tkinter as tk
from tkinter import ttk

from database import authenticate_user
from dashboard import DashboardWindow
from utils import apply_theme


class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mabest Secondary School Results Checker")
        self.geometry("420x260")
        self.resizable(True, True)
        apply_theme(self)

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="School Management System").pack(anchor="center", pady=(0, 10))

        ttk.Label(frame, text="Username").pack(anchor="w")
        ttk.Entry(frame, textvariable=self.username_var, width=30).pack(fill="x", pady=(4, 10))

        ttk.Label(frame, text="Password").pack(anchor="w")
        ttk.Entry(frame, textvariable=self.password_var, show="*", width=30).pack(fill="x", pady=(4, 12))

        ttk.Button(frame, text="Login", command=self.handle_login).pack(fill="x")

        ttk.Label(frame, text="Demo account: admin / admin123")
        
    def handle_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if not username or not password:
            self.show_error("Please enter both username and password.")
            return

        user = authenticate_user(username, password)
        if user is None:
            self.show_error("Invalid username or password.")
            return

        self.username_var.set("")
        self.password_var.set("")
        self.clear_window()
        DashboardWindow(self, user=user)

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_error(self, message):
        from tkinter import messagebox

        messagebox.showerror("Login Failed", message)

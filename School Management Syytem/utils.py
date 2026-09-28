import tkinter as tk
from tkinter import messagebox, ttk


def apply_theme(root):
    style = ttk.Style(root)
    try:
        style.theme_use("default")
    except tk.TclError:
        pass

    style.configure("TButton", padding=(8, 6))
    style.configure("TEntry", padding=4)
    style.configure("TLabel", padding=2)




def show_info(parent, title, message):
    if parent is not None:
        parent.focus_set()
    messagebox.showinfo(title, message)


def show_error(parent, title, message):
    if parent is not None:
        parent.focus_set()
    messagebox.showerror(title, message)


def confirm_action(parent, title, message):
    if parent is not None:
        parent.focus_set()
    return messagebox.askyesno(title, message)


def parse_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0

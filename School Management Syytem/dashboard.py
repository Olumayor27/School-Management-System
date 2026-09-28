import tkinter as tk
from tkinter import ttk

from attendance import AttendanceManager
from course import CourseManager
from database import get_dashboard_stats
from result import ResultManager
from student import StudentManager
from teacher import TeacherManager
from utils import apply_theme


class DashboardWindow(tk.Frame):
    def __init__(self, master, user):
        super().__init__(master)
        self.master = master
        self.user = user
        self.configure(bg="#f3f7ff")
        self.pack(fill="both", expand=True)
        self.build_ui()

    def build_ui(self):
        apply_theme(self.master)

        style = ttk.Style(self.master)
        style.configure(
            "Primary.TButton",
            background="#1d4ed8",
            foreground="#ffffff",
            padding=(10, 8),
            font=("Segoe UI", 10, "bold"),
        )
        style.map(
            "Primary.TButton",
            background=[("active", "#1e40af"), ("pressed", "#1e3a8a")],
            foreground=[("active", "#ffffff"), ("pressed", "#ffffff")],
        )

        header = tk.Frame(self, bg="#1d4ed8", height=110)
        header.pack(fill="x")
        header.pack_propagate(False)

        title = tk.Label(
            header,
            text=f"Welcome, {self.user['username'].title()}",
            font=("Segoe UI", 20, "bold"),
            fg="#ffffff",
            bg="#1d4ed8",
        )
        title.pack(anchor="w", padx=22, pady=(22, 0))

        subtitle = tk.Label(
            header,
            text="School Management Dashboard",
            font=("Segoe UI", 10),
            fg="#dbeafe",
            bg="#1d4ed8",
        )
        subtitle.pack(anchor="w", padx=22, pady=(4, 0))

        stats = get_dashboard_stats()
        cards = tk.Frame(self, bg="#f3f7ff")
        cards.pack(fill="x", padx=22, pady=18)

        self.create_card(cards, "Students", str(stats["students"]), "#dbeafe")
        self.create_card(cards, "Teachers", str(stats["teachers"]), "#dcfce7")
        self.create_card(cards, "Courses", str(stats["courses"]), "#fef3c7")
        self.create_card(cards, "Attendance", f"{stats['attendance_rate']}%", "#fce7f3")

        buttons = tk.Frame(self, bg="#f3f7ff", padx=22, pady=4)
        buttons.pack(fill="both", expand=True)

        actions = [
            ("Manage Students", self.open_students),
            ("Manage Teachers", self.open_teachers),
            ("Manage Courses", self.open_courses),
            ("Manage Results", self.open_results),
            ("Mark Attendance", self.open_attendance),
        ]

        for text, command in actions:
            btn = ttk.Button(buttons, text=text, command=command, style="Primary.TButton")
            btn.pack(fill="x", pady=6)

    def create_card(self, parent, label, value, color):
        frame = tk.Frame(parent, bg="#ffffff", bd=0, padx=12, pady=14, highlightthickness=0)
        frame.pack(side="left", expand=True, fill="x", padx=8)

        top = tk.Frame(frame, bg=color, height=8)
        top.pack(fill="x")
        top.pack_propagate(False)

        tk.Label(frame, text=label, bg="#ffffff", fg="#374151", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=14, pady=(12, 0))
        tk.Label(frame, text=value, bg="#ffffff", fg="#111827", font=("Segoe UI", 24, "bold")).pack(anchor="w", padx=14, pady=(6, 14))

    def open_students(self):
        StudentManager(self.master)

    def open_teachers(self):
        TeacherManager(self.master)

    def open_courses(self):
        CourseManager(self.master)

    def open_results(self):
        ResultManager(self.master)

    def open_attendance(self):
        AttendanceManager(self.master)

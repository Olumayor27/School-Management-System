import tkinter as tk
from tkinter import ttk, messagebox

from database import add_attendance, delete_attendance, fetch_attendance, fetch_courses, fetch_students, update_attendance


class AttendanceManager(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Mark Attendance")
        self.geometry("980x540")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        self.attendance_id = None
        self.student_var = tk.StringVar()
        self.course_var = tk.StringVar()
        self.date_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Present")

        form = ttk.Frame(self, padding=8)
        form.pack(fill="x")

        ttk.Label(form, text="Student:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.student_combo = ttk.Combobox(form, textvariable=self.student_var, width=26, state="readonly")
        self.student_combo.grid(row=0, column=1, padx=6, pady=6)

        ttk.Label(form, text="Course:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.course_combo = ttk.Combobox(form, textvariable=self.course_var, width=28, state="readonly")
        self.course_combo.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form, text="Date:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(form, textvariable=self.date_var, width=30).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form, text="Status:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        ttk.Combobox(
            form,
            textvariable=self.status_var,
            values=["Present", "Absent"],
            state="readonly",
            width=27,
        ).grid(row=1, column=3, padx=5, pady=5)

        button_row = ttk.Frame(self)
        button_row.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Button(button_row, text="Save", command=self.save_attendance).pack(side="left", padx=5)
        ttk.Button(button_row, text="Update", command=self.update_selected_attendance).pack(side="left", padx=5)
        ttk.Button(button_row, text="Delete", command=self.delete_selected_attendance).pack(side="left", padx=5)
        ttk.Button(button_row, text="Clear", command=self.clear_form).pack(side="left", padx=5)

        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        columns = ("id", "student", "course", "date", "status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("student", text="Student")
        self.tree.heading("course", text="Course")
        self.tree.heading("date", text="Date")
        self.tree.heading("status", text="Status")

        for col in columns:
            self.tree.column(col, anchor="center", width=170)

        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.refresh_choices()
        self.refresh_attendance()

    def refresh_choices(self):
        students = fetch_students()
        courses = fetch_courses()
        self.student_combo["values"] = [f"{student['id']} - {student['name']}" for student in students]
        self.course_combo["values"] = [f"{course['id']} - {course['name']}" for course in courses]
        if students:
            self.student_var.set(f"{students[0]['id']} - {students[0]['name']}")
        if courses:
            self.course_var.set(f"{courses[0]['id']} - {courses[0]['name']}")

    def get_selected_student_id(self):
        value = self.student_var.get()
        if not value:
            return None
        if " - " in value:
            try:
                return int(str(value).split(" - ")[0])
            except ValueError:
                pass
        for student in fetch_students():
            if student["name"] == value:
                return student["id"]
        return None

    def get_selected_course_id(self):
        value = self.course_var.get()
        if not value:
            return None
        if " - " in value:
            try:
                return int(str(value).split(" - ")[0])
            except ValueError:
                pass
        for course in fetch_courses():
            if course["name"] == value:
                return course["id"]
        return None

    def on_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected[0])
        values = item["values"]
        self.attendance_id = values[0]

        student_name = values[1]
        course_name = values[2]
        student_id = None
        course_id = None

        for student in fetch_students():
            if student["name"] == student_name:
                student_id = student["id"]
                break
        for course in fetch_courses():
            if course["name"] == course_name:
                course_id = course["id"]
                break

        if student_id is not None:
            student_name = f"{student_id} - {student_name}"
        if course_id is not None:
            course_name = f"{course_id} - {course_name}"

        self.student_var.set(student_name)
        self.course_var.set(course_name)
        self.date_var.set(values[3])
        self.status_var.set(values[4])

    def clear_form(self):
        self.attendance_id = None
        self.date_var.set("")
        self.status_var.set("Present")
        self.refresh_choices()
        self.tree.selection_remove(self.tree.selection())

    def validate_form(self):
        if not self.date_var.get().strip():
            messagebox.showerror("Validation", "Attendance date is required.")
            return False
        return True

    def save_attendance(self):
        if not self.validate_form():
            return
        add_attendance(
            self.get_selected_student_id(),
            self.get_selected_course_id(),
            self.date_var.get().strip(),
            self.status_var.get(),
        )
        self.refresh_attendance()
        self.clear_form()

    def update_selected_attendance(self):
        if self.attendance_id is None:
            messagebox.showerror("Update", "Please select an attendance record to update.")
            return
        if not self.validate_form():
            return
        update_attendance(
            self.attendance_id,
            self.get_selected_student_id(),
            self.get_selected_course_id(),
            self.date_var.get().strip(),
            self.status_var.get(),
        )
        self.refresh_attendance()
        self.clear_form()

    def delete_selected_attendance(self):
        if self.attendance_id is None:
            messagebox.showerror("Delete", "Please select an attendance record to delete.")
            return
        confirm = messagebox.askyesno("Confirm Delete", "Delete this attendance record?")
        if not confirm:
            return
        delete_attendance(self.attendance_id)
        self.refresh_attendance()
        self.clear_form()

    def refresh_attendance(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for record in fetch_attendance():
            self.tree.insert(
                "",
                "end",
                values=(
                    record["id"],
                    record["student_name"],
                    record["course_name"],
                    record["attendance_date"],
                    record["status"],
                ),
            )

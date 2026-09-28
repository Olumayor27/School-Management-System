import tkinter as tk
from tkinter import ttk, messagebox

from database import add_result, delete_result, fetch_courses, fetch_results, fetch_students, update_result


class ResultManager(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Manage Results")
        self.geometry("950x580")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        self.result_id = None
        self.student_var = tk.StringVar()
        self.course_var = tk.StringVar()
        self.exam_var = tk.StringVar()
        self.score_var = tk.StringVar()

        form = ttk.Frame(self, padding=10)
        form.pack(fill="x")

        ttk.Label(form, text="Student:").grid(row=0, column=0, sticky="w", padx=6, pady=5)
        self.student_combo = ttk.Combobox(form, textvariable=self.student_var, width=28, state="readonly")
        self.student_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form, text="Course:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.course_combo = ttk.Combobox(form, textvariable=self.course_var, width=28, state="readonly")
        self.course_combo.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form, text="Exam:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(form, textvariable=self.exam_var, width=30).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form, text="Score:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        ttk.Entry(form, textvariable=self.score_var, width=30).grid(row=1, column=3, padx=5, pady=5)

        button_row = ttk.Frame(self)
        button_row.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Button(button_row, text="Save", command=self.save_result).pack(side="left", padx=5)
        ttk.Button(button_row, text="Update", command=self.update_selected_result).pack(side="left", padx=5)
        ttk.Button(button_row, text="Delete", command=self.delete_selected_result).pack(side="left", padx=5)
        ttk.Button(button_row, text="Clear", command=self.clear_form).pack(side="left", padx=5)

        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        columns = ("id", "student", "course", "exam", "score", "grade")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("student", text="Student")
        self.tree.heading("course", text="Course")
        self.tree.heading("exam", text="Exam")
        self.tree.heading("score", text="Score")
        self.tree.heading("grade", text="Grade")

        for col in columns:
            self.tree.column(col, anchor="center", width=140)

        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.refresh_choices()
        self.refresh_results()

    def refresh_choices(self):
        students = fetch_students()
        courses = fetch_courses()
        student_values = [f"{student['id']} - {student['name']}" for student in students]
        course_values = [f"{course['id']} - {course['name']}" for course in courses]
        self.student_combo["values"] = student_values
        self.course_combo["values"] = course_values
        if student_values:
            self.student_var.set(student_values[0])
        if course_values:
            self.course_var.set(course_values[0])

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
        self.result_id = values[0]

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
        self.exam_var.set(values[3])
        self.score_var.set(values[4])

    def clear_form(self):
        self.result_id = None
        self.exam_var.set("")
        self.score_var.set("")
        self.refresh_choices()
        self.tree.selection_remove(self.tree.selection())

    def validate_form(self):
        if not self.exam_var.get().strip():
            messagebox.showerror("Validation", "Exam name is required.")
            return False
        try:
            score = float(self.score_var.get())
        except ValueError:
            messagebox.showerror("Validation", "Score must be numeric.")
            return False
        if not 0 <= score <= 100:
            messagebox.showerror("Validation", "Score must be between 0 and 100.")
            return False
        return True

    def save_result(self):
        if not self.validate_form():
            return
        add_result(
            self.get_selected_student_id(),
            self.get_selected_course_id(),
            self.exam_var.get().strip(),
            float(self.score_var.get()),
        )
        self.refresh_results()
        self.clear_form()

    def update_selected_result(self):
        if self.result_id is None:
            messagebox.showerror("Update", "Please select a result to update.")
            return
        if not self.validate_form():
            return
        update_result(
            self.result_id,
            self.get_selected_student_id(),
            self.get_selected_course_id(),
            self.exam_var.get().strip(),
            float(self.score_var.get()),
        )
        self.refresh_results()
        self.clear_form()

    def delete_selected_result(self):
        if self.result_id is None:
            messagebox.showerror("Delete", "Please select a result to delete.")
            return
        confirm = messagebox.askyesno("Confirm Delete", "Delete this result?")
        if not confirm:
            return
        delete_result(self.result_id)
        self.refresh_results()
        self.clear_form()

    def refresh_results(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for result in fetch_results():
            self.tree.insert(
                "",
                "end",
                values=(
                    result["id"],
                    result["student_name"],
                    result["course_name"],
                    result["exam_name"],
                    result["score"],
                    result["grade"],
                ),
            )

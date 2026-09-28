import tkinter as tk
from tkinter import ttk, messagebox

from database import add_course, delete_course, fetch_courses, fetch_teachers, update_course


class CourseManager(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Manage Courses")
        self.geometry("900x520")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        self.course_id = None
        self.name_var = tk.StringVar()
        self.code_var = tk.StringVar()
        self.credits_var = tk.StringVar()
        self.teacher_var = tk.StringVar()

        form = ttk.Frame(self, padding=10)
        form.pack(fill="x")

        ttk.Label(form, text="Course Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(form, textvariable=self.name_var, width=30).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form, text="Course Code:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        ttk.Entry(form, textvariable=self.code_var, width=30).grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form, text="Credits:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(form, textvariable=self.credits_var, width=30).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form, text="Teacher:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.teacher_combo = ttk.Combobox(form, textvariable=self.teacher_var, width=28, state="readonly")
        self.teacher_combo.grid(row=1, column=3, padx=5, pady=5)

        button_row = ttk.Frame(self)
        button_row.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Button(button_row, text="Save", command=self.save_course).pack(side="left", padx=5)
        ttk.Button(button_row, text="Update", command=self.update_selected_course).pack(side="left", padx=5)
        ttk.Button(button_row, text="Delete", command=self.delete_selected_course).pack(side="left", padx=5)
        ttk.Button(button_row, text="Clear", command=self.clear_form).pack(side="left", padx=5)

        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        columns = ("id", "name", "course_code", "credits", "teacher")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("course_code", text="Course Code")
        self.tree.heading("credits", text="Credits")
        self.tree.heading("teacher", text="Teacher")

        for col in columns:
            self.tree.column(col, anchor="center", width=150)

        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.refresh_teachers_list()
        self.refresh_courses()

    def refresh_teachers_list(self):
        teachers = fetch_teachers()
        options = ["No Teacher"]
        if teachers:
            options = ["No Teacher"] + [f"{teacher['id']} - {teacher['name']}" for teacher in teachers]
        self.teacher_combo["values"] = options
        if options:
            self.teacher_combo.set(options[0])

    def get_selected_teacher_id(self):
        value = self.teacher_var.get()
        if not value or value == "No Teacher":
            return None

        if " - " in value:
            try:
                return int(str(value).split(" - ")[0])
            except ValueError:
                pass

        for teacher in fetch_teachers():
            if teacher["name"] == value:
                return teacher["id"]
        return None

    def on_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected[0])
        values = item["values"]
        self.course_id = values[0]
        self.name_var.set(values[1])
        self.code_var.set(values[2])
        self.credits_var.set(values[3])
        teacher_display = values[4] if values[4] else "No Teacher"

        if teacher_display != "No Teacher":
            teacher_id = None
            for teacher in fetch_teachers():
                if teacher["name"] == teacher_display:
                    teacher_id = teacher["id"]
                    break
            if teacher_id is not None:
                teacher_display = f"{teacher_id} - {teacher_display}"

        self.teacher_var.set(teacher_display)

    def clear_form(self):
        self.course_id = None
        self.name_var.set("")
        self.code_var.set("")
        self.credits_var.set("")
        self.teacher_var.set("No Teacher")
        self.tree.selection_remove(self.tree.selection())

    def validate_form(self):
        if not self.name_var.get().strip():
            messagebox.showerror("Validation", "Course name is required.")
            return False
        if not self.code_var.get().strip():
            messagebox.showerror("Validation", "Course code is required.")
            return False
        try:
            int(self.credits_var.get())
        except ValueError:
            messagebox.showerror("Validation", "Credits must be a number.")
            return False
        return True

    def save_course(self):
        if not self.validate_form():
            return
        add_course(
            self.name_var.get().strip(),
            self.code_var.get().strip(),
            int(self.credits_var.get()),
            self.get_selected_teacher_id(),
        )
        self.refresh_courses()
        self.clear_form()

    def update_selected_course(self):
        if self.course_id is None:
            messagebox.showerror("Update", "Please select a course to update.")
            return
        if not self.validate_form():
            return
        update_course(
            self.course_id,
            self.name_var.get().strip(),
            self.code_var.get().strip(),
            int(self.credits_var.get()),
            self.get_selected_teacher_id(),
        )
        self.refresh_courses()
        self.clear_form()

    def delete_selected_course(self):
        if self.course_id is None:
            messagebox.showerror("Delete", "Please select a course to delete.")
            return
        confirm = messagebox.askyesno("Confirm Delete", "Delete this course?")
        if not confirm:
            return
        delete_course(self.course_id)
        self.refresh_courses()
        self.clear_form()

    def refresh_courses(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for course in fetch_courses():
            teacher_name = course.get("teacher_name") or "No Teacher"
            self.tree.insert(
                "",
                "end",
                values=(
                    course["id"],
                    course["name"],
                    course["course_code"],
                    course["credits"],
                    teacher_name,
                ),
            )

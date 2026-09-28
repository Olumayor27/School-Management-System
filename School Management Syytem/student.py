import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from database import add_student, delete_student, fetch_students, update_student


class StudentManager(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Manage Students")
        self.geometry("820x500")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        self.student_id = None
        self.name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.department_var = tk.StringVar()

        form = ttk.Frame(self, padding=10)
        form.pack(fill="x")

        ttk.Label(form, text="Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(form, textvariable=self.name_var, width=30).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form, text="Email:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        ttk.Entry(form, textvariable=self.email_var, width=30).grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form, text="Phone:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(form, textvariable=self.phone_var, width=30).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form, text="Department:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        ttk.Entry(form, textvariable=self.department_var, width=30).grid(row=1, column=3, padx=5, pady=5)

        button_row = ttk.Frame(self)
        button_row.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Button(button_row, text="Save", command=self.save_student).pack(side="left", padx=5)
        ttk.Button(button_row, text="Update", command=self.update_selected_student).pack(side="left", padx=5)
        ttk.Button(button_row, text="Delete", command=self.delete_selected_student).pack(side="left", padx=5)
        ttk.Button(button_row, text="Clear", command=self.clear_form).pack(side="left", padx=5)

        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        columns = ("id", "name", "email", "phone", "department")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("email", text="Email")
        self.tree.heading("phone", text="Phone")
        self.tree.heading("department", text="Department")

        for col in columns:
            self.tree.column(col, anchor="center", width=120)

        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.refresh_students()

    def on_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected[0])
        values = item["values"]
        self.student_id = values[0]
        self.name_var.set(values[1])
        self.email_var.set(values[2])
        self.phone_var.set(values[3])
        self.department_var.set(values[4])

    def clear_form(self):
        self.student_id = None
        self.name_var.set("")
        self.email_var.set("")
        self.phone_var.set("")
        self.department_var.set("")
        self.tree.selection_remove(self.tree.selection())

    def validate_form(self):
        if not self.name_var.get().strip():
            messagebox.showerror("Validation", "Student name is required.")
            return False
        return True

    def save_student(self):
        if not self.validate_form():
            return
        add_student(
            self.name_var.get().strip(),
            self.email_var.get().strip(),
            self.phone_var.get().strip(),
            self.department_var.get().strip(),
        )
        self.refresh_students()
        self.clear_form()

    def update_selected_student(self):
        if self.student_id is None:
            messagebox.showerror("Update", "Please select a student to update.")
            return
        if not self.validate_form():
            return
        update_student(
            self.student_id,
            self.name_var.get().strip(),
            self.email_var.get().strip(),
            self.phone_var.get().strip(),
            self.department_var.get().strip(),
        )
        self.refresh_students()
        self.clear_form()

    def delete_selected_student(self):
        if self.student_id is None:
            messagebox.showerror("Delete", "Please select a student to delete.")
            return
        confirm = messagebox.askyesno("Confirm Delete", "Delete this student?")
        if not confirm:
            return
        delete_student(self.student_id)
        self.refresh_students()
        self.clear_form()

    def refresh_students(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for student in fetch_students():
            self.tree.insert(
                "",
                "end",
                values=(
                    student["id"],
                    student["name"],
                    student["email"],
                    student["phone"],
                    student["department"],
                ),
            )

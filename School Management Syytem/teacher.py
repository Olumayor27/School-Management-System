import tkinter as tk
from tkinter import ttk, messagebox

from database import add_teacher, delete_teacher, fetch_teachers, update_teacher


class TeacherManager(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Manage Teachers")
        self.geometry("820x500")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        self.teacher_id = None
        self.name_var = tk.StringVar()
        self.subject_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.phone_var = tk.StringVar()

        form = ttk.Frame(self, padding=10)
        form.pack(fill="x")

        ttk.Label(form, text="Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(form, textvariable=self.name_var, width=30).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form, text="Subject:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        ttk.Entry(form, textvariable=self.subject_var, width=30).grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form, text="Email:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(form, textvariable=self.email_var, width=30).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form, text="Phone:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        ttk.Entry(form, textvariable=self.phone_var, width=30).grid(row=1, column=3, padx=5, pady=5)

        button_row = ttk.Frame(self)
        button_row.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Button(button_row, text="Save", command=self.save_teacher).pack(side="left", padx=5)
        ttk.Button(button_row, text="Update", command=self.update_selected_teacher).pack(side="left", padx=5)
        ttk.Button(button_row, text="Delete", command=self.delete_selected_teacher).pack(side="left", padx=5)
        ttk.Button(button_row, text="Clear", command=self.clear_form).pack(side="left", padx=5)

        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        columns = ("id", "name", "subject", "email", "phone")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("subject", text="Subject")
        self.tree.heading("email", text="Email")
        self.tree.heading("phone", text="Phone")

        for col in columns:
            self.tree.column(col, anchor="center", width=130)

        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.refresh_teachers()

    def on_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected[0])
        values = item["values"]
        self.teacher_id = values[0]
        self.name_var.set(values[1])
        self.subject_var.set(values[2])
        self.email_var.set(values[3])
        self.phone_var.set(values[4])

    def clear_form(self):
        self.teacher_id = None
        self.name_var.set("")
        self.subject_var.set("")
        self.email_var.set("")
        self.phone_var.set("")
        self.tree.selection_remove(self.tree.selection())

    def validate_form(self):
        if not self.name_var.get().strip():
            messagebox.showerror("Validation", "Teacher name is required.")
            return False
        return True

    def save_teacher(self):
        if not self.validate_form():
            return
        add_teacher(
            self.name_var.get().strip(),
            self.subject_var.get().strip(),
            self.email_var.get().strip(),
            self.phone_var.get().strip(),
        )
        self.refresh_teachers()
        self.clear_form()

    def update_selected_teacher(self):
        if self.teacher_id is None:
            messagebox.showerror("Update", "Please select a teacher to update.")
            return
        if not self.validate_form():
            return
        update_teacher(
            self.teacher_id,
            self.name_var.get().strip(),
            self.subject_var.get().strip(),
            self.email_var.get().strip(),
            self.phone_var.get().strip(),
        )
        self.refresh_teachers()
        self.clear_form()

    def delete_selected_teacher(self):
        if self.teacher_id is None:
            messagebox.showerror("Delete", "Please select a teacher to delete.")
            return
        confirm = messagebox.askyesno("Confirm Delete", "Delete this teacher?")
        if not confirm:
            return
        delete_teacher(self.teacher_id)
        self.refresh_teachers()
        self.clear_form()

    def refresh_teachers(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for teacher in fetch_teachers():
            self.tree.insert(
                "",
                "end",
                values=(
                    teacher["id"],
                    teacher["name"],
                    teacher["subject"],
                    teacher["email"],
                    teacher["phone"],
                ),
            )

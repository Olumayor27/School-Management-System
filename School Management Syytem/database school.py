import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("school_management.db")


def ensure_database_file():
    if DB_PATH.exists() and DB_PATH.stat().st_size == 0:
        DB_PATH.unlink(missing_ok=True)

    if DB_PATH.exists():
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("SELECT 1")
            conn.close()
            return
        except sqlite3.DatabaseError:
            DB_PATH.unlink(missing_ok=True)


def get_connection():
    ensure_database_file()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    ensure_database_file()
    conn = get_connection()

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'admin'
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            department TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            subject TEXT,
            email TEXT,
            phone TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            course_code TEXT NOT NULL UNIQUE,
            credits INTEGER NOT NULL,
            teacher_id INTEGER,
            FOREIGN KEY (teacher_id) REFERENCES teachers(id)
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            attendance_date TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('Present', 'Absent')),
            FOREIGN KEY (student_id) REFERENCES students(id),
            FOREIGN KEY (course_id) REFERENCES courses(id)
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            exam_name TEXT NOT NULL,
            score REAL NOT NULL,
            grade TEXT,
            FOREIGN KEY (student_id) REFERENCES students(id),
            FOREIGN KEY (course_id) REFERENCES courses(id)
        )
        """
    )

    conn.execute(
        "INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)",
        ("admin", "admin123", "admin"),
    )

    conn.commit()
    conn.close()


def authenticate_user(username, password):
    conn = get_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, password),
    ).fetchone()
    conn.close()
    if user is None:
        return None
    return dict(user)


# Student CRUD

def fetch_students():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM students ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def add_student(name, email, phone, department):
    conn = get_connection()
    conn.execute(
        "INSERT INTO students (name, email, phone, department) VALUES (?, ?, ?, ?)",
        (name, email, phone, department),
    )
    conn.commit()
    conn.close()


def update_student(student_id, name, email, phone, department):
    conn = get_connection()
    conn.execute(
        "UPDATE students SET name = ?, email = ?, phone = ?, department = ? WHERE id = ?",
        (name, email, phone, department, student_id),
    )
    conn.commit()
    conn.close()


def delete_student(student_id):
    conn = get_connection()
    conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.execute("DELETE FROM attendance WHERE student_id = ?", (student_id,))
    conn.execute("DELETE FROM results WHERE student_id = ?", (student_id,))
    conn.commit()
    conn.close()


# Teacher CRUD

def fetch_teachers():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM teachers ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def add_teacher(name, subject, email, phone):
    conn = get_connection()
    conn.execute(
        "INSERT INTO teachers (name, subject, email, phone) VALUES (?, ?, ?, ?)",
        (name, subject, email, phone),
    )
    conn.commit()
    conn.close()


def update_teacher(teacher_id, name, subject, email, phone):
    conn = get_connection()
    conn.execute(
        "UPDATE teachers SET name = ?, subject = ?, email = ?, phone = ? WHERE id = ?",
        (name, subject, email, phone, teacher_id),
    )
    conn.commit()
    conn.close()


def delete_teacher(teacher_id):
    conn = get_connection()
    conn.execute("UPDATE courses SET teacher_id = NULL WHERE teacher_id = ?", (teacher_id,))
    conn.execute("DELETE FROM teachers WHERE id = ?", (teacher_id,))
    conn.commit()
    conn.close()


# Course CRUD

def fetch_courses():
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT c.*, t.name AS teacher_name
        FROM courses c
        LEFT JOIN teachers t ON t.id = c.teacher_id
        ORDER BY c.id DESC
        """
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def add_course(name, course_code, credits, teacher_id):
    conn = get_connection()
    conn.execute(
        "INSERT INTO courses (name, course_code, credits, teacher_id) VALUES (?, ?, ?, ?)",
        (name, course_code, credits, teacher_id if teacher_id else None),
    )
    conn.commit()
    conn.close()


def update_course(course_id, name, course_code, credits, teacher_id):
    conn = get_connection()
    conn.execute(
        "UPDATE courses SET name = ?, course_code = ?, credits = ?, teacher_id = ? WHERE id = ?",
        (name, course_code, credits, teacher_id if teacher_id else None, course_id),
    )
    conn.commit()
    conn.close()


def delete_course(course_id):
    conn = get_connection()
    conn.execute("DELETE FROM courses WHERE id = ?", (course_id,))
    conn.execute("DELETE FROM attendance WHERE course_id = ?", (course_id,))
    conn.execute("DELETE FROM results WHERE course_id = ?", (course_id,))
    conn.commit()
    conn.close()


# Result CRUD

def fetch_results():
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT r.*, s.name AS student_name, c.name AS course_name
        FROM results r
        JOIN students s ON s.id = r.student_id
        JOIN courses c ON c.id = r.course_id
        ORDER BY r.id DESC
        """
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def add_result(student_id, course_id, exam_name, score):
    grade = "A"
    if score >= 90:
        grade = "A"
    elif score >= 80:
        grade = "B"
    elif score >= 70:
        grade = "C"
    elif score >= 60:
        grade = "D"
    else:
        grade = "F"

    conn = get_connection()
    conn.execute(
        "INSERT INTO results (student_id, course_id, exam_name, score, grade) VALUES (?, ?, ?, ?, ?)",
        (student_id, course_id, exam_name, score, grade),
    )
    conn.commit()
    conn.close()


def update_result(result_id, student_id, course_id, exam_name, score):
    grade = "A"
    if score >= 90:
        grade = "A"
    elif score >= 80:
        grade = "B"
    elif score >= 70:
        grade = "C"
    elif score >= 60:
        grade = "D"
    else:
        grade = "F"

    conn = get_connection()
    conn.execute(
        "UPDATE results SET student_id = ?, course_id = ?, exam_name = ?, score = ?, grade = ? WHERE id = ?",
        (student_id, course_id, exam_name, score, grade, result_id),
    )
    conn.commit()
    conn.close()


def delete_result(result_id):
    conn = get_connection()
    conn.execute("DELETE FROM results WHERE id = ?", (result_id,))
    conn.commit()
    conn.close()


# Attendance CRUD

def fetch_attendance():
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT a.*, s.name AS student_name, c.name AS course_name
        FROM attendance a
        JOIN students s ON s.id = a.student_id
        JOIN courses c ON c.id = a.course_id
        ORDER BY a.attendance_date DESC, a.id DESC
        """
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def add_attendance(student_id, course_id, date, status):
    conn = get_connection()
    conn.execute(
        "INSERT INTO attendance (student_id, course_id, attendance_date, status) VALUES (?, ?, ?, ?)",
        (student_id, course_id, date, status),
    )
    conn.commit()
    conn.close()


def update_attendance(attendance_id, student_id, course_id, date, status):
    conn = get_connection()
    conn.execute(
        "UPDATE attendance SET student_id = ?, course_id = ?, attendance_date = ?, status = ? WHERE id = ?",
        (student_id, course_id, date, status, attendance_id),
    )
    conn.commit()
    conn.close()


def delete_attendance(attendance_id):
    conn = get_connection()
    conn.execute("DELETE FROM attendance WHERE id = ?", (attendance_id,))
    conn.commit()
    conn.close()


def get_dashboard_stats():
    conn = get_connection()
    student_count = conn.execute("SELECT COUNT(*) AS total FROM students").fetchone()["total"]
    teacher_count = conn.execute("SELECT COUNT(*) AS total FROM teachers").fetchone()["total"]
    course_count = conn.execute("SELECT COUNT(*) AS total FROM courses").fetchone()["total"]
    result_count = conn.execute("SELECT COUNT(*) AS total FROM results").fetchone()["total"]
    attendance_total = conn.execute("SELECT COUNT(*) AS total FROM attendance").fetchone()["total"]
    present_total = conn.execute(
        "SELECT COUNT(*) AS total FROM attendance WHERE status = 'Present'"
    ).fetchone()["total"]
    attendance_rate = round((present_total / attendance_total) * 100, 1) if attendance_total else 0
    conn.close()
    return {
        "students": student_count,
        "teachers": teacher_count,
        "courses": course_count,
        "results": result_count,
        "attendance_rate": attendance_rate,
    }


init_db()

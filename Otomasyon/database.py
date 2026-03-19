import sqlite3
import os

DB_PATH = "database.db"

def get_conn():
    return sqlite3.connect(DB_PATH)

def create_tables():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin','ogretmen','ogrenci'))
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_no TEXT UNIQUE NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        credit INTEGER DEFAULT 3
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS enrollments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        course_id INTEGER NOT NULL,
        UNIQUE(student_id, course_id),
        FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
        FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS grades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        course_id INTEGER NOT NULL,
        grade REAL,
        UNIQUE(student_id, course_id),
        FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
        FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()

def seed_demo_data():
    """Eğitim amaçlı örnek kullanıcı/öğrenci/ders ekler."""
    conn = get_conn()
    cur = conn.cursor()

    # users
    demo_users = [
        ("admin", "1234", "admin"),
        ("ogretmen1", "1234", "ogretmen"),
        ("ogrenci1", "1234", "ogrenci"),
    ]
    for u, p, r in demo_users:
        try:
            cur.execute("INSERT INTO users (username,password,role) VALUES (?,?,?)", (u,p,r))
        except sqlite3.IntegrityError:
            pass

    # students
    demo_students = [
        ("2023001","Ali","Yılmaz","ali@example.com"),
        ("2023002","Ayşe","Demir","ayse@example.com"),
    ]
    for no, fn, ln, em in demo_students:
        try:
            cur.execute("INSERT INTO students (student_no,first_name,last_name,email) VALUES (?,?,?,?)",
                        (no,fn,ln,em))
        except sqlite3.IntegrityError:
            pass

    # courses
    demo_courses = [
        ("BTE101","Programlamaya Giriş",4),
        ("BTE202","Veritabanı",3),
    ]
    for code, name, credit in demo_courses:
        try:
            cur.execute("INSERT INTO courses (code,name,credit) VALUES (?,?,?)",
                        (code,name,credit))
        except sqlite3.IntegrityError:
            pass

    conn.commit()
    conn.close()

# ---- AUTH ----
def authenticate(username, password):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, role FROM users WHERE username=? AND password=?", (username, password))
    row = cur.fetchone()
    conn.close()
    if row:
        return {"user_id": row[0], "role": row[1]}
    return None

# ---- CRUD Helpers ----
def add_user(username, password, role):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (username,password,role) VALUES (?,?,?)", (username,password,role))
    conn.commit()
    conn.close()

def add_student(student_no, first_name, last_name, email):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO students (student_no,first_name,last_name,email)
        VALUES (?,?,?,?)
    """, (student_no, first_name, last_name, email))
    conn.commit()
    conn.close()

def delete_student(student_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM students WHERE id=?", (student_id,))
    conn.commit()
    conn.close()

def list_students():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, student_no, first_name, last_name, email FROM students ORDER BY student_no;")
    rows = cur.fetchall()
    conn.close()
    return rows

def add_course(code, name, credit):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO courses (code,name,credit) VALUES (?,?,?)", (code,name,credit))
    conn.commit()
    conn.close()

def delete_course(course_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM courses WHERE id=?", (course_id,))
    conn.commit()
    conn.close()

def list_courses():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, code, name, credit FROM courses ORDER BY code;")
    rows = cur.fetchall()
    conn.close()
    return rows

def enroll_student(student_id, course_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO enrollments (student_id, course_id) VALUES (?,?)", (student_id, course_id))
    conn.commit()
    conn.close()

def list_enrollments():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT e.id, s.student_no || ' - ' || s.first_name || ' ' || s.last_name AS student,
               c.code || ' - ' || c.name AS course
        FROM enrollments e
        JOIN students s ON s.id=e.student_id
        JOIN courses c ON c.id=e.course_id
        ORDER BY s.student_no, c.code;
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

def add_grade(student_id, course_id, grade):
    conn = get_conn()
    cur = conn.cursor()
    # upsert benzeri: varsa güncelle, yoksa ekle
    cur.execute("SELECT id FROM grades WHERE student_id=? AND course_id=?", (student_id, course_id))
    row = cur.fetchone()
    if row:
        cur.execute("UPDATE grades SET grade=? WHERE id=?", (grade, row[0]))
    else:
        cur.execute("INSERT INTO grades (student_id, course_id, grade) VALUES (?,?,?)", (student_id, course_id, grade))
    conn.commit()
    conn.close()

def list_grades(student_id=None):
    conn = get_conn()
    cur = conn.cursor()
    if student_id:
        cur.execute("""
            SELECT g.id, s.student_no, s.first_name || ' ' || s.last_name AS adsoyad,
                   c.code, c.name, g.grade
            FROM grades g
            JOIN students s ON s.id=g.student_id
            JOIN courses c ON c.id=g.course_id
            WHERE s.id=?
            ORDER BY c.code;
        """, (student_id,))
    else:
        cur.execute("""
            SELECT g.id, s.student_no, s.first_name || ' ' || s.last_name AS adsoyad,
                   c.code, c.name, g.grade
            FROM grades g
            JOIN students s ON s.id=g.student_id
            JOIN courses c ON c.id=g.course_id
            ORDER BY s.student_no, c.code;
        """)
    rows = cur.fetchall()
    conn.close()
    return rows

def delete_grade(grade_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM grades WHERE id=?", (grade_id,))
    conn.commit()
    conn.close()

# Başlangıçta tablo oluştur ve örnek veri ekle
if __name__ == "__main__":
    create_tables()
    seed_demo_data()
    print("Veritabanı hazırlandı. 'database.db' oluşturuldu/yenilendi.")

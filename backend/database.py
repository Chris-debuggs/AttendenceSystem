import sqlite3
import pickle
import base64
import hashlib
from datetime import datetime
import os

DB_NAME = "attendance.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

def init_database():
    """Initialize database with all required tables."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Employees Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                mobile_no TEXT,
                address TEXT,
                department TEXT,
                position TEXT,
                salary REAL,
                working_hours_per_day REAL,
                employee_type TEXT DEFAULT 'full_time',
                gender TEXT,
                face_embedding BLOB,
                photo_data BLOB,
                joining_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Attendance Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT REFERENCES employees(id) ON DELETE CASCADE,
                date TEXT NOT NULL,
                check_in TEXT,
                check_out TEXT,
                status TEXT,
                UNIQUE(employee_id, date)
            );
        """)

        # Holidays Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS holidays (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                description TEXT,
                type TEXT NOT NULL, -- NATIONAL, RELIGIOUS, COMPANY, OTHER
                is_recurring INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Leaves Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS leaves (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT REFERENCES employees(id) ON DELETE CASCADE,
                leave_date TEXT NOT NULL,
                leave_type TEXT NOT NULL, -- Casual, Sick, On Duty
                reason TEXT,
                status TEXT DEFAULT 'approved', -- approved, pending, rejected
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(employee_id, leave_date)
            );
        """)

        # Admin Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS admin (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Office Settings Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS office_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time TEXT,
                end_time TEXT,
                on_time_limit TEXT
            );
        """)

        # Initialize Office Settings if empty
        cur.execute("SELECT id FROM office_settings LIMIT 1;")
        if cur.fetchone() is None:
            cur.execute(
                "INSERT INTO office_settings (start_time, end_time, on_time_limit) VALUES (?, ?, ?)",
                ('09:00:00', '18:00:00', '09:30:00')
            )

        # Add default admin if not exists
        cur.execute("SELECT id FROM admin LIMIT 1;")
        if cur.fetchone() is None:
            default_password_hash = hashlib.sha256("admin".encode()).hexdigest()
            cur.execute(
                "INSERT INTO admin (username, password_hash) VALUES (?, ?)",
                ('admin', default_password_hash)
            )
        
        conn.commit()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error during database initialization: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def save_face_data(employee_id: str, face_embedding: bytes, photo_data: bytes):
    """Save face embedding and photo data to database"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            UPDATE employees 
            SET face_embedding = ?, photo_data = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (face_embedding, photo_data, employee_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving face data: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def get_face_data(employee_id: str):
    """Get face embedding and photo data from database"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT face_embedding, photo_data FROM employees WHERE id = ?
        """, (employee_id,))
        result = cur.fetchone()
        return result if result else (None, None)
    except Exception as e:
        print(f"Error getting face data: {e}")
        return None, None
    finally:
        cur.close()
        conn.close()

def get_all_face_embeddings():
    """Get all face embeddings for recognition"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT id, name, face_embedding FROM employees 
            WHERE face_embedding IS NOT NULL
        """)
        results = cur.fetchall()
        embeddings_dict = {}
        for row in results:
            emp_id = row['id']
            name = row['name']
            embedding_data = row['face_embedding']
            if embedding_data:
                embedding = pickle.loads(embedding_data)
                embeddings_dict[name] = embedding
        return embeddings_dict
    except Exception as e:
        print(f"Error getting face embeddings: {e}")
        return {}
    finally:
        cur.close()
        conn.close()

def delete_face_data(employee_id: str):
    """Delete face data when employee is deleted"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            UPDATE employees 
            SET face_embedding = NULL, photo_data = NULL, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (employee_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting face data: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def punch_out_employee(employee_name: str, date: str):
    """Update the check_out time for an employee's attendance record."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Use Python datetime to get local time instead of SQLite's UTC time
        from datetime import datetime
        current_time = datetime.now().strftime('%H:%M:%S')
        
        # SQLite doesn't support RETURNING in UPDATE in older versions, but we can check rowcount
        cur.execute("""
            UPDATE attendance 
            SET check_out = ?
            WHERE employee_id = (SELECT id FROM employees WHERE name = ?)
            AND date = ? AND check_out IS NULL
        """, (current_time, employee_name, date))
        
        if cur.rowcount > 0:
            conn.commit()
            return True
        else:
            return False
    except Exception as e:
        print(f"Error punching out: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def clear_database():
    """Drops all tables for a clean setup. Use with caution."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # SQLite doesn't support CASCADE in DROP TABLE like Postgres
        cur.execute("DROP TABLE IF EXISTS leaves;")
        cur.execute("DROP TABLE IF EXISTS holidays;")
        cur.execute("DROP TABLE IF EXISTS attendance;")
        cur.execute("DROP TABLE IF EXISTS employees;")
        cur.execute("DROP TABLE IF EXISTS admin;")
        cur.execute("DROP TABLE IF EXISTS office_settings;")
        conn.commit()
        print("Database cleared successfully.")
    except Exception as e:
        print(f"Error clearing database: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def get_office_settings():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT start_time, end_time, on_time_limit FROM office_settings ORDER BY id LIMIT 1")
        result = cur.fetchone()
        if result:
            return {
                'start_time': str(result[0]),
                'end_time': str(result[1]),
                'on_time_limit': str(result[2])
            }
        else:
            return None
    finally:
        cur.close()
        conn.close()

def update_office_settings(start_time, end_time, on_time_limit):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE office_settings SET start_time=?, end_time=?, on_time_limit=? WHERE id = (SELECT id FROM office_settings ORDER BY id LIMIT 1)",
                    (start_time, end_time, on_time_limit))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating office settings: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def get_employee_email(name):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT email FROM employees WHERE name = ?", (name,))
        result = cur.fetchone()
        if result:
            return result[0]
        return None
    finally:
        cur.close()
        conn.close()

# Migration functions are less relevant for a fresh SQLite DB, but keeping them for compatibility if called
def migrate_add_gender_column():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Check if column exists
        cur.execute("PRAGMA table_info(employees)")
        columns = [row['name'] for row in cur.fetchall()]
        if 'gender' not in columns:
            cur.execute("ALTER TABLE employees ADD COLUMN gender TEXT")
            conn.commit()
            print("[MIGRATION] 'gender' column ensured in employees table.")
    except Exception as e:
        print(f"[MIGRATION ERROR] {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def migrate_add_mobile_no_column():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("PRAGMA table_info(employees)")
        columns = [row['name'] for row in cur.fetchall()]
        if 'mobile_no' not in columns:
            cur.execute("ALTER TABLE employees ADD COLUMN mobile_no TEXT")
            conn.commit()
            print("[MIGRATION] 'mobile_no' column ensured in employees table.")
    except Exception as e:
        print(f"[MIGRATION ERROR] {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def migrate_add_address_column():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("PRAGMA table_info(employees)")
        columns = [row['name'] for row in cur.fetchall()]
        if 'address' not in columns:
            cur.execute("ALTER TABLE employees ADD COLUMN address TEXT")
            conn.commit()
            print("[MIGRATION] 'address' column ensured in employees table.")
    except Exception as e:
        print(f"[MIGRATION ERROR] {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def migrate_add_joining_date_column():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("PRAGMA table_info(employees)")
        columns = [row['name'] for row in cur.fetchall()]
        if 'joining_date' not in columns:
            cur.execute("ALTER TABLE employees ADD COLUMN joining_date TEXT")
            conn.commit()
            print("[MIGRATION] 'joining_date' column ensured in employees table.")
    except Exception as e:
        print(f"[MIGRATION ERROR] {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

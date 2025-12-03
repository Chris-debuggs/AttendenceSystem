#!/usr/bin/env python3
"""
Script to view all data in the database
"""

from database import get_db_connection

def view_database_contents():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        print("=" * 50)
        print("DATABASE CONTENTS")
        print("=" * 50)
        
        # View employees table
        print("\n1. EMPLOYEES TABLE:")
        print("-" * 30)
        cur.execute("""
            SELECT id, name, email, department, position, salary, working_hours_per_day, employee_type,
                   created_at, updated_at, 
                   CASE WHEN face_embedding IS NOT NULL THEN 'YES' ELSE 'NO' END as has_face_data,
                   CASE WHEN photo_data IS NOT NULL THEN 'YES' ELSE 'NO' END as has_photo
            FROM employees 
            ORDER BY created_at
        """)
        employees = cur.fetchall()
        
        if not employees:
            print("No employees found in database")
        else:
            for emp in employees:
                print(f"ID: {emp[0]}")
                print(f"Name: {emp[1]}")
                print(f"Email: {emp[2]}")
                print(f"Department: {emp[3]}")
                print(f"Position: {emp[4]}")
                print(f"Salary: {emp[5]}")
                print(f"Working Hours: {emp[6]}")
                print(f"Employee Type: {emp[7]}")
                print(f"Created: {emp[8]}")
                print(f"Updated: {emp[9]}")
                print(f"Has Face Data: {emp[10]}")
                print(f"Has Photo: {emp[11]}")
                print("-" * 20)
        
        # View attendance table
        print("\n2. ATTENDANCE TABLE:")
        print("-" * 30)
        cur.execute("""
            SELECT a.id, a.employee_id, e.name, a.check_in, a.check_out, a.status, a.date
            FROM attendance a
            LEFT JOIN employees e ON a.employee_id = e.id
            ORDER BY a.date DESC, a.check_in DESC
        """)
        attendance = cur.fetchall()
        
        if not attendance:
            print("No attendance records found in database")
        else:
            for att in attendance:
                print(f"Record ID: {att[0]}")
                print(f"Employee ID: {att[1]}")
                print(f"Employee Name: {att[2]}")
                print(f"Check In: {att[3]}")
                print(f"Check Out: {att[4]}")
                print(f"Status: {att[5]}")
                print(f"Date: {att[6]}")
                print("-" * 20)
        
        # View admin table
        print("\n3. ADMIN TABLE:")
        print("-" * 30)
        cur.execute("SELECT id, username, password_hash FROM admin")
        admins = cur.fetchall()
        
        if not admins:
            print("No admin users found in database")
        else:
            print(f"Total Admin Users: {len(admins)}", flush=True)
            print(f"DEBUG: Admins list: {admins}", flush=True)
            for admin in admins:
                print(f"ID: {admin[0]}", flush=True)
                print(f"Username: {admin[1]}", flush=True)
                print(f"Password Hash: {admin[2][:20]}...", flush=True)  # Show only first 20 chars
                print("-" * 20, flush=True)
        
        # Database statistics
        print("\n4. DATABASE STATISTICS:")
        print("-" * 30)
        cur.execute("SELECT COUNT(*) FROM employees")
        result = cur.fetchone()
        emp_count = result[0] if result else 0
        print(f"Total Employees: {emp_count}")
        
        cur.execute("SELECT COUNT(*) FROM attendance")
        result = cur.fetchone()
        att_count = result[0] if result else 0
        print(f"Total Attendance Records: {att_count}")
        
        cur.execute("SELECT COUNT(*) FROM employees WHERE face_embedding IS NOT NULL")
        result = cur.fetchone()
        face_count = result[0] if result else 0
        print(f"Employees with Face Data: {face_count}")
        
        cur.execute("SELECT COUNT(*) FROM admin")
        result = cur.fetchone()
        admin_count = result[0] if result else 0
        print(f"Admin Users: {admin_count}")
        
    except Exception as e:
        print(f"Error viewing database: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    view_database_contents() 
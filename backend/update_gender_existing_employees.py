import sys
from database import get_db_connection

def main():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, name, gender FROM employees;")
        employees = cur.fetchall()
        for emp_id, name, gender in employees:
            if not gender or gender.strip() == '':
                print(f"Employee: {name} (ID: {emp_id}) has no gender set.")
                while True:
                    g = input("Enter gender for this employee (male/female/other): ").strip().lower()
                    if g in ['male', 'female', 'other']:
                        break
                    print("Invalid input. Please enter 'male', 'female', or 'other'.")
                cur.execute("UPDATE employees SET gender = %s WHERE id = %s", (g, emp_id))
                conn.commit()
                print(f"Updated {name} (ID: {emp_id}) to gender: {g}")
        print("All employees updated.")
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main() 
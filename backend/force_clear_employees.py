from database import get_db_connection

def force_clear_employees():
    """Forcefully delete all records from the employees table."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        print("Attempting to delete all employees...")
        cur.execute("DELETE FROM employees;")
        count = cur.rowcount
        conn.commit()
        print(f"✅ Successfully deleted {count} employee records.")
    except Exception as e:
        print(f"❌ Error clearing employees table: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    print("WARNING: This script will permanently delete all employees from the database.")
    response = input("Are you sure you want to continue? (yes/no): ")
    if response.lower() == 'yes':
        force_clear_employees()
    else:
        print("Operation cancelled.") 
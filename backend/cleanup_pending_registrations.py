from database import get_db_connection

def find_pending_employees(minutes_old=10):
    """
    Finds employee records with pending face registration that are older than
    a specified time threshold to avoid race conditions with live registrations.
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        time_threshold = datetime.now() - timedelta(minutes=minutes_old)
        
        query = """
            SELECT id, name, created_at FROM employees
            WHERE face_embedding IS NULL AND photo_data IS NULL AND created_at < ?;
        """
        cur.execute(query, (time_threshold,))
        pending_employees = cur.fetchall()
        return pending_employees
    except Exception as e:
        print(f"❌ Error finding pending employees: {e}")
        return []
    finally:
        if conn:
            cur.close()
            conn.close()

def delete_employees_by_ids(employee_ids):
    """
    Deletes a list of employees from the database based on their IDs.
    """
    if not employee_ids:
        print("No employee IDs provided to delete.")
        return 0
        
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # SQLite handles tuple IN clause differently or same, but let's use standard placeholders
        placeholders = ', '.join(['?'] * len(employee_ids))
        query = f"DELETE FROM employees WHERE id IN ({placeholders});"
        cur.execute(query, tuple(employee_ids))
        
        deleted_count = cur.rowcount
        conn.commit()
        
        return deleted_count
    except Exception as e:
        print(f"❌ Error deleting employees: {e}")
        if conn:
            conn.rollback()
        return 0
    finally:
        if conn:
            cur.close()
            conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Cleanup script for pending employee registrations.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force delete records without interactive confirmation."
    )
    args = parser.parse_args()

    print("--- Cleanup Script for Pending Employee Registrations ---")
    print("This script will find and delete employee records that were created")
    print("but have no associated face data (i.e., incomplete registrations).\n")
    
    age_in_minutes = 10 
    print(f"🔍 Searching for pending registrations older than {age_in_minutes} minutes...")

    pending_list = find_pending_employees(minutes_old=age_in_minutes)
    
    if not pending_list:
        print("\n✅ No pending employee registrations found. Your database is clean!")
    else:
        print(f"\nFound {len(pending_list)} pending registration(s) to be deleted:")
        for emp_id, name, created_at in pending_list:
            print(f"  - ID: {emp_id}, Name: {name}, Created: {created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            
        print("\n⚠️  This action is IRREVERSIBLE. ⚠️")
        
        response = 'no'
        if args.force:
            print("\n--force flag detected. Proceeding with automatic deletion.")
            response = 'yes'
        else:
            try:
                response = input("Are you sure you want to permanently delete these records? (yes/no): ").lower()
            except EOFError:
                print("\nNon-interactive mode detected. Use --force to run without a TTY. Aborting.")
                response = "no"

        if response == 'yes':
            ids_to_delete = [emp[0] for emp in pending_list]
            deleted_count = delete_employees_by_ids(ids_to_delete)
            print(f"\n✅ Successfully deleted {deleted_count} employee record(s).")
        else:
            print("\nOperation cancelled. No records were deleted.") 
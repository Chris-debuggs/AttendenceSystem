from database import get_db_connection

def view_holidays_table():
    conn = get_db_connection()
    cur = conn.cursor()
    
    print("=" * 80)
    print("HOLIDAYS TABLE STRUCTURE")
    print("=" * 80)
    
    # Get table structure
    cur.execute("PRAGMA table_info(holidays);")
    
    columns = cur.fetchall()
    print(f"{'Column Name':<20} {'Data Type':<15} {'Nullable':<10} {'Default':<15}")
    print("-" * 80)
    for col in columns:
        # col is (cid, name, type, notnull, dflt_value, pk)
        name = col['name']
        dtype = col['type']
        nullable = "NO" if col['notnull'] else "YES"
        default = col['dflt_value']
        print(f"{name:<20} {dtype:<15} {nullable:<10} {str(default):<15}")
    
    print("\n" + "=" * 80)
    print("HOLIDAYS TABLE CONTENTS")
    print("=" * 80)
    
    # Get all holidays
    cur.execute("""
        SELECT id, date, name, description, type, is_recurring
        FROM holidays
        ORDER BY date;
    """)
    
    holidays = cur.fetchall()
    
    if not holidays:
        print("No holidays found in the table.")
    else:
        print(f"{'ID':<5} {'Date':<12} {'Name':<25} {'Type':<12} {'Recurring':<10} {'Description':<30}")
        print("-" * 100)
        for holiday in holidays:
            id, date, name, description, type_val, is_recurring = holiday
            recurring = "Yes" if is_recurring else "No"
            desc = description[:27] + "..." if description and len(description) > 30 else description or ""
            print(f"{id:<5} {str(date):<12} {name:<25} {type_val:<12} {recurring:<10} {desc:<30}")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total holidays: {len(holidays)}")
    
    # Count by type
    cur.execute("SELECT type, COUNT(*) FROM holidays GROUP BY type;")
    type_counts = cur.fetchall()
    print("\nHolidays by type:")
    for type_val, count in type_counts:
        print(f"  {type_val}: {count}")
    
    # Count recurring vs non-recurring
    cur.execute("SELECT is_recurring, COUNT(*) FROM holidays GROUP BY is_recurring;")
    recurring_counts = cur.fetchall()
    print("\nRecurring vs Non-recurring:")
    for is_recurring, count in recurring_counts:
        status = "Recurring" if is_recurring else "Non-recurring"
        print(f"  {status}: {count}")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    view_holidays_table() 
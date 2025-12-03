from database import get_db_connection
import sqlite3

conn = get_db_connection()
cur = conn.cursor()

print("Checking if 'holidays' table exists and its columns:")
# Check if table exists
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='holidays';")
if not cur.fetchone():
    print("Table 'holidays' does NOT exist.")
else:
    # Get columns info
    cur.execute("PRAGMA table_info(holidays);")
    rows = cur.fetchall()
    print("Table 'holidays' exists. Columns:")
    for row in rows:
        # row is (cid, name, type, notnull, dflt_value, pk)
        print(f"- {row['name']}: {row['type']}")
cur.close()
conn.close() 
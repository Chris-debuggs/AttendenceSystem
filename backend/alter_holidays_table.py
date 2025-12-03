from database import get_db_connection

conn = get_db_connection()
cur = conn.cursor()

# List of ALTER TABLE statements to add missing columns if they do not exist
# SQLite supports ADD COLUMN but not IF NOT EXISTS in the ADD COLUMN clause directly in older versions, 
# but modern SQLite does support it or we can catch the error.
# However, standard SQLite syntax is ALTER TABLE table_name ADD COLUMN column_name column_type;
# We will check if column exists first to simulate IF NOT EXISTS or just try/except.

columns_to_add = [
    ("date", "TEXT"),
    ("description", "TEXT"),
    ("type", "TEXT"),
    ("is_recurring", "INTEGER DEFAULT 0")
]

alter_statements = []
cur.execute("PRAGMA table_info(holidays)")
existing_columns = [row['name'] for row in cur.fetchall()]

for col_name, col_type in columns_to_add:
    if col_name not in existing_columns:
        alter_statements.append(f"ALTER TABLE holidays ADD COLUMN {col_name} {col_type};")

for stmt in alter_statements:
    try:
        cur.execute(stmt)
        print(f"Executed: {stmt.strip()}")
    except Exception as e:
        print(f"Error executing '{stmt.strip()}': {e}")
        conn.rollback()

conn.commit()
cur.close()
conn.close()
print("Table 'holidays' altered (if needed). Done.") 
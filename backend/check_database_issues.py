#!/usr/bin/env python3
"""
Script to check for database issues and diagnose problems
"""

from database import get_db_connection

def check_database_issues():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        print("=" * 60)
        print("DATABASE DIAGNOSTIC CHECK")
        print("=" * 60)
        
        # Check if tables exist
        print("\n1. TABLE EXISTENCE CHECK:")
        print("-" * 30)
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('employees', 'attendance', 'admin')
            ORDER BY table_name
        """)
        tables = cur.fetchall()
        print(f"Found tables: {[table[0] for table in tables]}")
        
        # Check table structures
        print("\n2. TABLE STRUCTURE CHECK:")
        print("-" * 30)
        for table_name in ['employees', 'attendance', 'admin']:
            cur.execute(f"""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
            """)
            columns = cur.fetchall()
            print(f"\n{table_name.upper()} table columns:")
            for col in columns:
                print(f"  {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
        
        # Check constraints
        print("\n3. CONSTRAINT CHECK:")
        print("-" * 30)
        cur.execute("""
            SELECT 
                tc.table_name, 
                tc.constraint_name, 
                tc.constraint_type,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints tc
            LEFT JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
            LEFT JOIN information_schema.constraint_column_usage ccu 
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.table_name IN ('employees', 'attendance', 'admin')
            ORDER BY tc.table_name, tc.constraint_type
        """)
        constraints = cur.fetchall()
        for constraint in constraints:
            print(f"  {constraint[0]}.{constraint[1]}: {constraint[2]} on {constraint[3]}")
            if constraint[4]:
                print(f"    -> references {constraint[4]}.{constraint[5]}")
        
        # Check sequences
        print("\n4. SEQUENCE CHECK:")
        print("-" * 30)
        cur.execute("""
            SELECT sequence_name, last_value, is_called
            FROM information_schema.sequences
            WHERE sequence_schema = 'public'
        """)
        sequences = cur.fetchall()
        for seq in sequences:
            print(f"  {seq[0]}: last_value={seq[1]}, is_called={seq[2]}")
        
        # Check data counts
        print("\n5. DATA COUNT CHECK:")
        print("-" * 30)
        for table_name in ['employees', 'attendance', 'admin']:
            cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cur.fetchone()[0]
            print(f"  {table_name}: {count} records")
        
        # Check for any orphaned data
        print("\n6. ORPHANED DATA CHECK:")
        print("-" * 30)
        cur.execute("""
            SELECT COUNT(*) 
            FROM attendance a 
            LEFT JOIN employees e ON a.employee_id = e.id 
            WHERE e.id IS NULL
        """)
        orphaned_attendance = cur.fetchone()[0]
        print(f"  Orphaned attendance records: {orphaned_attendance}")
        
        # Check database size
        print("\n7. DATABASE SIZE CHECK:")
        print("-" * 30)
        cur.execute("""
            SELECT 
                pg_size_pretty(pg_database_size(current_database())) as db_size,
                pg_size_pretty(pg_total_relation_size('employees')) as employees_size,
                pg_size_pretty(pg_total_relation_size('attendance')) as attendance_size,
                pg_size_pretty(pg_total_relation_size('admin')) as admin_size
        """)
        sizes = cur.fetchone()
        print(f"  Database size: {sizes[0]}")
        print(f"  Employees table: {sizes[1]}")
        print(f"  Attendance table: {sizes[2]}")
        print(f"  Admin table: {sizes[3]}")
        
    except Exception as e:
        print(f"Error during diagnostic: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    check_database_issues() 
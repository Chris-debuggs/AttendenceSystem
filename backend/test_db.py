#!/usr/bin/env python3
"""
Test script to verify database setup
"""

from database import get_db_connection, init_database

def test_database_connection():
    """Test database connection"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Test basic connection
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print(f"✅ Database connection successful")
        if version:
            print(f"PostgreSQL version: {version[0]}")
        else:
            print("PostgreSQL version: Unknown")
        
        # Test if tables exist
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('employees', 'attendance')
        """)
        tables = cur.fetchall()
        
        if len(tables) == 2:
            print("✅ All required tables exist")
            for table in tables:
                print(f"   - {table[0]}")
        else:
            print("❌ Some tables are missing")
            print("Creating tables...")
            init_database()
            print("✅ Tables created successfully")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing database setup...")
    success = test_database_connection()
    
    if success:
        print("\n🎉 Database setup is working correctly!")
    else:
        print("\n💥 Database setup failed. Please check your configuration.") 
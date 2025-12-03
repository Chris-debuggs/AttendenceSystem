#!/usr/bin/env python3
"""
Test script to verify database persistence and employee operations
"""

from database import get_db_connection, init_database
import requests
import json

def test_database_persistence():
    print("=" * 50)
    print("DATABASE PERSISTENCE TEST")
    print("=" * 50)
    
    # Initialize database
    print("\n1. Initializing database...")
    init_database()
    
    # Test adding an employee
    print("\n2. Testing employee creation...")
    test_employee = {
        "id": "TEST001",
        "name": "Test Employee",
        "email": "test@example.com",
        "department": "IT",
        "position": "Developer",
        "salary": 50000.0,
        "working_hours_per_day": 8.0
    }
    
    try:
        response = requests.post("http://localhost:8000/employees/", json=test_employee)
        print(f"Create employee response: {response.status_code}")
        if response.status_code == 200:
            print("✅ Employee created successfully")
        else:
            print(f"❌ Failed to create employee: {response.text}")
    except Exception as e:
        print(f"❌ Error creating employee: {e}")
    
    # Test getting employees
    print("\n3. Testing employee retrieval...")
    try:
        response = requests.get("http://localhost:8000/employees/")
        print(f"Get employees response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {len(data.get('employees', []))} employees")
        else:
            print(f"❌ Failed to get employees: {response.text}")
    except Exception as e:
        print(f"❌ Error getting employees: {e}")
    
    # Test deleting employee
    print("\n4. Testing employee deletion...")
    try:
        response = requests.delete("http://localhost:8000/employees/TEST001")
        print(f"Delete employee response: {response.status_code}")
        if response.status_code == 200:
            print("✅ Employee deleted successfully")
        else:
            print(f"❌ Failed to delete employee: {response.text}")
    except Exception as e:
        print(f"❌ Error deleting employee: {e}")
    
    # Test re-creating the same employee
    print("\n5. Testing re-creation of same employee...")
    try:
        response = requests.post("http://localhost:8000/employees/", json=test_employee)
        print(f"Re-create employee response: {response.status_code}")
        if response.status_code == 200:
            print("✅ Employee re-created successfully")
        else:
            print(f"❌ Failed to re-create employee: {response.text}")
    except Exception as e:
        print(f"❌ Error re-creating employee: {e}")
    
    print("\n" + "=" * 50)
    print("TEST COMPLETED")
    print("=" * 50)

if __name__ == "__main__":
    test_database_persistence() 
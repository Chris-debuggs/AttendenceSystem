#!/usr/bin/env python3
"""
Test script for the Leave Management system
"""

import requests
import json
from datetime import date, datetime

# API base URL
API_URL = "http://127.0.0.1:8000"

def test_leave_system():
    print("Testing Leave Management System...")
    print("=" * 50)
    
    # Test 1: Get employees
    print("\n1. Testing GET /employees/")
    try:
        response = requests.get(f"{API_URL}/employees/")
        if response.status_code == 200:
            employees = response.json()
            print(f"✅ Successfully fetched {len(employees.get('employees', []))} employees")
            if employees.get('employees'):
                print(f"   First employee: {employees['employees'][0]['name']} (ID: {employees['employees'][0]['id']})")
        else:
            print(f"❌ Failed to fetch employees: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error fetching employees: {e}")
        return False
    
    # Test 2: Get leaves for current month
    print("\n2. Testing GET /leaves/")
    current_year = datetime.now().year
    current_month = datetime.now().month
    try:
        response = requests.get(f"{API_URL}/leaves/?year={current_year}&month={current_month}")
        if response.status_code == 200:
            leaves = response.json()
            print(f"✅ Successfully fetched {len(leaves)} leaves for {current_month}/{current_year}")
        else:
            print(f"❌ Failed to fetch leaves: {response.status_code}")
    except Exception as e:
        print(f"❌ Error fetching leaves: {e}")
    
    # Test 3: Create a test leave (if employees exist)
    if employees.get('employees'):
        test_employee = employees['employees'][0]
        print(f"\n3. Testing POST /leaves/ for employee: {test_employee['name']}")
        
        # Create a test leave for tomorrow
        tomorrow = date.today().replace(day=date.today().day + 1)
        leave_data = {
            "employee_id": test_employee['id'],
            "leave_date": tomorrow.isoformat(),
            "leave_type": "CASUAL",
            "reason": "Test leave for system verification"
        }
        
        try:
            response = requests.post(
                f"{API_URL}/leaves/",
                json=leave_data,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                created_leave = response.json()
                print(f"✅ Successfully created leave: ID {created_leave['id']}")
                
                # Test 4: Delete the test leave
                print(f"\n4. Testing DELETE /leaves/{created_leave['id']}")
                delete_response = requests.delete(f"{API_URL}/leaves/{created_leave['id']}")
                if delete_response.status_code == 204:
                    print(f"✅ Successfully deleted leave: ID {created_leave['id']}")
                else:
                    print(f"❌ Failed to delete leave: {delete_response.status_code}")
            else:
                print(f"❌ Failed to create leave: {response.status_code}")
                if response.text:
                    print(f"   Error: {response.text}")
        except Exception as e:
            print(f"❌ Error creating/deleting leave: {e}")
    
    print("\n" + "=" * 50)
    print("Leave Management System Test Completed!")
    return True

if __name__ == "__main__":
    test_leave_system() 
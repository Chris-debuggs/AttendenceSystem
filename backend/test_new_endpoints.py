#!/usr/bin/env python3
"""
Test script for the new Leave Management endpoints
"""

import requests
import json
from datetime import date, datetime

# API base URL
API_URL = "http://127.0.0.1:8000"

def test_new_endpoints():
    print("Testing New Leave Management Endpoints...")
    print("=" * 50)
    
    current_year = datetime.now().year
    
    # Test 1: Get all leaves for year
    print(f"\n1. Testing GET /leaves/all/?year={current_year}")
    try:
        response = requests.get(f"{API_URL}/leaves/all/?year={current_year}")
        if response.status_code == 200:
            leaves = response.json()
            print(f"✅ Successfully fetched {len(leaves)} leaves for {current_year}")
            for leave in leaves:
                print(f"   - {leave['employee_id']}: {leave['leave_date']} ({leave['leave_type']})")
        else:
            print(f"❌ Failed to fetch all leaves: {response.status_code}")
    except Exception as e:
        print(f"❌ Error fetching all leaves: {e}")
    
    # Test 2: Get employees first
    print(f"\n2. Testing GET /employees/")
    try:
        response = requests.get(f"{API_URL}/employees/")
        if response.status_code == 200:
            employees = response.json()
            if employees.get('employees'):
                test_employee = employees['employees'][0]
                print(f"✅ Found employee: {test_employee['name']} (ID: {test_employee['id']})")
                
                # Test 3: Get leaves for specific employee
                print(f"\n3. Testing GET /leaves/employee/{test_employee['id']}/?year={current_year}")
                try:
                    response = requests.get(f"{API_URL}/leaves/employee/{test_employee['id']}/?year={current_year}")
                    if response.status_code == 200:
                        employee_leaves = response.json()
                        print(f"✅ Successfully fetched {len(employee_leaves)} leaves for {test_employee['name']}")
                        for leave in employee_leaves:
                            print(f"   - {leave['leave_date']}: {leave['leave_type']} - {leave['reason']}")
                    else:
                        print(f"❌ Failed to fetch employee leaves: {response.status_code}")
                except Exception as e:
                    print(f"❌ Error fetching employee leaves: {e}")
                
                # Test 4: Create a test leave and verify it appears
                print(f"\n4. Testing leave creation and verification")
                tomorrow = date.today().replace(day=date.today().day + 1)
                leave_data = {
                    "employee_id": test_employee['id'],
                    "leave_date": tomorrow.isoformat(),
                    "leave_type": "CASUAL",
                    "reason": "Test leave for endpoint verification"
                }
                
                try:
                    response = requests.post(
                        f"{API_URL}/leaves/",
                        json=leave_data,
                        headers={"Content-Type": "application/json"}
                    )
                    if response.status_code == 200:
                        created_leave = response.json()
                        print(f"✅ Created test leave: ID {created_leave['id']}")
                        
                        # Verify it appears in employee leaves
                        response = requests.get(f"{API_URL}/leaves/employee/{test_employee['id']}/?year={current_year}")
                        if response.status_code == 200:
                            updated_leaves = response.json()
                            print(f"✅ Employee now has {len(updated_leaves)} leaves")
                            
                            # Clean up - delete the test leave
                            delete_response = requests.delete(f"{API_URL}/leaves/{created_leave['id']}")
                            if delete_response.status_code == 204:
                                print(f"✅ Cleaned up test leave")
                            else:
                                print(f"❌ Failed to clean up test leave: {delete_response.status_code}")
                        else:
                            print(f"❌ Failed to verify leave creation: {response.status_code}")
                    else:
                        print(f"❌ Failed to create test leave: {response.status_code}")
                except Exception as e:
                    print(f"❌ Error in leave creation test: {e}")
            else:
                print("❌ No employees found for testing")
        else:
            print(f"❌ Failed to fetch employees: {response.status_code}")
    except Exception as e:
        print(f"❌ Error fetching employees: {e}")
    
    print("\n" + "=" * 50)
    print("New Endpoints Test Completed!")

if __name__ == "__main__":
    test_new_endpoints() 
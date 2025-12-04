#!/usr/bin/env python3
"""
Add Test Users Script
Creates test employees in the database for development and testing purposes.
Excludes photo/face embedding data.
"""

import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db_connection
from datetime import datetime, timedelta
import random

def generate_employee_id(name):
    """Generate a simple employee ID from name"""
    return name.replace(" ", "").upper()[:3] + str(random.randint(1000, 9999))

def add_test_employee(name, email, mobile_no, address, department, position, salary, 
                      working_hours, employee_type, gender, joining_date):
    """Add a single test employee to the database"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        employee_id = generate_employee_id(name)
        
        cur.execute("""
            INSERT INTO employees (
                id, name, email, mobile_no, address, department, position, 
                salary, working_hours_per_day, employee_type, gender, joining_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            employee_id, name, email, mobile_no, address, department, position,
            salary, working_hours, employee_type, gender, joining_date
        ))
        
        conn.commit()
        print(f"✓ Added: {name} (ID: {employee_id})")
        return True
    except Exception as e:
        print(f"✗ Error adding {name}: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def add_test_users():
    """Add multiple test employees with diverse data"""
    
    # Calculate some dates
    today = datetime.now()
    six_months_ago = today - timedelta(days=180)
    one_year_ago = today - timedelta(days=365)
    two_years_ago = today - timedelta(days=730)
    
    test_employees = [
        {
            "name": "John Smith",
            "email": "john.smith@nexoris.com",
            "mobile_no": "+1-555-0101",
            "address": "123 Main St, New York, NY 10001",
            "department": "Engineering",
            "position": "Senior Software Engineer",
            "salary": 120000.00,
            "working_hours": 8.0,
            "employee_type": "full_time",
            "gender": "Male",
            "joining_date": two_years_ago.strftime("%Y-%m-%d")
        },
        {
            "name": "Sarah Johnson",
            "email": "sarah.johnson@nexoris.com",
            "mobile_no": "+1-555-0102",
            "address": "456 Oak Ave, San Francisco, CA 94102",
            "department": "HR",
            "position": "HR Manager",
            "salary": 95000.00,
            "working_hours": 8.0,
            "employee_type": "full_time",
            "gender": "Female",
            "joining_date": one_year_ago.strftime("%Y-%m-%d")
        },
        {
            "name": "Michael Chen",
            "email": "michael.chen@nexoris.com",
            "mobile_no": "+1-555-0103",
            "address": "789 Pine Rd, Seattle, WA 98101",
            "department": "Engineering",
            "position": "DevOps Engineer",
            "salary": 110000.00,
            "working_hours": 8.0,
            "employee_type": "full_time",
            "gender": "Male",
            "joining_date": one_year_ago.strftime("%Y-%m-%d")
        },
        {
            "name": "Emily Davis",
            "email": "emily.davis@nexoris.com",
            "mobile_no": "+1-555-0104",
            "address": "321 Elm St, Boston, MA 02101",
            "department": "Finance",
            "position": "Financial Analyst",
            "salary": 85000.00,
            "working_hours": 8.0,
            "employee_type": "full_time",
            "gender": "Female",
            "joining_date": six_months_ago.strftime("%Y-%m-%d")
        },
        {
            "name": "David Martinez",
            "email": "david.martinez@nexoris.com",
            "mobile_no": "+1-555-0105",
            "address": "654 Maple Dr, Austin, TX 78701",
            "department": "Marketing",
            "position": "Marketing Specialist",
            "salary": 75000.00,
            "working_hours": 8.0,
            "employee_type": "full_time",
            "gender": "Male",
            "joining_date": six_months_ago.strftime("%Y-%m-%d")
        },
        {
            "name": "Lisa Anderson",
            "email": "lisa.anderson@nexoris.com",
            "mobile_no": "+1-555-0106",
            "address": "987 Cedar Ln, Denver, CO 80201",
            "department": "Engineering",
            "position": "Junior Developer",
            "salary": 70000.00,
            "working_hours": 8.0,
            "employee_type": "full_time",
            "gender": "Female",
            "joining_date": today.strftime("%Y-%m-%d")
        },
        {
            "name": "Robert Wilson",
            "email": "robert.wilson@nexoris.com",
            "mobile_no": "+1-555-0107",
            "address": "147 Birch St, Chicago, IL 60601",
            "department": "Sales",
            "position": "Sales Manager",
            "salary": 90000.00,
            "working_hours": 8.0,
            "employee_type": "full_time",
            "gender": "Male",
            "joining_date": one_year_ago.strftime("%Y-%m-%d")
        },
        {
            "name": "Jessica Taylor",
            "email": "jessica.taylor@nexoris.com",
            "mobile_no": "+1-555-0108",
            "address": "258 Willow Way, Miami, FL 33101",
            "department": "Design",
            "position": "UI/UX Designer",
            "salary": 80000.00,
            "working_hours": 6.0,
            "employee_type": "part_time",
            "gender": "Female",
            "joining_date": six_months_ago.strftime("%Y-%m-%d")
        },
        {
            "name": "James Brown",
            "email": "james.brown@nexoris.com",
            "mobile_no": "+1-555-0109",
            "address": "369 Spruce Ct, Portland, OR 97201",
            "department": "Operations",
            "position": "Operations Manager",
            "salary": 105000.00,
            "working_hours": 8.0,
            "employee_type": "full_time",
            "gender": "Male",
            "joining_date": two_years_ago.strftime("%Y-%m-%d")
        },
        {
            "name": "Maria Garcia",
            "email": "maria.garcia@nexoris.com",
            "mobile_no": "+1-555-0110",
            "address": "741 Redwood Blvd, Los Angeles, CA 90001",
            "department": "Customer Support",
            "position": "Support Specialist",
            "salary": 65000.00,
            "working_hours": 8.0,
            "employee_type": "contract",
            "gender": "Female",
            "joining_date": today.strftime("%Y-%m-%d")
        }
    ]
    
    print("\n" + "="*60)
    print("Adding Test Employees to Database")
    print("="*60 + "\n")
    
    success_count = 0
    for emp in test_employees:
        if add_test_employee(**emp):
            success_count += 1
    
    print("\n" + "="*60)
    print(f"Results: {success_count}/{len(test_employees)} employees added successfully")
    print("="*60 + "\n")

if __name__ == "__main__":
    print("\n🚀 Test User Generator\n")
    add_test_users()

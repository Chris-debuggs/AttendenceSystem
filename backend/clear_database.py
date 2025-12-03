#!/usr/bin/env python3
"""
Script to clear the database - use with caution!
This will delete all employees, attendance records, and admin users.
"""

from database import clear_database

if __name__ == "__main__":
    print("WARNING: This will delete ALL data from the database!")
    print("This includes all employees, attendance records, and admin users.")
    response = input("Are you sure you want to continue? (yes/no): ")
    
    if response.lower() == 'yes':
        clear_database()
        print("Database cleared. You may need to restart the server.")
    else:
        print("Operation cancelled.") 
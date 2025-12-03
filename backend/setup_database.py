#!/usr/bin/env python3
"""
Database setup script - run this once to initialize the database
"""

from database import init_database

if __name__ == "__main__":
    print("Setting up database...")
    init_database()
    print("Database setup completed!")
    print("\nYou can now start the server with: uvicorn main:app --reload") 
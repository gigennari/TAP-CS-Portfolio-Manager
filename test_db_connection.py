#!/usr/bin/env python3
"""
Test script to verify database connection and users table
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'server'))

from db import init_db

def test_database_connection():
    """Test database connection and users table"""
    try:
        print("🔍 Testing database connection...")
        conn = init_db()
        cursor = conn.cursor(dictionary=True)
        
        # Test connection
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        print(f"✅ Database connection successful: {result}")
        
        # Check if users table exists
        cursor.execute("SHOW TABLES LIKE 'users'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("✅ Users table exists")
            
            # Count users
            cursor.execute("SELECT COUNT(*) as count FROM users")
            count_result = cursor.fetchone()
            user_count = count_result['count']
            print(f"📊 Users in table: {user_count}")
            
            if user_count > 0:
                # Show sample users
                cursor.execute("SELECT user_id, username, email, first_name, last_name FROM users LIMIT 5")
                users = cursor.fetchall()
                print("\n👥 Sample users:")
                for user in users:
                    print(f"  - ID: {user['user_id']}, Username: {user['username']}, Email: {user['email']}")
                    print(f"    Name: {user['first_name']} {user['last_name']}")
            else:
                print("⚠️  Users table is empty")
                print("\n💡 To add test users, run:")
                print("INSERT INTO users (username, email, first_name, last_name) VALUES")
                print("('john_doe', 'john@example.com', 'John', 'Doe'),")
                print("('jane_smith', 'jane@example.com', 'Jane', 'Smith');")
        else:
            print("❌ Users table does not exist")
            print("\n💡 Create users table with:")
            print("""
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
            """)
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        print("\n🔧 Check:")
        print("1. MySQL server is running")
        print("2. Database 'bygDB' exists")
        print("3. Connection credentials in db.py are correct")

if __name__ == "__main__":
    test_database_connection()
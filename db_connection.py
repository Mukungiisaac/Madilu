"""
Database Connection Module
Using MySQL Connector Python
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_db_connection():
    """
    Create and return a database connection
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'itech_events'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASS', ''),
            port=int(os.getenv('DB_PORT', 3306))
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        raise e

def close_connection(connection):
    """
    Close database connection
    """
    if connection and connection.is_connected():
        connection.close()

def generate_booking_reference():
    """
    Generate unique booking reference
    """
    import hashlib
    import time
    random_str = hashlib.md5(str(time.time()).encode()).hexdigest()[:6]
    return f"ITECH-{random_str.upper()}"

def format_price(price):
    """
    Format price to KSh format
    """
    return f"KSh {price:,.0f}"

if __name__ == "__main__":
    # Test connection
    try:
        conn = get_db_connection()
        if conn.is_connected():
            print("Connected to MySQL database successfully")
            cursor = conn.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"MySQL Version: {version[0]}")
            close_connection(conn)
    except Error as e:
        print(f"Error: {e}")

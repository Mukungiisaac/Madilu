"""
Database Setup Script
Run this to initialize the database with sample data
Usage: python setup_database.py
"""

from db_connection import get_db_connection, close_connection

def setup_database():
    """Initialize database with sample data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Use the database
        cursor.execute("USE itech_events")
        
        # Check if categories exist
        cursor.execute("SELECT COUNT(*) FROM categories")
        if cursor.fetchone()[0] == 0:
            print("Inserting categories...")
            cursor.execute("""
                INSERT INTO categories (name, icon) VALUES
                ('music', 'fa-guitar'),
                ('sports', 'fa-running'),
                ('arts', 'fa-mask'),
                ('business', 'fa-briefcase'),
                ('food', 'fa-utensils'),
                ('tech', 'fa-microchip')
            """)
        
        # Check if default venue exists
        cursor.execute("SELECT COUNT(*) FROM venues")
        if cursor.fetchone()[0] == 0:
            print("Inserting default venue...")
            cursor.execute("""
                INSERT INTO venues (name, address, city, capacity, description)
                VALUES ('Kenya International Trade Centre', 'Mombasa Road', 'Nairobi', 5000, 'Premium event venue in Nairobi')
            """)
            cursor.execute("""
                INSERT INTO venues (name, address, city, capacity, description)
                VALUES ('Nairobi Convention Centre', 'Kenyatta Avenue', 'Nairobi', 2000, 'Modern convention facility')
            """)
        
        # Check if test organizer exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s", ('organizer@test.com',))
        if cursor.fetchone()[0] == 0:
            print("Inserting test organizer...")
            cursor.execute("""
                INSERT INTO users (full_name, email, phone, id_number, password, user_type)
                VALUES ('Test Organizer', 'organizer@test.com', '254700000000', '12345678', 'password123', 'organizer')
            """)
        
        # Check if sample events exist
        cursor.execute("SELECT COUNT(*) FROM events")
        if cursor.fetchone()[0] == 0:
            print("Inserting sample events...")
            cursor.execute("""
                INSERT INTO events (organizer_id, venue_id, title, description, category, event_date, standard_price, vip_price, image_url, status)
                VALUES 
                (1, 1, 'Tech Innovation Summit 2024', 'Join us for the biggest tech conference in East Africa featuring industry leaders and innovative startups.', 'tech', DATE_ADD(NOW(), INTERVAL 7 DAY), 5000, 15000, 'images/event-tech.jpg', 'published'),
                (1, 2, 'Jazz Night Live', 'An evening of smooth jazz with renowned artists from around the world.', 'music', DATE_ADD(NOW(), INTERVAL 14 DAY), 3000, 8000, 'images/event-music.jpg', 'published'),
                (1, 1, 'Food Festival Kenya', 'Taste the best of Kenyan cuisine from top restaurants and chefs.', 'food', DATE_ADD(NOW(), INTERVAL 21 DAY), 2000, 5000, 'images/event-food.jpg', 'published')
            """)
            
            # Insert ticket types for events
            cursor.execute("""
                INSERT INTO ticket_types (event_id, type_name, price, available_quantity, sold_quantity)
                VALUES 
                (1, 'standard', 5000, 1000, 0),
                (1, 'vip', 15000, 100, 0),
                (2, 'standard', 3000, 500, 0),
                (2, 'vip', 8000, 50, 0),
                (3, 'standard', 2000, 2000, 0),
                (3, 'vip', 5000, 200, 0)
            """)
        
        conn.commit()
        print("Database setup completed successfully!")
        
        # Print test credentials
        print("\nTest Organizer Login:")
        print("Email: organizer@test.com")
        print("Password: password123")
        
        close_connection(conn)
        
    except Exception as e:
        print(f"Error: {e}")
        raise e

if __name__ == '__main__':
    setup_database()

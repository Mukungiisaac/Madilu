"""
Add Sample Events for Merchant ID 2
Run this to add sample events for testing
Usage: python add_sample_events.py
"""

from db_connection import get_db_connection, close_connection

def add_sample_events_for_merchant2():
    """Add sample events for merchant ID 2"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Use the database
        cursor.execute("USE itech_events")
        
        # Check if merchant 2 exists, if not create them
        cursor.execute("SELECT id FROM users WHERE id = 2 AND user_type = 'organizer'")
        merchant = cursor.fetchone()
        
        if not merchant:
            print("Creating merchant with ID 2...")
            cursor.execute("""
                INSERT INTO users (id, full_name, email, phone, id_number, password, user_type)
                VALUES (2, 'Event Organizer 2', 'organizer2@test.com', '254700000001', '87654321', 'password123', 'organizer')
            """)
        
        # Check if venue exists for this merchant's events
        cursor.execute("SELECT COUNT(*) FROM venues")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO venues (name, address, city, capacity, description)
                VALUES ('Nairobi International Showground', 'Langata Road', 'Nairobi', 10000, 'Large outdoor venue')
            """)
        
        # Check if events already exist for merchant 2
        cursor.execute("SELECT COUNT(*) FROM events WHERE organizer_id = 2")
        if cursor.fetchone()[0] > 0:
            print("Events already exist for merchant 2. Skipping...")
        else:
            print("Adding sample events for merchant 2...")
            
            # Add sample events for merchant 2
            cursor.execute("""
                INSERT INTO events (organizer_id, venue_id, title, description, category, event_date, standard_price, vip_price, image_url, status)
                VALUES 
                (2, 1, 'Tech Innovation Summit 2024', 'Join us for the biggest tech conference in East Africa featuring industry leaders and innovative startups.', 'tech', DATE_ADD(NOW(), INTERVAL 7 DAY), 5000, 15000, 'images/event-tech.jpg', 'published'),
                (2, 1, 'Jazz Night Live', 'An evening of smooth jazz with renowned artists from around the world.', 'music', DATE_ADD(NOW(), INTERVAL 14 DAY), 3000, 8000, 'images/event-music.jpg', 'published'),
                (2, 2, 'Food Festival Kenya', 'Taste the best of Kenyan cuisine from top restaurants and chefs.', 'food', DATE_ADD(NOW(), INTERVAL 21 DAY), 2000, 5000, 'images/event-food.jpg', 'published'),
                (2, 2, 'Championship Finals', 'Watch the exciting championship finals live!', 'sports', DATE_ADD(NOW(), INTERVAL 30 DAY), 2500, 7500, 'images/event-sports.jpg', 'published')
            """)
            
            # Insert ticket types for events
            cursor.execute("""
                INSERT INTO ticket_types (event_id, type_name, price, available_quantity, sold_quantity)
                VALUES 
                ((SELECT id FROM events WHERE organizer_id = 2 AND category = 'tech' ORDER BY id DESC LIMIT 1), 'standard', 5000, 1000, 0),
                ((SELECT id FROM events WHERE organizer_id = 2 AND category = 'tech' ORDER BY id DESC LIMIT 1), 'vip', 15000, 100, 0),
                ((SELECT id FROM events WHERE organizer_id = 2 AND category = 'music' ORDER BY id DESC LIMIT 1), 'standard', 3000, 500, 0),
                ((SELECT id FROM events WHERE organizer_id = 2 AND category = 'music' ORDER BY id DESC LIMIT 1), 'vip', 8000, 50, 0),
                ((SELECT id FROM events WHERE organizer_id = 2 AND category = 'food' ORDER BY id DESC LIMIT 1), 'standard', 2000, 2000, 0),
                ((SELECT id FROM events WHERE organizer_id = 2 AND category = 'food' ORDER BY id DESC LIMIT 1), 'vip', 5000, 200, 0),
                ((SELECT id FROM events WHERE organizer_id = 2 AND category = 'sports' ORDER BY id DESC LIMIT 1), 'standard', 2500, 3000, 0),
                ((SELECT id FROM events WHERE organizer_id = 2 AND category = 'sports' ORDER BY id DESC LIMIT 1), 'vip', 7500, 500, 0)
            """)
        
        conn.commit()
        print("Sample events added successfully for merchant ID 2!")
        
        close_connection(conn)
        
    except Exception as e:
        print(f"Error: {e}")
        raise e

if __name__ == '__main__':
    add_sample_events_for_merchant2()

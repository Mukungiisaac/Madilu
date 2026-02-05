"""
Add More Sample Events for Merchant ID 2
Run this to add more sample events for testing
Usage: py add_more_events.py
"""

from db_connection import get_db_connection, close_connection

def add_more_events_for_merchant2():
    """Add more sample events for merchant ID 2"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Use the database
        cursor.execute("USE itech_events")
        
        # Add more sample events for merchant 2
        print("Adding more sample events for merchant 2...")
            
        cursor.execute("""
            INSERT INTO events (organizer_id, venue_id, title, description, category, event_date, standard_price, vip_price, image_url, status)
            VALUES 
            (2, 1, 'Tech Innovation Summit 2024', 'Join us for the biggest tech conference in East Africa featuring industry leaders and innovative startups.', 'tech', DATE_ADD(NOW(), INTERVAL 7 DAY), 5000, 15000, 'images/event-tech.jpg', 'published'),
            (2, 2, 'Jazz Night Live', 'An evening of smooth jazz with renowned artists from around the world.', 'music', DATE_ADD(NOW(), INTERVAL 14 DAY), 3000, 8000, 'images/event-music.jpg', 'published'),
            (2, 1, 'Food Festival Kenya', 'Taste the best of Kenyan cuisine from top restaurants and chefs.', 'food', DATE_ADD(NOW(), INTERVAL 21 DAY), 2000, 5000, 'images/event-food.jpg', 'published'),
            (2, 2, 'Championship Finals', 'Watch the exciting championship finals live!', 'sports', DATE_ADD(NOW(), INTERVAL 30 DAY), 2500, 7500, 'images/event-sports.jpg', 'published')
        """)
        
        # Get the event IDs that were just added
        cursor.execute("SELECT id FROM events WHERE organizer_id = 2 ORDER BY id DESC LIMIT 4")
        event_ids = [row[0] for row in cursor.fetchall()]
        
        print(f"Added events with IDs: {event_ids}")
        
        # Insert ticket types for events (reversed order to match)
        for event_id in reversed(event_ids):
            cursor.execute("""
                INSERT INTO ticket_types (event_id, type_name, price, available_quantity, sold_quantity)
                VALUES (%s, 'standard', 5000, 1000, 0),
                       (%s, 'vip', 15000, 100, 0)
            """, (event_id, event_id))
        
        conn.commit()
        print("Sample events added successfully for merchant ID 2!")
        
        # Verify
        cursor.execute("SELECT id, title FROM events WHERE organizer_id = 2")
        events = cursor.fetchall()
        print(f"Total events for merchant 2: {len(events)}")
        for e in events:
            print(f"  - {e[0]}: {e[1]}")
        
        close_connection(conn)
        
    except Exception as e:
        print(f"Error: {e}")
        raise e

if __name__ == '__main__':
    add_more_events_for_merchant2()

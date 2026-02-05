"""
Create Sample Events for All Merchants
Run this to add sample events for all users so they see something in their dashboards
Usage: py create_all_events.py
"""

from db_connection import get_db_connection, close_connection

def create_events_for_all_merchants():
    """Create sample events for all merchants"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Use the database
        cursor.execute("USE itech_events")
        
        # Get all organizers
        cursor.execute("SELECT id, email, full_name FROM users WHERE user_type = 'organizer'")
        users = cursor.fetchall()
        
        print(f"Found {len(users)} organizers")
        
        event_templates = [
            {
                'title': 'Annual Tech Conference',
                'description': 'Join industry leaders for the biggest tech event of the year.',
                'category': 'tech',
                'standard_price': 5000,
                'vip_price': 15000,
                'image_url': 'images/event-tech.jpg'
            },
            {
                'title': 'Summer Music Festival',
                'description': 'Three days of amazing live music performances.',
                'category': 'music',
                'standard_price': 3000,
                'vip_price': 8000,
                'image_url': 'images/event-music.jpg'
            },
            {
                'title': 'Food & Wine Expo',
                'description': 'Taste the finest cuisines from top chefs.',
                'category': 'food',
                'standard_price': 2000,
                'vip_price': 5000,
                'image_url': 'images/event-food.jpg'
            }
        ]
        
        for user in users:
            user_id, email, full_name = user
            print(f"\nProcessing user {user_id}: {email} ({full_name})")
            
            # Check if user already has events
            cursor.execute("SELECT COUNT(*) FROM events WHERE organizer_id = %s", (user_id,))
            existing_count = cursor.fetchone()[0]
            
            if existing_count > 0:
                print(f"  Already has {existing_count} events, skipping...")
                continue
            
            # Ensure venue exists
            cursor.execute("SELECT COUNT(*) FROM venues")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO venues (name, address, city, capacity, description)
                    VALUES ('Default Venue', 'Nairobi', 'Nairobi', 1000, 'Auto-created default venue')
                """)
            
            # Create events for this user
            for i, template in enumerate(event_templates):
                days_ahead = (i + 1) * 7
                
                cursor.execute("""
                    INSERT INTO events (organizer_id, venue_id, title, description, category, event_date, standard_price, vip_price, image_url, status)
                    VALUES (%s, 1, %s, %s, %s, DATE_ADD(NOW(), INTERVAL %s DAY), %s, %s, %s, 'published')
                """, (
                    user_id,
                    template['title'] + f' - {full_name.split()[0]}',
                    template['description'],
                    template['category'],
                    days_ahead,
                    template['standard_price'],
                    template['vip_price'],
                    template['image_url']
                ))
                
                event_id = cursor.lastrowid
                
                # Insert ticket types
                cursor.execute("""
                    INSERT INTO ticket_types (event_id, type_name, price, available_quantity, sold_quantity)
                    VALUES (%s, 'standard', %s, 1000, %s),
                           (%s, 'vip', %s, 100, %s)
                """, (
                    event_id, template['standard_price'], i * 10,
                    event_id, template['vip_price'], i * 5
                ))
                
                print(f"  Created: {template['title']} - {full_name.split()[0]}")
        
        conn.commit()
        
        # Print summary
        print("\n" + "="*50)
        print("Summary of events per user:")
        cursor.execute("""
            SELECT u.id, u.email, u.full_name, COUNT(e.id) as event_count
            FROM users u
            LEFT JOIN events e ON u.id = e.organizer_id
            WHERE u.user_type = 'organizer'
            GROUP BY u.id, u.email, u.full_name
            ORDER BY u.id
        """)
        results = cursor.fetchall()
        for row in results:
            print(f"  {row[0]}: {row[1]} - {row[2]}: {row[3]} events")
        
        close_connection(conn)
        print("\nDone!")
        
    except Exception as e:
        print(f"Error: {e}")
        raise e

if __name__ == '__main__':
    create_events_for_all_merchants()

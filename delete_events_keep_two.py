"""
Script to delete events from database, keeping only 2
Usage: python delete_events_keep_two.py
"""

from db_connection import get_db_connection, close_connection

def delete_events_keep_two():
    """Delete events but keep only 2 in the database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Use the database
        cursor.execute("USE itech_events")
        
        # Get all event IDs
        cursor.execute("SELECT id, title FROM events ORDER BY id")
        events = cursor.fetchall()
        
        print(f"Found {len(events)} events in the database:")
        for event in events:
            print(f"  - ID {event[0]}: {event[1]}")
        
        if len(events) <= 2:
            print("Already 2 or fewer events. No deletion needed.")
        else:
            # Keep only the first 2 events (by ID)
            events_to_delete = events[2:]  # Skip first 2
            
            print(f"\nDeleting {len(events_to_delete)} events, keeping 2...")
            
            for event in events_to_delete:
                event_id = event[0]
                event_title = event[1]
                
                # Delete related booking tickets first
                cursor.execute("""
                    DELETE bt FROM booking_tickets bt
                    JOIN ticket_types tt ON bt.ticket_type_id = tt.id
                    WHERE tt.event_id = %s
                """, (event_id,))
                
                # Delete ticket types
                cursor.execute("DELETE FROM ticket_types WHERE event_id = %s", (event_id,))
                
                # Delete the event
                cursor.execute("DELETE FROM events WHERE id = %s", (event_id,))
                
                print(f"  - Deleted: {event_title} (ID: {event_id})")
            
            conn.commit()
            print(f"\nSuccessfully deleted {len(events_to_delete)} events!")
        
        # Show remaining events
        cursor.execute("SELECT id, title FROM events ORDER BY id")
        remaining_events = cursor.fetchall()
        
        print(f"\nRemaining events ({len(remaining_events)}):")
        for event in remaining_events:
            print(f"  - ID {event[0]}: {event[1]}")
        
        close_connection(conn)
        
    except Exception as e:
        print(f"Error: {e}")
        raise e

if __name__ == '__main__':
    delete_events_keep_two()

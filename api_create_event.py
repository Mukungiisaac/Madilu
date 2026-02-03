"""
API - Create Event Endpoint
Run with: python -m http.server 8000
Access at: http://localhost:8000/api_create_event.py
"""

import json
from db_connection import get_db_connection, close_connection
from http.server import BaseHTTPRequestHandler
import urllib.parse
from datetime import datetime

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class CreateEventHandler(BaseHTTPRequestHandler):
    def send_cors_headers(self):
        """Send CORS headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
    
    def do_POST(self):
        """
        Handle POST requests to create events
        """
        try:
            # Get POST data
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            
            # Convert to simple dict
            data = {k: v[0] for k, v in data.items()}
            
            # Validate required fields
            required_fields = ['organizerId', 'venueId', 'title', 'description', 'category', 'eventDate', 'standardPrice', 'vipPrice']
            for field in required_fields:
                if field not in data:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'success': False,
                        'message': f'Missing required field: {field}'
                    }, cls=DateTimeEncoder).encode())
                    return
            
            organizer_id = int(data['organizerId'])
            venue_id = data.get('venueId')
            venue_name = data.get('venueName', '')
            title = data['title']
            description = data['description']
            category = data['category']
            event_date = data['eventDate']
            standard_price = float(data['standardPrice'])
            vip_price = float(data['vipPrice'])
            image_url = data.get('imageUrl', '')
            
            # Get database connection
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Verify organizer exists
            cursor.execute("SELECT id, user_type FROM users WHERE id = %s", (organizer_id,))
            organizer = cursor.fetchone()
            
            if not organizer:
                close_connection(conn)
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'message': 'Organizer not found'
                }, cls=DateTimeEncoder).encode())
                return
            
            # Verify venue exists (by ID or by name)
            if venue_id and str(venue_id).isdigit():
                cursor.execute("SELECT id, name FROM venues WHERE id = %s", (venue_id,))
                venue = cursor.fetchone()
                if not venue:
                    venue_id = None
            
            # If no valid venue ID, try to find by name or create new
            if not venue_id and venue_name:
                cursor.execute("SELECT id, name FROM venues WHERE name = %s", (venue_name,))
                venue = cursor.fetchone()
                if venue:
                    venue_id = venue['id']
                else:
                    # Create new venue with the provided name
                    cursor.execute("""
                        INSERT INTO venues (name, address, city, capacity, description)
                        VALUES (%s, 'Address Pending', 'Nairobi', 1000, 'Auto-created venue')
                    """, (venue_name,))
                    venue_id = cursor.lastrowid
                    conn.commit()
            elif not venue_id:
                # No venue provided, create default venue
                cursor.execute("""
                    INSERT INTO venues (name, address, city, capacity, description)
                    VALUES ('Default Venue', 'Nairobi', 'Nairobi', 1000, 'Auto-created default venue')
                """)
                venue_id = cursor.lastrowid
                conn.commit()
            
            # Insert the event
            cursor.execute("""
                INSERT INTO events (organizer_id, venue_id, title, description, category, event_date, standard_price, vip_price, image_url, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'published')
            """, (organizer_id, venue_id, title, description, category, event_date, standard_price, vip_price, image_url))
            
            event_id = cursor.lastrowid
            
            # Insert ticket types
            cursor.execute("""
                INSERT INTO ticket_types (event_id, type_name, price, available_quantity, sold_quantity)
                VALUES (%s, 'standard', %s, 1000, 0), (%s, 'vip', %s, 100, 0)
            """, (event_id, standard_price, event_id, vip_price))
            
            # Commit and close
            conn.commit()
            close_connection(conn)
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'message': 'Event created successfully',
                'data': {
                    'eventId': event_id,
                    'title': title,
                    'eventDate': event_date
                }
            }, cls=DateTimeEncoder).encode())
            
        except Exception as e:
            print(f"Error: {e}")
            try:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'message': str(e)
                }, cls=DateTimeEncoder).encode())
            except:
                pass
    
    def log_message(self, format, *args):
        """Override to disable default logging"""
        pass

if __name__ == '__main__':
    from http.server import HTTPServer
    
    server = HTTPServer(('localhost', 8000), CreateEventHandler)
    print("Create Event API running on http://localhost:8000")
    print("Use POST to /api_create_event.py")
    server.serve_forever()

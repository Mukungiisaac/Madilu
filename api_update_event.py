"""
API - Update Event Endpoint
Update an existing event
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

class UpdateEventHandler(BaseHTTPRequestHandler):
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
        """Handle POST requests to update events"""
        try:
            # Get POST data
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            
            # Convert to simple dict
            data = {k: v[0] for k, v in data.items()}
            
            # Validate required fields
            required_fields = ['eventId', 'title', 'description', 'category', 'eventDate', 'standardPrice', 'vipPrice']
            for field in required_fields:
                if field not in data or not data[field]:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'success': False,
                        'message': f'Missing required field: {field}'
                    }).encode())
                    return
            
            event_id = data['eventId']
            title = data['title']
            description = data['description']
            category = data['category']
            event_date = data['eventDate']
            standard_price = float(data['standardPrice'])
            vip_price = float(data['vipPrice'])
            venue_name = data.get('venueName', '')
            status = data.get('status', 'published')
            
            # Get database connection
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Verify event exists
            cursor.execute("SELECT id, organizer_id FROM events WHERE id = %s", (event_id,))
            event = cursor.fetchone()
            
            if not event:
                close_connection(conn)
                self.send_response(404)
                self.send_header('Content-Type', 'application/json')
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'message': 'Event not found'
                }).encode())
                return
            
            # Handle venue update
            if venue_name:
                cursor.execute("SELECT id FROM venues WHERE name = %s", (venue_name,))
                venue = cursor.fetchone()
                if venue:
                    venue_id = venue['id']
                else:
                    cursor.execute("""
                        INSERT INTO venues (name, address, city, capacity, description)
                        VALUES (%s, 'Address Pending', 'Nairobi', 1000, 'Auto-created venue')
                    """, (venue_name,))
                    venue_id = cursor.lastrowid
                    conn.commit()
            else:
                # Keep existing venue
                venue_id = event['venue_id']
            
            # Update event
            cursor.execute("""
                UPDATE events 
                SET title = %s, description = %s, category = %s, event_date = %s,
                    standard_price = %s, vip_price = %s, venue_id = %s, status = %s
                WHERE id = %s
            """, (title, description, category, event_date, standard_price, vip_price, venue_id, status, event_id))
            
            conn.commit()
            close_connection(conn)
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'message': 'Event updated successfully',
                'data': {
                    'eventId': event_id,
                    'title': title,
                    'status': status
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
                }).encode())
            except:
                pass
    
    def log_message(self, format, *args):
        """Override to disable default logging"""
        pass

if __name__ == '__main__':
    from http.server import HTTPServer
    
    server = HTTPServer(('localhost', 8000), UpdateEventHandler)
    print("Update Event API running on http://localhost:8000")
    print("Use POST to /api_update_event.py")
    server.serve_forever()

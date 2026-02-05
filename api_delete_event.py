"""
API - Delete Event Endpoint
Delete an existing event
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

class DeleteEventHandler(BaseHTTPRequestHandler):
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
        """Handle POST requests to delete events"""
        try:
            # Get POST data
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            
            # Convert to simple dict
            data = {k: v[0] for k, v in data.items()}
            
            # Validate required fields
            if 'eventId' not in data:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'message': 'Missing eventId parameter'
                }).encode())
                return
            
            event_id = data['eventId']
            
            # Get database connection
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Verify event exists
            cursor.execute("SELECT id, title FROM events WHERE id = %s", (event_id,))
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
            
            conn.commit()
            close_connection(conn)
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'message': 'Event deleted successfully',
                'data': {
                    'eventId': event_id,
                    'title': event['title']
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
    
    server = HTTPServer(('localhost', 8000), DeleteEventHandler)
    print("Delete Event API running on http://localhost:8000")
    print("Use POST to /api_delete_event.py")
    server.serve_forever()

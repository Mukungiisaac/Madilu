"""
API - Get Events Endpoint
Run with: python -m http.server 8000
Access at: http://localhost:8000/api_get_events.py
"""

import json
from db_connection import get_db_connection, close_connection, format_price
from http.server import BaseHTTPRequestHandler

class EventsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """
        Handle GET requests for events
        """
        try:
            # Get database connection
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Get all published events
            cursor.execute("""
                SELECT e.*, v.name as venue_name, v.address, v.city
                FROM events e
                JOIN venues v ON e.venue_id = v.id
                WHERE e.status = 'published' AND e.event_date >= NOW()
                ORDER BY e.event_date ASC
            """)
            events = cursor.fetchall()
            
            # Format data
            for event in events:
                event['standard_price_formatted'] = format_price(event['standard_price'])
                event['vip_price_formatted'] = format_price(event['vip_price'])
                event['event_date_formatted'] = event['event_date'].strftime('%b %d, %Y') if event['event_date'] else ''
                event['event_date'] = event['event_date'].isoformat() if event['event_date'] else None
            
            close_connection(conn)
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'data': events
            }).encode())
            
        except Exception as e:
            print(f"Error: {e}")
            try:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'message': str(e)
                }).encode())
            except:
                pass
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Override to disable default logging"""
        pass

if __name__ == '__main__':
    from http.server import HTTPServer
    
    server = HTTPServer(('localhost', 8000), EventsHandler)
    print("Events API running on http://localhost:8000")
    print("Use GET to /api_get_events.py")
    server.serve_forever()

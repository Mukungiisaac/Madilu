"""
API - Get Merchant Events Endpoint
Returns all events for a specific merchant/organizer
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

class GetMerchantEventsHandler(BaseHTTPRequestHandler):
    def send_cors_headers(self):
        """Send CORS headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests to get merchant events"""
        try:
            # Parse query parameters
            query_params = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query_params)
            merchant_id = params.get('merchantId', [None])[0]

            if not merchant_id:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'message': 'Missing merchantId parameter'
                }).encode())
                return

            # Get database connection
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # Get all events for this merchant
            cursor.execute("""
                SELECT e.*, v.name as venue_name, v.address, v.city
                FROM events e
                LEFT JOIN venues v ON e.venue_id = v.id
                WHERE e.organizer_id = %s
                ORDER BY e.created_at DESC
            """, (merchant_id,))
            
            events = cursor.fetchall()

            # Get ticket sales for each event
            for event in events:
                event['standard_price'] = float(event['standard_price'])
                event['vip_price'] = float(event['vip_price'])
                event['event_date'] = event['event_date'].isoformat() if event['event_date'] else None
                event['created_at'] = event['created_at'].isoformat() if event['created_at'] else None

                # Get ticket sales count
                cursor.execute("""
                    SELECT SUM(bt.quantity) as total_sold
                    FROM booking_tickets bt
                    JOIN ticket_types tt ON bt.ticket_type_id = tt.id
                    WHERE tt.event_id = %s
                """, (event['id'],))
                
                ticket_sales = cursor.fetchone()
                event['tickets_sold'] = ticket_sales['total_sold'] or 0

                # Calculate revenue
                event['revenue'] = float(event['standard_price']) * event['tickets_sold']

                # Placeholder for views (would need to be tracked separately)
                event['views'] = 0

            close_connection(conn)

            # Send success response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'data': events
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
    
    server = HTTPServer(('localhost', 8000), GetMerchantEventsHandler)
    print("Get Merchant Events API running on http://localhost:8000")
    print("Use GET to /api_get_merchant_events.py?merchantId=X")
    server.serve_forever()

#!/usr/bin/env python3
"""
Madilu Event Booking System - API Server
Run this script to start the API server
Usage: python server.py
"""

from http.server import HTTPServer, BaseHTTPRequestHandler, SimpleHTTPRequestHandler
import json
import urllib.parse
import os
from db_connection import get_db_connection, close_connection
from datetime import datetime

# DateTime Encoder for JSON
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# API Router
def handle_request(path, method, headers, post_data=None):
    """Route request to appropriate handler"""
    
    # Remove query parameters from path
    if '?' in path:
        path = path.split('?')[0]
    
    # API: Get Events
    if path == '/api_get_events.py' and method == 'GET':
        return handle_get_events()
    
    # API: Create Event
    if path == '/api_create_event.py' and method == 'POST':
        return handle_create_event(post_data)
    
    # API: Register Merchant
    if path == '/api_register_merchant.py' and method == 'POST':
        return handle_register_merchant(post_data)
    
    # API: Book Ticket
    if path == '/api_book_ticket.py' and method == 'POST':
        return handle_book_ticket(post_data)
    
    return {'status': 404, 'body': {'success': False, 'message': 'Not found'}}

def handle_get_events():
    """Handle GET /api_get_events.py"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT e.*, v.name as venue_name, v.address, v.city
            FROM events e
            JOIN venues v ON e.venue_id = v.id
            WHERE e.status = 'published' AND e.event_date >= NOW()
            ORDER BY e.event_date ASC
        """)
        events = cursor.fetchall()
        
        for event in events:
            event['standard_price'] = float(event['standard_price'])
            event['vip_price'] = float(event['vip_price'])
            event['event_date_formatted'] = event['event_date'].strftime('%b %d, %Y') if event['event_date'] else ''
            event['event_date'] = event['event_date'].isoformat() if event['event_date'] else None
        
        close_connection(conn)
        
        return {'status': 200, 'body': {'success': True, 'data': events}}
    
    except Exception as e:
        return {'status': 500, 'body': {'success': False, 'message': str(e)}}

def handle_create_event(post_data):
    """Handle POST /api_create_event.py"""
    try:
        data = urllib.parse.parse_qs(post_data.decode('utf-8'))
        data = {k: v[0] for k, v in data.items()}
        
        required_fields = ['organizerId', 'venueId', 'title', 'description', 'category', 'eventDate', 'standardPrice', 'vipPrice']
        for field in required_fields:
            if field not in data:
                return {'status': 400, 'body': {'success': False, 'message': f'Missing required field: {field}'}}
        
        organizer_id = int(data['organizerId'])
        venue_id = int(data['venueId'])
        title = data['title']
        description = data['description']
        category = data['category']
        event_date = data['eventDate']
        standard_price = float(data['standardPrice'])
        vip_price = float(data['vipPrice'])
        image_url = data.get('imageUrl', '')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verify organizer
        cursor.execute("SELECT id, user_type FROM users WHERE id = %s AND user_type = 'organizer'", (organizer_id,))
        if not cursor.fetchone():
            close_connection(conn)
            return {'status': 400, 'body': {'success': False, 'message': 'Organizer not found'}}
        
        # Verify venue
        cursor.execute("SELECT id FROM venues WHERE id = %s", (venue_id,))
        if not cursor.fetchone():
            # Auto-create venue
            cursor.execute("""
                INSERT INTO venues (name, address, city, capacity, description)
                VALUES ('Default Venue', 'Nairobi', 'Nairobi', 1000, 'Auto-created default venue')
            """)
            venue_id = cursor.lastrowid
            conn.commit()
        
        # Insert event
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
        
        conn.commit()
        close_connection(conn)
        
        return {'status': 200, 'body': {
            'success': True,
            'message': 'Event created successfully',
            'data': {'eventId': event_id, 'title': title, 'eventDate': event_date}
        }}
    
    except Exception as e:
        return {'status': 500, 'body': {'success': False, 'message': str(e)}}

def handle_register_merchant(post_data):
    """Handle POST /api_register_merchant.py"""
    try:
        data = urllib.parse.parse_qs(post_data.decode('utf-8'))
        data = {k: v[0] for k, v in data.items()}
        
        required_fields = ['fullName', 'email', 'phone', 'idNumber', 'password', 'companyName']
        for field in required_fields:
            if field not in data or not data[field]:
                return {'status': 400, 'body': {'success': False, 'message': f'Missing required field: {field}'}}
        
        full_name = data['fullName']
        email = data['email']
        phone = data['phone']
        id_number = data['idNumber']
        password = data['password']
        company_name = data['companyName']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Check email exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            close_connection(conn)
            return {'status': 400, 'body': {'success': False, 'message': 'Email already registered'}}
        
        # Insert user
        cursor.execute("""
            INSERT INTO users (full_name, email, phone, id_number, password, user_type)
            VALUES (%s, %s, %s, %s, %s, 'organizer')
        """, (full_name, email, phone, id_number, password))
        
        user_id = cursor.lastrowid
        conn.commit()
        close_connection(conn)
        
        return {'status': 200, 'body': {
            'success': True,
            'message': 'Merchant registered successfully',
            'data': {'id': user_id, 'fullName': full_name, 'email': email, 'companyName': company_name, 'userType': 'organizer'}
        }}
    
    except Exception as e:
        return {'status': 500, 'body': {'success': False, 'message': str(e)}}

def handle_book_ticket(post_data):
    """Handle POST /api_book_ticket.py"""
    try:
        data = urllib.parse.parse_qs(post_data.decode('utf-8'))
        data = {k: v[0] for k, v in data.items()}
        
        required_fields = ['eventId', 'fullName', 'email', 'phone', 'idNumber', 'standardQty', 'vipQty', 'totalAmount']
        for field in required_fields:
            if field not in data:
                return {'status': 400, 'body': {'success': False, 'message': f'Missing required field: {field}'}}
        
        event_id = int(data['eventId'])
        full_name = data['fullName']
        email = data['email']
        phone = data['phone']
        id_number = data['idNumber']
        standard_qty = int(data['standardQty'])
        vip_qty = int(data['vipQty'])
        total_amount = float(data['totalAmount'])
        payment_method = data.get('paymentMethod', 'mpesa')
        
        if standard_qty == 0 and vip_qty == 0:
            return {'status': 400, 'body': {'success': False, 'message': 'At least one ticket required'}}
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Generate booking reference
        import random
        import string
        ref = 'ITECH-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        # Insert booking
        cursor.execute("""
            INSERT INTO bookings (user_id, event_id, booking_reference, full_name, email, phone, id_number, total_amount, payment_method, payment_status)
            VALUES (1, %s, %s, %s, %s, %s, %s, %s, %s, 'completed')
        """, (event_id, ref, full_name, email, phone, id_number, total_amount, payment_method))
        
        booking_id = cursor.lastrowid
        
        # Get ticket types
        cursor.execute("SELECT id, type_name FROM ticket_types WHERE event_id = %s", (event_id,))
        ticket_types = cursor.fetchall()
        
        for tt in ticket_types:
            if tt['type_name'] == 'standard' and standard_qty > 0:
                cursor.execute("""
                    INSERT INTO booking_tickets (booking_id, ticket_type_id, quantity, unit_price, subtotal)
                    VALUES (%s, %s, %s, (SELECT standard_price FROM ticket_types WHERE id = %s), %s)
                """, (booking_id, tt['id'], standard_qty, tt['id'], standard_qty * float(data.get('standardPrice', 0))))
            elif tt['type_name'] == 'vip' and vip_qty > 0:
                cursor.execute("""
                    INSERT INTO booking_tickets (booking_id, ticket_type_id, quantity, unit_price, subtotal)
                    VALUES (%s, %s, %s, (SELECT vip_price FROM ticket_types WHERE id = %s), %s)
                """, (booking_id, tt['id'], vip_qty, tt['id'], vip_qty * float(data.get('vipPrice', 0))))
        
        conn.commit()
        close_connection(conn)
        
        return {'status': 200, 'body': {
            'success': True,
            'message': 'Booking successful',
            'data': {'bookingReference': ref, 'bookingId': booking_id}
        }}
    
    except Exception as e:
        return {'status': 500, 'body': {'success': False, 'message': str(e)}}

class APIHandler(BaseHTTPRequestHandler):
    """Custom HTTP request handler"""
    
    def do_GET(self):
        """Handle GET requests"""
        # Remove query parameters from path
        path = self.path
        if '?' in path:
            path = path.split('?')[0]
        
        print(f"GET request: path={path}")
        
        # Check if it's an API endpoint
        if path.startswith('/api_'):
            result = handle_request(path, 'GET', self.headers)
            self.send_response(result['status'])
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result['body'], cls=DateTimeEncoder).encode())
        else:
            # Serve static files
            file_path = '.' + path
            if path == '/':
                file_path = './index.html'
            
            if os.path.exists(file_path) and os.path.isfile(file_path):
                self.send_response(200)
                if file_path.endswith('.html'):
                    self.send_header('Content-Type', 'text/html')
                elif file_path.endswith('.css'):
                    self.send_header('Content-Type', 'text/css')
                elif file_path.endswith('.js'):
                    self.send_header('Content-Type', 'application/javascript')
                elif file_path.endswith('.png'):
                    self.send_header('Content-Type', 'image/png')
                elif file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
                    self.send_header('Content-Type', 'image/jpeg')
                else:
                    self.send_header('Content-Type', 'application/octet-stream')
                self.end_headers()
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<h1>404 - Not Found</h1><p>The requested file was not found.</p>')
    
    def do_POST(self):
        """Handle POST requests"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        # Remove query parameters from path
        path = self.path
        if '?' in path:
            path = path.split('?')[0]
        
        print(f"POST request: path={path}, data={post_data[:100]}")
        result = handle_request(path, 'POST', self.headers, post_data)
        self.send_response(result['status'])
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(result['body'], cls=DateTimeEncoder).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[{self.log_date_time_string()}] {args[0]}")

def run_server(port=8000):
    """Start the API server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, APIHandler)
    print(f"Madilu API Server running on http://localhost:{port}")
    print("Available endpoints:")
    print("  GET  /api_get_events.py       - Get all published events")
    print("  POST /api_create_event.py     - Create a new event")
    print("  POST /api_register_merchant.py - Register as merchant/organizer")
    print("  POST /api_book_ticket.py      - Book tickets for an event")
    print("\nPress Ctrl+C to stop the server")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        httpd.server_close()

if __name__ == '__main__':
    run_server()

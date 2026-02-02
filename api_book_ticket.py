"""
API - Book Ticket Endpoint
Run with: python -m http.server 8000
Access at: http://localhost:8000/api_book_ticket.py
"""

import json
from db_connection import get_db_connection, close_connection, generate_booking_reference
from http.server import BaseHTTPRequestHandler
import urllib.parse

class BookingHandler(BaseHTTPRequestHandler):
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
        Handle POST requests for booking tickets
        """
        try:
            # Get POST data
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            
            # Convert to simple dict
            data = {k: v[0] for k, v in data.items()}
            
            # Validate required fields
            required_fields = ['eventId', 'fullName', 'email', 'phone', 'idNumber']
            for field in required_fields:
                if field not in data:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'success': False,
                        'message': f'Missing required field: {field}'
                    }).encode())
                    return
            
            event_id = int(data['eventId'])
            full_name = data['fullName']
            email = data['email']
            phone = data['phone']
            id_number = data['idNumber']
            standard_qty = int(data.get('standardQty', 0))
            vip_qty = int(data.get('vipQty', 0))
            
            # Validate at least one ticket
            if standard_qty == 0 and vip_qty == 0:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'message': 'Please select at least one ticket'
                }).encode())
                return
            
            # Get database connection
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Get event details
            cursor.execute("SELECT * FROM events WHERE id = %s AND status = 'published'", (event_id,))
            event = cursor.fetchone()
            
            if not event:
                close_connection(conn)
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'message': 'Event not found or not available'
                }).encode())
                return
            
            # Calculate total
            total = (standard_qty * event['standard_price']) + (vip_qty * event['vip_price'])
            
            # Generate booking reference
            booking_ref = generate_booking_reference()
            
            # Check if user exists
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            
            if user:
                user_id = user['id']
            else:
                cursor.execute(
                    "INSERT INTO users (full_name, email, phone, id_number, user_type) VALUES (%s, %s, %s, %s, 'customer')",
                    (full_name, email, phone, id_number)
                )
                user_id = cursor.lastrowid
            
            # Create booking
            cursor.execute(
                """INSERT INTO bookings (user_id, event_id, booking_reference, full_name, email, phone, id_number, total_amount, payment_status)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'pending')""",
                (user_id, event_id, booking_ref, full_name, email, phone, id_number, total)
            )
            booking_id = cursor.lastrowid
            
            # Insert standard tickets
            if standard_qty > 0:
                cursor.execute("SELECT id FROM ticket_types WHERE event_id = %s AND type_name = 'standard'", (event_id,))
                ticket_type = cursor.fetchone()
                
                if not ticket_type:
                    cursor.execute(
                        "INSERT INTO ticket_types (event_id, type_name, price, available_quantity) VALUES (%s, 'standard', %s, 1000)",
                        (event_id, event['standard_price'])
                    )
                    ticket_type_id = cursor.lastrowid
                else:
                    ticket_type_id = ticket_type['id']
                
                cursor.execute(
                    "INSERT INTO booking_tickets (booking_id, ticket_type_id, quantity, unit_price, subtotal) VALUES (%s, %s, %s, %s, %s)",
                    (booking_id, ticket_type_id, standard_qty, event['standard_price'], standard_qty * event['standard_price'])
                )
                
                cursor.execute("UPDATE ticket_types SET sold_quantity = sold_quantity + %s WHERE id = %s", (standard_qty, ticket_type_id))
            
            # Insert VIP tickets
            if vip_qty > 0:
                cursor.execute("SELECT id FROM ticket_types WHERE event_id = %s AND type_name = 'vip'", (event_id,))
                ticket_type = cursor.fetchone()
                
                if not ticket_type:
                    cursor.execute(
                        "INSERT INTO ticket_types (event_id, type_name, price, available_quantity) VALUES (%s, 'vip', %s, 100)",
                        (event_id, event['vip_price'])
                    )
                    ticket_type_id = cursor.lastrowid
                else:
                    ticket_type_id = ticket_type['id']
                
                cursor.execute(
                    "INSERT INTO booking_tickets (booking_id, ticket_type_id, quantity, unit_price, subtotal) VALUES (%s, %s, %s, %s, %s)",
                    (booking_id, ticket_type_id, vip_qty, event['vip_price'], vip_qty * event['vip_price'])
                )
                
                cursor.execute("UPDATE ticket_types SET sold_quantity = sold_quantity + %s WHERE id = %s", (vip_qty, ticket_type_id))
            
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
                'message': 'Booking created successfully',
                'data': {
                    'bookingReference': booking_ref,
                    'totalAmount': total,
                    'eventTitle': event['title'],
                    'tickets': {
                        'standard': standard_qty,
                        'vip': vip_qty
                    }
                }
            }).encode())
            
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
    
    server = HTTPServer(('localhost', 8000), BookingHandler)
    print("Booking API running on http://localhost:8000")
    print("Use POST to /api_book_ticket.py")
    server.serve_forever()

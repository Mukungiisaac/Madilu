"""
API - Register Merchant Endpoint
Run with: python -m http.server 8000
Access at: http://localhost:8000/api_register_merchant.py
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

class RegisterMerchantHandler(BaseHTTPRequestHandler):
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
        Handle POST requests to register merchants
        """
        try:
            # Get POST data
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            
            # Convert to simple dict
            data = {k: v[0] for k, v in data.items()}
            
            # Validate required fields
            required_fields = ['fullName', 'email', 'phone', 'idNumber', 'password', 'companyName']
            for field in required_fields:
                if field not in data or not data[field]:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'success': False,
                        'message': f'Missing required field: {field}'
                    }, cls=DateTimeEncoder).encode())
                    return
            
            full_name = data['fullName']
            email = data['email']
            phone = data['phone']
            id_number = data['idNumber']
            password = data['password']
            company_name = data['companyName']
            business_type = data.get('businessType', 'events')
            
            # Get database connection
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Check if email already exists
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                close_connection(conn)
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'message': 'Email already registered'
                }, cls=DateTimeEncoder).encode())
                return
            
            # Insert the merchant/user
            cursor.execute("""
                INSERT INTO users (full_name, email, phone, id_number, password, user_type)
                VALUES (%s, %s, %s, %s, %s, 'organizer')
            """, (full_name, email, phone, id_number, password))
            
            user_id = cursor.lastrowid
            
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
                'message': 'Merchant registered successfully',
                'data': {
                    'id': user_id,
                    'fullName': full_name,
                    'email': email,
                    'companyName': company_name,
                    'userType': 'organizer'
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
    
    server = HTTPServer(('localhost', 8000), RegisterMerchantHandler)
    print("Register Merchant API running on http://localhost:8000")
    print("Use POST to /api_register_merchant.py")
    server.serve_forever()

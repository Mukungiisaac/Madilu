# Database Setup Guide (Python/MySQL)

## Prerequisites

1. **MySQL Client** - Install MySQL from [mysql.com](https://dev.mysql.com/downloads/installer/)
2. **Python 3.7+**
3. **MySQL Connector Python**:
   ```bash
   pip install mysql-connector-python
   ```

## Step 1: Create the Database

Open MySQL Client or command line:

```sql
-- Login to MySQL
mysql -u root -p

-- Create database
CREATE DATABASE itech_events;

-- Use the database
USE itech_events;

-- Import schema
SOURCE path/to/database.sql;
```

## Step 2: Configure Environment Variables

Create a `.env` file in the project root:

```env
DB_HOST=localhost
DB_NAME=itech_events
DB_USER=root
DB_PASS=your_password_here
DB_PORT=3306
```

Or set environment variables in your system.

## Step 3: Run the API Server

```bash
# Start the Python API server
python -m http.server 8000

# API will be available at:
# - GET events: http://localhost:8000/api_get_events.py
# - POST book: http://localhost:8000/api_book_ticket.py
```

## Python Files Overview

| File | Description |
|------|-------------|
| `db_connection.py` | Database connection module |
| `api_get_events.py` | GET endpoint to fetch events |
| `api_book_ticket.py` | POST endpoint to book tickets |

## Database Tables

| Table | Description |
|-------|-------------|
| `users` | Customers, organizers, admins |
| `venues` | Event venues/locations |
| `events` | Event listings |
| `ticket_types` | Standard and VIP tickets |
| `bookings` | Customer bookings |
| `booking_tickets` | Individual tickets |
| `payments` | Payment records |
| `categories` | Event categories |

## Sample Data

```sql
-- Add a sample venue
INSERT INTO venues (name, address, city, capacity) VALUES
('Nairobi Convention Center', 'Kenyatta ICC', 'Nairobi', 5000);

-- Add a sample event (create user first)
INSERT INTO users (full_name, email, phone, id_number, user_type) VALUES
('Admin', 'admin@itech.com', '254700000000', '12345678', 'organizer');

INSERT INTO events (organizer_id, venue_id, title, description, category, event_date, standard_price, vip_price, status) VALUES
(1, 1, 'Winter Music Festival 2024', 'Amazing music festival', 'music', '2024-12-15 19:00:00', 3250, 6500, 'published');

-- Add ticket types
INSERT INTO ticket_types (event_id, type_name, price, available_quantity) VALUES
(1, 'standard', 3250, 4000),
(1, 'vip', 6500, 500);
```

## API Usage Examples

### Get Events (JavaScript)
```javascript
fetch('http://localhost:8000/api_get_events.py')
  .then(res => res.json())
  .then(data => console.log(data));
```

### Book Tickets (JavaScript)
```javascript
fetch('http://localhost:8000/api_book_ticket.py', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: new URLSearchParams({
    eventId: 1,
    fullName: 'John Doe',
    email: 'john@example.com',
    phone: '254712345678',
    idNumber: '12345678',
    standardQty: 2,
    vipQty: 1
  })
})
  .then(res => res.json())
  .then(data => console.log(data));
```

## Testing with cURL

```bash
# Get events
curl http://localhost:8000/api_get_events.py

# Book tickets
curl -X POST http://localhost:8000/api_book_ticket.py \
  -d "eventId=1" \
  -d "fullName=John Doe" \
  -d "email=john@example.com" \
  -d "phone=254712345678" \
  -d "idNumber=12345678" \
  -d "standardQty=2" \
  -d "vipQty=1"
```

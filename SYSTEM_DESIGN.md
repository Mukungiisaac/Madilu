# Madilu Event Booking System - System Design

## Overview

The Madilu Event Booking System is a web-based platform for discovering and booking tickets to events. It follows a **client-server architecture** with a Python backend API and HTML/CSS/JavaScript frontend.

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                             │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                     index.html                             │  │
│  │  (Main HTML page with structure, modals, forms)           │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                     script.js                              │  │
│  │  (Client-side logic: API calls, DOM manipulation,         │  │
│  │   event handling, booking workflow)                        │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                     styles.css                            │  │
│  │  (All styling, animations, responsive design)              │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP Requests (GET/POST)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         SERVER LAYER                             │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                   server.py                                │  │
│  │  (Main HTTP server, request routing, static file serving) │  │
│  └───────────────────────────────────────────────────────────┘  │
│                        ▲        ▲                               │
│                        │        │                               │
│  ┌─────────────────────┴────┬───┴─────────────────────────────┐ │
│  │      API ENDPOINTS   │   │                              │ │
│  │  ┌────────────────┐  │   │  ┌────────────────────────┐   │ │
│  │  │ api_get_events │  │   │  │ db_connection.py        │   │ │
│  │  │ .py            │  │   │  │ (Database connection)   │   │ │
│  │  └────────────────┘  │   │  └────────────────────────┘   │ │
│  │  ┌────────────────┐  │   │                             │ │
│  │  │ api_book_ticket│  │   │                             │ │
│  │  │ .py            │  │   │                             │ │
│  │  └────────────────┘  │   │                             │ │
│  │  ┌────────────────┐  │   │                             │ │
│  │  │ api_create_    │  │   │                             │ │
│  │  │ event.py       │  │   │                             │ │
│  │  └────────────────┘  │   │                             │ │
│  │  ┌────────────────┐  │   │                             │ │
│  │  │ api_register_  │  │   │                             │ │
│  │  │ merchant.py    │  │   │                             │ │
│  │  └────────────────┘  │   │                             │ │
│  └───────────────────────┴───┴───────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ MySQL Queries
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATABASE LAYER                              │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                   MySQL Database                          │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │  │
│  │  │  users   │ │  venues  │ │  events  │ │ bookings │    │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘    │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐                │  │
│  │  │ ticket_  │ │payments  │ │categories│                │  │
│  │  │ types    │ └──────────┘ └──────────┘                │  │
│  │  └──────────┘                                          │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## File Interaction Flow

### 1. Startup Flow

```
User runs: python server.py
         │
         ▼
┌──────────────────┐
│   server.py      │ ◄── Main entry point
│   (port 8000)    │
└────────┬─────────┘
         │
         ├─ Imports db_connection.py
         │         │
         │         ▼
         │   ┌─────────────────┐
         │   │ db_connection.py│ ◄── Loads .env file
         │   └────────┬────────┘         Gets DB credentials
         │            │
         │            ▼
         │      ┌────────────────┐
         │      │   MySQL DB     │ ◄── Establishes connection
         │      └────────────────┘
         │
         ▼
Server starts listening on http://localhost:8000
```

### 2. Page Load Flow (Static Files)

```
Browser requests: http://localhost:8000/
                  │
                  ▼
         ┌─────────────────┐
         │   server.py     │ ◄── Matches route "/"
         └────────┬────────┘
                  │
                  ▼
         ┌─────────────────┐
         │   index.html    │ ◄── Serves static file
         └────────┬────────┘
                  │
                  │ HTML references:
                  │ - styles.css
                  │ - script.js
                  │ - images/*.jpg
                  ▼
         ┌─────────────────┐
         │   script.js    │ ◄── Executes on DOMContentLoaded
         └────────┬────────┘
                  │
                  ├─ fetchEvents() ──┐
                  │                  │
                  ▼                  ▼
         ┌─────────────────┐  ┌─────────────────┐
         │  server.py      │  │  styles.css     │ ◄── Applies styles
         │ (API endpoint)  │  └─────────────────┘
         └────────┬────────┘
                  │
                  ▼
         ┌─────────────────┐
         │  api_get_events │ ◄── Handler in server.py
         │     function    │     (no separate file needed)
         └────────┬────────┘
                  │
                  ▼
         ┌─────────────────┐
         │ db_connection.py│ ◄── get_db_connection()
         └────────┬────────┘
                  │
                  ▼
         ┌─────────────────┐
         │  MySQL Query    │ ◄── SELECT * FROM events
         │                 │     JOIN venues
         └─────────────────┘
                  │
                  ▼
         ┌─────────────────┐
         │ JSON Response   │ ◄── [{event1}, {event2}, ...]
         └────────┬────────┘
                  │
                  ▼
         ┌─────────────────┐
         │  script.js      │ ◄── generateEventCards(data)
         │  (Updates DOM)   │
         └─────────────────┘
```

### 3. Booking Flow

```
User clicks "Get Tickets"
         │
         ▼
┌─────────────────┐
│   script.js     │ ◄── Button click handler
└────────┬────────┘
         │
         ├─ Opens modal
         │  (ticketModal div)
         │
         ▼
User fills booking form
         │
         ├─ standardQty, vipQty
         ├─ fullName, email
         ├─ phone, idNumber
         │
         ▼
User clicks "Proceed to Payment"
         │
         ▼
┌─────────────────────────────────┐
│     api_book_ticket() in        │ ◄── Form submission handler
│     server.py                   │     (POST request)
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│     script.js                   │ ◄── fetch() POST request
│     processPayment()             │     with form data
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│     server.py                   │ ◄── Routes to handle_book_ticket()
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│     db_connection.py            │ ◄── get_db_connection()
│     (transaction)                │     insert into bookings
             │                     │     insert into booking_tickets
             ▼                     │     update ticket_types
┌────────────────────────────────┐│
│  MySQL (in transaction)        ││
│  ┌──────────────────────────┐  ││
│  │ INSERT INTO bookings     │  ││
│  │ INSERT INTO booking_tickets│ │
│  │ INSERT INTO payments     │  ││
│  │ UPDATE ticket_types      │◄─┘│
│  └──────────────────────────┘   │
└─────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│     JSON Response               │ ◄── {success: true, bookingRef: "..."}
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│     script.js                   │ ◄── showSuccessStep()
│     (Updates UI)                │     Displays receipt
└─────────────────────────────────┘
```

---

## File Descriptions

### Frontend Layer

| File | Purpose | Key Functions |
|------|---------|---------------|
| [`index.html`](index.html) | Main HTML page | Structure, modals, forms |
| [`script.js`](script.js) | Client-side logic | `fetchEvents()`, `processPayment()`, `generateEventCards()` |
| [`styles.css`](styles.css) | Styling | Animations, responsive design |

### Backend Layer

| File | Purpose | Key Functions |
|------|---------|---------------|
| [`server.py`](server.py) | HTTP server & router | `run_server()`, `handle_request()`, API handlers |
| [`db_connection.py`](db_connection.py) | Database utilities | `get_db_connection()`, `close_connection()` |
| [`setup_database.py`](setup_database.py) | Database initialization | `setup_database()` |

### Database

| File | Purpose |
|------|---------|
| [`database.sql`](database.sql) | Schema definitions |
| [`DATABASE_README.md`](DATABASE_README.md) | Database documentation |

### Configuration

| File | Purpose |
|------|---------|
| [`.env`](.env) | Environment variables (DB credentials) |

---

## Database Schema

```
┌──────────────────────────────────────────────────────────────┐
│                         users                                 │
│  id, full_name, email, phone, id_number, password, user_type  │
│  (customer, organizer, admin)                                │
└──────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│      venues      │ │      events       │ │     bookings     │
│ id, name,        │ │ id, organizer_id, │ │ id, user_id,     │
│ address, city,   │ │ venue_id, title,  │ │ event_id,        │
│ capacity, desc   │ │ description,      │ │ booking_reference│
│                  │ │ category, date,   │ │ full_name,       │
│                  │ │ prices, status    │ │ email, total_amt │
└──────────────────┘ └──────────────────┘ └─────────┬────────┘
                                                    │
                                                    ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│   ticket_types   │ │    payments      │ │  booking_tickets │
│ id, event_id,    │ │ id, booking_id,   │ │ id, booking_id,  │
│ type_name, price,│ │ amount, method,   │ │ ticket_type_id, │
│ quantity, sold   │ │ status, trans_id  │ │ quantity, price  │
└──────────────────┘ └──────────────────┘ └──────────────────┘
```

---

## API Endpoints

| Method | Endpoint | Handler Function | Description |
|--------|----------|-----------------|-------------|
| GET | `/api_get_events.py` | `handle_get_events()` | Fetch published events |
| POST | `/api_create_event.py` | `handle_create_event()` | Create new event |
| POST | `/api_register_merchant.py` | `handle_register_merchant()` | Register organizer |
| POST | `/api_book_ticket.py` | `handle_book_ticket()` | Book tickets |

---

## Data Flow Summary

### Event Discovery Flow
```
Browser → GET / → server.py → index.html → script.js
                                          ↓
                                    GET /api_get_events.py
                                          ↓
                                    server.py → db_connection.py
                                          ↓
                                    MySQL → JSON → DOM Update
```

### Booking Flow
```
Browser (Form) → POST /api_book_ticket.py → server.py
                                          ↓
                                    db_connection.py
                                          ↓
                                    MySQL (transaction)
                                          ↓
                                    JSON Response → Browser (Receipt)
```

---

## Key Design Patterns

1. **Separation of Concerns**: Static files served separately from API logic
2. **Database Abstraction**: All DB operations go through `db_connection.py`
3. **Request Routing**: Centralized in `server.py` using path-based routing
4. **Form Data Parsing**: Uses `urllib.parse.parse_qs()` for POST data
5. **Error Handling**: Try-catch blocks return consistent JSON error responses
6. **CORS Support**: Headers allow cross-origin requests

---

## Dependencies

### Python Packages
- `mysql-connector-python` - MySQL database driver
- `python-dotenv` - Environment variable loading (optional)

### External Libraries
- Font Awesome 6.4 - Icons (CDN)

### Database
- MySQL 5.7+ or MySQL 8.0

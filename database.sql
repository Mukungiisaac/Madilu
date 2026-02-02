-- iTech Events Database Schema
-- Create database
CREATE DATABASE IF NOT EXISTS itech_events;
USE itech_events;

-- Users table (customers and organizers)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    id_number VARCHAR(20) NOT NULL,
    password VARCHAR(255) NOT NULL,
    user_type ENUM('customer', 'organizer', 'admin') DEFAULT 'customer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Venues table
CREATE TABLE venues (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    address VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    capacity INT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Events table
CREATE TABLE events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    organizer_id INT NOT NULL,
    venue_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    category ENUM('music', 'sports', 'arts', 'business', 'food', 'tech') NOT NULL,
    event_date DATETIME NOT NULL,
    standard_price DECIMAL(10,2) NOT NULL,
    vip_price DECIMAL(10,2) NOT NULL,
    image_url VARCHAR(255),
    status ENUM('draft', 'published', 'cancelled', 'completed') DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organizer_id) REFERENCES users(id),
    FOREIGN KEY (venue_id) REFERENCES venues(id)
);

-- Ticket types table
CREATE TABLE ticket_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    type_name ENUM('standard', 'vip') NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    available_quantity INT NOT NULL,
    sold_quantity INT DEFAULT 0,
    FOREIGN KEY (event_id) REFERENCES events(id)
);

-- Bookings table
CREATE TABLE bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    event_id INT NOT NULL,
    booking_reference VARCHAR(20) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    id_number VARCHAR(20) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    payment_status ENUM('pending', 'completed', 'failed', 'refunded') DEFAULT 'pending',
    payment_method ENUM('mpesa', 'card', 'airtel') DEFAULT 'mpesa',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (event_id) REFERENCES events(id)
);

-- Booking tickets table (for mixed ticket bookings)
CREATE TABLE booking_tickets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    ticket_type_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (booking_id) REFERENCES bookings(id),
    FOREIGN KEY (ticket_type_id) REFERENCES ticket_types(id)
);

-- Payments table
CREATE TABLE payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    transaction_id VARCHAR(100),
    payment_status ENUM('pending', 'completed', 'failed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(id)
);

-- Categories table
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    icon VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default categories
INSERT INTO categories (name, icon) VALUES
('music', 'fa-guitar'),
('sports', 'fa-running'),
('arts', 'fa-mask'),
('business', 'fa-briefcase'),
('food', 'fa-utensils'),
('tech', 'fa-microchip');

-- Indexes for better performance
CREATE INDEX idx_events_date ON events(event_date);
CREATE INDEX idx_events_category ON events(category);
CREATE INDEX idx_bookings_reference ON bookings(booking_reference);
CREATE INDEX idx_bookings_user ON bookings(user_id);
CREATE INDEX idx_payments_booking ON payments(booking_id);
